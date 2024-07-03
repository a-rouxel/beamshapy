import numpy as np
import time
from LightPipes import CircAperture, CircScreen, GaussScreen, GaussAperture, GaussBeam
from LightPipes import Begin,  Intensity, Phase, PlaneWave, SubIntensity, SubPhase, MultPhase
from LightPipes import PipFFT
from LightPipes import Field,  mm, nm, um

from beamshapy.mask_generation.MaskGenerator import MaskGenerator
from beamshapy.amplitude_generation.AmplitudeGenerator import AmplitudeGenerator
from beamshapy.intensity_generation.IntensityGenerator import IntensityGenerator


class BeamShaper():

    """Class that contains the main attributes and methods to simulate beam shaping simulations"""

    def __init__(self,simulation_config,input_beam_config,optical_system_config):
        """
        Initialization of the main attributes : Mask Generator and Amplitude Generator.
        We also calculate and set the spatial sampling of the system in the different planes of interest based on the simulation configuration and on the optical system configuration.

        Args:
            simulation_config (dict): simulation configuration
            input_beam_config (dict): input beam configuration
            optical_system_config (dict): optical system configuration
        """

        self.simulation_config = simulation_config
        self.input_beam_config = input_beam_config
        self.optical_system_config = optical_system_config

        self.mask_generator = MaskGenerator(self)
        self.mask_generator.generate_correction_tab()

        self.amplitude_generator = AmplitudeGenerator(self)
        self.intensity_generator = IntensityGenerator(self)

        self.generate_sampling(simulation_config,input_beam_config,optical_system_config)

    def generate_input_beam(self,input_beam_config):

        """
        Generate the input beam field based on the input beam configuration. We use LightPipes to generate the field.
        Note : the input beam field power (integral of Intensity) is normalized to 100000 for numerical stability purposes.

        Args:
            input_beam_config (dict): input beam configuration

        Returns:
            Fin: input beam field
        """

        self.input_waist = input_beam_config["beam"]["waist"]*mm
        self.input_beam_type = input_beam_config["beam"]["type"]
        self.input_LG = input_beam_config["beam"]["LG"]
        self.input_n = input_beam_config["beam"]["n"]
        self.input_m = input_beam_config["beam"]["m"]


        F = Begin(self.input_grid_size, self.input_wavelength,  self.nb_of_samples)


        if self.input_beam_type == "Gaussian":

            F = GaussBeam(F,
                          w0=self.input_waist,
                          LG=self.input_LG,
                          n=self.input_n,
                          m=self.input_m)

        elif self.input_beam_type == "Plane":

            F = PlaneWave(F, w=self.input_waist*2)
        else:
            raise ValueError("Unknown field type")

        self.input_beam = F
        self.input_beam = self.normalize_field_power(self.input_beam)
        self.input_power = np.sum(np.sum(Intensity(self.input_beam)))

        return self.input_beam

    def generate_sampling(self,simulation_config,input_beam_config,optical_system_config):

        """
        Generate the sampling of the system in the different planes of interest based on the simulation configuration and on the optical system configuration.

        Args:
            simulation_config (dict): simulation configuration
            input_beam_config (dict): input beam configuration
            optical_system_config (dict): optical system configuration

        Returns:
            dict: dictionary containing the sampling of the system in the different planes of interest
                * delta_x_in (m) : distance between spatial samples in the input plane
                * delta_x_out (m) : distance between spatial samples in the output plane
                * x_array_in (m) : array of spatial coordinates in the input plane
                * x_array_out (m) : array of spatial coordinates in the output plane
                * GridPositionMatrix_X_in (m) : Grid matrix of spatial coordinates in the Input plane
                * GridPositionMatrix_Y_in (m) : Grid matrix of spatial coordinates in the Input plane
                * GridPositionMatrix_X_out (m) : Grid matrix of spatial coordinates in the Fourier Plane (Fourier conjugate)
                * GridPositionMatrix_Y_out (m) : Grid matrix of spatial coordinates in the Fourier Plane (Fourier conjugate)
        """

        self.input_grid_size = simulation_config["grid size"]*mm
        self.input_grid_sampling = simulation_config["grid sampling"] *um
        self.nb_of_samples = int(self.input_grid_size//self.input_grid_sampling)
        self.input_wavelength = input_beam_config["beam"]["wavelength"]*nm
        self.focal_length = optical_system_config["focal length"]*mm

        delta_x_in = self.input_grid_sampling
        delta_x_out = self.input_wavelength * self.focal_length / (self.input_grid_size)

        x_array_in = np.round(np.linspace(-self.input_grid_size / 2, self.input_grid_size / 2, self.nb_of_samples), 9)

        x_array_out = np.arange(-self.nb_of_samples / 2, self.nb_of_samples / 2, 1)
        x_array_out *= delta_x_out

        GridPositionMatrix_X_in, GridPositionMatrix_Y_in = np.meshgrid(x_array_in, x_array_in)
        GridPositionMatrix_X_out, GridPositionMatrix_Y_out = np.meshgrid(x_array_out, x_array_out)


        self.delta_x_in = delta_x_in
        self.delta_x_out = delta_x_out
        self.x_array_in = x_array_in
        self.x_array_out = x_array_out
        self.GridPositionMatrix_X_in = GridPositionMatrix_X_in
        self.GridPositionMatrix_Y_in = GridPositionMatrix_Y_in
        self.GridPositionMatrix_X_out = GridPositionMatrix_X_out
        self.GridPositionMatrix_Y_out = GridPositionMatrix_Y_out

        sampling_dict = {"delta_x_in":self.delta_x_in,
                             "delta_x_out":self.delta_x_out,
                             "x_array_in":self.x_array_in,
                             "x_array_out":self.x_array_out,
                             "GridPositionMatrix_X_in":self.GridPositionMatrix_X_in,
                             "GridPositionMatrix_Y_in":self.GridPositionMatrix_Y_in,
                             "GridPositionMatrix_X_out":self.GridPositionMatrix_X_out,
                             "GridPositionMatrix_Y_out":self.GridPositionMatrix_Y_out}

        return sampling_dict


    def inverse_fourier_transform(self,complex_amplitude,inverse_fourier_type="PipFFT"):
        
        """
        Perform the inverse Fourier transform of the complex amplitude in the Fourier Plane to obtain the field in the input beam plane.
        Note that the phase of the complex amplitude is thresholded to avoid numerical errors. See phase_thresholder function for more details
        Note that the inverse Fourier transform is performed with the PipFFT function of the LightPipes.

        Args:
            complex_amplitude (np.ndarray): complex amplitude in the Fourier plane.

        Returns:
            Fin: inverse Fourier transform of the complex amplitude.
        """

        # check if complex amplitude has same dimensions as GridPositionMatrix
        if complex_amplitude.shape != self.GridPositionMatrix_X_in.shape:
            raise ValueError("Complex amplitude must have same dimensions as GridPositionMatrix")

        self.target_field = SubIntensity(self.input_beam,np.abs(complex_amplitude)**2)
        self.target_field = SubPhase(self.target_field,np.angle(complex_amplitude))

        if inverse_fourier_type == "PipFFT":
            self.inverse_fourier_target_field = PipFFT(self.target_field , -1)
            return None

        self.inverse_fourier_target_field = self.phase_thresholder(self.inverse_fourier_target_field)

        return self.inverse_fourier_target_field


    def phase_thresholder(self,field,threshold=10**-9):

        """
        Threshold the phase of the field to avoid numerical errors. The phase is thresholded to 0 or pi if values are close (threshold to 10^-9 by defaults)

        Args:
            field (Fin): field to threshold
            threshold (float): threshold value (default: 10^-9)

        Returns:
            Fin: thresholded field

        """

        phase = Phase(field)
        phase[np.pi - np.abs(phase)<threshold] = np.pi
        phase[np.abs(phase)<threshold] = 0
        thresh_field = SubPhase(field,phase)

        return thresh_field

    def normalize_field_power(self,field,norm_value=100000):

        """
        Normalize the field power (integral of density) to a given value (default: 100000)

        Args:
            field (Fin): field to normalize
            norm_value (float): value to normalize the field power to (default: 100000)

        Returns:
            Fin: normalized field

        """

        field_power = np.sum(np.sum(Intensity(field)))
        normalized_intensity = Intensity(field) * norm_value / field_power
        normalized_field = SubIntensity(field,normalized_intensity)


        return normalized_field

    def normalize_field_intensity_by_max_input(self,field):

        """
        Normalize the field intensity by the maximum intensity of the input beam

        Args:
            field (Fin): field to normalize

        Returns:
            Fin: normalized field

        """
        max_input_value = Intensity(self.input_beam).max()
        max_target_value = Intensity(field).max()
        normalized_field = SubIntensity(field,Intensity(field)*max_input_value/max_target_value)

        return normalized_field

    def get_field_phase(self,field):

        """
        Get the phase of a given field

        Args:
            field (Fin): field to get the phase from

        Returns:
            array: phase of the field

        """

        return Phase(field)

    def generate_target_field_from_intensity(self,target_intensity_profile):

        if target_intensity_profile.shape != self.GridPositionMatrix_X_out.shape:
            raise ValueError("Target Intensity must have same dimensions as GridPositionMatrix")

        self.target_field = Field.copy(self.input_beam)
        self.target_field = SubIntensity(self.target_field,target_intensity_profile)

        target_phase = np.zeros(self.GridPositionMatrix_X_out.shape)
        self.target_field = SubPhase(self.target_field,target_phase)
        self.target_field = self.normalize_field_power(self.target_field)

        return self.target_field




    def phase_modulate_input_beam(self,mask):

        """
        Modulate the phase of the input beam with a given phase mask

        Args:
            mask (array): phase mask to apply to the input beam

        Returns:
            Fin: modulated beam

        """

        self.modulated_input_beam = MultPhase(self.input_beam,mask)

        return self.modulated_input_beam



    def propagate_FFT_modulated_beam(self,propagation_type="PipFFT"):

        """
        Propagate the modulated beam with the Fourier transform. We use the PipFFT function of the LightPipes library.

        Args:
            propagation_type (str): type of propagation to use (default: "PipFFT")

        Returns:
            Fin: propagated beam in the Fourier plane

        """

        if propagation_type == "PipFFT":
            self.propagated_beam_fourier = PipFFT(self.modulated_input_beam)
        else:
            pass

        self.propagated_beam_fourier = self.normalize_field_power(self.propagated_beam_fourier,self.input_power)

        return self.propagated_beam_fourier

    def filter_beam(self,filter_type=None,pos_x=0,pos_y=0,radius=0):

        """
        Filter the beam in the Fourier plane with a given filter type and parameters

        Args:
            filter_type (str): type of filter to apply (default: None)
            pos_x (float): x position of the filter in mm  (default: 0)
            pos_y (float): y position of the filter in mm (default: 0)
            radius (float): radius of the filterin mm  (default: 0)

        Returns:
            Fin: filtered beam in the Fourier plane

        """

        pos_y *= -1

        if filter_type == "CircScreen":

            self.filtered_beam_fourier = CircScreen(Fin=self.propagated_beam_fourier,
                                                      R=radius,
                                                      x_shift=pos_x,
                                                      y_shift=pos_y)
        elif filter_type == "GaussScreen":
            self.filtered_beam_fourier = GaussScreen(Fin=self.propagated_beam_fourier,
                                                      w=radius,
                                                      x_shift=pos_x,
                                                      y_shift=pos_y)

        elif filter_type == "CircAperture":
            self.filtered_beam_fourier = CircAperture(Fin=self.propagated_beam_fourier,
                                                        R=radius,
                                                        x_shift=pos_x,
                                                        y_shift=pos_y)

        elif filter_type == "GaussAperture":
            self.filtered_beam_fourier = GaussAperture(Fin=self.propagated_beam_fourier,
                                                        w=radius,
                                                        x_shift=pos_x,
                                                        y_shift=pos_y)


        else:
            self.filtered_beam_fourier = self.propagated_beam_fourier

        self.input_power_filtered = np.sum(np.sum(Intensity(self.filtered_beam_fourier)))


        return self.filtered_beam_fourier

    def propagate_FFT_to_image_plane(self,propagation_type="PipFFT"):

        """
        Propagate the filtered beam to the Image Plane with the Fourier transform. We use the PipFFT function of the LightPipes library.

        Args:
            propagation_type (str): type of propagation to use (default: "PipFFT")

        Returns:
            Fin: propagated beam in the Image plane

        """

        if propagation_type == "PipFFT":
            self.propagated_beam_image = PipFFT(self.filtered_beam_fourier)
        else:
            pass

        self.propagated_beam_image = self.normalize_field_power(self.propagated_beam_image,self.input_power_filtered)
        self.propagated_beam_image._set_grid_size(self.input_grid_size)

        return self.propagated_beam_image
