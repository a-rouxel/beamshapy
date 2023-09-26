import numpy as np
import yaml
from LightPipes import *
from utils import *
from scipy import interpolate
from skimage.measure import block_reduce
class BeamShaper():

    def __init__(self,simulation_config,input_beam_config,initial_config_file):
        self.simulation_config = simulation_config
        self.input_beam_config = input_beam_config
        self.initial_config_file = initial_config_file

        # Load the initial configuration file if one was provided
        if self.initial_config_file is not None:
            self.load_config(self.initial_config_file)

        self.generate_sampling(simulation_config,input_beam_config)
        self.generate_correction_tab(nb_of_samples=1000,func=root_theorical_deformation_sinc)

    def generate_input_beam(self,input_beam_config):

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
        self.input_beam = self.normalize_field_by_100000(self.input_beam)
        self.power = np.sum(np.sum(Intensity(self.input_beam)))

        return F

    def generate_sampling(self,simulation_config,input_beam_config):

        self.input_grid_size = simulation_config["grid size"]*mm
        self.input_grid_sampling = simulation_config["grid sampling"] *um
        self.nb_of_samples = int(self.input_grid_size//self.input_grid_sampling)
        self.input_wavelength = input_beam_config["beam"]["wavelength"]*nm

        self.focal_length = self.config["focal length"]*mm

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

    def generate_correction_tab(self,nb_of_samples=1000,func=root_theorical_deformation_sinc):
        a_values, correction_tab = generate_correction_tab(nb_of_samples, func=func)
        self.correction_tab = correction_tab
        self.correction_a_values = a_values

        return a_values, correction_tab
    def generate_mask(self,mask_type,period=None,position = None, charge=None,orientation=None,angle = None, width = None, height = None, sigma_x=None,sigma_y=None,threshold=None,mask_path=None,amplitude_factor=1):


        if self.x_array_in is None:
            raise ValueError("Please generate Input Beam first")

        if mask_type == "Grating":
            M1 = Simple1DBlazedGratingMask(self.x_array_in, period)
            mask = np.tile(M1, (self.nb_of_samples, 1))
            if orientation== "Vertical":
                mask = np.transpose(mask)
            return mask

        if mask_type == "Gaussian":

            sigma_x *= 10**-6
            sigma_y *= 10**-6

            if sigma_x is None or sigma_y is None:
                raise ValueError("Please provide values for sigma_x and sigma_y for the Gaussian mask.")

            x, y = np.meshgrid(self.x_array_in, self.x_array_in)
            mask = np.exp(-((x) ** 2 / (2 * sigma_x ** 2) + (y) ** 2 / (2 * sigma_y ** 2)))

            return mask

        if mask_type == "Vortex":
            mask = VortexMask(self.x_array_in, charge)

            return mask

        if mask_type == "Wedge":
            x_proj = np.cos(angle)*position
            y_proj = np.sin(angle)*position

            mask_x = Simple2DWedgeMask(self.x_array_in,self.input_wavelength,x_proj,self.focal_length)
            mask_y = np.flip(np.transpose(Simple2DWedgeMask(self.x_array_in,self.input_wavelength,y_proj,self.focal_length)),0)
            mask = mask_x + mask_y

            return mask

        if mask_type == "ϕ target field":
            target_field = self.inverse_fourier_target_field
            mask = self.get_field_phase(target_field)
            return mask

        if mask_type == "modulation amplitude":
            normalized_target_field = self.normalize_both_field_intensity(self.inverse_fourier_target_field)
            target_abs_amplitude = np.sqrt(Intensity(normalized_target_field)) * amplitude_factor
            input_abs_amplitude = np.sqrt(Intensity(self.input_beam))
            print("input amplitude",np.max(input_abs_amplitude))
            print("target amplitude",np.max(target_abs_amplitude))
            mask = WeightsMask(input_abs_amplitude,target_abs_amplitude,threshold)
            return mask


        if mask_type == "Rect Amplitude":
            mask = RectangularAmplitudeMask(self.GridPositionMatrix_X_in,self.GridPositionMatrix_Y_in,angle, width,height)
            return mask

        if mask_type == "Phase Jump":
            mask = PiPhaseJumpMask(self.GridPositionMatrix_X_in,self.GridPositionMatrix_Y_in,orientation, position)
            return mask

        if mask_type == "Phase Reversal":
            self.sigma_x = sigma_x
            self.sigma_y = sigma_y
            mask = PhaseReversalMask(self.GridPositionMatrix_X_in,self.GridPositionMatrix_Y_in,self.input_waist,sigma_x,sigma_y)
            self.phase_inversed_Field = SubPhase(self.input_beam,mask)

            return mask

        if mask_type == "Weights Sinc":
            sinc_mask_x = sinc_resized(self.GridPositionMatrix_X_in, self.input_waist*self.sigma_x)
            sinc_mask_y = sinc_resized(self.GridPositionMatrix_Y_in, self.input_waist*self.sigma_y)
            target_amplitude = sinc_mask_x*sinc_mask_y

            input_amplitude = self.phase_inversed_Field.field.real


            mask = WeightsMask(input_amplitude,target_amplitude,threshold)
            return mask


        if mask_type == "Custom h5 Mask":
            if mask_path is None:
                raise ValueError("Please provide h5 file path for custom mask.")

            with h5py.File(mask_path, 'r') as f:
                mask = f['mask'][:]

            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            if mask.shape != self.GridPositionMatrix_X_in.shape:
                new_mask = np.zeros_like(self.GridPositionMatrix_X_in)
                x_offset = (new_mask.shape[0] - mask.shape[0]) // 2
                y_offset = (new_mask.shape[1] - mask.shape[1]) // 2
                new_mask[x_offset: x_offset + mask.shape[0], y_offset: y_offset + mask.shape[1]] = mask
                mask = new_mask

            else:
                print("mask_type not recognized")
            return mask

    def generate_target_amplitude(self,amplitude_type, period=None,position = None, scale_factor=1,orientation=None,angle = None, width = None, height = None, sigma_x=None,sigma_y=None,threshold=None,amplitude_path=None,phase_offset=0):
        if self.x_array_in is None:
            raise ValueError("Please generate Input Beam first")

        if amplitude_type == "Rectangle":
            amplitude = RectangularAmplitudeMask(self.GridPositionMatrix_X_out,self.GridPositionMatrix_Y_out,angle, width,height)
            return amplitude

        if amplitude_type == "Wedge":
            x_proj = np.cos(angle)*position
            y_proj = np.sin(angle)*position

            amplitude_x = Simple2DWedgeMask(self.x_array_in,self.input_wavelength,x_proj,self.focal_length)
            amplitude_y = np.flip(np.transpose(Simple2DWedgeMask(self.x_array_in,self.input_wavelength,y_proj,self.focal_length)),0)
            amplitude = amplitude_x + amplitude_y

            return amplitude

        if amplitude_type == "Sinus":
            amplitude = SinusAmplitudeArray(self.GridPositionMatrix_X_out,self.GridPositionMatrix_Y_out,period,angle,phase_offset)
            return amplitude

        if amplitude_type == "Cosinus":
            amplitude = CosinusAmplitudeArray(self.GridPositionMatrix_X_out,self.GridPositionMatrix_Y_out,period,angle)
            return amplitude

        if amplitude_type == "Custom h5 Amplitude":

            if amplitude_path =='':
                return

            with h5py.File(amplitude_path, 'r') as f:
                mask = f['amplitude'][:]

            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            if mask.shape != self.GridPositionMatrix_X_in.shape:
                new_mask = np.zeros_like(self.GridPositionMatrix_X_in)
                x_offset = (new_mask.shape[0] - mask.shape[0]) // 2
                y_offset = (new_mask.shape[1] - mask.shape[1]) // 2
                new_mask[x_offset: x_offset + mask.shape[0], y_offset: y_offset + mask.shape[1]] = mask
                mask = new_mask



            # Get original shape
            original_shape = mask.shape

            if scale_factor > 1:
                # First crop
                crop_size = (int(original_shape[0] / scale_factor), int(original_shape[1] / scale_factor))
                startx = original_shape[1] // 2 - (crop_size[1] // 2)
                starty = original_shape[0] // 2 - (crop_size[0] // 2)
                mask = mask[starty:starty + crop_size[0], startx:startx + crop_size[1]]

            elif scale_factor < 1:

                reduction_factor = int(1 / scale_factor)
                mask = block_reduce(mask, block_size=(reduction_factor, reduction_factor), func=np.mean)
                # Padding
                pad_size_x = original_shape[1] - mask.shape[1]
                pad_size_y = original_shape[0] - mask.shape[0]
                mask = np.pad(mask, [(pad_size_y // 2, pad_size_y - pad_size_y // 2),
                                     (pad_size_x // 2, pad_size_x - pad_size_x // 2)],
                              mode='constant')

            # Then interpolate to the original size
            x = np.linspace(0, mask.shape[1], original_shape[1])
            y = np.linspace(0, mask.shape[0], original_shape[0])
            xx, yy = np.meshgrid(x, y)
            newfunc = interpolate.interp2d(np.arange(mask.shape[1]), np.arange(mask.shape[0]), mask, kind='linear')
            new_mask = newfunc(x, y)

            amplitude = new_mask

            return amplitude
        else:
            print("amplitude type not recognized")


    def inverse_fourier_transform(self,complex_amplitude):

        # check if complex amplitude has same dimensions as GridPositionMatrix
        if complex_amplitude.shape != self.GridPositionMatrix_X_in.shape:
            raise ValueError("Complex amplitude must have same dimensions as GridPositionMatrix")


        self.target_field = SubIntensity(self.input_beam,np.abs(complex_amplitude)**2)
        self.target_field = SubPhase(self.target_field,np.angle(complex_amplitude))


        self.inverse_fourier_target_field = PipFFT(self.target_field , -1)

        self.inverse_fourier_target_field = self.phase_filter(self.inverse_fourier_target_field)


        return self.inverse_fourier_target_field

    def get_field_phase(self,field):
        return Phase(field)

    def get_field_intensity(self,field):
        return Intensity(field)

    def phase_filter(self,field):
        phase = Phase(field)
        phase[np.pi - np.abs(phase)<10**-9] = np.pi
        phase[np.abs(phase)<10**-9] = 0
        field = SubPhase(field,phase)

        return field

    def normalize_field_by_100000(self,field):
        field_power = np.sum(np.sum(Intensity(field)))
        normalized_intensity = Intensity(field) * 100000 / field_power
        normalized_field = SubIntensity(field,normalized_intensity)
        return normalized_field
    def normalize_field_by_input_power(self,field):
        field_power = np.sum(np.sum(Intensity(field)))
        normalized_intensity = Intensity(field) * self.power / field_power
        normalized_field = SubIntensity(field,normalized_intensity)
        return normalized_field

    def normalize_by_filtered_power(self,field):
        field_power = np.sum(np.sum(Intensity(field)))
        normalized_intensity = Intensity(field) * self.power_filtered / field_power
        normalized_field = SubIntensity(field,normalized_intensity)
        return normalized_field

    def normalize_both_field_intensity(self,field):
        max_input_value = Intensity(self.input_beam).max()
        print(max_input_value)
        max_target_value = Intensity(field).max()
        print(max_target_value)
        normalized_field = SubIntensity(field,Intensity(field)*max_input_value/max_target_value)

        return normalized_field
    def phase_modulate_input_beam(self,mask):
        self.modulated_input_beam = MultPhase(self.input_beam,mask)
        return self.modulated_input_beam

    def propagate_FFT_modulated_beam(self,propagation_type="PipFFT"):
        if propagation_type == "PipFFT":
            self.propagated_beam_fourier = PipFFT(self.modulated_input_beam)
        else:
            pass

        self.propagated_beam_fourier = self.normalize_field_by_input_power(self.propagated_beam_fourier)
        self.propagated_beam_fourier._set_grid_size(self.input_grid_size*self.delta_x_out/self.delta_x_in)

        return self.propagated_beam_fourier

    def filter_beam(self,filter_type=None,pos_x=0,pos_y=0,radius=0):

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

        self.power_filtered = np.sum(np.sum(Intensity(self.filtered_beam_fourier)))

        print("Power after filter: ",self.power)
        print("Power after filter: ",self.power_filtered)

        return self.filtered_beam_fourier

    def propagate_FFT_to_image_plane(self,propagation_type="PipFFT"):
        if propagation_type == "PipFFT":
            self.propagated_beam_image = PipFFT(self.filtered_beam_fourier)
        else:
            pass

        self.propagated_beam_image = self.normalize_by_filtered_power(self.propagated_beam_image)

        return self.propagated_beam_image

    def load_config(self, file_name):
        with open(file_name, 'r') as file:
            self.config = yaml.safe_load(file)
        # Call a method to update the GUI with the loaded config