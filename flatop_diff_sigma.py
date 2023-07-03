import matplotlib.pyplot as plt

from BeamShaper import BeamShaper
from utils import *



simulation_config = load_yaml_config("config/simulation.yml")
input_beam_config = load_yaml_config("config/input_beam.yml")


results_directory = "experiment_results"



BeamShaper = BeamShaper(simulation_config,
                        input_beam_config,
                        initial_config_file="config/optical_system.yml")

# Generate System Sampling
BeamShaper.generate_sampling(simulation_config,input_beam_config)

# Generate System Input Beam Field
input_field = BeamShaper.generate_input_beam(input_beam_config)
# Save Input Beam Field
# save_input_beam(results_directory, BeamShaper, input_field)

# Generate SLM Mask
sigma_range = np.linspace(0.4, 1.2, 9)

for sigma in sigma_range:

    angle = 0
    position = 1.5*mm
    # width_flat = 200*um
    # height_flat = 200*um
    wavelength = 1.55*10**-6
    f = 0.3
    waist = 2.3*10**-3

    width_flat = wavelength*f/(sigma*waist)
    height_flat = width_flat

    print(width_flat*10**6)


    target_amplitude = BeamShaper.generate_target_amplitude(width=width_flat,height=height_flat,amplitude_type="Rectangle",angle=0)
    inverse_tf_amplitude = BeamShaper.inverse_fourier_transform(target_amplitude)



    mask_wedge = BeamShaper.generate_mask(mask_type="Wedge",
                                          angle=angle,
                                          position=position)
    mask_WFC = BeamShaper.generate_mask(mask_type="Custom h5 Mask",
                                        mask_path="/home/arouxel/Documents/beam-shaping-fft/masks/slm6608_at1550_WFC_unwrapped.h5")
    mask_phase_m = BeamShaper.generate_mask(mask_type="ϕ target field")
    mask_mod_amp = BeamShaper.generate_mask(mask_type="modulation amplitude",amplitude_factor=1,threshold=0.001)

    total_mask = wrap_phase(mask_wedge + mask_WFC + mask_phase_m)* correct(mask_mod_amp,BeamShaper.correction_a_values,BeamShaper.correction_tab)

    crop_and_save_as_bmp(total_mask, results_directory, f"flatop_{round(sigma,2)}_{round(width_flat*10**6,0)}")


    # plt.imshow(total_mask)
    # plt.show()

# # Modulate and propagate
# modulated_input_field = BeamShaper.phase_modulate_input_beam(total_mask)
# fourier_plane_field = BeamShaper.propagate_FFT_modulated_beam(propagation_type="PipFFT")
#
#
# plt.imshow(np.abs(fourier_plane_field.field)**2)
# plt.show()
#
#
# fourier_filtered_field = BeamShaper.filter_beam()
# output_field = BeamShaper.propagate_FFT_to_image_plane(propagation_type="PipFFT")

# Save results
# save_generated_fields(BeamShaper, modulated_input_field, fourier_plane_field, fourier_filtered_field, output_field,
#                           results_directory)
