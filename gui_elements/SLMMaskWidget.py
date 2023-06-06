from PyQt5.QtWidgets import (QTabWidget, QGroupBox, QHBoxLayout, QFileDialog, QLineEdit, QComboBox, QFormLayout, QLabel, QScrollArea, QVBoxLayout, QCheckBox, QSpinBox, QDoubleSpinBox, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot

from PyQt5.QtWidgets import (QWidget, QFormLayout, QComboBox, QDoubleSpinBox,
                             QPushButton, QLineEdit, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog
import numpy as np
from LightPipes import mm,um
import os
from datetime import datetime
import h5py
from utils import save_result_mask, normalize, discretize_array
class MaskParamsWidget(QWidget):

    maskGenerated = pyqtSignal(np.ndarray,np.ndarray)
    def __init__(self,beam_shaper,mask_number):
        super().__init__()

        self.beam_shaper = beam_shaper
        self.mask_number = mask_number
        self.group_box = QGroupBox(f"Mask {mask_number}")
        self.inner_layout = QFormLayout(self.group_box)

        self.mask_type_selector = QComboBox()
        self.mask_type_selector.addItem("None")
        self.mask_type_selector.addItem("Grating")
        self.mask_type_selector.addItem("Wedge")
        self.mask_type_selector.addItem("Phase Reversal")
        self.mask_type_selector.addItem("Weights Sinc")
        self.mask_type_selector.addItem("Custom H5 Mask")
        self.mask_type_selector.currentIndexChanged.connect(self.update_mask_params)



        self.inner_layout.addRow("Mask Type", self.mask_type_selector)

        self.generate_mask_button = QPushButton("Generate Mask")
        self.generate_mask_button.clicked.connect(self.generate_phase_mask)



        self.inner_layout.addRow(self.generate_mask_button)



        self.normalize_layout = QVBoxLayout()
        self.normalize_checkbox = QCheckBox("Normalize")
        self.normalize_checkbox.stateChanged.connect(self.handle_normalize_checked)
        self.normalize_layout.addWidget(self.normalize_checkbox)

        self.min_value_input = QLineEdit("0")
        self.min_group = QGroupBox("Min Value")
        self.min_group.setLayout(QHBoxLayout())
        self.min_group.layout().addWidget(self.min_value_input)
        self.normalize_layout.addWidget(self.min_group)

        self.max_value_input = QLineEdit("1")
        self.max_group = QGroupBox("Max Value")
        self.max_group.setLayout(QHBoxLayout())
        self.max_group.layout().addWidget(self.max_value_input)
        self.normalize_layout.addWidget(self.max_group)

        # Initially hide the min and max value inputs
        self.min_group.hide()
        self.max_group.hide()

        # Add normalize layout to a QWidget and then add the QWidget to the inner layout
        self.normalize_widget = QWidget()
        self.normalize_widget.setLayout(self.normalize_layout)
        self.inner_layout.addRow(self.normalize_widget)

        self.layout = QVBoxLayout(self)  # This will set QVBoxLayout as the layout of this widget
        self.layout.addWidget(self.group_box)  # Now adding group_box to the QVBoxLayout

        self.group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid gray;
                border-radius: 5px;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)

    def handle_normalize_checked(self, state):
        # Show or hide the min and max value inputs based on the checkbox state
        if state == Qt.Checked:
            self.min_group.show()
            self.max_group.show()
        else:
            self.min_group.hide()
            self.max_group.hide()

    def enable_generate_mask_button(self):
        # Enable the "Generate Mask" button
        self.generate_mask_button.setEnabled(True)

    def generate_phase_mask(self):
        # Get the mask type
        mask_type = self.mask_type_selector.currentText()

        # Generate the mask
        if mask_type == "Grating":
            mask = self.beam_shaper.generate_mask(mask_type=mask_type,
                                                  period=int(self.period.text()),
                                                  orientation=self.orientation.currentText())
        elif mask_type == "Wedge":

            mask = self.beam_shaper.generate_mask(mask_type=mask_type,
                                                  angle=float(self.angle.text()),
                                                  orientation=self.orientation.currentText())
        elif mask_type == "Phase Reversal":
            mask = self.beam_shaper.generate_mask(mask_type=mask_type,
                                                  sigma_x=float(self.sigma_x.text()),
                                                  sigma_y=float(self.sigma_y.text()))
            print(mask)

        elif mask_type == "Weights Sinc":
            mask = self.beam_shaper.generate_mask(mask_type=mask_type,threshold=float(self.threshold.text()))

        elif mask_type == "Custom H5 Mask":
            # Open a file dialog to select the mask
            mask_path, _ = QFileDialog.getOpenFileName(self, "Select H5 Mask File", "", "H5 Files (*.h5)")
            mask = self.beam_shaper.generate_mask(mask_type=mask_type,
                                           mask_path=mask_path)
        else :
            raise ValueError("Invalid mask type")

        if self.normalize_checkbox.isChecked():
            min_value = float(self.min_value_input.text())
            max_value = float(self.max_value_input.text())
            mask = normalize(mask, min_value, max_value)



        self.generated_mask = mask
        self.generate_mask_button.setDisabled(True)
        self.maskGenerated.emit(mask, self.beam_shaper.x_array_in)

    def update_mask_params(self):
        # Clear the previous parameters (if any) by removing the layout's rows, but keep the first 2 rows
        for i in range(self.inner_layout.rowCount() - 1, 2, -1):  # start from last row, stop at 2 (exclusive), step backwards
            # Remove row at index i from the layout
            self.inner_layout.removeRow(i)

        self.mask_type_selector.currentIndexChanged.connect(self.enable_generate_mask_button)

        # Circular Mask parameters: radius, intensity
        if self.mask_type_selector.currentText() == "Grating":
            self.period = QLineEdit()
            self.period.setText(str(5))
            self.orientation = QComboBox()
            self.orientation.addItems(["Horizontal", "Vertical"])
            self.inner_layout.addRow("pixels number per groove [no units]", self.period)
            self.inner_layout.addRow("Orientation", self.orientation)

            # Connect the textChanged signal for these parameters
            self.period.textChanged.connect(self.enable_generate_mask_button)
            self.orientation.currentIndexChanged.connect(self.enable_generate_mask_button)


        if self.mask_type_selector.currentText() == "Wedge":
            self.angle = QLineEdit()
            self.angle.setText(str(0.5))
            self.orientation = QComboBox()
            self.orientation.addItems(["Horizontal", "Vertical"])
            self.inner_layout.addRow("angle [in degree]", self.angle)
            self.inner_layout.addRow("Orientation", self.orientation)

            # Connect the textChanged signal for these parameters
            self.angle.textChanged.connect(self.enable_generate_mask_button)
            self.orientation.currentIndexChanged.connect(self.enable_generate_mask_button)


        if self.mask_type_selector.currentText() == "Phase Reversal":
            self.sigma_x = QLineEdit()
            self.sigma_x.setText(str(1))
            self.sigma_y = QLineEdit()
            self.sigma_y.setText(str(0.5))
            self.inner_layout.addRow("sigma_x [no units]", self.sigma_x)
            self.inner_layout.addRow("sigma_y [no units]", self.sigma_y)

            # Connect the textChanged signal for these parameters
            self.sigma_x.textChanged.connect(self.enable_generate_mask_button)
            self.sigma_y.textChanged.connect(self.enable_generate_mask_button)


        if self.mask_type_selector.currentText() == "Weights Sinc":
            self.threshold = QLineEdit()
            self.threshold.setText(str(0.01))
            self.inner_layout.addRow("threshold [no units]", self.threshold)

            self.threshold.textChanged.connect(self.enable_generate_mask_button)

        # Custom H5 Mask parameters: file path
        elif self.mask_type_selector.currentText() == "Custom H5 Mask":
            self.file_path = QLineEdit()

            self.browse_button = QPushButton("Browse")
            self.browse_button.clicked.connect(self.browse_file)

            self.inner_layout.addRow("File Path", self.file_path)
            self.inner_layout.addRow("", self.browse_button)

            self.file_path.textChanged.connect(self.enable_generate_mask_button)
    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select h5 file", "", "H5 Files (*.h5)")
        if file_path:
            self.file_path.setText(file_path)


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QTabWidget, QVBoxLayout, QWidget

class DisplayWidget(QWidget):
    def __init__(self,beam_shaper):
        super().__init__()

        self.beam_shaper = beam_shaper
        # Create a tab widget to hold the plots
        self.tabWidget = QTabWidget(self)

        # Create figures and figure canvases for the plots
        self.maskFigure = Figure()
        self.maskCanvas = FigureCanvas(self.maskFigure)
        self.maskToolbar = NavigationToolbar(self.maskCanvas, self)

        self.cutXFigure = Figure()
        self.cutXCanvas = FigureCanvas(self.cutXFigure)
        self.cutXToolbar = NavigationToolbar(self.cutXCanvas, self)

        self.cutYFigure = Figure()
        self.cutYCanvas = FigureCanvas(self.cutYFigure)
        self.cutYToolbar = NavigationToolbar(self.cutYCanvas, self)

        # Create Widgets for each tab to hold the toolbar and the figure canvas
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

        # Add the Widgets to the tab widget
        self.tabWidget.addTab(self.maskWidget, "Image Map")
        self.tabWidget.addTab(self.cutXWidget, "Cut X")
        self.tabWidget.addTab(self.cutYWidget, "Cut Y")

        # Create a QVBoxLayout and add the tab widget to it

        layout = QVBoxLayout(self)

        layout.addWidget(self.tabWidget)

    @pyqtSlot(np.ndarray,np.ndarray)
    def displayMask(self, mask,x_array):
        # Plot the mask
        self.x_array_in = x_array/mm
        self.maskFigure.clear()
        ax1 = self.maskFigure.add_subplot(111)
        im = ax1.imshow(mask,extent=[self.x_array_in[0],self.x_array_in[-1], self.x_array_in[0],self.x_array_in[-1]])
        ax1.set_title('Mask')
        ax1.set_xlabel('Position along X [in mm]')
        ax1.set_ylabel('Position along Y [in mm]')
        self.maskFigure.colorbar(im, ax=ax1,label='Phase Value [in rad]')
        self.maskCanvas.draw()

        # Plot the cut along X
        self.cutXFigure.clear()
        ax2 = self.cutXFigure.add_subplot(111)
        ax2.plot(self.x_array_in,mask[mask.shape[0] // 2, :])
        ax2.set_title('Cut along X')
        ax2.set_xlabel('Position along X [in mm]')
        ax2.set_ylabel('Phase Value [in rad]')
        self.cutXCanvas.draw()

        # Plot the cut along Y
        self.cutYFigure.clear()
        ax3 = self.cutYFigure.add_subplot(111)
        ax3.plot(self.x_array_in,mask[:, mask.shape[1] // 2])
        ax3.set_title('Cut along Y')
        ax3.set_xlabel('Position along Y [in mm]')
        ax3.set_ylabel('Phase Value [in rad]')
        self.cutYCanvas.draw()


class SLMMaskWidget(QWidget):
    def __init__(self, beam_shaper, infos_editor, simulation_editor, slm_mask_config_path="config/slm_mask.yml"):

        super().__init__()
        self.beam_shaper = beam_shaper
        self.infos_editor = infos_editor
        self.simulation_editor = simulation_editor
        self.slm_mask_config_path = slm_mask_config_path
        self.result_tab_index = None

        # Create the result display widget (tab widget in this case)
        self.result_display_widget = QTabWidget()

        # Create a QVBoxLayout for the left side (mask parameters and buttons)
        self.left_layout = QVBoxLayout()
        self.left_layout_masks = QVBoxLayout()

        self.new_mask_button = QPushButton("Add Mask")
        self.new_mask_button.clicked.connect(self.new_mask)
        self.left_layout_masks.addWidget(self.new_mask_button)

        self.delete_mask_button = QPushButton("Delete Last Mask")
        self.delete_mask_button.clicked.connect(self.delete_mask)
        self.left_layout_masks.addWidget(self.delete_mask_button)

        # Create QLineEdit for user input
        self.operation_input = QLineEdit(self)
        self.operation_input.setPlaceholderText("ex: warp ( M1 + M2 ) * M3")

        self.discretize_checkbox = QCheckBox("Discretize")

        # Add a button to evaluate the user input
        self.evaluate_button = QPushButton("Generate final mask", self)
        self.evaluate_button.clicked.connect(self.evaluate_operation)

        self.save_mask_button = QPushButton("Save final mask")
        self.save_mask_button.setDisabled(True)
        self.save_mask_button.clicked.connect(self.on_resulting_mask_save)

        # List to store references to the mask widgets
        self.masks_params_widgets = []

        # List to store references to the masks data
        self.masks_dict = dict()

        self.mask_area = QScrollArea()
        self.mask_area.setWidgetResizable(True)
        self.mask_layout = QVBoxLayout()
        self.mask_area_widget = QWidget()
        self.mask_area_widget.setLayout(self.mask_layout)
        self.mask_area.setWidget(self.mask_area_widget)
        self.mask_area.setStyleSheet("QScrollArea { border: none; }")
        self.left_layout_masks.addWidget(self.mask_area)

        # Create a QVBoxLayout for the operation input and button
        self.group_box = QGroupBox(f"Operations on masks")
        self.operation_layout = QFormLayout(self.group_box)

        self.operation_layout.addRow(self.operation_input)
        self.operation_layout.addRow(self.discretize_checkbox)
        self.operation_layout.addRow(self.evaluate_button)

        self.left_layout_masks.addWidget(self.group_box)

        # Create a QVBoxLayout for the save button and result display
        self.result_layout = QVBoxLayout()
        self.result_layout.addWidget(self.save_mask_button)
        self.result_layout.addWidget(self.result_display_widget)

        # Create a QHBoxLayout for the whole widget
        self.layout = QHBoxLayout(self)
        self.layout.addLayout(self.left_layout_masks)  # Add the left layout (mask parameters and buttons)
        self.layout.addLayout(self.result_layout)  # Add the save button and result display layout

        self.layout.setStretchFactor(self.left_layout_masks, 1)
        self.layout.setStretchFactor(self.result_layout, 2)

        self.group_box.setStyleSheet("""
            QGroupBox {
                border: 1px solid;
                border-radius: 7px;
                margin-top: 0.5em;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
        """)



    def on_resulting_mask_save(self):
        # self.result_directory = initialize_directory(self.infos_editor.config)
        self.simulation_name = self.infos_editor.config['simulation name']
        self.results_directory = self.infos_editor.config['results directory']
        results_directory = os.path.join(self.results_directory, self.simulation_name)


        # Save the resulting mask
        save_result_mask(self.result_mask, results_directory)


        self.save_mask_button.setDisabled(True)

    @pyqtSlot()
    def evaluate_operation(self):

        # Get the operation from the QLineEdit
        operation = self.operation_input.text()

        # Define the allowed operations and masks
        allowed_ops = {"+", "-", "*", "/", "(", ")", "warp"}  # Add your custom operation name here
        allowed_masks = set(self.masks_dict.keys())  # Dynamically get the list of current masks

        # Custom operations dictionary
        operations = {
            "warp": lambda x: np.angle(np.exp(1j*x))  # define your warp function here
        }

        # Split the operation into parts
        parts = operation.split()

        # Check each part of the operation
        for part in parts:
            if part not in allowed_ops and part not in allowed_masks:
                try:
                    # If the part can be converted to a float, it's a number and valid
                    float(part)
                except ValueError:
                    # If it can't be converted to a float, it's invalid
                    print(f"Invalid operation: {part}")
                    return

        # Replace mask names with their numpy array representation
        for mask_name in allowed_masks:
            operation = operation.replace(mask_name, f"self.masks_dict['{mask_name}']")

        # Replace custom operation names with their callable function string representation
        for op_name in operations:
            operation = operation.replace(op_name, f"operations['{op_name}']")

        try :
            self.result_mask
            if len(self.result_display_widget) > len(self.masks_params_widgets):
                self.result_display_widget.removeTab(self.result_display_widget.count()-1)
        except:
            print('no')
            pass

        # Initialize the resulting mask as an empty mask
        self.result_mask = np.zeros_like(next(iter(self.masks_dict.values())))

        # Evaluate the operation
        if operation != "":
            try:
                self.result_mask = eval(operation)
            except Exception as e:
                print(f"Error evaluating operation: {e}")
                return

        if operation == "" and len(self.masks_dict) >0:
            self.result_mask = self.masks_dict["M1"]

        if self.discretize_checkbox.isChecked():
            self.result_mask = discretize_array(self.result_mask)

        # Create a new widget for the display
        result_display = DisplayWidget(self.beam_shaper)  # replace with your actual Display Widget here
        result_display.displayMask(self.result_mask,self.beam_shaper.x_array_in)  # Display the result mask
        # Add the result display as a new tab to the result_display_widget and store its index
        self.result_tab_index = self.result_display_widget.addTab(result_display, "Resulting Mask")

        mask_number = len(self.masks_params_widgets) + 1
        print(f"M{mask_number}")
        self.masks_dict[
            f"resulting_M"] = self.result_mask

        self.save_mask_button.setDisabled(False)
    @pyqtSlot(np.ndarray, int)
    def update_masks_dict(self, mask, mask_number):
        self.masks_dict[f"M{mask_number}"] = mask


    def new_mask(self):
        mask_number = len(self.masks_params_widgets) + 1

        new_mask_params_widget = MaskParamsWidget(self.beam_shaper,mask_number)

        self.masks_params_widgets.append(new_mask_params_widget)
        self.mask_layout.addWidget(new_mask_params_widget)

        # Create a new widget for the display
        new_mask_display = DisplayWidget(self.beam_shaper)  # replace with your actual Display Widget here

        # Connect the maskGenerated signal to the displayMask slot
        new_mask_params_widget.maskGenerated.connect(new_mask_display.displayMask)
        new_mask_params_widget.maskGenerated.connect(lambda mask: self.update_masks_dict(mask, new_mask_params_widget.mask_number))

        print(len(self.result_display_widget) -1,len(self.masks_params_widgets))
        # Add the new display as a new tab to the result_display_widget
        if len(self.masks_params_widgets) == len(self.result_display_widget) +1:
            self.result_display_widget.addTab(new_mask_display, f"Mask {mask_number} Display")
        elif len(self.masks_params_widgets) < len(self.result_display_widget) +1:
            self.result_display_widget.insertTab(self.result_display_widget.count()-1,new_mask_display, f"Mask {mask_number} Display")

        # Add the new mask to the dictionary of masks
        self.masks_dict[
            f"M{mask_number}"] = ""

    def delete_mask(self):
        if self.masks_params_widgets:


            # Remove the last mask from the dictionary of masks
            mask_number = len(self.masks_params_widgets)

            try :
                self.masks_dict["resulting_M"]
                del self.masks_dict[f"M{mask_number}"]
                mask_to_remove = self.masks_params_widgets.pop()
                self.mask_layout.removeWidget(mask_to_remove)
                mask_to_remove.deleteLater()
                # Remove the last tab from result_display_widget
                self.result_display_widget.removeTab(self.result_display_widget.count() - 2)

                if len(self.masks_params_widgets)==0:
                    self.result_display_widget.removeTab(self.result_display_widget.count() - 1)
                    del self.masks_dict["resulting_M"]

            except KeyError:
                del self.masks_dict[f"M{mask_number}"]
                # Remove the last mask widget from the mask_layout and the list
                mask_to_remove = self.masks_params_widgets.pop()
                self.mask_layout.removeWidget(mask_to_remove)
                mask_to_remove.deleteLater()
                # Remove the last tab from result_display_widget
                self.result_display_widget.removeTab(self.result_display_widget.count() - 1)




