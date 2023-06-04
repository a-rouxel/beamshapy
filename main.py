import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QDockWidget
from PyQt5.QtGui import QIcon
from gui_elements import InputBeamWidget
from gui_elements import InputBeamEditorWidget
from gui_elements import SimulationConfigEditorWidget
from gui_elements import SLMMaskWidget
from gui_elements import InfosEditorWidget
from gui_elements import FourierPlaneDetectionWidget
from BeamShaper import BeamShaper

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('logo_beam_shaper.png'))  # Uncomment this line
        self.setWindowTitle('Beam Shaping Simulator')



        self.infos_editor = InfosEditorWidget(initial_infos_config_path="config/infos.yml")
        self.input_beam_editor = InputBeamEditorWidget(initial_input_beam_config_path="config/input_beam.yml")
        self.simulation_editor = SimulationConfigEditorWidget(simulation_config_path="config/simulation.yml")

        self.BeamShaper = BeamShaper(self.simulation_editor,
                                    self.input_beam_editor,
                                     initial_config_file="config/optical_system.yml")

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
        self.fourier_plane_detection_widget = FourierPlaneDetectionWidget(self.BeamShaper,
                                                                         self.SLM_mask_widget,
                                                                         )
        self.fourier_plane_detection_dock = QDockWidget("Detection")
        self.fourier_plane_detection_dock.setWidget(self.fourier_plane_detection_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.fourier_plane_detection_dock)

        self.tabifyDockWidget(self.input_beam_dock, self.SLM_mask_dock)
        self.tabifyDockWidget(self.SLM_mask_dock, self.fourier_plane_detection_dock)
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
    app.setWindowIcon(QIcon('logo_beam_shaper.png')) # Add this line
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())