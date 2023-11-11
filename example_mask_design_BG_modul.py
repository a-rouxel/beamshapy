from beamshapy.BeamShaper import BeamShaper, um, mm
from beamshapy.helpers import *
import matplotlib.pyplot as plt


simulation_config = load_yaml_config("./config/simulation.yml")
input_beam_config = load_yaml_config("./config/input_beam.yml")
optical_system_config = load_yaml_config("./config/optical_system.yml")

results_directory = "experiment_results"



beam_shaper = BeamShaper(simulation_config,
                        input_beam_config,
                        optical_system_config)


# Generate System Input Beam Field
input_field = beam_shaper.generate_input_beam(input_beam_config)

# Target Amplitude Parameters
width = 500*um
height = 300*um
sinus_period = 500*um / 2 

target_amplitude = beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type="Rectangle",width=width,height=height)
target_amplitude *= beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type="Sinus",period=sinus_period)

plt.imshow(target_amplitude)
plt.show()

# Generate SLM Mask
mask_type = "Wedge"
angle = 0
position = 1.5*mm

mask = BeamShaper.mask_generator.design_mask(mask_type=mask_type,angle=angle,position=position)

# Modulate and propagate
modulated_input_field = BeamShaper.phase_modulate_input_beam(mask)
fourier_plane_field = BeamShaper.propagate_FFT_modulated_beam(propagation_type="PipFFT")
fourier_filtered_field = BeamShaper.filter_beam()
output_field = BeamShaper.propagate_FFT_to_image_plane(propagation_type="PipFFT")

# Save results
save_generated_fields(BeamShaper, modulated_input_field, fourier_plane_field, fourier_filtered_field, output_field,
                          results_directory)
