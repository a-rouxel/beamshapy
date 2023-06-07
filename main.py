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
        self.setWindowTitle('Beam Shaping FFT')



        self.infos_editor = InfosEditorWidget(initial_infos_config_path="config/infos.yml")
        self.input_beam_editor = InputBeamEditorWidget(initial_input_beam_config_path="config/input_beam.yml")
        self.simulation_editor = SimulationConfigEditorWidget(simulation_config_path="config/simulation.yml")

        self.BeamShaper = BeamShaper(self.simulation_editor.get_config(),
                                    self.input_beam_editor.get_config(),
                                     initial_config_file="config/optical_system.yml")

        self.input_beam_widget = InputBeamWidget(self.BeamShaper,
                                                 self.infos_editor,
                                                 self.simulation_editor,
                                                 self.input_beam_editor)
        self.input_beam_dock = QDockWidget("Input Beam")
        self.input_beam_dock.setWidget(self.input_beam_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.input_beam_dock)

        self.SLM_mask_widget = SLMMaskWidget(self.BeamShaper,
                                             self.infos_editor,
                                             self.simulation_editor,
                                             slm_mask_config_path="config/slm_mask.yml")
        self.SLM_mask_dock = QDockWidget("SLM Masks")
        self.SLM_mask_dock.setWidget(self.SLM_mask_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.SLM_mask_dock)
        #
        self.fourier_plane_detection_widget = FourierPlaneDetectionWidget(self,self.BeamShaper,
                                                                          self.infos_editor,
                                                                         self.SLM_mask_widget,
                                                                         )
        self.fourier_plane_detection_dock = QDockWidget("Detection")
        self.fourier_plane_detection_dock.setWidget(self.fourier_plane_detection_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.fourier_plane_detection_dock)

        self.tabifyDockWidget(self.input_beam_dock, self.SLM_mask_dock)
        self.tabifyDockWidget(self.SLM_mask_dock, self.fourier_plane_detection_dock)

        self.input_beam_dock.raise_()
        #
        # # Load and apply the stylesheet
        # with open("./Ubuntu.qss", "r") as file:
        #     qss = file.read()
        #     self.setStyleSheet(qss)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('logo_beam_shaper.png'))

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec_())