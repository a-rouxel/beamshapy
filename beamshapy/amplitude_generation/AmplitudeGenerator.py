from beamshapy.spatial_profiles.functions_basic_shapes import *
import h5py
from scipy import interpolate, ndimage


class AmplitudeGenerator():

    """
    Class to design target amplitude profiles

    Args:
        beam_shaper (BeamShaper): BeamShaper object

    """

    def __init__(self,beam_shaper):
        self.beam_shaper = beam_shaper

    def generate_target_amplitude(self, amplitude_type, period=0, position=(0,0), scale_factor=1,
                                  angle=0, width=0, height=0, coef=None, sigma=0, n=0,
                                  amplitude_path=None, phase_offset=0):
        
        """
        Main function for generating target amplitude profiles

        Args:
            amplitude_type (str): Type of amplitude profile to generate
            period (float): Period of the amplitude profile (in m)
            position (float): Position of the amplitude profile (in m)
            scale_factor (float): Scale factor of the amplitude profile
            angle (float): Rotation angle of the amplitude profile (in rad)
            width (float): Width of the rectange profile (in m)
            height (float): Height of the rectange profile (in m)
            coef (float): Coefficient of the parabola profile (in no units)
            sigma (float): Sigma of the Gaussian profile (in m)
            n (int): Order of the supergaussian profile
            amplitude_path (str): Path to the amplitude profile H5 file
            phase_offset (float): Phase offset of the sinusoidal profile (in rad)
        """

        if self.beam_shaper.x_array_in is None:
            raise ValueError("Please generate Input Beam first")

        if amplitude_type == "Rectangle":
            amplitude = RectangularMask(self.beam_shaper.GridPositionMatrix_X_out, self.beam_shaper.GridPositionMatrix_Y_out, angle,
                                                 width, height,position=position)
            return amplitude

        if amplitude_type == "Gaussian":

            amplitude = supergaussian2D(self.beam_shaper.x_array_in, n, sigma)

            return amplitude

        if amplitude_type == "Wedge":
            x_proj = np.cos(angle) * position
            y_proj = np.sin(angle) * position

            amplitude_x = Simple2DWedgeMask(self.beam_shaper.x_array_in, self.beam_shaper.input_wavelength, x_proj, self.beam_shaper.focal_length)
            amplitude_y = np.flip(
                np.transpose(Simple2DWedgeMask(self.beam_shaper.x_array_in, self.beam_shaper.input_wavelength, y_proj, self.beam_shaper.focal_length)), 0)
            amplitude = amplitude_x + amplitude_y

            return amplitude

        if amplitude_type == "Parabola":

            amplitude = ParabolaMask(self.beam_shaper.GridPositionMatrix_X_out, self.beam_shaper.GridPositionMatrix_Y_out, coef)
            return amplitude

        if amplitude_type == "Sinus":
            amplitude = SinusMask(self.beam_shaper.GridPositionMatrix_X_out, self.beam_shaper.GridPositionMatrix_Y_out, period, angle,
                                            phase_offset)
            return amplitude

        if amplitude_type == "Cosinus":
            amplitude = CosinusMask(self.beam_shaper.GridPositionMatrix_X_out, self.beam_shaper.GridPositionMatrix_Y_out, period,
                                              angle)
            return amplitude

        if amplitude_type == "Custom h5 Amplitude":

            if amplitude_path == '':
                return

            with h5py.File(amplitude_path, 'r') as f:
                mask = f['amplitude'][:]

            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            if mask.shape != self.beam_shaper.GridPositionMatrix_X_out.shape:
                new_mask = np.zeros_like(self.beam_shaper.GridPositionMatrix_X_out)
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
                mask = ndimage.zoom(mask, zoom=(1/reduction_factor), order=0)
                # Padding
                pad_size_x = original_shape[1] - mask.shape[1]
                pad_size_y = original_shape[0] - mask.shape[0]
                mask = np.pad(mask, [(pad_size_y // 2, pad_size_y - pad_size_y // 2),(pad_size_x // 2, pad_size_x - pad_size_x // 2)],mode='constant')

            # Then interpolate to the original size
            x = np.linspace(0, mask.shape[1], original_shape[1])
            y = np.linspace(0, mask.shape[0], original_shape[0])

            newfunc = interpolate.interp2d(np.arange(mask.shape[1]), np.arange(mask.shape[0]), mask, kind='linear')
            new_mask = newfunc(x, y)

            amplitude = new_mask

            return amplitude
        else:
            print("amplitude type not recognized")
            return None