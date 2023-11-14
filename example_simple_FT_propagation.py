from beamshapy.BeamShaper import BeamShaper
from beamshapy.helpers import *



simulation_config = load_yaml_config("./config/simulation.yml")
input_beam_config = load_yaml_config("./config/input_beam.yml")
optical_system_config = load_yaml_config("./config/optical_system.yml")

results_directory = "experiment_results"



beam_shaper = BeamShaper(simulation_config,
                        input_beam_config,
                        optical_system_config)

# Generate System Input Beam Field
input_field = beam_shaper.generate_input_beam(input_beam_config)
# Save Input Beam Field
save_input_beam(results_directory, beam_shaper, input_field)

# Generate SLM Mask
mask_type = "Wedge"
angle = 0
position = 1.5*mm

mask = beam_shaper.mask_generator.design_mask(mask_type=mask_type,angle=angle,position=position)

# Modulate and propagate
modulated_input_field = beam_shaper.phase_modulate_input_beam(mask)
fourier_plane_field = beam_shaper.propagate_FFT_modulated_beam(propagation_type="PipFFT")
fourier_filtered_field = beam_shaper.filter_beam()
output_field = beam_shaper.propagate_FFT_to_image_plane(propagation_type="PipFFT")
 
# Save results
save_generated_fields(beam_shaper, modulated_input_field, fourier_plane_field, fourier_filtered_field, output_field,
                          results_directory)
