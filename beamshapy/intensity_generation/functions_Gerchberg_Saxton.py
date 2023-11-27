from beamshapy.spatial_profiles.functions_basic_shapes import *
from LightPipes import Field, Intensity, SubIntensity, Phase, SubPhase, PipFFT, Power, mm, um
import time

def apply_GSA_initial_phase(field, GridPositionMatrix_X_in, GridPositionMatrix_Y_in,init_gsa_parabola_coef,phase_type):
    """
    Generates the initial phase mask.

    Returns:
        np.ndarray: 2D array with the initial phase mask.

    """

    if phase_type == 'parabola':
        init_phase = ParabolaMask(GridPositionMatrix_X_in, GridPositionMatrix_Y_in, coef=init_gsa_parabola_coef)
    else:
        print('Phase type not recognized')

    field = SubPhase(init_phase,field)

    return field

def generate_phase_mask_GSA(input_field, target_field,
                            GridPositionMatrix_X_in,GridPositionMatrix_Y_in,
                            init_gsa_parabola_coef,
                            tolerance=0.02, max_iterations=15,
                            first_rmse_threshold=0.5,consecutive_stagnant_iterations=3):



    current_field = Field.copy(input_field)
    current_field = apply_GSA_initial_phase(current_field, GridPositionMatrix_X_in,GridPositionMatrix_Y_in,init_gsa_parabola_coef,phase_type='parabola')

    t0 = time.time()
    list_rmse_image_plane = []
    list_image_plane_intensity = []
    list_phase_masks = []

    prev_rmse = None
    stagnant_counter = 0
    iter = 0

    gaussian_window = supergaussian2D(GridPositionMatrix_X_in[0,:], 8, 8*mm)

    output_pix_surf = (GridPositionMatrix_X_in[0,1] - GridPositionMatrix_X_in[0,0]) * (GridPositionMatrix_Y_in[1,0] - GridPositionMatrix_Y_in[0,0]) / um

    while iter < max_iterations:

        list_phase_masks.append(Phase(current_field))

        current_field = PipFFT(current_field, 1)

        norm_reconstructed_intens = Intensity(current_field) * (Power(target_field) / Power(current_field))
        current_field = SubIntensity(current_field, norm_reconstructed_intens)

        RMSE_image_plane = ((Intensity(target_field) - Intensity(current_field))*output_pix_surf) ** 2
        RMSE_image_plane = np.sqrt(
            np.sum(np.sum(RMSE_image_plane)))

        list_rmse_image_plane.append(RMSE_image_plane)
        list_image_plane_intensity.append(Intensity(current_field))

        print(f"Iteration {iter}: RMSE = {RMSE_image_plane}")

        Last_field = target_field
        Last_field = SubIntensity(Last_field,Intensity(current_field))
        Last_field = SubPhase(Last_field, Phase(current_field)*gaussian_window)

        if prev_rmse is not None:
            rmse_diff = abs(RMSE_image_plane - prev_rmse) / RMSE_image_plane

            if rmse_diff < tolerance:
                stagnant_counter += 1
            else:
                stagnant_counter = 0

            if stagnant_counter >= consecutive_stagnant_iterations:
                print("RMSE converged or stagnated.")
                break
        if list_rmse_image_plane[0] > first_rmse_threshold:
            print("RMSE too high.")
            break

        prev_rmse = RMSE_image_plane
        iter += 1

        max_intensity_target = Intensity(target_field).max()
        diff_weights = (Intensity(target_field) - Intensity(current_field)) / max_intensity_target
        weights_map = np.exp(diff_weights)

        weighted_target_intensity = Intensity(target_field) * weights_map







        current_field = SubIntensity(weighted_target_intensity,
                                 current_field)  # Substitute the measured far field into the field

        current_field = PipFFT(current_field, -1)

        current_field = SubIntensity(Intensity(input_field), current_field)  # Substitute the measured far field into the field

        

    else:
        print("Maximum iterations reached without RMSE convergence or stagnation.")

    t1 = time.time()
    print(t1 - t0, " s")

    sim_run_time = t1 - t0

    return list_phase_masks,list_image_plane_intensity,list_rmse_image_plane,sim_run_time
