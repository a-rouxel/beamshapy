from beamshapy.amplitude_generation.functions_amplitude_generation import *
from beamshapy.spatial_profiles.functions_basic_shapes import *
from beamshapy.intensity_generation.functions_intensity_profile import *

from skimage.measure import block_reduce
from scipy import interpolate

class IntensityGenerator():

    def __init__(self,beam_shaper):
        self.beam_shaper = beam_shaper


    def generate_target_intensity_profile(self, profile_type,radius= None,parabola_coef = None,hyper_gauss_order = None,intensity_path=None,scale_factor=1):

        if profile_type == "Fresnel Lens":

            target_intensity = fresnel_lens(self.beam_shaper.GridPositionMatrix_X_out, self.beam_shaper.GridPositionMatrix_Y_out, radius,parabola_coef,hyper_gauss_order)

            return target_intensity

        if profile_type == "Custom h5 intensity":

            if intensity_path == '':
                return None

            with h5py.File(intensity_path, 'r') as f:
                intensity = f['intensity'][:]

            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            if intensity.shape != self.beam_shaper.GridPositionMatrix_X_out.shape:
                new_intensity = np.zeros_like(self.beam_shaper.GridPositionMatrix_X_out)
                x_offset = (new_intensity.shape[0] - intensity.shape[0]) // 2
                y_offset = (new_intensity.shape[1] - intensity.shape[1]) // 2
                new_intensity[x_offset: x_offset + intensity.shape[0], y_offset: y_offset + intensity.shape[1]] = intensity
                intensity = new_intensity

            # Get original shape
            original_shape = intensity.shape

            if scale_factor > 1:
                # First crop
                crop_size = (int(original_shape[0] / scale_factor), int(original_shape[1] / scale_factor))
                startx = original_shape[1] // 2 - (crop_size[1] // 2)
                starty = original_shape[0] // 2 - (crop_size[0] // 2)
                mask = mask[starty:starty + crop_size[0], startx:startx + crop_size[1]]

            elif scale_factor < 1:

                reduction_factor = int(1 / scale_factor)
                mask = block_reduce(intensity, block_size=(reduction_factor, reduction_factor), func=np.mean)
                # Padding
                pad_size_x = original_shape[1] - mask.shape[1]
                pad_size_y = original_shape[0] - mask.shape[0]
                intensity = np.pad(mask, [(pad_size_y // 2, pad_size_y - pad_size_y // 2),
                                     (pad_size_x // 2, pad_size_x - pad_size_x // 2)],
                              mode='constant')

            # Then interpolate to the original size
            x = np.linspace(0, intensity.shape[1], original_shape[1])
            y = np.linspace(0, intensity.shape[0], original_shape[0])

            newfunc = interpolate.interp2d(np.arange(intensity.shape[1]), np.arange(intensity.shape[0]), mask, kind='linear')
            new_intensity = newfunc(x, y)

            target_intensity = new_intensity

            return target_intensity

        else :
            print("intensity profile type not recognized")
            target_intensity = None

        return target_intensity

