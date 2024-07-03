from beamshapy.mask_generation.functions_masks_generation import WeightsMask, root_theorical_deformation_sinc, generate_correction_tab, correct_modulation_values
from beamshapy.intensity_generation.functions_Gerchberg_Saxton import Intensity, SubPhase
from beamshapy.intensity_generation.functions_Gerchberg_Saxton import generate_phase_mask_GSA, Simple1DBlazedGratingMask, \
                                                                    VortexMask, Simple2DWedgeMask, RectangularMask, PiPhaseJumpMask, PhaseReversalMask
from beamshapy.helpers import h5py, np


class MaskGenerator():
    """
    Class used to generate Spatial Light Modulator masks. It can either be based on a target amplitude/intensity or purely in design mode
    """

    def __init__(self,beam_shaper):

        self.beam_shaper = beam_shaper


    def generate_GSA_mask(self,input_field, target_field, init_gsa_parabola_coef=10**7.2,
                          tolerance=0.003, max_iterations=25,first_rmse_threshold=2,consecutive_stagnant_iterations=3):

        list_phase_masks,list_image_plane_intensity,list_rmse_image_plane,sim_run_time = generate_phase_mask_GSA(input_field,
                                                                                                                 target_field,
                                                                                                                 self.beam_shaper.GridPositionMatrix_X_in,
                                                                                                                 self.beam_shaper.GridPositionMatrix_Y_in,
                                                                                                                 init_gsa_parabola_coef=init_gsa_parabola_coef,
                                                                                                                 tolerance=tolerance,
                                                                                                                 max_iterations=max_iterations,
                                                                                                                 first_rmse_threshold=first_rmse_threshold,
                                                                                                                 consecutive_stagnant_iterations=consecutive_stagnant_iterations)
        # get the index of the minimum RMSE
        min_rmse_index = np.argmin(list_rmse_image_plane)
        best_mask = list_phase_masks[min_rmse_index]
        best_intensity = list_image_plane_intensity[min_rmse_index]

        results_dict = {'list phase masks':list_phase_masks,
                'list image plane intensity':list_image_plane_intensity,
                'list rmse':list_rmse_image_plane,
                'sim run time':sim_run_time}

        return results_dict



    def generate_target_mask(self,mask_type,threshold=0.001, amplitude_factor=1):
        """
        Generate a mask based on a Target Amplitude or Intensity.

        Args:
            mask_type (str): Type of mask to generate. Available options are:
                - "ϕ target field": Phase mask based on the target field
                - "modulation amplitude": Amplitude mask based on the target field
            amplitude_factor (float): Factor to multiply the target amplitude by. Default is 1.

        Returns:
            np.array: Mask to be applied to the SLM

        """

        if self.beam_shaper.x_array_in is None:
            raise ValueError("Please generate Input Beam first")

        if mask_type == "phase target field":
            target_field = self.beam_shaper.inverse_fourier_target_field
            mask = self.beam_shaper.get_field_phase(target_field)
            return mask

        if mask_type == "modulation amplitude":
            normalized_target_field = self.beam_shaper.normalize_field_intensity_by_max_input(self.beam_shaper.inverse_fourier_target_field)
            target_abs_amplitude = np.sqrt(Intensity(normalized_target_field)) * amplitude_factor
            input_abs_amplitude = np.sqrt(Intensity(self.beam_shaper.input_beam))
            mask = WeightsMask(input_abs_amplitude,target_abs_amplitude,threshold)

            corrected_mask = correct_modulation_values(mask, self.correction_a_values, self.correction_tab)

            return corrected_mask

        else:
            print("mask_type not recognized")
            return None


    def design_mask(self,mask_type,period=None,position = None, charge=None,orientation=None,angle = None, width = None, height = None, sigma_x=None,sigma_y=None,threshold=None,mask_path=None,amplitude_factor=1):

        """
        Design a mask based on the parameters provided.

        Avalailable mask types are:
            - Grating
            - Gaussian
            - Vortex
            - Wedge
            - Custom h5 Mask
            - Rectangle
            - Phase reversal
            - Phase Jump

        Args:
            mask_type (str): Type of mask to generate
            period (float): Period of the mask (in m)
            position (float): Position of the mask (in m)
            charge (int): Charge of the vortex mask
            orientation (str): Orientation of the mask. Can be "Horizontal" or "Vertical"
            angle (float): Angle of the mask (in rad)
            width (float): Width of the rectangle (in m)
            height (float): Height of the rectangle (in m)
            sigma_x (float): Sigma of the Gaussian mask in the x direction (in m)
            sigma_y (float): Sigma of the Gaussian mask in the y direction (in m)
            threshold (float): Threshold of the mask
            mask_path (str): Path to the custom mask
            amplitude_factor (float): Amplitude factor of the mask

        Returns:
            np.array: Generated mask
        """

        if self.beam_shaper.x_array_in is None:
            raise ValueError("Please generate Input Beam first")

        if mask_type == "Grating":
            M1 = Simple1DBlazedGratingMask(self.beam_shaper.x_array_in, period)
            mask = np.tile(M1, (self.beam_shaper.nb_of_samples, 1))
            if orientation== "Vertical":
                mask = np.transpose(mask)
            return mask

        if mask_type == "Gaussian":

            sigma_x *= 10**-6
            sigma_y *= 10**-6

            if sigma_x is None or sigma_y is None:
                raise ValueError("Please provide values for sigma_x and sigma_y for the Gaussian mask.")

            x, y = np.meshgrid(self.beam_shaper.x_array_in, self.beam_shaper.x_array_in)
            mask = np.exp(-((x) ** 2 / (2 * sigma_x ** 2) + (y) ** 2 / (2 * sigma_y ** 2)))

            return mask

        if mask_type == "Vortex":
            mask = VortexMask(self.beam_shaper.x_array_in, charge)

            return mask

        if mask_type == "Wedge":
            x_proj = np.cos(angle)*position
            y_proj = np.sin(angle)*position

            mask_x = Simple2DWedgeMask(self.beam_shaper.x_array_in,self.beam_shaper.input_wavelength,x_proj,self.beam_shaper.focal_length)
            mask_y = np.flip(np.transpose(Simple2DWedgeMask(self.beam_shaper.x_array_in,self.beam_shaper.input_wavelength,y_proj,self.beam_shaper.focal_length)),0)
            mask = mask_x + mask_y

            return mask




        if mask_type == "Rectangle":
            mask = RectangularMask(self.beam_shaper.GridPositionMatrix_X_in,self.beam_shaper.GridPositionMatrix_Y_in,angle, width,height)
            return mask

        if mask_type == "Phase Jump":
            mask = PiPhaseJumpMask(self.beam_shaper.GridPositionMatrix_X_in,self.beam_shaper.GridPositionMatrix_Y_in,orientation, position)
            return mask

        if mask_type == "Phase Reversal":
            self.sigma_x = sigma_x
            self.sigma_y = sigma_y
            mask = PhaseReversalMask(self.beam_shaper.GridPositionMatrix_X_in,self.beam_shaper.GridPositionMatrix_Y_in,self.beam_shaper.input_waist,sigma_x,sigma_y)
            self.phase_inversed_Field = SubPhase(self.beam_shaper.input_beam,mask)

            return mask

        # if mask_type == "Weights Sinc":
        #
        #     sinc_mask_x = sinc_resized(self.beam_shaper.GridPositionMatrix_X_in, self.input_waist*self.sigma_x)
        #     sinc_mask_y = sinc_resized(self.beam_shaper.GridPositionMatrix_Y_in, self.input_waist*self.sigma_y)
        #     target_amplitude = sinc_mask_x*sinc_mask_y
        #
        #     input_amplitude = self.phase_inversed_Field.field.real
        #
        #
        #     mask = WeightsMask(input_amplitude,target_amplitude,threshold)
        #     return mask


        if mask_type == "Custom h5 Mask":
            if mask_path is None:
                raise ValueError("Please provide h5 file path for custom mask.")

            with h5py.File(mask_path, 'r') as f:
                mask = f['mask'][:]

            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            # If the mask is too small, center it in a new array matching the GridPositionMatrix dimensions
            if mask.shape != self.beam_shaper.GridPositionMatrix_X_in.shape:
                new_mask = np.zeros_like(self.beam_shaper.GridPositionMatrix_X_in)
                x_offset = (new_mask.shape[0] - mask.shape[0]) // 2
                y_offset = (new_mask.shape[1] - mask.shape[1]) // 2
                new_mask[x_offset: x_offset + mask.shape[0], y_offset: y_offset + mask.shape[1]] = mask
                mask = new_mask

            else:
                print("mask_type not recognized")
            return mask


    def generate_correction_tab(self,nb_of_samples=1000,func=root_theorical_deformation_sinc):
        """Generates the correction tab corresponding to the sinc. Cf. Modulation amplitude of a blazed grating.pdf

        Args:
            nb_of_samples (int, optional): Number of samples for the correction tab. Defaults to 1000.
            func (function, optional): Function to use for the correction tab. Defaults to root_theorical_deformation_sinc.

        Returns:
            a_values (np.array): Array of values between 0 and 1 for the correction tab.
            correction_tab (np.array): Array of correction values for the correction tab.

        """

        a_values, correction_tab = generate_correction_tab(nb_of_samples, func=func)
        self.correction_tab = correction_tab
        self.correction_a_values = a_values

        return a_values, correction_tab

