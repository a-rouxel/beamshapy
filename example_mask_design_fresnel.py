from beamshapy.BeamShaper import BeamShaper
from beamshapy.helpers import load_yaml_config, save_input_beam

from LightPipes import mm, um,Power, Intensity
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

simulation_config = load_yaml_config("./config/simulation.yml")
input_beam_config = load_yaml_config("./config/input_beam.yml")
optical_system_config = load_yaml_config("./config/optical_system.yml")

results_directory = "experiment_results"


beam_shaper = BeamShaper(simulation_config,input_beam_config, optical_system_config)

# Generate System Input Beam Field
input_field = beam_shaper.generate_input_beam(input_beam_config)
# Save Input Beam Field
# save_input_beam(results_directory, beam_shaper, input_field)

# # Fresnel Lens parameters
# radius = 1*mm
# parabola_coef = 10**6.32
# hyper_gauss_order = 12
#
# # Generate Target Intensity Profile
# target_intensity = beam_shaper.intensity_generator.generate_target_intensity_profile(profile_type="Fresnel Lens",
#                                                                                      radius= radius,
#                                                                                      parabola_coef = parabola_coef,
#                                                                                      hyper_gauss_order = hyper_gauss_order)
#
#
# img = Image.fromarray(target_intensity*255)
# # Convert to a supported mode (e.g., 'RGB')
# converted_image = img.convert('L')
# # Save the converted ima
# converted_image.save('fresenl_lens_1aillette.png')
#
# # Fresnel Lens parameters
# radius = 1*mm
# parabola_coef = 10**6.48
# hyper_gauss_order = 12
#
# # Generate Target Intensity Profile
# target_intensity = beam_shaper.intensity_generator.generate_target_intensity_profile(profile_type="Fresnel Lens",
#                                                                                      radius= radius,
#                                                                                      parabola_coef = parabola_coef,
#                                                                                      hyper_gauss_order = hyper_gauss_order)
#
#
# img = Image.fromarray(target_intensity*255)
# # Convert to a supported mode (e.g., 'RGB')
# converted_image = img.convert('L')
# # Save the converted ima
# converted_image.save('fresenl_lens_2aillettes.png')



# Fresnel Lens parameters
radius = 1*mm
parabola_coef = 10**6.62
hyper_gauss_order = 12

# Generate Target Intensity Profile
target_intensity = beam_shaper.intensity_generator.generate_target_intensity_profile(profile_type="Fresnel Lens",
                                                                                     radius= radius,
                                                                                     parabola_coef = parabola_coef,
                                                                                     hyper_gauss_order = hyper_gauss_order)

plt.imshow(target_intensity)
plt.show()

plt.plot(target_intensity[target_intensity.shape[0]//2,:])
plt.show()


img = Image.fromarray(target_intensity*255)
# Convert to a supported mode (e.g., 'RGB')
converted_image = img.convert('L')
# Save the converted ima
converted_image.save('fresenl_lens_3aillettes.png')


# conv_target_intensity = beam_shaper.intensity_generator.convolve_with_gaussian(target_intensity, sigma=10*um,kernel_size=10)
#
#


