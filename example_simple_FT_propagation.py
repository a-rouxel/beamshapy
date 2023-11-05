from beamshapy.BeamShaper import BeamShaper
from beamshapy.helpers import *



simulation_config = load_yaml_config("beamshapy/config/simulation.yml")
input_beam_config = load_yaml_config("beamshapy/config/input_beam.yml")
optical_system_config = load_yaml_config("beamshapy/config/optical_system.yml")

results_directory = "experiment_results"



BeamShaper = BeamShaper(simulation_config,
                        input_beam_config,
                        optical_system_config)

# Generate System Sampling
BeamShaper.generate_sampling(simulation_config,input_beam_config,optical_system_config)

# Generate System Input Beam Field
input_field = BeamShaper.generate_input_beam(input_beam_config)
# Save Input Beam Field
save_input_beam(results_directory, BeamShaper, input_field)

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
