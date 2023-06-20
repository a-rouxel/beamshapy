from BeamShaper import BeamShaper
from utils import *
from LightPipes import *
from scipy.ndimage import gaussian_filter

simulation_config = load_yaml_config("config/simulation.yml")
input_beam_config = load_yaml_config("config/input_beam.yml")


results_directory = "experiment_results"



BeamShaper = BeamShaper(simulation_config,
                        input_beam_config,
                        initial_config_file="config/optical_system.yml")

# Generate System Sampling
BeamShaper.generate_sampling()

# Generate System Input Beam Field
input_field = BeamShaper.generate_input_beam(input_beam_config)

import matplotlib.pyplot as plt

def sinc(x,w):
    return np.sin(np.pi*x/w)/(np.pi*x/w)

w_0 = 2.3*mm
sampling = BeamShaper.nb_of_samples
new_amp = sinc(BeamShaper.GridPositionMatrix_X,w_0)
phase = np.zeros_like(new_amp)
phase[new_amp>0] = np.pi


w = 1*mm

X,Y = np.meshgrid(BeamShaper.x_array_in,BeamShaper.x_array_in)

wedge_mask = Simple2DWedgeMask(BeamShaper.x_array_in,BeamShaper.input_wavelength,5*mm,0.3)


# Load png image
from PIL import Image
R_img = Image.open('R.png')
R_np = np.array(R_img)
R_np = R_np[:,:,0]/np.max(R_np[:,:,0])
R_np = 1 - R_np

# R_np_complex = R_np*np.exp(1j*wedge_mask)
#
# R_np = R_np_complex


# Apply Gaussian blur
R_np_blurred = gaussian_filter(R_np, sigma=1)

# plt.imshow(R_np_blurred)
# plt.show()

complex_amp =R_np

sinc_field = SubIntensity(input_field, np.abs(complex_amp)**2)
sinc_field = SubPhase(sinc_field, np.angle(complex_amp))


Target_amplitude_SLM= PipFFT(sinc_field,-1)


# Encoding over SLM


phase_target = Phase(Target_amplitude_SLM)
complex_amplitude_slm = np.sqrt(Intensity(Target_amplitude_SLM))*np.exp(1j*phase_target)


# modulated_beam = SubPhase(input_field, phase_target)
# modulated_beam = SubIntensity(modulated_beam, np.abs(complex_amplitude_slm)**2)
#
# fourier_test_plane = PipFFT(modulated_beam)
# plt.imshow(Intensity(fourier_test_plane))
# plt.show()




# phase_to_display = np.zeros_like(phase_target)
# phase_to_display[complex_amplitude_slm>0] = -np.pi/2
# phase_to_display[complex_amplitude_slm<0] = np.pi/2
phase_to_display = phase_target

plt.imshow(phase_to_display)
plt.show()

SLM_mask = phase_to_display + wedge_mask
SLM_mask = SLM_mask % (2*np.pi)
SLM_mask -= np.pi

mod_amp = np.abs(complex_amplitude_slm)**2
mod_amp = mod_amp/np.max(mod_amp)

SLM_mask = SLM_mask*mod_amp



# phase_to_display = phase_to_display*complex_amplitude_slm.max()/np.pi/2


plt.imshow(Intensity(Target_amplitude_SLM),extent=[BeamShaper.x_array_in[0]/mm,BeamShaper.x_array_in[-1]/mm,BeamShaper.x_array_in[0]/mm,BeamShaper.x_array_in[-1]/mm])
plt.xlabel("Position X [mm]")
plt.ylabel("Position Y [mm]")
plt.title("Target Intensity in the SLM plane")
plt.show()


plt.plot(complex_amplitude_slm[BeamShaper.nb_of_samples//2,:],label="complex amplitude - real part")
plt.plot(np.abs(complex_amplitude_slm)[BeamShaper.nb_of_samples//2,:],label="complex amplitude - intensity")
plt.plot(phase_to_display[BeamShaper.nb_of_samples//2,:],label="complex amplitude - binary phase")
plt.legend()
plt.show()

plt.imshow(Intensity(input_field))
plt.show()

modulated_beam = SubPhase(input_field, SLM_mask)
# modulated_beam = SubIntensity(modulated_beam, np.abs(complex_amplitude_slm)**2)


plt.plot(Intensity(modulated_beam)[BeamShaper.nb_of_samples//2,:])
plt.show()
plt.plot(Phase(modulated_beam)[BeamShaper.nb_of_samples//2,:])
plt.show()



Fourier_field = PipFFT(modulated_beam)

intensity_fourier_field = Intensity(Fourier_field)
intensity_fourier_field[BeamShaper.nb_of_samples//2 - 50:BeamShaper.nb_of_samples//2 + 50,BeamShaper.nb_of_samples//2 - 50:BeamShaper.nb_of_samples//2 + 50] = 0

plt.imshow(intensity_fourier_field,extent=[BeamShaper.x_array_out[0]/mm,BeamShaper.x_array_out[-1]/mm,BeamShaper.x_array_out[0]/mm,BeamShaper.x_array_out[-1]/mm])
plt.xlabel("Position X [mm]")
plt.ylabel("Position Y [mm]")
plt.title("Target Intensity in the Fourier plane")
plt.show()



# plt.plot(BeamShaper.x_array_out/mm,rect_(BeamShaper.x_array_out, w_0))
# plt.show()

# plt.plot(BeamShaper.x_array_in/mm, Intensity(input_field)[BeamShaper.nb_of_samples//2,:])
# plt.show()


# fig, ax = plt.subplots(1,1,figsize=(12, 5))
#
# ax[0].plot(u,gauss,label = "input amplitude")
# ax[0].plot(u,np.abs(sinc),label="|target amplitude|")
# ax[0].set_xlabel("u [no units]", fontsize=15)
# ax[0].set_ylabel("amplitude values [no units]", fontsize=15)
#
# plt.legend()
# plt.savefig("input_vs_target_amp.svg")
# plt.show()



# # Save Input Beam Field
# save_input_beam(results_directory, BeamShaper, input_field)
#
# # Generate SLM Mask
# mask_type = "Wedge"
# angle = 2
# orientation = "Horizontal"
# mask = BeamShaper.generate_mask(mask_type=mask_type,
#                                       angle=angle,
#                                       orientation=orientation)
#
# # Modulate and propagate
# modulated_input_field = BeamShaper.phase_modulate_input_beam(mask)
# fourier_plane_field = BeamShaper.propagate_FFT_modulated_beam(propagation_type="PipFFT")
# fourier_filtered_field = BeamShaper.filter_beam()
# output_field = BeamShaper.propagate_FFT_to_image_plane(propagation_type="PipFFT")
#
# # Save results
# save_generated_fields(BeamShaper, modulated_input_field, fourier_plane_field, fourier_filtered_field, output_field,
#                           results_directory)




