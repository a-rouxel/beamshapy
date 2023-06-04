import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget
from PyQt5.QtGui import QIcon
from gui_elements import InputBeamWidget
from gui_elements import InputBeamEditorWidget
from gui_elements import SimulationConfigEditorWidget
from gui_elements import SLMMaskWidget
from gui_elements import InfosEditorWidget
from gui_elements import DetectionWidget
from BeamShaper import BeamShaper

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.setWindowIcon(QIcon('Figure_1.ico'))
        self.setWindowTitle('Beam Shaping Simulator')

        self.BeamShaper = BeamShaper(initial_config_file="config/optical_system.yml")

        self.infos_editor = InfosEditorWidget(initial_infos_config_path="config/infos.yml")
        self.input_beam_editor = InputBeamEditorWidget(initial_input_beam_config_path="config/input_beam.yml")
        self.simulation_editor = SimulationConfigEditorWidget(simulation_config_path="config/simulation.yml")


        self.input_beam_widget = InputBeamWidget(self.BeamShaper,
                                                 self.infos_editor,
                                                 self.simulation_editor,
                                                 self.input_beam_editor)
        self.input_beam_dock = QDockWidget("Input Beam")
        self.input_beam_dock.setWidget(self.input_beam_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.input_beam_dock)

        self.SLM_mask_widget = SLMMaskWidget(self.BeamShaper,
                                             self.simulation_editor,
                                             slm_mask_config_path="config/slm_mask.yml")
        self.SLM_mask_dock = QDockWidget("SLM Masks")
        self.SLM_mask_dock.setWidget(self.SLM_mask_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.SLM_mask_dock)
        #
        # self.detection_widget = DetectionWidget(self.system_editor,detection_config_path="config/detection.yml")
        # self.detection_dock = QDockWidget("Detection")
        # self.detection_dock.setWidget(self.detection_widget)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.detection_dock)

        self.tabifyDockWidget(self.input_beam_dock, self.SLM_mask_dock)
        # self.tabifyDockWidget(self.SLM_mask_dock, self.detection_dock)
        #
        # self.input_beam_dock.raise_()
        # # Connect the signal to the slot
    #     self.tabifiedDockWidgetActivated.connect(self.check_dock_visibility)
    # #
    # def check_dock_visibility(self, dock_widget):
    #     # If the currently selected dock widget is the Scene dock, hide the system_config_dock
    #     if dock_widget is self.input_beam_dock :
    #         self.system_config_dock.setVisible(False)
    #     else:
    #         self.system_config_dock.setVisible(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())