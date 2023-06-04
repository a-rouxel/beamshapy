import numpy as np
import yaml
from LightPipes import *

class BeamShaper():

    def __init__(self,initial_config_file):
        self.initial_config_file = initial_config_file

        # Load the initial configuration file if one was provided
        if self.initial_config_file is not None:
            self.load_config(self.initial_config_file)



    def generate_input_beam(self,simulation_config,input_beam_config):

        F = Begin(simulation_config["grid size"], input_beam_config["beam"]["wavelength"], simulation_config["sampling"])

        print(input_beam_config)

        if input_beam_config["beam"]["type"] == "Gaussian":
            F = GaussBeam(F,
                          w0=input_beam_config["beam"]["waist"],
                          LG=input_beam_config["beam"]["LG"],
                          n=input_beam_config["beam"]["n"],
                          m=input_beam_config["beam"]["m"])
        elif input_beam_config["beam"]["type"] == "Plane":
            F = PlaneWave(F, w=simulation_config["grid size"])
        else:
            raise ValueError("Unknown field type")

        return F

    def generate_sampling(self,simulation_config,input_beam_config):

        grid_size = simulation_config["grid size"]*mm
        sampling = simulation_config["sampling"]
        focal_length = self.config["focal length"]*mm

        wavelength = input_beam_config["beam"]["wavelength"]*nm

        delta_x_in = grid_size / sampling
        delta_x_out = wavelength * focal_length / (delta_x_in * sampling)

        x_array_in = np.round(np.linspace(-grid_size / 2, grid_size / 2, sampling), 9)

        x_array_out = np.arange(-sampling / 2, sampling / 2, 1)
        x_array_out *= delta_x_out

        x = np.linspace(-grid_size / 2, grid_size / 2, sampling)
        y = np.linspace(-grid_size / 2, grid_size / 2, sampling)
        GridPositionMatrix_X, GridPositionMatrix_Y = np.meshgrid(x, y)

        self.delta_x_in = delta_x_in
        self.delta_x_out = delta_x_out
        self.x_array_in = x_array_in
        self.x_array_out = x_array_out
        self.GridPositionMatrix_X = GridPositionMatrix_X
        self.GridPositionMatrix_Y = GridPositionMatrix_Y



    def load_config(self, file_name):
        with open(file_name, 'r') as file:
            self.config = yaml.safe_load(file)
        # Call a method to update the GUI with the loaded config