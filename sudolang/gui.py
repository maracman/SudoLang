import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QVBoxLayout, QFormLayout, QMainWindow, QWidget,
    QApplication, QPushButton, QHBoxLayout,
    QAction, QTabWidget, QLineEdit, QSlider, QLabel, QCheckBox, QGridLayout,
    QListWidget, QListWidgetItem, QFileDialog,
)
from PyQt5.QtGui import QIntValidator
from PyQt5 import sip
from PyQt5.QtCore import pyqtSlot, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from sudolang.config import settings_default_path


# ---------------------------------------------------------------------------
# Enter_Name — simple participant ID dialog (survey mode)
# ---------------------------------------------------------------------------

class Enter_Name(QMainWindow):
    def __init__(self, settings, parent=None):
        super(Enter_Name, self).__init__(parent)
        self.settings = settings
        self.exit_application = True

        self.setWindowTitle("Enter User ID")
        self.resize(250, 130)

        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        self.IDtextbox = QLineEdit(self)
        self.IDtextbox.setText(settings.id_name)
        self.IDtextbox.setMinimumHeight(30)
        self.IDtextbox.setMinimumWidth(200)
        button = QPushButton('Continue', self)
        button.clicked.connect(lambda: self.on_click())

        self.layout.addWidget(self.IDtextbox)
        self.layout.addWidget(button)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    @pyqtSlot()
    def on_click(self):
        self.exit_application = False
        self.settings.id_name = self.IDtextbox.text()
        self.close()


# ---------------------------------------------------------------------------
# App — researcher settings window with 4 tabs
# ---------------------------------------------------------------------------

class App(QMainWindow):
    EXIT_CODE_REBOOT = -7654321

    def __init__(self, settings, parent=None):
        super(App, self).__init__(parent)
        self.settings = settings
        self.exit_application = True

        self.setWindowTitle("Game Settings")
        self.resize(470, 500)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        tabs = QTabWidget()
        tabs.addTab(self.tab1_UI(), "Object Labels")
        tabs.addTab(self.tab2_UI(), "Gameplay")
        tabs.addTab(self.tab4_UI(), "Display/Audio")
        tabs.addTab(self.tab3_UI(), "Outputs")

        self.layout.addWidget(tabs)
        hlayout = QHBoxLayout()

        button = QPushButton('Continue', self)
        button.clicked.connect(lambda: self.on_click(save_file_path=settings_default_path, isExit=True))
        self.setting_export = QCheckBox("   Export these settings\n    for survey application", self)
        self.setting_export.toggle()
        self.setting_export.setChecked(False)

        open_action = QAction("open settings", self)
        open_action.triggered.connect(self.open_settings)
        save_action = QAction("save settings", self)
        save_action.triggered.connect(self.save_settings)

        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)

        hlayout.addWidget(self.setting_export)
        hlayout.addWidget(button)
        self.layout.addLayout(hlayout)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def exit_reboot(self):
        QApplication.exit(App.EXIT_CODE_REBOOT)

    def open_settings(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '', 'All Files (*.*)')
        if path != ('', ''):
            print("File path : " + path[0])
            try:
                print("executing load")
                self.settings.load_and_save_to_default(path[0])
                print("load completed")
            except IOError:
                print("cant load file")
            self.exit_reboot()

    def save_settings(self):
        file_save = QFileDialog()
        file_save.setDefaultSuffix('pkl')
        name, _ = file_save.getSaveFileName(self, 'Save File', "", "PKL (*.pkl)")
        if name != '' and name != '.pkl':
            self.on_click(isExit=False, save_file_path=name)

    # ------------------------------------------------------------------
    # Tab 1: Object Labels
    # ------------------------------------------------------------------

    def tab1_UI(self):
        s = self.settings
        tab1 = QWidget()
        outer_layout = QVBoxLayout()
        hbox_top = QHBoxLayout()
        top_layout = QFormLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox3 = QVBoxLayout()
        hbox2 = QHBoxLayout()
        vbox4 = QVBoxLayout()

        self.canvas = Canvas(self, *s.word_slider_values, width=0, height=0)
        self.canvas.setStyleSheet("""QWidget {background-color:   grey}""")
        self.canvas.setMinimumHeight(30)
        self.canvas.setMaximumHeight(40)

        self.canvas1 = Canvas(self, *s.object_slider_values, width=0, height=0)
        self.canvas1.setStyleSheet("""QWidget {background-color:   grey}""")
        self.canvas1.setMinimumHeight(30)
        self.canvas1.setMaximumHeight(40)

        self.IDtextbox = QLineEdit(self)
        self.IDtextbox.setText(s.id_name)

        self.rareness_ordering = QCheckBox("  objects rareness \n according to label complexity", self)
        self.rareness_ordering.toggle()
        self.rareness_ordering.setChecked(s.rareness)
        self.rareness_ordering.setToolTip('Checking this box makes object-label pairs appear as the target stimulus \n'
                                          'according to probabilities based on the label category.')

        self.prior_word_set_box = QCheckBox("  load objects and labels \n  from (user ID's) previous session", self)
        self.prior_word_set_box.toggle()
        self.prior_word_set_box.setChecked(s.load_previous)
        self.prior_word_set_box.setToolTip("objects and their labels will be taken \n"
                                           "from the player's previous game. \n"
                                           'Settings for word weights will be ignored ')

        self.fixed_labels_box = QCheckBox(" Fixed labels ", self)
        self.fixed_labels_box.toggle()
        self.fixed_labels_box.setChecked(s.isFixed)
        self.fixed_labels_box.setToolTip("Create object labels according to the object image name")

        word_slider_tip = ("set the relative proportion of words from \n"
                           "this category to be used in user's object-label set")

        # Word sliders
        word_labels = ['Two letter weight', 'One syllable weight', 'Two syllable weight',
                       'Two syllable (long) weight', 'Three syllable weight', 'Four syllable weight']
        self.wrd_sliders = []
        self.wrd_v_labels = []
        wrd_labels = []

        for idx, label_text in enumerate(word_labels):
            slider = QSlider(Qt.Horizontal, self)
            slider.setValue(s.word_slider_values[idx])
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setToolTip(word_slider_tip)

            v_label = QLineEdit('0', self)
            v_label.setMinimumWidth(30)
            v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            v_label.setText(str(s.word_slider_values[idx]))
            v_label.setValidator(QIntValidator(0, 100))

            v_label.returnPressed.connect(
                lambda sl=slider, vl=v_label: sl.setValue(int(vl.text())))
            slider.valueChanged.connect(
                lambda val, vl=v_label: vl.setText(str(val)))
            slider.valueChanged.connect(lambda: self.value_change(s.word_slider_values))

            lbl = QLabel(label_text, self)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.adjustSize()

            self.wrd_sliders.append(slider)
            self.wrd_v_labels.append(v_label)
            wrd_labels.append(lbl)

        # Object sliders
        object_slider_tip = ("set the relative proportion of objects from \n"
                             "this category to be used in user's object-label set")
        obj_label_texts = ['Object Category One', 'Object Category Two', 'Object Category Three']
        self.obj_sliders = []
        self.obj_v_labels = []
        obj_labels = []

        for idx, label_text in enumerate(obj_label_texts):
            slider = QSlider(Qt.Horizontal, self)
            slider.setValue(s.object_slider_values[idx])
            slider.setMinimum(0)
            slider.setMaximum(100)
            slider.setToolTip(object_slider_tip)

            v_label = QLineEdit('0', self)
            v_label.setMinimumWidth(30)
            v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            v_label.setText(str(s.object_slider_values[idx]))
            v_label.setValidator(QIntValidator(0, 100))

            v_label.returnPressed.connect(
                lambda sl=slider, vl=v_label: sl.setValue(int(vl.text())))
            slider.valueChanged.connect(
                lambda val, vl=v_label: vl.setText(str(val)))
            slider.valueChanged.connect(lambda: self.value_change1(s.object_slider_values))

            lbl = QLabel(label_text, self)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.adjustSize()
            lbl.setToolTip("")

            self.obj_sliders.append(slider)
            self.obj_v_labels.append(v_label)
            obj_labels.append(lbl)

        self.bg_match_slider = QSlider(Qt.Horizontal, self)
        self.bg_match_slider.setValue(s.bg_matchingness)
        self.bg_match_slider.setMinimum(0)
        self.bg_match_slider.setMaximum(100)
        self.bg_match_slider.setEnabled(False)

        bg_match_v_label = QLabel('0', self)
        bg_match_v_label.setMinimumWidth(80)
        bg_match_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        bg_match_v_label.setText(str(s.bg_matchingness))
        bg_match_v_label.setEnabled(False)

        bg_match_label = QLabel('object/background \n matchingness', self)
        bg_match_label.setAlignment(Qt.AlignCenter)
        bg_match_label.adjustSize()
        bg_match_label.setToolTip("")

        self.start_vocab_slider = QSlider(Qt.Horizontal, self)
        self.start_vocab_slider.setValue(s.starting_vocabulary)
        self.start_vocab_slider.setMinimum(2)
        self.start_vocab_slider.setMaximum(10)
        self.start_vocab_slider.setToolTip("sets the number of possible object-label pairs \n"
                                           "that the user begins with")

        start_vocab_v_label = QLabel('0', self)
        start_vocab_v_label.setMinimumWidth(80)
        start_vocab_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        start_vocab_v_label.setText(str(s.starting_vocabulary))

        start_vocab_label = QLabel('starting vocabulary size', self)
        start_vocab_label.setAlignment(Qt.AlignCenter)
        start_vocab_label.adjustSize()
        start_vocab_label.setToolTip("")

        # Add widgets to layouts
        top_layout.addRow("User ID:", self.IDtextbox)
        hbox_top.addWidget(self.canvas)

        vbox1.addSpacing(15)
        for i in range(3):
            vbox1.addWidget(wrd_labels[i])
            vbox1.addWidget(self.wrd_sliders[i])
            vbox1.addWidget(self.wrd_v_labels[i])
            vbox1.addSpacing(10)

        vbox2.addSpacing(15)
        for i in range(3, 6):
            vbox2.addWidget(wrd_labels[i])
            vbox2.addWidget(self.wrd_sliders[i])
            vbox2.addWidget(self.wrd_v_labels[i])
            vbox2.addSpacing(10)

        vbox3.addWidget(self.canvas1)
        for i in range(3):
            vbox3.addWidget(obj_labels[i])
            vbox3.addWidget(self.obj_sliders[i])
            vbox3.addWidget(self.obj_v_labels[i])
            vbox3.addSpacing(15)

        vbox4.addSpacing(20)
        vbox4.addWidget(bg_match_label)
        vbox4.addWidget(self.bg_match_slider)
        vbox4.addWidget(bg_match_v_label)
        vbox4.addSpacing(10)

        vbox4.addWidget(start_vocab_label)
        vbox4.addWidget(self.start_vocab_slider)
        vbox4.addWidget(start_vocab_v_label)
        vbox4.addSpacing(10)

        vbox4.addWidget(self.fixed_labels_box)
        vbox4.addSpacing(15)
        vbox4.addWidget(self.rareness_ordering)
        vbox4.addSpacing(15)
        vbox4.addWidget(self.prior_word_set_box)

        self.bg_match_slider.valueChanged.connect(
            lambda: bg_match_v_label.setText(str(self.bg_match_slider.value())))
        self.start_vocab_slider.valueChanged.connect(
            lambda: start_vocab_v_label.setText(str(self.start_vocab_slider.value())))

        outer_layout.addLayout(top_layout)
        outer_layout.addLayout(hbox_top)
        outer_layout.addLayout(hbox1)
        hbox1.addLayout(vbox1)
        hbox1.addLayout(vbox2)
        outer_layout.addLayout(hbox2)
        hbox2.addLayout(vbox3)
        hbox2.addSpacing(30)
        hbox2.addLayout(vbox4)
        tab1.setLayout(outer_layout)
        return tab1

    def value_change(self, weights):
        for i, slider in enumerate(self.wrd_sliders):
            weights[i] = slider.value()
        self.canvas.plot(*weights)
        self.canvas.draw()

    def value_change1(self, weights):
        for i, slider in enumerate(self.obj_sliders):
            weights[i] = slider.value()
        self.canvas1.plot(*weights)
        self.canvas1.draw()

    # ------------------------------------------------------------------
    # Tab 2: Gameplay
    # ------------------------------------------------------------------

    def tab2_UI(self):
        s = self.settings
        tab2 = QWidget()
        outer_layout = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()
        top_layout = QFormLayout()
        energy_slider_values = [0, s.impact_max, s.impact_min, s.energy_mean]

        self.successive_diff = QCheckBox("different successive target stimuli", self)
        self.successive_diff.toggle()
        self.successive_diff.setChecked(s.diff_successive)
        self.successive_diff.setToolTip('prevent the same target object from \n'
                                        'being presented successively')

        self.LivesBox = QLineEdit(self)
        self.onlyInt = QIntValidator()
        self.LivesBox.setValidator(self.onlyInt)
        self.LivesBox.setText('0')
        self.LivesBox.setToolTip('Set to zero for infinite lives')

        self.canvas3 = PlotCanvas(self, *energy_slider_values, width=300, height=270)
        self.canvas3.setStyleSheet("""QWidget {background-color:   grey}""")
        self.canvas3.setMinimumHeight(300)
        self.canvas3.setMaximumHeight(450)

        self.continuous_energy = QCheckBox(" linear energy impact ", self)
        self.continuous_energy.toggle()
        self.continuous_energy.setChecked(s.isEnergy_linear)
        self.continuous_energy.setToolTip('Positive and negative impacts to energy \n '
                                          'will be equal to the maximum value \n'
                                          'at all levels of player energy.')

        self.starting_energy_slider = QSlider(Qt.Horizontal, self)
        self.starting_energy_slider.setValue(s.energy)
        self.starting_energy_slider.setMinimum(0)
        self.starting_energy_slider.setMaximum(99)
        self.starting_energy_slider.setToolTip("set the user's starting energy level")

        self.starting_energy_value_label = QLineEdit('0', self)
        self.starting_energy_value_label.setMinimumWidth(80)
        self.starting_energy_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.starting_energy_value_label.setText(str(s.energy))
        self.starting_energy_value_label.setValidator(QIntValidator(0, 100))

        self.starting_energy_value_label.returnPressed.connect(
            lambda: self.starting_energy_slider.setValue(int(self.starting_energy_value_label.text())))
        self.starting_energy_slider.valueChanged.connect(
            lambda: self.starting_energy_value_label.setText(str(self.starting_energy_slider.value())))

        starting_energy_label = QLabel('Starting energy', self)
        starting_energy_label.setAlignment(Qt.AlignCenter)
        starting_energy_label.adjustSize()

        self.stick_point_slider = QSlider(Qt.Horizontal, self)
        self.stick_point_slider.setValue(energy_slider_values[3])
        self.stick_point_slider.setMinimum(1)
        self.stick_point_slider.setMaximum(99)
        self.stick_point_slider.setToolTip("The point above which it becomes increasingly \n"
                                           "difficult to increase energy supply and below which \n"
                                           "negative impacts to energy are increasingly negligible")

        self.stick_point_value_label = QLineEdit('0', self)
        self.stick_point_value_label.setMinimumWidth(80)
        self.stick_point_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.stick_point_value_label.setText(str(energy_slider_values[3]))
        self.stick_point_value_label.setValidator(QIntValidator(1, 99))

        self.stick_point_value_label.returnPressed.connect(
            lambda: self.stick_point_slider.setValue(int(self.stick_point_value_label.text())))
        self.stick_point_slider.valueChanged.connect(
            lambda: self.stick_point_value_label.setText(str(self.stick_point_slider.value())))

        stick_point_label = QLabel('Energy stick point', self)
        stick_point_label.setAlignment(Qt.AlignCenter)
        stick_point_label.adjustSize()
        stick_point_label.setToolTip('Negative impact to energy will approach the minimum value \n'
                                     'as player energy decreases below this point, whilst positive  \n'
                                     'impact to energy will decrease to the minimum value as  \n'
                                     'player energy exceeds this point. ')

        self.min_impact_slider = QSlider(Qt.Horizontal, self)
        self.min_impact_slider.setMinimum(1)
        self.min_impact_slider.setMaximum(15)
        self.min_impact_slider.setValue(energy_slider_values[2])
        self.min_impact_slider.setToolTip('Negative impact to energy will decrease to this value \n'
                                          'when player energy drops below below the "stick-point", whilst positive  \n'
                                          'impact to energy will decrease to this value when  \n'
                                          'player energy exceeds the "stick-point".')

        self.min_impact_value_label = QLineEdit('0', self)
        self.min_impact_value_label.setMinimumWidth(80)
        self.min_impact_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.min_impact_value_label.setText(str(energy_slider_values[2]))
        self.min_impact_value_label.setValidator(QIntValidator(1, 15))

        self.min_impact_value_label.returnPressed.connect(
            lambda: self.min_impact_slider.setValue(int(self.min_impact_value_label.text())))
        self.min_impact_slider.valueChanged.connect(
            lambda: self.min_impact_value_label.setText(str(self.min_impact_slider.value())))

        min_impact_label = QLabel('Minimum energy impact', self)
        min_impact_label.setAlignment(Qt.AlignCenter)
        min_impact_label.adjustSize()

        self.max_impact_slider = QSlider(Qt.Horizontal, self)
        self.max_impact_slider.setMinimum(5)
        self.max_impact_slider.setMaximum(20)
        self.max_impact_slider.setValue(energy_slider_values[1])
        self.max_impact_slider.setToolTip('Negative impact to energy will increase to this value \n'
                                          'when player energy exceeds the "stick-point", whilst positive  \n'
                                          'impact to energy will increase to this value when  \n'
                                          'player energy drops below the "stick-point".')

        self.max_impact_value_label = QLineEdit('0', self)
        self.max_impact_value_label.setMinimumWidth(80)
        self.max_impact_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.max_impact_value_label.setText(str(energy_slider_values[1]))
        self.max_impact_value_label.setValidator(QIntValidator(5, 20))

        self.max_impact_value_label.returnPressed.connect(
            lambda: self.max_impact_slider.setValue(int(self.max_impact_value_label.text())))
        self.max_impact_slider.valueChanged.connect(
            lambda: self.max_impact_value_label.setText(str(self.max_impact_slider.value())))

        max_impact_label = QLabel('Maximum energy impact', self)
        max_impact_label.setAlignment(Qt.AlignCenter)
        max_impact_label.adjustSize()

        self.tally_theshold_slider = QSlider(Qt.Horizontal, self)
        self.tally_theshold_slider.setMinimum(0)
        self.tally_theshold_slider.setMaximum(100)
        self.tally_theshold_slider.setValue(s.thresh)

        self.tally_theshold_value_label = QLineEdit('0', self)
        self.tally_theshold_value_label.setMinimumWidth(80)
        self.tally_theshold_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.tally_theshold_value_label.setText(str(s.thresh))
        self.tally_theshold_value_label.setValidator(QIntValidator(0, 100))

        self.tally_theshold_value_label.returnPressed.connect(
            lambda: self.tally_theshold_slider.setValue(int(self.tally_theshold_value_label.text())))
        self.tally_theshold_slider.valueChanged.connect(
            lambda: self.tally_theshold_value_label.setText(str(self.tally_theshold_slider.value())))

        tally_theshold_label = QLabel('threshold for target image', self)
        tally_theshold_label.setAlignment(Qt.AlignCenter)
        tally_theshold_label.adjustSize()
        self.tally_theshold_slider.setToolTip('set the number of correct responses associated with an object, \n '
                                              'after which the target image for that object will no longer \n'
                                              'be displayed as part of the stimulus.')

        self.stick_point_slider.valueChanged.connect(lambda: self.draw_plot(energy_slider_values))
        self.min_impact_slider.valueChanged.connect(lambda: self.draw_plot(energy_slider_values))
        self.max_impact_slider.valueChanged.connect(lambda: self.draw_plot(energy_slider_values))

        top_layout.addRow("Number of Lives:", self.LivesBox)
        outer_layout.addWidget(self.canvas3)

        vbox1.addSpacing(15)
        vbox1.addWidget(starting_energy_label)
        vbox1.addWidget(self.starting_energy_slider)
        vbox1.addWidget(self.starting_energy_value_label)

        vbox2.addWidget(stick_point_label)
        vbox2.addWidget(self.stick_point_slider)
        vbox2.addWidget(self.stick_point_value_label)
        vbox2.addWidget(min_impact_label)
        vbox2.addWidget(self.min_impact_slider)
        vbox2.addWidget(self.min_impact_value_label)
        vbox2.addWidget(max_impact_label)
        vbox2.addWidget(self.max_impact_slider)
        vbox2.addWidget(self.max_impact_value_label)

        vbox1.addSpacing(15)
        vbox1.addWidget(tally_theshold_label)
        vbox1.addWidget(self.tally_theshold_slider)
        vbox1.addWidget(self.tally_theshold_value_label)
        vbox1.addSpacing(52)
        vbox1.addWidget(self.continuous_energy)
        vbox1.addSpacing(52)

        vbox3.addWidget(self.successive_diff)
        vbox3.addSpacing(100)

        outer_layout.addLayout(hbox1)
        hbox1.addLayout(vbox1)
        hbox1.addLayout(vbox2)
        outer_layout.addLayout(vbox3)
        outer_layout.addLayout(top_layout)
        tab2.setLayout(outer_layout)
        return tab2

    def draw_plot(self, weights):
        weights[1] = self.max_impact_slider.value()
        weights[2] = self.min_impact_slider.value()
        weights[3] = self.stick_point_slider.value()
        self.canvas3.plot(*weights)
        self.canvas3.draw()

    # ------------------------------------------------------------------
    # Tab 3 (Display/Audio tab — labelled tab4_UI in original)
    # ------------------------------------------------------------------

    def tab4_UI(self):
        s = self.settings
        tab4 = QWidget()
        outer_layout = QVBoxLayout()
        gridlay = QGridLayout()

        self.feedback_check = QCheckBox(" feedback sounds ", self)
        self.feedback_check.toggle()
        self.feedback_check.setChecked(s.isFeedback)
        self.feedback_check.setToolTip("turn on feedback sound effects (correct or incorrect) \n"
                                       "that play after the user clicks a response object.")

        self.energy_overlay_check = QCheckBox(" low-health vignette overlay  ", self)
        self.energy_overlay_check.toggle()
        self.energy_overlay_check.setChecked(s.isEnergy_overlay)
        self.energy_overlay_check.setEnabled(False)

        self.label_audio_check = QCheckBox(" play audio for stimulus ", self)
        self.label_audio_check.toggle()
        self.label_audio_check.setChecked(s.isLabel_audio)
        self.label_audio_check.setToolTip("turn on the audio that reads the label \n"
                                          "of each newly displayed target object.")

        self.energy_animate_check = QCheckBox(" animate energy bar ", self)
        self.energy_animate_check.toggle()
        self.energy_animate_check.setChecked(s.isAnimate_energy)
        self.energy_animate_check.setEnabled(False)

        self.increase_scroll_check = QCheckBox(" gradually increase scroll speed ", self)
        self.increase_scroll_check.toggle()
        self.increase_scroll_check.setChecked(s.increase_scroll)
        self.increase_scroll_check.setToolTip("incrementally speed up the scrolling each time \n"
                                              "the player crosses the threshold for correct \n"
                                              "responses relating to an object.")

        # Feedback delay widgets
        feedback_delay_label = QLabel('feedback delay', self)
        feedback_delay_label.setAlignment(Qt.AlignCenter)
        feedback_delay_label.adjustSize()

        self.feedback_delay_slider = QSlider(Qt.Horizontal, self)
        self.feedback_delay_slider.setMinimum(0)
        self.feedback_delay_slider.setMaximum(100)
        self.feedback_delay_slider.setValue(s.feedback_delay_value)
        self.feedback_delay_slider.setEnabled(False)
        self.feedback_delay_slider.setToolTip("adjust the length of the delay between the response \n"
                                              "click and the feedback sound effect for that click.")

        self.feedback_delay_v_label = QLineEdit('0', self)
        self.feedback_delay_v_label.setMaximumWidth(30)
        self.feedback_delay_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.feedback_delay_v_label.setText(str(s.feedback_delay_value))
        self.feedback_delay_v_label.setEnabled(False)
        self.feedback_delay_v_label.setValidator(QIntValidator(0, 100))

        self.feedback_delay_v_label.returnPressed.connect(
            lambda: self.feedback_delay_slider.setValue(int(self.feedback_delay_v_label.text())))
        self.feedback_delay_slider.valueChanged.connect(
            lambda: self.feedback_delay_v_label.setText(str(self.feedback_delay_slider.value())))

        # Randomise feedback audio widgets
        feedback_random_label = QLabel('feedback audio randomisation', self)
        feedback_random_label.setAlignment(Qt.AlignCenter)
        feedback_random_label.adjustSize()

        self.feedback_random_slider = QSlider(Qt.Horizontal, self)
        self.feedback_random_slider.setMinimum(0)
        self.feedback_random_slider.setMaximum(100)
        self.feedback_random_slider.setValue(s.feedback_random_value)
        self.feedback_random_slider.setToolTip("set how often the feedback sound effects (correct/incorrect) \n"
                                               "will be swapped around.")

        self.feedback_random_v_label = QLineEdit('0', self)
        self.feedback_random_v_label.setMaximumWidth(30)
        self.feedback_random_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.feedback_random_v_label.setText(str(s.feedback_random_value))

        self.feedback_random_v_label.returnPressed.connect(
            lambda: self.feedback_random_slider.setValue(int(self.feedback_random_v_label.text())))
        self.feedback_random_slider.valueChanged.connect(
            lambda: self.feedback_random_v_label.setText(str(self.feedback_random_slider.value())))

        # Scroll speed widgets
        scroll_speed_label = QLabel('scroll speed', self)
        scroll_speed_label.setAlignment(Qt.AlignCenter)
        scroll_speed_label.adjustSize()

        self.scroll_speed_slider = QSlider(Qt.Horizontal, self)
        self.scroll_speed_slider.setMinimum(0)
        self.scroll_speed_slider.setMaximum(10)
        self.scroll_speed_slider.setValue(s.scroll_speed_value)
        self.scroll_speed_slider.setToolTip("set the speed of the vertical scrolling in the game.")

        self.scroll_speed_v_label = QLineEdit('0', self)
        self.scroll_speed_v_label.setMaximumWidth(30)
        self.scroll_speed_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.scroll_speed_v_label.setText(str(s.scroll_speed_value))

        self.scroll_speed_v_label.returnPressed.connect(
            lambda: self.scroll_speed_slider.setValue(int(self.scroll_speed_v_label.text())))
        self.scroll_speed_slider.valueChanged.connect(
            lambda: self.scroll_speed_v_label.setText(str(self.scroll_speed_slider.value())))

        # FPS settings widgets
        max_fps_label = QLabel('frames per second', self)
        max_fps_label.setAlignment(Qt.AlignCenter)
        max_fps_label.adjustSize()

        self.max_fps_slider = QSlider(Qt.Horizontal, self)
        self.max_fps_slider.setMinimum(15)
        self.max_fps_slider.setMaximum(100)
        self.max_fps_slider.setValue(s.fps)
        self.max_fps_slider.setToolTip("set the animation frame rate (FPS). A higher \n"
                                       "FPS makes the game run more smoothly but \n"
                                       "requires more computer resources")

        self.max_fps_v_label = QLineEdit('0', self)
        self.max_fps_v_label.setMaximumWidth(30)
        self.max_fps_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.max_fps_v_label.setText(str(s.fps))

        self.max_fps_v_label.returnPressed.connect(
            lambda: self.max_fps_slider.setValue(int(self.max_fps_v_label.text())))
        self.max_fps_slider.valueChanged.connect(
            lambda: self.max_fps_v_label.setText(str(self.max_fps_slider.value())))

        gridlay.addWidget(self.feedback_check, 0, 1, 1, 3)
        gridlay.addWidget(feedback_delay_label, 1, 0, 2, 2)
        gridlay.addWidget(self.feedback_delay_v_label, 1, 2, 2, 3)
        gridlay.addWidget(self.feedback_delay_slider, 1, 3, 2, 5)
        gridlay.addWidget(feedback_random_label, 2, 0, 3, 2)
        gridlay.addWidget(self.feedback_random_v_label, 2, 2, 3, 3)
        gridlay.addWidget(self.feedback_random_slider, 2, 3, 3, 5)
        gridlay.addWidget(scroll_speed_label, 3, 0, 4, 2)
        gridlay.addWidget(self.scroll_speed_v_label, 3, 2, 4, 3)
        gridlay.addWidget(self.scroll_speed_slider, 3, 3, 4, 5)
        gridlay.addWidget(max_fps_label, 4, 0, 5, 2)
        gridlay.addWidget(self.max_fps_v_label, 4, 2, 5, 3)
        gridlay.addWidget(self.max_fps_slider, 4, 3, 5, 5)
        gridlay.addWidget(self.increase_scroll_check, 5, 1, 6, 3)
        gridlay.addWidget(self.label_audio_check, 6, 1, 7, 3)
        gridlay.addWidget(self.energy_animate_check, 7, 1, 8, 3)
        gridlay.addWidget(self.energy_overlay_check, 8, 1, 9, 3)

        outer_layout.addSpacing(15)
        outer_layout.addLayout(gridlay)
        tab4.setLayout(outer_layout)
        return tab4

    # ------------------------------------------------------------------
    # Tab 4 (Outputs tab — labelled tab3_UI in original)
    # ------------------------------------------------------------------

    def tab3_UI(self):
        s = self.settings
        tab3 = QWidget()
        outer_layout = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()

        check_values = s.output_checkboxes['boolean_value']
        check_variables = s.output_checkboxes['description']
        self.checkbox_list = QListWidget()
        list_items = list(range(len(s.output_checkboxes['variable_name'])))
        for i in range(len(check_variables)):
            list_items[i] = QListWidgetItem(check_variables[i])
            list_items[i].setFlags(list_items[i].flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if check_values[i]:
                list_items[i].setCheckState(Qt.Checked)
            else:
                list_items[i].setCheckState(Qt.Unchecked)
            self.checkbox_list.addItem(list_items[i])

        self.checkbox_list.setMaximumHeight(400)
        self.checkbox_list.setToolTip("selection of any of the following indicates its  \n"
                                      "inclusion as a variable in the exported .csv file")

        self.mouse_export = QCheckBox("   Export mouse tracking", self)
        self.mouse_export.toggle()
        self.mouse_export.setChecked(s.isMousetrack)
        self.mouse_export.setToolTip("exports files to '/mouse_tracking' containing \n"
                                     "mouse coordinate information for each response")

        outer_layout.addWidget(self.checkbox_list)
        outer_layout.addWidget(self.mouse_export)
        outer_layout.addSpacing(200)
        outer_layout.addLayout(hbox1)
        hbox1.addLayout(vbox1)
        hbox1.addLayout(vbox2)
        outer_layout.addLayout(vbox3)
        tab3.setLayout(outer_layout)
        return tab3

    # ------------------------------------------------------------------
    # on_click — collect values from UI and save settings
    # ------------------------------------------------------------------

    @pyqtSlot()
    def on_click(self, save_file_path, isExit):
        s = self.settings
        s.export_settings = self.setting_export.isChecked()

        for j in range(len(s.output_checkboxes['variable_name'])):
            if self.checkbox_list.item(j).checkState() == Qt.Checked:
                s.output_checkboxes.at[j, 'boolean_value'] = True
            else:
                s.output_checkboxes.at[j, 'boolean_value'] = False

        for i, slider in enumerate(self.wrd_sliders):
            s.word_slider_values[i] = slider.value()
        for i, slider in enumerate(self.obj_sliders):
            s.object_slider_values[i] = slider.value()

        s.bg_matchingness = self.bg_match_slider.value()
        s.impact_max = self.max_impact_slider.value()
        s.impact_min = self.min_impact_slider.value()
        s.energy_mean = self.stick_point_slider.value()
        s.scroll_speed_value = self.scroll_speed_slider.value()
        s.id_name = self.IDtextbox.text()
        s.energy = self.starting_energy_slider.value()
        s.starting_vocabulary = self.start_vocab_slider.value()
        s.thresh = self.tally_theshold_slider.value()
        s.fps = self.max_fps_slider.value()

        s.lives = -1
        if int(self.LivesBox.text()) > 0:
            s.lives = int(self.LivesBox.text())
        s.load_previous = self.prior_word_set_box.isChecked()
        s.isMousetrack = self.mouse_export.isChecked()
        s.rareness = self.rareness_ordering.isChecked()
        s.isFixed = self.fixed_labels_box.isChecked()
        s.isEnergy_linear = self.continuous_energy.isChecked()
        s.diff_successive = self.successive_diff.isChecked()
        s.feedback_random_value = self.feedback_random_slider.value()
        s.isFeedback = self.feedback_check.isChecked()

        s.save(save_file_path)
        if isExit:
            self.exit_application = False
            self.close()


# ---------------------------------------------------------------------------
# Matplotlib canvas widgets
# ---------------------------------------------------------------------------

class Canvas(FigureCanvas):
    @pyqtSlot()
    def __init__(self, *weights, parent=None, width=8, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#E1E1E1')
        FigureCanvas.__init__(self, fig)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setParent(parent)
        self.plot(*weights)

    def plot(self, *weights):
        self.figure.clear()
        if len(weights) > 1:
            columns = ['v' + str(i + 1) for i in range(len(weights))]
            df = pd.DataFrame([weights], columns=columns)
            word_slider_colours = ["blue", "red", "yellow", "pink", "orange", "green"]
            self.figure.clear()
            self.ax = self.figure.subplots()
            df.plot.barh(stacked=True, ax=self.ax, legend=False, edgecolor='black', color=word_slider_colours)
            self.ax.axis("off")


class PlotCanvas(FigureCanvas):
    @pyqtSlot()
    def __init__(self, *weights, parent=None, width=5, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, facecolor='#E1E1E1')
        FigureCanvas.__init__(self, fig)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setParent(parent)
        self.plot(weights)

    def adjust_spines(self, ax, spines):
        for loc, spine in ax.spines.items():
            if loc in spines:
                spine.set_position(('outward', 10))
            else:
                spine.set_color('none')
        if 'left' in spines:
            ax.yaxis.set_ticks_position('left')
        else:
            ax.yaxis.set_ticks([])
        if 'bottom' in spines:
            ax.xaxis.set_ticks_position('bottom')
        else:
            ax.xaxis.set_ticks([])

    def plot(self, *weights):
        self.figure.clear()

        # Use defaults from first weight tuple or individual args
        if len(weights) >= 1 and isinstance(weights[0], tuple):
            weights = weights[0]

        a = 6  # default impact_max
        b = 3  # default impact_min
        c = 0.3  # default energy_mean / 100
        if len(weights) > 3:
            a = int(weights[1])
            b = int(weights[2])
            c = int(weights[3]) / 100

        x = np.linspace(-2, 2, 100)
        ax = self.figure.add_subplot(1, 1, 1)

        if a >= b:
            if c >= .5:
                y = np.divide(a - b, 10) * np.divide(
                    np.exp(2 * np.divide(a, b - a) * (np.divide(x, c) - 1)) - 1,
                    np.exp(2 * np.divide(a, b - a) * (np.divide(x, c) - 1)) + 1)
            else:
                y = np.divide(a - b, 10) * np.divide(
                    1 - np.exp(2 * np.divide(a, b - a) * (np.divide(1 - x, 1 - c) - 1)),
                    1 + np.exp(2 * np.divide(a, b - a) * (np.divide(1 - x, 1 - c) - 1)))

            ax.spines['left'].set_position('center')
            ax.spines['bottom'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            ax.yaxis.set_ticks([])
            ax.xaxis.set_ticks([])
            self.adjust_spines(ax, ['left', 'bottom'])
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
            ax.set_xlim([-.5, 1.5])
            ax.set_ylim([-3, 3])
            ax.set_xlabel("Player Energy (0 --> 100)")
            ax.set_ylabel("Relative Ability to Gain Energy")
            ax.plot(x, y)
        else:
            y = x * 0 + np.divide(b, 2)
            ax.plot(x, y, label='Minimum must not exceed maximum')
            ax.axis("off")
            ax.legend(loc='center')
            ax.set_xlim([0, 1])
            ax.set_ylim([-20, 20])
