# Beamshapy: Laser Beam Shaping Module

Beamshapy is a Python-based module designed for crafting laser beam shaping masks for use on phase-only Spatial Light Modulators (SLM). It leverages Fast Fourier Transform (FFT) propagation and relies on the Lightpipes package for its core functionality.

## Features

Beamshapy provides two primary methods for mask design:

1. **Manual Design**:
   - Craft appropriate masks for a targeted profile using the method described in *Encoding amplitude information onto phase-only filters*, JA Davis, 1999 [Read the article](https://doi.org/10.1364/AO.38.005004)
   - Suitable for controlling amplitude and phase in the conjugate Fourier plane.

2. **Gerchberg and Saxton Algorithm**:
   - Design masks when only the intensity profile is important.
   - Optimizes the phase mask to achieve the targeted intensity in the conjugate Fourier plane.

## Examples

Beamshapy includes several examples to demonstrate its capabilities:

- `example_simple_FT_propagation.py`: Simple propagation with a wrapped wedge displayed on the SLM.
- `example_mask_design_BG_modul.py`: Mask design and propagation, used to design the masks featured in the associated article.
- `example_mask_design_fresnel.py`: Mask design for a Fresnel lens.
- `example_mask_design_GSA.py`: Target intensity design and Gerchberg and Saxton optimization routine to obtain the phase mask for the targeted intensity in the conjugate Fourier plane.

For a practical application of Beamshapy, refer to our article: *Selective excitation of high-order modes in two-dimensional cavity resonator integrated grating filters*, A. Rouxel et al, 2024. [Read the article](https://doi.org/10.1364/OL.519472)

## Installation

To install `beamshapy`, follow these steps:

1. **Clone the repository from GitHub**:

   ```bash
   git clone https://github.com/a-rouxel/beamshapy.git
   cd beamshapy
   ```

2. **Create a dedicated Python environment using Miniconda**:
   If you don't have Miniconda installed, follow the instructions [here](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html).

   ```bash
   # Create a new Python environment
   conda create -n beamshapy python=3.9

   # Activate the environment
   conda activate beamshapy
   ```

3. **Install the necessary Python packages**:
   The required packages are listed in the `requirements.txt` file in the repository.

   ```bash
   # Install necessary Python packages with pip
   pip install -r requirements.txt
   ```

## License

Beamshapy is open-source and available under the [MIT License](LICENSE).

## Contributions

Contributions are welcome! Please feel free to submit issues, fork the repository, and send pull requests.

## Contact

For any questions or feedback, please contact the repository owner at [arouxel@laas.fr](mailto:arouxel@laas.fr).
