import numpy as np
import yaml
from LightPipes import *
from utils import *
class BeamShaper():

    def __init__(self,simulation_config,input_beam_config,initial_config_file):
        self.simulation_config = simulation_config
        self.input_beam_config = input_beam_config
        self.initial_config_file = initial_config_file

        # Load the initial configuration file if one was provided
        if self.initial_config_file is not None:
            self.load_config(self.initial_config_file)

        self.generate_sampling(simulation_config,input_beam_config)

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
            F = PlaneWave(F, w=self.input_grid_size)
        else:
            raise ValueError("Unknown field type")

        self.input_beam = F

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

        x = np.linspace(-self.input_grid_size / 2, self.input_grid_size / 2, self.nb_of_samples)
        y = np.linspace(-self.input_grid_size / 2, self.input_grid_size / 2, self.nb_of_samples)
        GridPositionMatrix_X, GridPositionMatrix_Y = np.meshgrid(x, y)

        self.delta_x_in = delta_x_in
        self.delta_x_out = delta_x_out
        self.x_array_in = x_array_in
        self.x_array_out = x_array_out
        self.GridPositionMatrix_X = GridPositionMatrix_X
        self.GridPositionMatrix_Y = GridPositionMatrix_Y

    def generate_mask(self,mask_type, period=None,position = None, orientation=None,angle = None, width = None, height = None, sigma_x=None,sigma_y=None,threshold=None,mask_path=None):


        if self.x_array_in is None:
            raise ValueError("Please generate Input Beam first")

        if mask_type == "Grating":
            M1 = Simple1DBlazedGratingMask(self.x_array_in, period)
            mask = np.tile(M1, (self.nb_of_samples, 1))
            if orientation== "Vertical":
                mask = np.transpose(mask)
            return mask
        if mask_type == "Wedge":
            x_proj = np.cos(angle)*position
            y_proj = np.sin(angle)*position

            mask_x = Simple2DWedgeMask(self.x_array_in,self.input_wavelength,x_proj,self.focal_length)
            mask_y = np.flip(np.transpose(Simple2DWedgeMask(self.x_array_in,self.input_wavelength,y_proj,self.focal_length)),0)
            mask = mask_x + mask_y

            return mask

        if mask_type == "Rect Amplitude":
            mask = RectangularAmplitudeMask(self.GridPositionMatrix_X,self.GridPositionMatrix_Y,angle, width,height)
            return mask

        if mask_type == "Phase Jump":
            mask = PiPhaseJumpMask(self.GridPositionMatrix_X,self.GridPositionMatrix_Y,orientation, position)
            return mask

        if mask_type == "Phase Reversal":
            self.sigma_x = sigma_x
            self.sigma_y = sigma_y
            mask = PhaseReversalMask(self.GridPositionMatrix_X,self.GridPositionMatrix_Y,self.input_waist,sigma_x,sigma_y)
            self.phase_inversed_Field = SubPhase(self.input_beam,mask)

            return mask

        if mask_type == "Weights Sinc":
            sinc_mask_x = sinc_resized(self.GridPositionMatrix_X, self.input_waist*self.sigma_x)
            sinc_mask_y = sinc_resized(self.GridPositionMatrix_Y, self.input_waist*self.sigma_y)
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
            if mask.shape != self.GridPositionMatrix_X.shape:
                new_mask = np.zeros_like(self.GridPositionMatrix_X)
                x_offset = (new_mask.shape[0] - mask.shape[0]) // 2
                y_offset = (new_mask.shape[1] - mask.shape[1]) // 2
                new_mask[x_offset: x_offset + mask.shape[0], y_offset: y_offset + mask.shape[1]] = mask
                mask = new_mask

            else:
                print("mask_type not recognized")
            return mask


    def phase_modulate_input_beam(self,mask):
        self.modulated_input_beam = MultPhase(self.input_beam,mask)
        return self.modulated_input_beam

    def propagate_FFT_modulated_beam(self,propagation_type="PipFFT"):
        if propagation_type == "PipFFT":
            self.propagated_beam_fourier = PipFFT(self.modulated_input_beam)
        else:
            pass
        return self.propagated_beam_fourier

    def filter_beam(self,filter_type=None,pos_x=None,pos_y=None,radius=None):
        if filter_type == "Circular":
            self.filtered_beam_fourier = CircAperture(Fin=self.propagated_beam_fourier,
                                                      R=radius,
                                                      x_shift=pos_x,
                                                      y_shift=pos_y)
        elif filter_type == "Gaussian":
            self.filtered_beam_fourier = GaussAperture(Fin=self.propagated_beam_fourier,
                                                      w=radius,
                                                      x_shift=pos_x,
                                                      y_shift=pos_y)
        else:
            self.filtered_beam_fourier = self.propagated_beam_fourier

        return self.filtered_beam_fourier

    def propagate_FFT_to_image_plane(self,propagation_type="PipFFT"):
        if propagation_type == "PipFFT":
            self.propagated_beam_image = PipFFT(self.filtered_beam_fourier)
        else:
            pass
        return self.propagated_beam_image

    def load_config(self, file_name):
        with open(file_name, 'r') as file:
            self.config = yaml.safe_load(file)
        # Call a method to update the GUI with the loaded config