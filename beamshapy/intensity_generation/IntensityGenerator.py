from beamshapy.spatial_profiles.functions_basic_shapes import *
from beamshapy.intensity_generation.functions_intensity_profile import *
import numpy as np
from scipy.ndimage import convolve

from scipy import interpolate, ndimage
import scipy.fftpack as fftpack
import h5py

class IntensityGenerator():
    """
    Class to design target intensity profiles
    """

    def __init__(self,beam_shaper):
        self.beam_shaper = beam_shaper


    def generate_target_intensity_profile(self, profile_type,radius= None,parabola_coef = None,hyper_gauss_order = None,intensity_path=None,scale_factor=1):
        """Main function for generating target intensity profiles

        Args:
            profile_type (str): Type of intensity profile to generate
            radius (float): Radius of the Fresnel lens (in m)
            parabola_coef (float): Coefficient of the parabola profile (in no units)
            hyper_gauss_order (float): Order of the supergaussian profile
            intensity_path (str): Path to the intensity profile H5 file
            scale_factor (float): Scale factor of the intensity profile

        Returns:
            np.ndarray: target intensity profile
        """

        if profile_type == "Fresnel Lens":

            target_intensity = fresnel_lens(self.beam_shaper.GridPositionMatrix_X_out, self.beam_shaper.GridPositionMatrix_Y_out, radius,parabola_coef)

            return target_intensity

        if profile_type == "Custom h5 intensity":

            if intensity_path == '':
                return None

            with h5py.File(intensity_path, 'r') as f:
                intensity = f['intensity'][:]

            # If the intensity is too small, center it in a new array matching the GridPositionMatrix dimensions
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
                intensity = intensity[starty:starty + crop_size[0], startx:startx + crop_size[1]]

            elif scale_factor < 1:

                reduction_factor = int(1 / scale_factor)
                intensity = ndimage.zoom(intensity, zoom=(1/reduction_factor), order=0)
                # Padding
                pad_size_x = original_shape[1] - intensity.shape[1]
                pad_size_y = original_shape[0] - intensity.shape[0]
                intensity = np.pad(intensity, [(pad_size_y // 2, pad_size_y - pad_size_y // 2), (pad_size_x // 2, pad_size_x - pad_size_x // 2)], mode='constant')

            # Then interpolate to the original size
            x = np.linspace(0, intensity.shape[1], original_shape[1])
            y = np.linspace(0, intensity.shape[0], original_shape[0])

            newfunc = interpolate.interp2d(np.arange(intensity.shape[1]), np.arange(intensity.shape[0]), intensity, kind='linear')
            new_intensity = newfunc(x, y)

            target_intensity = new_intensity

            return target_intensity

        else :
            print("intensity profile type not recognized")
            target_intensity = None

            return target_intensity

    def filter_intensity(self,target_intensity,filter_radius):

        # Step 1: Compute the Fourier Transform of the wrapped parabola
        tf_target_intensity = fftpack.fft2(target_intensity)

        x_array_in = self.beam_shaper.GridPositionMatrix_X_out[0,:]

        gaussian_filter = supergaussian2D(x_array_in, 1, filter_radius)

        # Step 3: Apply the supergaussian filter
        filtered_ft = tf_target_intensity * gaussian_filter

        # Step 4: Compute the Inverse Fourier Transform
        filtered_intensity = fftpack.ifft2(filtered_ft)

        return np.abs(filtered_intensity)

    import numpy as np

    def gaussian_kernel(self, kernel_size,sigma):
        """
        Function to generate a Gaussian kernel based on a given grid position.

        Args:
            sigma (float): Standard deviation of the Gaussian distribution.

        Returns:
            np.ndarray: Gaussian kernel.
        """
        ax = self.beam_shaper.GridPositionMatrix_X_out[0, :]  # Assuming uniform grid along x-axis
        ax = ax[ax.shape[0] // 2 - kernel_size // 2: ax.shape[0] // 2 + kernel_size // 2]
        xx, yy = np.meshgrid(ax, ax)

        kernel = np.exp(-0.5 * (np.square(xx) + np.square(yy)) / np.square(sigma))
        return kernel / np.sum(kernel)

    def convolve_with_gaussian(self,target_intensity, sigma,kernel_size=10):
        """
        Function to convolve target intensity with a Gaussian kernel.

        Args:
            target_intensity (np.ndarray): Target intensity array.
            sigma (float): Standard deviation of the Gaussian.
            kernel_size (int, optional): Size of the Gaussian kernel. Defaults to 10.

        Returns:
            np.ndarray: Convolved intensity.
        """
        # Generate a 10x10 Gaussian kernel
        gaussian_kernel = self.gaussian_kernel(kernel_size, sigma)


        # Perform convolution
        convolved_intensity = convolve(target_intensity, gaussian_kernel, mode='constant', cval=0.0)

        return convolved_intensity
