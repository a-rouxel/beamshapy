from PyQt5.QtWidgets import (QTabWidget,QHBoxLayout, QPushButton, QFileDialog,
                             QLineEdit, QComboBox,QFormLayout, QGroupBox, QScrollArea,
                             QVBoxLayout, QCheckBox, QSpinBox, QWidget)
from PyQt5.QtCore import Qt,QThread, pyqtSignal, pyqtSlot
import yaml
import pyqtgraph as pg
from pyqtgraph import ImageView
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from LightPipes import Field, Phase, Intensity
# from InputBeamEditorWidget import InputBeamEditorWidget
# from SimulationConfigEditorWidget import SimulationConfigEditorWidget
from utils import *
import h5py
import matplotlib.figure as mpl_fig
import matplotlib.backends.backend_qt5agg as mpl_backend
import numpy as np
from LightPipes import mm

class InputBeamIntensityDisplay(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.figure_cam = plt.figure()
        self.canvas_cam = FigureCanvas(self.figure_cam)
        self.toolbar_cam = NavigationToolbar(self.canvas_cam, self)

        self.layout.addWidget(self.toolbar_cam)
        self.layout.addWidget(self.canvas_cam)

    def display_input_beam_intensity(self, intensity, x_range_mm, y_range_mm):

        self.figure_cam.clear()

        ax = self.figure_cam.add_subplot(111)
        imshow = ax.imshow(intensity, cmap='viridis', extent=[-x_range_mm/2, x_range_mm/2, -y_range_mm/2, y_range_mm/2])

        # Set labels with LaTeX font.
        ax.set_xlabel(f'Position along X [mm]', fontsize=10)
        ax.set_ylabel(f'Position along Y [mm]', fontsize=10)
        ax.set_title(f'Intensity Map', fontsize=12)

        self.canvas_cam.draw()


class InputBeamPhaseDisplay(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QVBoxLayout for the widget
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.figure_cam = plt.figure()
        self.canvas_cam = FigureCanvas(self.figure_cam)
        self.toolbar_cam = NavigationToolbar(self.canvas_cam, self)

        self.layout.addWidget(self.toolbar_cam)
        self.layout.addWidget(self.canvas_cam)


    def display_input_beam_phase(self, phase, x_range_mm, y_range_mm):
        """
        Display the phase map.
        """

        self.figure_cam.clear()

        ax = self.figure_cam.add_subplot(111)
        imshow = ax.imshow(phase, cmap='viridis', extent=[-x_range_mm/2, x_range_mm/2, -y_range_mm/2, y_range_mm/2])

        # Set labels with LaTeX font.
        ax.set_xlabel(f'Position along X [mm]', fontsize=10)
        ax.set_ylabel(f'Position along Y [mm]', fontsize=10)
        ax.set_title(f'Phase Map', fontsize=12)

        self.canvas_cam.draw()


class Worker(QThread):
    finished_generate_input_beam = pyqtSignal(Field)

    def __init__(self, input_beam_editor,simulation_editor,beam_shaper):
        super().__init__()
        self.input_beam_config = input_beam_editor.config
        self.simulation_editor = simulation_editor
        self.simulation_config = simulation_editor.config
        self.beam_shaper = beam_shaper

    def run(self):
        # Put your analysis here

        self.beam_shaper.generate_sampling()
        self.simulation_editor.update_nb_of_samples(self.beam_shaper.nb_of_samples)
        input_field = self.beam_shaper.generate_input_beam(self.input_beam_config)
        self.finished_generate_input_beam.emit(input_field)



class InputBeamWidget(QWidget):
    def __init__(self, beam_shaper, infos_editor,simulation_editor,input_beam_editor):
        super().__init__()

        # Create the dimensioning configuration editor
        self.beam_shaper = beam_shaper
        self.infos_editor = infos_editor
        self.simulation_editor = simulation_editor
        self.input_beam_editor = input_beam_editor

        # Create the result display widget (tab widget in this case)
        self.result_display_widget = QTabWidget()

        # Create the result displays and store them as attributes
        self.input_beam_intensity_display = InputBeamIntensityDisplay()
        self.input_beam_phase_display = InputBeamPhaseDisplay()

        # Add the result displays to the tab widget
        self.result_display_widget.addTab(self.input_beam_intensity_display, "Input Beam Intensity")
        self.result_display_widget.addTab(self.input_beam_phase_display, "Input Beam Phase")

        # Create the run button
        self.run_button = QPushButton('Generate Input Beam')
        # self.run_button.setStyleSheet('QPushButton {background-color: gray; color: white;}')        # Connect the button to the run_dimensioning method
        self.run_button.clicked.connect(self.run_beam_generation)

        self.save_input_beam_button = QPushButton("Save Intensity and Phase")
        self.save_input_beam_button.setDisabled(True)
        self.save_input_beam_button.clicked.connect(self.on_input_beam_saved)

        # Create a group box for the run button
        self.run_button_group_box = QGroupBox()
        run_button_group_layout = QVBoxLayout()
        run_button_group_layout.addWidget(self.run_button)
        run_button_group_layout.addWidget(self.save_input_beam_button)
        run_button_group_layout.addWidget(self.result_display_widget)
        self.run_button_group_box.setLayout(run_button_group_layout)

        # Create a QVBoxLayout for the editors
        self.editor_layout = QVBoxLayout()

        self.editor_layout.addWidget(self.infos_editor)
        self.editor_layout.addWidget(self.simulation_editor)
        self.editor_layout.addWidget(self.input_beam_editor)


        # Create a QHBoxLayout for the whole widget
        self.layout = QHBoxLayout()
        self.layout.addLayout(self.editor_layout)  # Add the editor layout
        self.layout.addWidget(self.run_button_group_box)
        self.layout.setStretchFactor(self.run_button_group_box, 1)
        self.layout.setStretchFactor(self.result_display_widget, 2)

        # Set the layout on the widget
        self.setLayout(self.layout)

    def on_input_beam_saved(self):
        # self.result_directory = initialize_directory(self.infos_editor.config)
        self.simulation_name = self.infos_editor.config['simulation name']
        self.results_directory = self.infos_editor.config['results directory']
        results_directory = os.path.join(self.results_directory, self.simulation_name)

        save_input_beam(results_directory, self.beam_shaper, self.last_generated_beam_field)

        self.save_input_beam_button.setDisabled(True)

    def run_beam_generation(self):
        # Get the configs from the editors
        self.input_beam_editor.get_config()
        self.simulation_editor.get_config()

        self.worker = Worker(self.input_beam_editor,self.simulation_editor, self.beam_shaper)
        self.worker.finished_generate_input_beam.connect(self.display_input_beam_intensity)
        self.worker.finished_generate_input_beam.connect(self.display_input_beam_phase)
        self.worker.start()

    @pyqtSlot(Field)
    def display_input_beam_intensity(self, input_beam):
        print("Displaying input beam intensity")
        self.save_input_beam_button.setDisabled(False)
        self.last_generated_beam_field = input_beam
        self.input_beam_intensity_display.display_input_beam_intensity(Intensity(input_beam),self.simulation_editor.config['grid size'], self.simulation_editor.config['grid size'])

    @pyqtSlot(Field)
    def display_input_beam_phase(self, input_beam):
        self.input_beam_phase_display.display_input_beam_phase(Phase(input_beam), self.simulation_editor.config['grid size'], self.simulation_editor.config['grid size'])

    def load_simulation_config(self, file_name):
        with open(file_name, 'r') as file:
            return yaml.safe_load(file)
