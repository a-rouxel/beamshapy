from beamshapy.BeamShaper import BeamShaper
from beamshapy.helpers import load_yaml_config, save_input_beam

from LightPipes import mm, um,Power, Intensity
import matplotlib.pyplot as plt
import numpy as np

simulation_config = load_yaml_config("./config/simulation.yml")
input_beam_config = load_yaml_config("./config/input_beam.yml")
optical_system_config = load_yaml_config("./config/optical_system.yml")

results_directory = "experiment_results"


beam_shaper = BeamShaper(simulation_config,input_beam_config, optical_system_config)

# Generate System Input Beam Field
input_field = beam_shaper.generate_input_beam(input_beam_config)
# Save Input Beam Field
# save_input_beam(results_directory, beam_shaper, input_field)

# Fresnel Lens parameters
radius = 1*mm
parabola_coef = 10**6.62
hyper_gauss_order = 12

# Generate Target Intensity Profile
target_intensity = beam_shaper.intensity_generator.generate_target_intensity_profile(profile_type="Fresnel Lens",
                                                                                     radius= radius,
                                                                                     parabola_coef = parabola_coef,
                                                                                     hyper_gauss_order = hyper_gauss_order)



conv_target_intensity = beam_shaper.intensity_generator.convolve_with_gaussian(target_intensity, sigma=10*um,kernel_size=10)


plt.plot(target_intensity[target_intensity.shape[0]//2,:],label="Target Intensity")
plt.plot(conv_target_intensity[conv_target_intensity.shape[0]//2,:],label="Convolved Target Intensity")
plt.legend()
plt.show()

# Generate Target Field from the given Target Intensity Profile
target_field = beam_shaper.generate_target_field_from_intensity(conv_target_intensity)


#Apply Gerchberg-Saxton Algorithm to generate the mask
results_dict = beam_shaper.mask_generator.generate_GSA_mask(input_field, target_field,init_gsa_parabola_coef=10**6)

# get the index of the minimum RMSE
min_rmse_index = np.argmin(results_dict["list rmse"])
best_mask = results_dict["list phase masks"][min_rmse_index]
best_intensity = results_dict["list image plane intensity"][min_rmse_index]

fig, ax = plt.subplots(1,2)
ax[0].imshow(best_mask,extent=[(beam_shaper.x_array_in/mm).min(),(beam_shaper.x_array_in/mm).max(),(beam_shaper.x_array_in/mm).min(),(beam_shaper.x_array_in/mm).max()])
ax[0].set_title("Best Mask")

ax[1].imshow(best_intensity,extent=[(beam_shaper.x_array_out/mm).min(),(beam_shaper.x_array_out/mm).max(),(beam_shaper.x_array_out/mm).min(),(beam_shaper.x_array_out/mm).max()])
ax[1].set_title(f"Best Intensity - radius={radius/mm}mm - coeff={int(parabola_coef)} - order={hyper_gauss_order}")
plt.show()

fig, ax = plt.subplots(1,2)
ax[0].plot(beam_shaper.x_array_out/mm,best_intensity[best_intensity.shape[0]//2,:],label="Achieved Intensity")
ax[0].plot(beam_shaper.x_array_out/mm,Intensity(target_field)[Intensity(target_field).shape[0]//2,:],label="Target Intensity")
ax[0].set_title("Best Intensity - Cut along X (min RMSE)")
ax[0].legend()

ax[1].plot(beam_shaper.x_array_out/mm,best_intensity[:,best_intensity.shape[1]//2],label="Achieved Intensity")
ax[1].plot(beam_shaper.x_array_out/mm,Intensity(target_field)[:,Intensity(target_field).shape[1]//2],label="Target Intensity")
ax[1].set_title("Best Intensity - Cut along Y (min RMSE)")
ax[1].legend()
plt.show()





