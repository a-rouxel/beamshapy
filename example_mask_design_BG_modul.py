from beamshapy.BeamShaper import BeamShaper, Intensity,Phase, um, mm
from beamshapy.mask_generation.functions_masks_generation import wrap_phase
from beamshapy.helpers import *
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


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

# Calculate inverse fourier transform of the target amplitude
beam_shaper.inverse_fourier_transform(target_amplitude)

# Generate SLM Mask
mask_type = "Wedge"
angle = 0
position = 1.5*mm

wedge_mask = beam_shaper.mask_generator.design_mask(mask_type=mask_type,angle=angle,position=position)
phase_inversion_mask = beam_shaper.mask_generator.generate_target_mask(mask_type="phase target field")
amplitude_modulation_mask = beam_shaper.mask_generator.generate_target_mask(mask_type="modulation amplitude")

resulting_mask =  wrap_phase(wedge_mask + phase_inversion_mask) * amplitude_modulation_mask

# Modulate and propagate
modulated_input_field = beam_shaper.phase_modulate_input_beam(resulting_mask)
fourier_plane_field = beam_shaper.propagate_FFT_modulated_beam(propagation_type="PipFFT")



plt.imshow(Intensity(fourier_plane_field),norm=LogNorm())
plt.show()

