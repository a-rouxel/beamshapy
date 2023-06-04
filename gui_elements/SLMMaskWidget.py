from PyQt5.QtWidgets import (QTabWidget, QGroupBox, QPushButton, QFileDialog, QLineEdit, QComboBox, QFormLayout, QLabel, QScrollArea, QVBoxLayout, QCheckBox, QSpinBox, QDoubleSpinBox, QWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot

from PyQt5.QtWidgets import (QWidget, QFormLayout, QComboBox, QDoubleSpinBox,
                             QPushButton, QLineEdit, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

class MaskParamsWidget(QWidget):
    def __init__(self, mask_number):
        super().__init__()

        self.group_box = QGroupBox(f"Mask {mask_number}")
        self.inner_layout = QFormLayout(self.group_box)  # Changed name to avoid confusion

        self.mask_type_selector = QComboBox()
        self.mask_type_selector.addItem("None")
        self.mask_type_selector.addItem("Circular Mask")
        self.mask_type_selector.addItem("Custom H5 Mask")
        self.mask_type_selector.currentIndexChanged.connect(self.update_mask_params)

        self.inner_layout.addRow("Mask Type", self.mask_type_selector)

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

    def update_mask_params(self):
        # Clear the previous parameters (if any) by removing the layout's rows, but keep the first 2 rows
        for i in range(self.inner_layout.rowCount() - 1, 0, -1):
            # Get the widgets in the row
            label = self.inner_layout.labelForField(self.inner_layout.itemAt(i, QFormLayout.FieldRole).widget())
            field = self.inner_layout.itemAt(i, QFormLayout.FieldRole).widget()

            # Remove row at index i from the layout
            self.inner_layout.removeRow(i)


        # Circular Mask parameters: radius, intensity
        if self.mask_type_selector.currentText() == "Circular Mask":
            self.radius = QDoubleSpinBox()
            self.radius.setMinimum(0)
            self.radius.setMaximum(100)
            self.radius.setValue(50)

            self.intensity = QDoubleSpinBox()
            self.intensity.setMinimum(0)
            self.intensity.setMaximum(100)
            self.intensity.setValue(50)

            self.inner_layout.addRow("Radius", self.radius)
            self.inner_layout.addRow("Intensity", self.intensity)

        # Custom H5 Mask parameters: file path
        elif self.mask_type_selector.currentText() == "Custom H5 Mask":
            self.file_path = QLineEdit()

            self.browse_button = QPushButton("Browse")
            self.browse_button.clicked.connect(self.browse_file)

            self.inner_layout.addRow("File Path", self.file_path)
            self.inner_layout.addRow("", self.browse_button)

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select h5 file", "", "H5 Files (*.h5)")
        if file_path:
            self.file_path.setText(file_path)




class SLMMaskWidget(QWidget):
    def __init__(self,beam_shaper,simulation_editor,slm_mask_config_path="config/slm_mask.yml"):

        super().__init__()
        self.beam_shaper = beam_shaper
        self.simulation_editor = simulation_editor
        self.slm_mask_config_path = slm_mask_config_path

        # Create the result display widget (tab widget in this case)
        self.result_display_widget = QTabWidget()

        self.layout = QVBoxLayout(self)


        self.new_mask_button = QPushButton("New Mask")
        self.new_mask_button.clicked.connect(self.new_mask)
        self.layout.addWidget(self.new_mask_button)


        self.delete_mask_button = QPushButton("Delete Last Mask")
        self.delete_mask_button.clicked.connect(self.delete_mask)
        self.layout.addWidget(self.delete_mask_button)

        # List to store references to the mask widgets
        self.masks = []

        self.mask_area = QScrollArea()
        self.mask_area.setWidgetResizable(True)
        self.mask_layout = QVBoxLayout()
        self.mask_area_widget = QWidget()
        self.mask_area_widget.setLayout(self.mask_layout)
        self.mask_area.setWidget(self.mask_area_widget)
        self.layout.addWidget(self.mask_area)

    def new_mask(self):
        mask_number = len(self.masks) + 1
        new_mask_params_widget = MaskParamsWidget(mask_number)
        self.masks.append(new_mask_params_widget)
        self.mask_layout.addWidget(new_mask_params_widget)

    def delete_mask(self):
        if self.masks:
            # Remove the last mask widget from the mask_layout and the list
            mask_to_remove = self.masks.pop()
            self.mask_layout.removeWidget(mask_to_remove)
            mask_to_remove.deleteLater()

