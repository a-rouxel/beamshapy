from BeamShaper import BeamShaper
from utils import *
from LightPipes import *


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

# w_0 = 2.3*mm
# sampling = BeamShaper.nb_of_samples
# new_amp = sinc(BeamShaper.GridPositionMatrix_X,w_0)
# phase = np.zeros_like(new_amp)
# phase[new_amp>0] = np.pi


def rect_(x, w):
    """Rectangular function (porte) of width T_0."""
    return np.where(np.abs(x) < w / 2., 1, 0)

def sin_(x,period):
    return np.sin(2*np.pi*x/period)

w = 0.1
x_in = np.linspace(-5,5,BeamShaper.nb_of_samples)
y_in = np.linspace(-5,5,BeamShaper.nb_of_samples)
X,Y = np.meshgrid(x_in,y_in)

# plt.plot(x_in,rect_(x_in,2*w ),label="flat top")
# plt.plot(x_in,sin_(x_in,4*w/1 ),label="sinus - period = 4w")
# plt.plot(x_in,sin_(x_in,4*w/2 ),label="sinus - period = 2w")
# plt.plot(x_in,sin_(x_in,4*w/3 ),label="sinus - period = w")
# plt.plot(x_in,rect_(x_in,2*w )*sin_(x_in,4*w/1 ),label="flattop x sin - p = 4w")
# plt.plot(x_in,rect_(x_in,2*w )*sin_(x_in,4*w/2 ),'--',label="flattop x sin - p = 2w")
# plt.plot(x_in,rect_(x_in,2*w )*sin_(x_in,4*w/3 ),'--',label="flat top x sin - p = 4w/3")
# plt.plot(x_in,rect_(x_in,2*w )*sin_(x_in,4*w/4 ),'--',label="flat top x sin - p = w")

plt.legend()
plt.show()

complex_amp = rect_(X,4*w )*rect_(Y,2*w )*sin_(X,4*w/8 )


plt.imshow(np.angle(complex_amp))
plt.show()




#
# import matplotlib.pyplot as plt
#
# def sinc(x,w):
#     return np.sin(np.pi*x/w)/(np.pi*x/w)
#
# w_0 = 2.3*mm
# sampling = BeamShaper.nb_of_samples
# new_amp = sinc(BeamShaper.GridPositionMatrix_X,w_0)
# phase = np.zeros_like(new_amp)
# phase[new_amp>0] = np.pi


# plt.plot(BeamShaper.x_array_in/mm,sinc(BeamShaper.GridPositionMatrix_X, w_0)[sampling//2,:])
# plt.show()
#
fourier_field = SubIntensity(input_field, np.abs(complex_amp)**2)
fourier_field = SubPhase(fourier_field, np.angle(complex_amp))


#
SLM_field = PipFFT(fourier_field,-1)

plt.plot(np.sqrt(Intensity(SLM_field)[BeamShaper.nb_of_samples//2,:])*Phase(SLM_field)[BeamShaper.nb_of_samples//2,:])
plt.show()

fig, ax = plt.subplots(1,2)

ax[0].imshow(Phase(SLM_field))


phase_simp = Phase(SLM_field)
phase_simp[phase_simp>0] = np.pi/2
phase_simp[phase_simp<0] = -np.pi/2
ax[1].imshow(phase_simp)
plt.show()
#

