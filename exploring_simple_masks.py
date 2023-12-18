import numpy as np

from beamshapy.BeamShaper import BeamShaper, Intensity,Phase, um, mm
from beamshapy.mask_generation.functions_masks_generation import wrap_phase
from beamshapy.helpers import *
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

def overlap(a,b):
        numerator = np.sum(a * np.conjugate(b))
        denominator = np.sqrt(np.sum(np.abs(a) ** 2) * np.sum(np.abs(b) ** 2))
        return np.abs(numerator) / denominator

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
height = 500*um

for i in range(1,5):


        sinus_period = 500*um *2/i

        target_amplitude = beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type="Rectangle",width=width,height=height,position=(0,0))

        if i%2 == 0:
            target_amplitude *= beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type="Sinus",period=sinus_period)
        else:
            target_amplitude *= beam_shaper.amplitude_generator.generate_target_amplitude(amplitude_type="Cosinus",period=sinus_period)

        plt.imshow(target_amplitude,extent=[(beam_shaper.x_array_out/mm).min(),(beam_shaper.x_array_out/mm).max(),(beam_shaper.x_array_out/mm).min(),(beam_shaper.x_array_out/mm).max()])
        plt.title(f"Target Amplitude - period={sinus_period/um}um")
        plt.colorbar()
        plt.xlim(-1.5,1.5)
        plt.ylim(-1.5,1.5)
        plt.savefig(f"./target_amplitude_{i}.png")
        plt.show()


        # Calculate inverse fourier transform of the target amplitude
        beam_shaper.inverse_fourier_transform(target_amplitude,inverse_fourier_type="JaxFFT")

        # Generate SLM Mask
        mask_type = "Wedge"
        angle = 0
        position = 1.5*mm

        wedge_mask = beam_shaper.mask_generator.design_mask(mask_type=mask_type,angle=angle,position=position)
        phase_inversion_mask = beam_shaper.mask_generator.generate_target_mask(mask_type="phase target field")
        amplitude_modulation_mask = beam_shaper.mask_generator.generate_target_mask(mask_type="modulation amplitude")
        #
        fig, ax = plt.subplots(1,2)

        im = ax[0].imshow(phase_inversion_mask)
        im2 = ax[1].imshow(amplitude_modulation_mask)
        ax[0].set_title("Phase Inversion Mask")
        ax[1].set_title("Amplitude Modulation Mask")
        plt.savefig(f"./phase_inversion_mask_amplitude_modulation_mask_{i}.png")

        plt.show()


        resulting_mask =  wrap_phase(wedge_mask + phase_inversion_mask) * amplitude_modulation_mask

        # Modulate and propagate
        modulated_input_field = beam_shaper.phase_modulate_input_beam(phase_inversion_mask)
        fourier_plane_field = beam_shaper.propagate_FFT_modulated_beam(propagation_type="JaxFFT")

        plt.plot(np.real(fourier_plane_field.field)[1250,:])
        plt.xlim(500,1800)
        plt.title("Fourier Plane Field")
        plt.savefig(f"./fourier_plane_field_{i}.png")
        plt.show()

        plt.imshow(Intensity(fourier_plane_field))
        plt.colorbar()
        plt.show()

        norm = 10000

        # Recalculate the initial squared sum (total power) for each field
        initial_power_target = np.sum(np.abs(target_amplitude) ** 2)
        initial_power_fourier = np.sum(np.abs(fourier_plane_field.field) ** 2)

        # Calculate the scaling factors
        scaling_factor_target = np.sqrt(norm / initial_power_target)
        scaling_factor_fourier = np.sqrt(norm / initial_power_fourier)

        # Apply the scaling
        normalized_target_amplitude = target_amplitude * scaling_factor_target
        normalized_fourier_plane_field_field = fourier_plane_field.field * scaling_factor_fourier

        final_power_target = np.sum(np.abs(normalized_target_amplitude) ** 2)
        final_power_fourier = np.sum(np.abs(normalized_fourier_plane_field_field) ** 2)

        print("Total power of target field: ", final_power_target)
        print("Total power of fourier plane field: ", final_power_fourier)
        print("Overlap between target amplitude and fourier plane field: ", np.abs(overlap(normalized_target_amplitude,normalized_fourier_plane_field_field)))