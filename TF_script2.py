# from BeamShaper import BeamShaper
# from utils import *
# from LightPipes import *
# #
# #
# # simulation_config = load_yaml_config("config/simulation.yml")
# # input_beam_config = load_yaml_config("config/input_beam.yml")
# #
# #
# # results_directory = "experiment_results"
# #
# #
# #
# # BeamShaper = BeamShaper(simulation_config,
# #                         input_beam_config,
# #                         initial_config_file="config/optical_system.yml")
# #
# # # Generate System Sampling
# # BeamShaper.generate_sampling()
# #
# # # Generate System Input Beam Field
# # input_field = BeamShaper.generate_input_beam(input_beam_config)
#
# import matplotlib.pyplot as plt
#
# def sinc(x,w):
#     return np.sin(np.pi*x/w)/(np.pi*x/w)
#
# # w_0 = 2.3*mm
# # sampling = BeamShaper.nb_of_samples
# # new_amp = sinc(BeamShaper.GridPositionMatrix_X,w_0)
# # phase = np.zeros_like(new_amp)
# # phase[new_amp>0] = np.pi
#
#
# def rect_(x, w):
#     """Rectangular function (porte) of width T_0."""
#     return np.where(np.abs(x) < w / 2., 1, 0)
#
# def sin_(x,period):
#     return np.sin(2*np.pi*x/period)
#
# w = 2
# x_in = np.linspace(-5,5,1000)
# # plt.plot(x_in,rect_(x_in,2*w ),label="flat top")
# # plt.plot(x_in,sin_(x_in,4*w/1 ),label="sinus - period = 4w")
# # plt.plot(x_in,sin_(x_in,4*w/2 ),label="sinus - period = 2w")
# # plt.plot(x_in,sin_(x_in,4*w/3 ),label="sinus - period = w")
# plt.plot(x_in,rect_(x_in,2*w )*sin_(x_in,4*w/1 ),label="flattop x sin - p = 4w")
# plt.plot(x_in,rect_(x_in,2*w )*sin_(x_in,4*w/2 ),'--',label="flattop x sin - p = 2w")
# plt.plot(x_in,rect_(x_in,2*w )*sin_(x_in,4*w/3 ),'--',label="flat top x sin - p = 4w/3")
# plt.plot(x_in,rect_(x_in,2*w )*sin_(x_in,4*w/4 ),'--',label="flat top x sin - p = w")
#
# plt.legend()
# plt.show()
# # plt.plot(BeamShaper.x_array_in/mm,sinc(BeamShaper.GridPositionMatrix_X, w_0)[sampling//2,:])
# # plt.show()
# #
# # sinc_field = SubIntensity(input_field, np.abs(new_amp)**2)
# # sinc_field = SubPhase(sinc_field, phase)
# #
# # fourier_plane = PipFFT(sinc_field)
#
# # plt.plot(BeamShaper.x_array_out/mm,(Intensity(fourier_plane)[sampling//2,:]))
# # plt.show()
# #
# # plt.plot(BeamShaper.x_array_out/mm,rect_(BeamShaper.x_array_out, w_0))
# # plt.show()
#
# # plt.plot(BeamShaper.x_array_in/mm, Intensity(input_field)[BeamShaper.nb_of_samples//2,:])
# # plt.show()
#
#
# # fig, ax = plt.subplots(1,1,figsize=(12, 5))
# #
# # ax[0].plot(u,gauss,label = "input amplitude")
# # ax[0].plot(u,np.abs(sinc),label="|target amplitude|")
# # ax[0].set_xlabel("u [no units]", fontsize=15)
# # ax[0].set_ylabel("amplitude values [no units]", fontsize=15)
# #
# # plt.legend()
# # plt.savefig("input_vs_target_amp.svg")
# # plt.show()
#
#
#
# # # Save Input Beam Field
# # save_input_beam(results_directory, BeamShaper, input_field)
# #
# # # Generate SLM Mask
# # mask_type = "Wedge"
# # angle = 2
# # orientation = "Horizontal"
# # mask = BeamShaper.generate_mask(mask_type=mask_type,
# #                                       angle=angle,
# #                                       orientation=orientation)
# #
# # # Modulate and propagate
# # modulated_input_field = BeamShaper.phase_modulate_input_beam(mask)
# # fourier_plane_field = BeamShaper.propagate_FFT_modulated_beam(propagation_type="PipFFT")
# # fourier_filtered_field = BeamShaper.filter_beam()
# # output_field = BeamShaper.propagate_FFT_to_image_plane(propagation_type="PipFFT")
# #
# # # Save results
# # save_generated_fields(BeamShaper, modulated_input_field, fourier_plane_field, fourier_filtered_field, output_field,
# #                           results_directory)
#
#
#
#
import pyqtgraph.examples
pyqtgraph.examples.run()
