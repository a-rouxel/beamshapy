from PyQt5.QtWidgets import (QTabWidget,QHBoxLayout, QPushButton, QFileDialog,
                             QLineEdit, QComboBox,QFormLayout, QGroupBox, QScrollArea,
                             QVBoxLayout, QCheckBox, QSpinBox, QWidget)
from PyQt5.QtCore import Qt,QThread, pyqtSignal, pyqtSlot
from LightPipes import Field, Phase, Intensity
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget
from LightPipes import mm,um,nm
from PyQt5.QtWidgets import QMessageBox
import numpy as np
import os
import h5py
from utils import *
class DisplayWidget(QWidget):
    def __init__(self, beam_shaper):
        super().__init__()

        self.beam_shaper = beam_shaper

        # Create a tab widget to hold the plots
        self.tabWidget = QTabWidget(self)

        # Create figures and figure canvases for the plots
        # Existing figures, canvases and toolbars
        self.maskFigure = Figure()
        self.maskCanvas = FigureCanvas(self.maskFigure)
        self.maskToolbar = NavigationToolbar(self.maskCanvas, self)

        self.cutXFigure = Figure()
        self.cutXCanvas = FigureCanvas(self.cutXFigure)
        self.cutXToolbar = NavigationToolbar(self.cutXCanvas, self)

        self.cutYFigure = Figure()
        self.cutYCanvas = FigureCanvas(self.cutYFigure)
        self.cutYToolbar = NavigationToolbar(self.cutYCanvas, self)

        # New figures, canvases and toolbars for Phase
        self.phaseFigure = Figure()
        self.phaseCanvas = FigureCanvas(self.phaseFigure)
        self.phaseToolbar = NavigationToolbar(self.phaseCanvas, self)

        self.phaseCutXFigure = Figure()
        self.phaseCutXCanvas = FigureCanvas(self.phaseCutXFigure)
        self.phaseCutXToolbar = NavigationToolbar(self.phaseCutXCanvas, self)

        self.phaseCutYFigure = Figure()
        self.phaseCutYCanvas = FigureCanvas(self.phaseCutYFigure)
        self.phaseCutYToolbar = NavigationToolbar(self.phaseCutYCanvas, self)

        # Create Widgets for each tab to hold the toolbar and the figure canvas
        # Existing widgets
        self.maskWidget = QWidget()
        self.maskLayout = QVBoxLayout(self.maskWidget)
        self.maskLayout.addWidget(self.maskToolbar)
        self.maskLayout.addWidget(self.maskCanvas)

        self.cutXWidget = QWidget()
        self.cutXLayout = QVBoxLayout(self.cutXWidget)
        self.cutXLayout.addWidget(self.cutXToolbar)
        self.cutXLayout.addWidget(self.cutXCanvas)

        self.cutYWidget = QWidget()
        self.cutYLayout = QVBoxLayout(self.cutYWidget)
        self.cutYLayout.addWidget(self.cutYToolbar)
        self.cutYLayout.addWidget(self.cutYCanvas)

        # New widgets for Phase
        self.phaseWidget = QWidget()
        self.phaseLayout = QVBoxLayout(self.phaseWidget)
        self.phaseLayout.addWidget(self.phaseToolbar)
        self.phaseLayout.addWidget(self.phaseCanvas)

        self.phaseCutXWidget = QWidget()
        self.phaseCutXLayout = QVBoxLayout(self.phaseCutXWidget)
        self.phaseCutXLayout.addWidget(self.phaseCutXToolbar)
        self.phaseCutXLayout.addWidget(self.phaseCutXCanvas)

        self.phaseCutYWidget = QWidget()
        self.phaseCutYLayout = QVBoxLayout(self.phaseCutYWidget)
        self.phaseCutYLayout.addWidget(self.phaseCutYToolbar)
        self.phaseCutYLayout.addWidget(self.phaseCutYCanvas)

        # Add the Widgets to the tab widget
        # Existing tabs
        self.tabWidget.addTab(self.maskWidget, "Intensity Map")
        self.tabWidget.addTab(self.cutXWidget, "Intensity Cut X")
        self.tabWidget.addTab(self.cutYWidget, "Intensity Cut Y")

        # New tabs for Phase
        self.tabWidget.addTab(self.phaseWidget, "Phase Map")
        self.tabWidget.addTab(self.phaseCutXWidget, "Phase Cut X")
        self.tabWidget.addTab(self.phaseCutYWidget, "Phase Cut Y")


        # Create a QVBoxLayout and add the tab widget to it

        layout = QVBoxLayout(self)

        layout.addWidget(self.tabWidget)

    @pyqtSlot(np.ndarray)
    def displayMask(self, field,x_array,downsampling_checkbox=False, downsample_factor=1):
        # Plot the mask
        self.maskFigure.clear()
        ax1 = self.maskFigure.add_subplot(111)

        x_array = x_array

        if downsampling_checkbox:
            intensity_field = downsample(Intensity(field), downsample_factor)
            phase_field = downsample(Phase(field), downsample_factor)
            x_array_2D = downsample_1d(x_array, downsample_factor)
        else :
            intensity_field = Intensity(field)
            phase_field = Phase(field)
            x_array_2D = x_array

        im = ax1.imshow(intensity_field,extent=[x_array_2D[0],x_array_2D[-1], x_array_2D[0],x_array_2D[-1]])
        ax1.set_title('Intensity Map')
        ax1.set_xlabel('Position along X [in mm]')
        ax1.set_ylabel('Position along Y [in mm]')
        self.maskFigure.colorbar(im, ax=ax1,label='Intensity Value [no units]')
        self.maskCanvas.draw()

        # Plot the cut along X
        self.cutXFigure.clear()
        ax2 = self.cutXFigure.add_subplot(111)
        ax2.plot(x_array,Intensity(field)[Intensity(field).shape[0] // 2, :])
        ax2.set_title('Cut along X')
        ax2.set_xlabel('Position along X [in mm]')
        ax2.set_ylabel('Intensity Value [no units]')
        self.cutXCanvas.draw()

        # Plot the cut along Y
        self.cutYFigure.clear()
        ax3 = self.cutYFigure.add_subplot(111)
        ax3.plot(x_array,Intensity(field)[:, Intensity(field).shape[1] // 2])
        ax3.set_title('Cut along Y')
        ax3.set_xlabel('Position along Y [in mm]')
        ax3.set_ylabel('Intensity Value [no units]')
        self.cutYCanvas.draw()

        self.phaseFigure.clear()
        ax4 = self.phaseFigure.add_subplot(111)
        im = ax4.imshow(phase_field, extent=[x_array_2D[0], x_array_2D[-1], x_array_2D[0], x_array_2D[-1]],cmap="twilight")
        ax4.set_title('Phase Map')
        ax4.set_xlabel('Position along X [in mm]')
        ax4.set_ylabel('Position along Y [in mm]')
        self.phaseFigure.colorbar(im, ax=ax4, label='Phase Value [no units]')
        self.phaseCanvas.draw()

        # For Phase Cut X (assuming phaseCutX(field) returns the required data for phase cut along X)
        self.phaseCutXFigure.clear()
        ax5 = self.phaseCutXFigure.add_subplot(111)
        ax5.plot(x_array, Phase(field)[Phase(field).shape[0] // 2, :])
        ax5.set_title('Phase Cut along X')
        ax5.set_xlabel('Position along X [in mm]')
        ax5.set_ylabel('Phase Value [no units]')
        self.phaseCutXCanvas.draw()

        # For Phase Cut Y (assuming phaseCutY(field) returns the required data for phase cut along Y)
        self.phaseCutYFigure.clear()
        ax6 = self.phaseCutYFigure.add_subplot(111)
        ax6.plot(x_array, Phase(field)[:, Phase(field).shape[1] // 2])
        ax6.set_title('Phase Cut along Y')
        ax6.set_xlabel('Position along Y [in mm]')
        ax6.set_ylabel('Phase Value [no units]')
        self.phaseCutYCanvas.draw()
class ModulatedInputFieldDisplay(DisplayWidget):
    @pyqtSlot(Field)
    def display_modulated_input_field(self, modulated_input_field,downsample_check,downsample_factor):
        self.displayMask(modulated_input_field,self.beam_shaper.x_array_in/mm,downsample_check,downsample_factor)

class PropagatedFFTModulatedBeamDisplay(QWidget):
    def __init__(self, beam_shaper):
        super().__init__()
        self.layout = QVBoxLayout(self)

        self.propagated_display = DisplayWidget(beam_shaper)
        self.filtered_display = DisplayWidget(beam_shaper)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.propagated_display, "Propagated FFT Modulated Beam")
        self.tabWidget.addTab(self.filtered_display, "Filtered Beam")

        self.layout.addWidget(self.tabWidget)

    @pyqtSlot(Field)
    def display_fourier_plane_field(self, fourier_plane_field,downsampling_checkbox, downsample_factor):
        self.propagated_display.displayMask(fourier_plane_field, self.propagated_display.beam_shaper.x_array_out / mm,downsampling_checkbox, downsample_factor)

    @pyqtSlot(Field)
    def display_fourier_filtered_field(self, fourier_filtered_field,downsampling_checkbox, downsample_factor):
        self.filtered_display.displayMask(fourier_filtered_field,self.filtered_display.beam_shaper.x_array_out / mm,downsampling_checkbox, downsample_factor)

class PropagatedImagePlaneDisplay(DisplayWidget):
    @pyqtSlot(Field)
    def display_output_field(self, output_field,downsampling_checkbox, downsample_factor):
        self.displayMask(output_field,self.beam_shaper.x_array_in/mm,downsampling_checkbox, downsample_factor)

class PropagationEditor(QWidget):
    def __init__(self):
        super().__init__()

        # Create a QScrollArea
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)

        # Create a widget for the scroll area
        scroll_widget = QWidget()

        # Create general QFormLayout
        general_layout = QFormLayout()
        general_group = QGroupBox("General Settings")
        general_group.setLayout(general_layout)

        # Create Fourier Plane QFormLayout
        fourier_plane_layout = QFormLayout()
        # self.crop_factor_fourier_x = QLineEdit()
        # self.crop_factor_fourier_x.setText(str(2))
        # self.crop_factor_fourier_y = QLineEdit()
        # self.crop_factor_fourier_y.setText(str(4))
        # self.crop_button = QPushButton('crop')  # Create a button
        # # self.run_button.clicked.connect(self.crop_fourier_plane)
        # self.interpolate_fourier_factor = QLineEdit()
        # self.interpolate_fourier_factor.setText(str(2))
        # self.interpolate_button = QPushButton('interpolate')  # Create a button
        # self.interpolate_button.clicked.connect(self.interpolate_fourier_plane)

        # fourier_plane_layout.addRow("crop factor X", self.crop_factor_fourier_x)
        # fourier_plane_layout.addRow("crop factor Y", self.crop_factor_fourier_y)
        # fourier_plane_layout.addRow(self.crop_button)
        # fourier_plane_layout.addRow("interpolation factor", self.interpolate_fourier_factor)
        # fourier_plane_layout.addRow(self.interpolate_button)

        fourier_plane_group = QGroupBox("Fourier Plane Settings")
        fourier_plane_group.setLayout(fourier_plane_layout)

        # Create Image Plane QFormLayout
        image_plane_layout = QFormLayout()
        # self.crop_factor_image_x = QLineEdit()
        # self.crop_factor_image_x.setText(str(2))
        # self.crop_factor_image_y = QLineEdit()
        # self.crop_factor_image_y.setText(str(4))
        # self.crop_button = QPushButton('crop')  # Create a button
        # # self.run_button.clicked.connect(self.crop_fourier_plane)
        # self.interpolate_image_factor = QLineEdit()
        # self.interpolate_image_factor.setText(str(2))
        # self.interpolate_button = QPushButton('interpolate')  # Create a button
        # self.interpolate_button.clicked.connect(self.interpolate_fourier_plane)

        # image_plane_layout.addRow("crop factor X", self.crop_factor_image_y)
        # image_plane_layout.addRow("crop factor Y", self.crop_factor_fourier_y)
        # image_plane_layout.addRow(self.crop_button)
        # image_plane_layout.addRow("interpolation factor", self.interpolate_image_factor)
        # image_plane_layout.addRow(self.interpolate_button)

        image_plane_group = QGroupBox("Image Plane Settings")

        image_plane_group.setLayout(image_plane_layout)

        # Add groups to main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(general_group)
        main_layout.addWidget(fourier_plane_group)
        main_layout.addWidget(image_plane_group)

        # Set the layout of the widget within the scroll area
        scroll_widget.setLayout(main_layout)

        # Set the widget for the scroll area
        scroll.setWidget(scroll_widget)

        # Create a layout for the current widget and add the scroll area
        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

class Worker(QThread):
    finished_modulate_input_beam = pyqtSignal(Field)
    finished_propagate_FFT_modulated_beam = pyqtSignal(Field)
    finished_propagate_filter_beam = pyqtSignal(Field)
    finished_propagate_to_image_plane = pyqtSignal(Field)

    def __init__(self,beam_shaper,slm_widget):
        super().__init__()
        self.beam_shaper = beam_shaper
        self.slm_widget = slm_widget

    def run(self):
        print("worker started")

        self.result_mask = self.slm_widget.result_mask

        modulated_input_beam = self.beam_shaper.phase_modulate_input_beam(self.result_mask)
        self.finished_modulate_input_beam.emit(modulated_input_beam)
        fourier_plane_field = self.beam_shaper.propagate_FFT_modulated_beam(propagation_type="PipFFT")
        self.finished_propagate_FFT_modulated_beam.emit(fourier_plane_field)
        fourier_filtered_field = self.beam_shaper.filter_beam()
        self.finished_propagate_filter_beam.emit(fourier_filtered_field)
        output_field = self.beam_shaper.propagate_FFT_to_image_plane(propagation_type="PipFFT")
        self.finished_propagate_to_image_plane.emit(output_field)

        print("worker finished")
class FourierPlaneDetectionWidget(QWidget):
    def __init__(self,main_window,beam_shaper,infos_editor,slm_widget):
        super().__init__()

        self.main_window = main_window
        self.beam_shaper = beam_shaper
        self.infos_editor = infos_editor
        self.slm_widget = slm_widget

        self.layout = QHBoxLayout()

        self.propagation_editor = PropagationEditor()
        self.layout.addWidget(self.propagation_editor)

        self.result_display_widget = QTabWidget()

        self.modulated_input_field_display = ModulatedInputFieldDisplay(self.beam_shaper)
        self.fourier_plane_field_display = PropagatedFFTModulatedBeamDisplay(self.beam_shaper)
        self.image_plane_field_display = PropagatedImagePlaneDisplay(self.beam_shaper)


        self.result_display_widget.addTab(self.modulated_input_field_display, "Modulated Input Field")
        self.result_display_widget.addTab(self.fourier_plane_field_display, "Fourier Plane")
        self.result_display_widget.addTab(self.image_plane_field_display, "Image Plane")

        self.propagate_button = QPushButton('Propagate')  # Create a button
        # self.propagate_button.setStyleSheet('QPushButton {background-color: gray; color: white;}')        # Connect the button to the run_dimensioning method
        self.propagate_button.clicked.connect(self.run_propagate)

        
        self.save_button = QPushButton('Save Propagated Fields')  # Create a button
        self.save_button.setDisabled(True)
        self.save_button.clicked.connect(self.on_propagated_beams_save)

        self.downsampling_horizontal_layout = QHBoxLayout()
        # Create checkbox for downsampling
        self.downsampling_checkbox = QCheckBox("Downsample for Map Display")
        self.downsampling_checkbox.setChecked(True)

        # Create a QLineEdit for downsampling factor
        self.downsampling_factor_edit = QLineEdit()
        self.downsampling_factor_edit.setText("4")
        self.downsampling_factor_edit.setDisabled(True)
        # Enable/Disable QLineEdit depending on the state of the checkbox
        self.downsampling_checkbox.stateChanged.connect(self.enable_disable_factor_edit)

        self.downsampling_horizontal_layout.addWidget(self.downsampling_checkbox)
        self.downsampling_horizontal_layout.addWidget(self.downsampling_factor_edit)

        # Create a group box for the run button
        self.run_button_group_box = QGroupBox()
        run_button_group_layout = QVBoxLayout()

        run_button_group_layout.addWidget(self.propagate_button)
        run_button_group_layout.addWidget(self.save_button)
        run_button_group_layout.addLayout(self.downsampling_horizontal_layout)
        run_button_group_layout.addWidget(self.result_display_widget)

        self.run_button_group_box.setLayout(run_button_group_layout)
        self.layout.addWidget(self.run_button_group_box)


        self.layout.setStretchFactor(self.run_button_group_box, 1)
        self.layout.setStretchFactor(self.result_display_widget, 3)
        self.setLayout(self.layout)


    def on_propagated_beams_save(self):
        # self.result_directory = initialize_directory(self.infos_editor.config)
        self.simulation_name = self.infos_editor.config['simulation name']
        self.results_directory = self.infos_editor.config['results directory']
        results_directory = os.path.join(self.results_directory, self.simulation_name)


        save_generated_fields(self.beam_shaper, self.modulated_input_field, self.fourier_plane_field, self.fourier_filtered_field, self.output_field,
                              results_directory)

        self.save_button.setDisabled(True)

    def enable_disable_factor_edit(self, state):
        if state == Qt.Checked:
            self.downsampling_factor_edit.setDisabled(False)
        else:
            self.downsampling_factor_edit.setDisabled(True)

    def run_propagate(self):

        try:
            self.beam_shaper.input_beam
        except :
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("No Input Field Detected")
            msg.setInformativeText("Please create an input field before propagating.")
            msg.setWindowTitle("Error")
            msg.exec_()

        try:
            self.beam_shaper.mask
        except :
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("No SLM Mask Detected")
            msg.setInformativeText("Please create a SLM mask before propagating.")
            msg.setWindowTitle("Error")
            msg.exec_()

        if self.downsampling_checkbox.isChecked():
            self.downsample_factor = int(self.downsampling_factor_edit.text())

        self.worker = Worker(self.beam_shaper, self.slm_widget)
        self.worker.finished_modulate_input_beam.connect(self.display_modulated_input_field)
        self.worker.finished_propagate_FFT_modulated_beam.connect(self.display_fourier_plane_field)
        self.worker.finished_propagate_filter_beam.connect(self.display_fourier_filtered_field)
        self.worker.finished_propagate_to_image_plane.connect(self.display_output_field)
        self.worker.start()



    @pyqtSlot(Field)
    def display_modulated_input_field(self, modulated_input_field):
        self.save_button.setDisabled(False)
        self.modulated_input_field = modulated_input_field
        self.modulated_input_field_display.display_modulated_input_field(self.modulated_input_field,self.downsampling_checkbox.isChecked(), self.downsample_factor)

    @pyqtSlot(Field)
    def display_fourier_plane_field(self, fourier_plane_field):
        self.fourier_plane_field = fourier_plane_field
        self.fourier_plane_field_display.display_fourier_plane_field(self.fourier_plane_field,self.downsampling_checkbox.isChecked(), self.downsample_factor)

    @pyqtSlot(Field)
    def display_fourier_filtered_field(self, fourier_filtered_field):
        self.fourier_filtered_field = fourier_filtered_field
        self.fourier_plane_field_display.display_fourier_filtered_field(self.fourier_filtered_field,self.downsampling_checkbox.isChecked(), self.downsample_factor)

    @pyqtSlot(Field)
    def display_output_field(self, output_field):
        self.output_field = output_field
        self.image_plane_field_display.display_output_field(self.output_field,self.downsampling_checkbox.isChecked(), self.downsample_factor)