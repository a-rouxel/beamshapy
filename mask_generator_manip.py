import matplotlib.pyplot as plt

from BeamShaper import BeamShaper
from utils import *



simulation_config = load_yaml_config("config/simulation.yml")
input_beam_config = load_yaml_config("config/input_beam.yml")


results_directory = "monolobe"



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
height_range = np.linspace(300*um, 800*um, 15)

for height in height_range:

    i = 1
    angle = -4*np.pi/180
    # angle = 0
    position = 1.5*mm
    width_flat = 300*um


    if i%2 == 0:
        phase_offset = 0
    else:
        phase_offset = np.pi/2

    target_amplitude = BeamShaper.generate_target_amplitude(width=width_flat,height=height,amplitude_type="Rectangle",angle=angle)
    target_amplitude *= BeamShaper.generate_target_amplitude(period=2*height/i,angle=0,amplitude_type="Sinus",phase_offset=phase_offset)


    target_intens = target_amplitude**2
    plt.plot(target_intens[int(target_intens.shape[0]/2),:])


    inverse_tf_amplitude = BeamShaper.inverse_fourier_transform(target_amplitude)



    mask_wedge = BeamShaper.generate_mask(mask_type="Wedge",
                                          angle=0,
                                          position=position)
    # mask_WFC = BeamShaper.generate_mask(mask_type="Custom h5 Mask",
    #                                     mask_path="/home/arouxel/Documents/beam-shaping-fft/masks/slm6608_at1550_WFC_unwrapped.h5")
    mask_phase_m = BeamShaper.generate_mask(mask_type="ϕ target field")
    mask_mod_amp = BeamShaper.generate_mask(mask_type="modulation amplitude",amplitude_factor=1,threshold=0.001)

    total_mask = wrap_phase(mask_wedge + mask_phase_m)* mask_mod_amp

    crop_and_save_as_bmp(total_mask, results_directory, f"flatop_{round(height/um)}")

# plt.show()

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
