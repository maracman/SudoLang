import pygame
from pygame import mixer

import random
import math
import time
from datetime import datetime
import csv
import pickle
import sys
import pandas as pd
import numpy as np
import re
import os
import platform
from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QMainWindow, QWidget, \
    QApplication, QWidget, QPushButton, QMessageBox, QHBoxLayout, \
    QAction, QTabWidget, QLineEdit, QSlider, QLabel, QCheckBox, QGridLayout, \
    QListWidget, QListWidgetItem, QFileDialog, qApp
from PyQt5.QtGui import QIntValidator
from PyQt5 import sip
from PyQt5.QtCore import pyqtSlot, Qt, QCoreApplication
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')


clock = pygame.time.Clock()

operating_system = sys.platform
if operating_system == "darwin":
    dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
    if not os.path.exists(os.path.join(dir_path, 'SL_data')):
        parent_dir = os.path.split(dir_path)[0]
        for i in range(4):
            print("searching parent directories for program data")
            if os.path.exists(os.path.join(parent_dir, 'SL_data')):
                dir_path = parent_dir
                break
            else:
                parent_dir = os.path.split(parent_dir)[0]
else:
    dir_path = os.getcwd()

data_path = os.path.join(dir_path, 'SL_data/')

# default settings paths
settings_default_path = os.path.join(data_path, 'current_settings.pkl')
survey_settings_path = os.path.join(data_path, 'survey_settings.pkl')
font_location = os.path.join(data_path, 'freesansbold.ttf')
outputs_path = os.path.join(dir_path, 'outputs/')
previous_data_sets_path = os.path.join(data_path, 'saved_game_states/')

# load input CSV
inputData = pd.read_csv(os.path.join(data_path, 'game_input_data.csv'))

#change to True for Survey program
isSurvey = False

isEnergy_overlay = False
isAnimate_energy = False
feedback_delay_value = 10
isFeedback = True
feedback_random_value = 0
export_settings_glob = False

exit_application_glob = True
reload_settings = False

#create default settings and save out to file

word_slider_values = [5, 20, 45, 35, 15, 10]
object_slider_values = [50, 50, 0]

#output_checkboxes is used as basis for output_dataframe later on
output_checkboxes = pd.DataFrame(
    [['click_time', True, "'click_time': Timestamp for click"],
     ['since_last_click', True, "'since_last_click': Time since last response click "],
     ['since_stimulus', True, "'since_stimulus': Time since last matching response"],
     ['score_for_clicked', True, "'score_for_clicked': No. of prior matches for clicked object"],
     ['score_for_target', True, "'score_for_target': No. of prior matches for target object"],
     ['clicked_word_category', True, "'clicked_word_category': Numerical category of the clicked's label"],
     ['target_word_category', True, "'target_word_category': Numerical category of the target's label"],
     ['target_object_category', True, "'target_object_category': Category of the target object"],
     ['clicked_object_category', True, "'clicked_object_category': Category of the clicked object"],
     ['isRepeat', True, "'isRepeat': Was the same target shown for the prior stimulus"],
     ['isMatch', True, "'isMatch': Did the response match the target"],
     ['x_position', True, "'x_position': Horizontal position of the response click "],
     ['player_energy', True, "'player_energy': player's energy at time of response"],
     ['user_ID', True, "'user_ID': Tag each response with the user_ID"],
     ['isDisplayed', True, "'isDisplayed': is target object image represented as stimulus"],
     ['clicked_label', True, "clicked_label: The label for the object clicked"],
     ['clicked_img', True, "'clicked_img': The image name for the object clicked"],
     ['target_label', True, "target_label: The label for the target object"],
     ['target_img', True, "'target_img': The image name of the target object"],
     ['vocab_size', True, "'vocab_size': size of player vocabulary at click"],
     ['time_date', False, "'time_date': time stamp of the start of the session"],
     ['feedback_type', True, "'feedback_type': correct (+1) or incorrect (-1) sound played on click"],
     ['coord_file_name', False, "'coord_file_name': file name of mouse track data for click"],
     ['objects_on_screen', False, "'objects_on_screen': the number of objects on screen"],
     ['scroll_speed', False, "'scroll_speed': the speed objects are progressing down the screen"]],
    columns=pd.Index(['variable_name', 'boolean_value', 'description'])
)

id_name = '_'
energy = 50
impact_max = 6
impact_min = 3
energy_mean = 30 #"stick-point"
isEnergy_linear = False
load_previous = False
rareness = True
diff_successive = True
increase_scroll = True
thresh = 4
starting_vocabulary = 3
fps = 50
isLabel_audio = True
scroll_speed_value = 3
bg_matchingness = 0
isMousetrack = False
lives = -1
isFixed = False


def pickle_load_and_save_settings(file_path):
    with open(file_path, 'rb') as f:
        word_slider_values, object_slider_values, energy_mean, impact_max, impact_min, \
        output_checkboxes, id_name, lives, starting_vocabulary, bg_matchingness, energy, \
        thresh, isEnergy_linear, load_previous, isMousetrack, rareness, fps, increase_scroll, isFixed, scroll_speed_value, \
        diff_successive, isLabel_audio, feedback_random_value, isFeedback = pickle.load(f)

    with open(settings_default_path, 'wb') as f:
        pickle.dump([word_slider_values,
                     object_slider_values,
                     energy_mean,
                     impact_max,
                     impact_min,
                     output_checkboxes,
                     id_name,
                     lives,
                     starting_vocabulary,
                     bg_matchingness,
                     energy,
                     thresh,
                     isEnergy_linear,
                     load_previous,
                     isMousetrack,
                     rareness,
                     fps,
                     increase_scroll,
                     isFixed,
                     scroll_speed_value,
                     diff_successive,
                     isLabel_audio,
                     feedback_random_value,
                     isFeedback
                     ], f)


def pickle_save_settings(file_path):
    with open(file_path, 'wb') as f:
        pickle.dump([word_slider_values,
                     object_slider_values,
                     energy_mean,
                     impact_max,
                     impact_min,
                     output_checkboxes,
                     id_name,
                     lives,
                     starting_vocabulary,
                     bg_matchingness,
                     energy,
                     thresh,
                     isEnergy_linear,
                     load_previous,
                     isMousetrack,
                     rareness,
                     fps,
                     increase_scroll,
                     isFixed,
                     scroll_speed_value,
                     diff_successive,
                     isLabel_audio,
                     feedback_random_value,
                     isFeedback
                     ], f)


if not os.path.isfile(settings_default_path):
    print("default settings file not found, initialising settings")
    pickle_save_settings(settings_default_path)
else:
    try:
        with open(settings_default_path, 'rb') as f:
            word_slider_values, object_slider_values, energy_mean, impact_max, impact_min, \
            output_checkboxes, id_name, lives, starting_vocabulary, bg_matchingness, energy, \
            thresh, isEnergy_linear, load_previous, isMousetrack, rareness, fps, increase_scroll, isFixed, scroll_speed_value, \
            diff_successive, isLabel_audio, feedback_random_value, isFeedback = pickle.load(f)

    except IOError:
        print("could not load latest settings")
        pickle_save_settings(settings_default_path)

class Enter_Name(QMainWindow):
    def __init__(self, parent=None):
        super(Enter_Name, self).__init__(parent)
        self.setWindowTitle("Enter User ID")
        self.resize(250, 130)

        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        self.IDtextbox = QLineEdit(self)
        self.IDtextbox.setText(id_name)
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
        global id_name
        global exit_application_glob
        exit_application_glob = False
        id_name = self.IDtextbox.text()
        self.close()



class App(QMainWindow):
    EXIT_CODE_REBOOT = -7654321
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setWindowTitle("Game Settings")
        self.resize(470, 500)
        self.setAttribute(Qt.WA_DeleteOnClose)
        # Create a top-level layout

        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)

        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(self.tab1_UI(), "Object Labels")
        tabs.addTab(self.tab2_UI(), "Gameplay")
        tabs.addTab(self.tab4_UI(), "Display/Audio")
        tabs.addTab(self.tab3_UI(), "Outputs")

        self.layout.addWidget(tabs)
        hlayout = QHBoxLayout()

        # Create a button in the window
        button = QPushButton('Continue', self)
        button.clicked.connect(lambda: self.on_click(save_file_path=settings_default_path, isExit=True))
        load_previous = False
        self.setting_export = QCheckBox("   Export these settings\n    for survey application", self)
        self.setting_export.toggle()
        self.setting_export.setChecked(load_previous)

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
        path = QFileDialog.getOpenFileName(self, 'Open a file', '',
                                        'All Files (*.*)')
        if path != ('', ''):
            print("File path : "+ path[0]) # path as list

            try:
                print("executing load")
                pickle_load_and_save_settings(path[0])
                print("load completed")
            except IOError:
                print("cant load file")

            self.exit_reboot()


    def save_settings(self):
        file_save = QFileDialog()
        file_save.setDefaultSuffix('pkl')
        name, _ = file_save.getSaveFileName(self, 'Save File',"", "PKL (*.pkl)")
        if name != '' and name != '.pkl':
            self.on_click(isExit=False, save_file_path=name)

    def tab1_UI(self):

        # define layouts
        tab1 = QWidget()
        #tab1.setStyleSheet("""background: white""")
        outer_layout = QVBoxLayout()
        hbox_top = QHBoxLayout()
        top_layout = QFormLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox3 = QVBoxLayout()
        hbox2 = QHBoxLayout()
        vbox4 = QVBoxLayout()

        self.canvas = Canvas(self, *word_slider_values, width=0, height=0)
        self.canvas.setStyleSheet("""QWidget {background-color:   grey}""")
        self.canvas.setMinimumHeight(30)
        self.canvas.setMaximumHeight(40)

        self.canvas1 = Canvas(self, *object_slider_values, width=0, height=0)
        self.canvas1.setStyleSheet("""QWidget {background-color:   grey}""")
        self.canvas1.setMinimumHeight(30)
        self.canvas1.setMaximumHeight(40)

        #Define settings widgets
        self.IDtextbox = QLineEdit(self)
        self.IDtextbox.setText(id_name)

        self.rareness_ordering = QCheckBox("  objects rareness \n according to label complexity", self)
        self.rareness_ordering.toggle()
        self.rareness_ordering.setChecked(rareness)
        self.rareness_ordering.setToolTip('Checking this box makes object-label pairs appear as the target stimulus \n'
                                            'according to probabilities based on the label category.')

        self.prior_word_set_box = QCheckBox("  load objects and labels \n  from (user ID's) previous session", self)
        self.prior_word_set_box.toggle()
        self.prior_word_set_box.setChecked(load_previous)
        self.prior_word_set_box.setToolTip("objects and their labels will be taken \n"
                                           "from the player's previous game. \n"
                                            'Settings for word weights will be ignored ')

        self.fixed_labels_box = QCheckBox(" Fixed labels ", self)
        self.fixed_labels_box.toggle()
        self.fixed_labels_box.setChecked(isFixed)
        self.fixed_labels_box.setToolTip("Create object labels according to the object image name")

        word_slider_tip = "set the relative proportion of words from \n"\
                          "this category to be used in user's object-label set"
        self.wrd1_slider = QSlider(Qt.Horizontal, self)
        self.wrd1_slider.setValue(word_slider_values[0])
        self.wrd1_slider.setMinimum(0)
        self.wrd1_slider.setMaximum(100)
        self.wrd1_slider.setToolTip(word_slider_tip)

        self.wrd1_v_label = QLineEdit('0', self)
        self.wrd1_v_label.setMinimumWidth(30)
        self.wrd1_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.wrd1_v_label.setText(str(word_slider_values[0]))
        wrd1_validator = QIntValidator(0, 100)
        self.wrd1_v_label.setValidator(wrd1_validator)

        self.wrd1_v_label.returnPressed.connect(
            lambda: self.wrd1_slider.setValue(int(self.wrd1_v_label.text())))
        self.wrd1_slider.valueChanged.connect(
            lambda: self.wrd1_v_label.setText(str(self.wrd1_slider.value())))
        self.wrd1_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))

        wrd1_label = QLabel('Two letter weight', self)
        wrd1_label.setAlignment(Qt.AlignCenter)
        wrd1_label.adjustSize()

        self.wrd2_slider = QSlider(Qt.Horizontal, self)
        self.wrd2_slider.setValue(word_slider_values[1])
        self.wrd2_slider.setMinimum(0)
        self.wrd2_slider.setMaximum(100)
        self.wrd2_slider.setToolTip(word_slider_tip)

        self.wrd2_v_label = QLineEdit('0', self)
        self.wrd2_v_label.setMinimumWidth(30)
        self.wrd2_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.wrd2_v_label.setText(str(word_slider_values[1]))
        wrd2_validator = QIntValidator(0, 100)
        self.wrd2_v_label.setValidator(wrd2_validator)

        self.wrd2_v_label.returnPressed.connect(
            lambda: self.wrd2_slider.setValue(int(self.wrd2_v_label.text())))
        self.wrd2_slider.valueChanged.connect(
            lambda: self.wrd2_v_label.setText(str(self.wrd2_slider.value())))
        self.wrd2_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))

        wrd2_label = QLabel('One syllable weight', self)
        wrd2_label.setAlignment(Qt.AlignCenter)
        wrd2_label.adjustSize()

        self.wrd3_slider = QSlider(Qt.Horizontal, self)
        self.wrd3_slider.setValue(word_slider_values[2])
        self.wrd3_slider.setMinimum(0)
        self.wrd3_slider.setMaximum(100)
        self.wrd3_slider.setToolTip(word_slider_tip)

        self.wrd3_v_label = QLineEdit('0', self)
        self.wrd3_v_label.setMinimumWidth(30)
        self.wrd3_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.wrd3_v_label.setText(str(word_slider_values[2]))
        wrd3_validator = QIntValidator(0, 100)
        self.wrd3_v_label.setValidator(wrd3_validator)
        self.wrd3_v_label.returnPressed.connect(
            lambda: self.wrd3_slider.setValue(int(self.wrd3_v_label.text())))
        self.wrd3_slider.valueChanged.connect(
            lambda: self.wrd3_v_label.setText(str(self.wrd3_slider.value())))
        self.wrd3_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))

        wrd3_label = QLabel('Two syllable weight', self)
        wrd3_label.setAlignment(Qt.AlignCenter)
        wrd3_label.adjustSize()

        self.wrd4_slider = QSlider(Qt.Horizontal, self)
        self.wrd4_slider.setValue(word_slider_values[3])
        self.wrd4_slider.setMinimum(0)
        self.wrd4_slider.setMaximum(100)
        self.wrd4_slider.setToolTip(word_slider_tip)

        self.wrd4_v_label = QLineEdit('0', self)
        self.wrd4_v_label.setMinimumWidth(30)
        self.wrd4_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.wrd4_v_label.setText(str(word_slider_values[3]))
        wrd4_validator = QIntValidator(0, 100)
        self.wrd3_v_label.setValidator(wrd4_validator)

        self.wrd4_v_label.returnPressed.connect(
            lambda: self.wrd4_slider.setValue(int(self.wrd4_v_label.text())))
        self.wrd4_slider.valueChanged.connect(
            lambda: self.wrd4_v_label.setText(str(self.wrd4_slider.value())))
        self.wrd4_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))

        wrd4_label = QLabel('Two syllable (long) weight', self)
        wrd4_label.setAlignment(Qt.AlignCenter)
        wrd4_label.adjustSize()

        self.wrd5_slider = QSlider(Qt.Horizontal, self)
        self.wrd5_slider.setValue(word_slider_values[4])
        self.wrd5_slider.setMinimum(0)
        self.wrd5_slider.setMaximum(100)
        self.wrd5_slider.setToolTip(word_slider_tip)

        self.wrd5_v_label = QLineEdit('0', self)
        self.wrd5_v_label.setMinimumWidth(30)
        self.wrd5_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.wrd5_v_label.setText(str(word_slider_values[4]))
        wrd5_validator = QIntValidator(0, 100)
        self.wrd5_v_label.setValidator(wrd5_validator)

        self.wrd5_v_label.returnPressed.connect(
            lambda: self.wrd5_slider.setValue(int(self.wrd5_v_label.text())))
        self.wrd5_slider.valueChanged.connect(
            lambda: self.wrd5_v_label.setText(str(self.wrd5_slider.value())))
        self.wrd5_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))

        wrd5_label = QLabel('Three syllable weight', self)
        wrd5_label.setAlignment(Qt.AlignCenter)
        wrd5_label.adjustSize()

        self.wrd6_slider = QSlider(Qt.Horizontal, self)
        self.wrd6_slider.setValue(word_slider_values[5])
        self.wrd6_slider.setMinimum(0)
        self.wrd6_slider.setMaximum(100)
        self.wrd6_slider.setToolTip(word_slider_tip)

        self.wrd6_v_label = QLineEdit('0', self)
        self.wrd6_v_label.setMinimumWidth(30)
        self.wrd6_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.wrd6_v_label.setText(str(word_slider_values[5]))
        wrd6_validator = QIntValidator(0, 100)
        self.wrd6_v_label.setValidator(wrd6_validator)

        self.wrd6_v_label.returnPressed.connect(
            lambda: self.wrd6_slider.setValue(int(self.wrd6_v_label.text())))
        self.wrd6_slider.valueChanged.connect(
            lambda: self.wrd6_v_label.setText(str(self.wrd6_slider.value())))
        self.wrd6_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))

        wrd6_label = QLabel('Four syllable weight', self)
        wrd6_label.setAlignment(Qt.AlignCenter)
        wrd6_label.adjustSize()

        object_slider_tip = "set the relative proportion of objects from \n"\
                          "this category to be used in user's object-label set"
        self.obj1_slider = QSlider(Qt.Horizontal, self)
        self.obj1_slider.setValue(object_slider_values[0])
        self.obj1_slider.setMinimum(0)
        self.obj1_slider.setMaximum(100)
        self.obj1_slider.setToolTip(object_slider_tip)

        self.obj1_v_label = QLineEdit('0', self)
        self.obj1_v_label.setMinimumWidth(30)
        self.obj1_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.obj1_v_label.setText(str(object_slider_values[0]))
        obj1_validator = QIntValidator(0,100)
        self.obj1_v_label.setValidator(obj1_validator)

        self.obj1_v_label.returnPressed.connect(
            lambda: self.obj1_slider.setValue(int(self.obj1_v_label.text())))
        self.obj1_slider.valueChanged.connect(
            lambda: self.obj1_v_label.setText(str(self.obj1_slider.value())))
        self.obj1_slider.valueChanged.connect(lambda: self.value_change1(object_slider_values))

        obj1_label = QLabel('Object Category One', self)
        obj1_label.setAlignment(Qt.AlignCenter)
        obj1_label.adjustSize()
        obj1_label.setToolTip("")

        self.obj2_slider = QSlider(Qt.Horizontal, self)
        self.obj2_slider.setValue(object_slider_values[1])
        self.obj2_slider.setMinimum(0)
        self.obj2_slider.setMaximum(100)
        self.obj2_slider.setToolTip(object_slider_tip)

        self.obj2_v_label = QLineEdit('0', self)
        self.obj2_v_label.setMinimumWidth(30)
        self.obj2_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.obj2_v_label.setText(str(object_slider_values[1]))
        obj2_validator = QIntValidator(0, 100)
        self.obj2_v_label.setValidator(obj2_validator)

        self.obj2_v_label.returnPressed.connect(
            lambda: self.obj2_slider.setValue(int(self.obj2_v_label.text())))
        self.obj2_slider.valueChanged.connect(
            lambda: self.obj2_v_label.setText(str(self.obj2_slider.value())))
        self.obj2_slider.valueChanged.connect(lambda: self.value_change1(object_slider_values))

        obj2_label = QLabel('Object Category Two', self)
        obj2_label.setAlignment(Qt.AlignCenter)
        obj2_label.adjustSize()
        obj2_label.setToolTip("")

        self.obj3_slider = QSlider(Qt.Horizontal, self)
        self.obj3_slider.setValue(object_slider_values[2])
        self.obj3_slider.setMinimum(0)
        self.obj3_slider.setMaximum(100)
        self.obj3_slider.setToolTip(object_slider_tip)

        self.obj3_v_label = QLineEdit('0', self)
        self.obj3_v_label.setMinimumWidth(30)
        self.obj3_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.obj3_v_label.setText(str(object_slider_values[2]))
        obj3_validator = QIntValidator(0, 100)
        self.obj3_v_label.setValidator(obj3_validator)

        self.obj3_v_label.returnPressed.connect(
            lambda: self.obj3_slider.setValue(int(self.obj3_v_label.text())))
        self.obj3_slider.valueChanged.connect(
            lambda: self.obj3_v_label.setText(str(self.obj3_slider.value())))
        self.obj3_slider.valueChanged.connect(lambda: self.value_change1(object_slider_values))


        obj3_label = QLabel('Object Category Three', self)
        obj3_label.setAlignment(Qt.AlignCenter)
        obj3_label.adjustSize()
        obj3_label.setToolTip("")


        self.bg_match_slider = QSlider(Qt.Horizontal, self)
        self.bg_match_slider.setValue(bg_matchingness)
        self.bg_match_slider.setMinimum(0)
        self.bg_match_slider.setMaximum(100)
        self.bg_match_slider.setEnabled(False)

        bg_match_v_label = QLabel('0', self)
        bg_match_v_label.setMinimumWidth(80)
        bg_match_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        bg_match_v_label.setText(str(bg_matchingness))
        bg_match_v_label.setEnabled(False)

        bg_match_label = QLabel('object/background \n matchingness', self)
        bg_match_label.setAlignment(Qt.AlignCenter)
        bg_match_label.adjustSize()
        bg_match_label.setToolTip("")

        self.start_vocab_slider = QSlider(Qt.Horizontal, self)
        self.start_vocab_slider.setValue(starting_vocabulary)
        self.start_vocab_slider.setMinimum(2)
        self.start_vocab_slider.setMaximum(10)
        self.start_vocab_slider.setToolTip("sets the number of possible object-label pairs \n"
                                           "that the user begins with")

        start_vocab_v_label = QLabel('0', self)
        start_vocab_v_label.setMinimumWidth(80)
        start_vocab_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        start_vocab_v_label.setText(str(starting_vocabulary))

        start_vocab_label = QLabel('starting vocabulary size', self)
        start_vocab_label.setAlignment(Qt.AlignCenter)
        start_vocab_label.adjustSize()
        start_vocab_label.setToolTip("")

        # Add widgets to layouts
        top_layout.addRow("User ID:", self.IDtextbox)

        hbox_top.addWidget(self.canvas)

        vbox1.addSpacing(15)
        vbox1.addWidget(wrd1_label)
        vbox1.addWidget(self.wrd1_slider)
        vbox1.addWidget(self.wrd1_v_label)
        vbox1.addSpacing(10)

        vbox1.addWidget(wrd2_label)
        vbox1.addWidget(self.wrd2_slider)
        vbox1.addWidget(self.wrd2_v_label)
        vbox1.addSpacing(10)

        vbox1.addWidget(wrd3_label)
        vbox1.addWidget(self.wrd3_slider)
        vbox1.addWidget(self.wrd3_v_label)
        vbox1.addSpacing(15)

        vbox2.addSpacing(15)
        vbox2.addWidget(wrd4_label)
        vbox2.addWidget(self.wrd4_slider)
        vbox2.addWidget(self.wrd4_v_label)
        vbox2.addSpacing(10)

        vbox2.addWidget(wrd5_label)
        vbox2.addWidget(self.wrd5_slider)
        vbox2.addWidget(self.wrd5_v_label)
        vbox2.addSpacing(10)

        vbox2.addWidget(wrd6_label)
        vbox2.addWidget(self.wrd6_slider)
        vbox2.addWidget(self.wrd6_v_label)
        vbox2.addSpacing(15)

        vbox3.addWidget(self.canvas1)

        vbox3.addWidget(obj1_label)
        vbox3.addWidget(self.obj1_slider)
        vbox3.addWidget(self.obj1_v_label)
        vbox3.addSpacing(15)

        vbox3.addWidget(obj2_label)
        vbox3.addWidget(self.obj2_slider)
        vbox3.addWidget(self.obj2_v_label)
        vbox3.addSpacing(15)

        vbox3.addWidget(obj3_label)
        vbox3.addWidget(self.obj3_slider)
        vbox3.addWidget(self.obj3_v_label)
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

        # Set Style Sheets
        #self.wrd1_slider.setStyleSheet("""QSlider::handle:horizontal { background: blue; border-radius: 10px; }""")
        #tab1.setStyleSheet()

        self.bg_match_slider.valueChanged.connect(
            lambda: bg_match_v_label.setText(str(self.bg_match_slider.value())))

        self.start_vocab_slider.valueChanged.connect(
            lambda: start_vocab_v_label.setText(str(self.start_vocab_slider.value())))

        # nest layouts
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
        weights[0] = self.wrd1_slider.value()
        weights[1] = self.wrd2_slider.value()
        weights[2] = self.wrd3_slider.value()
        weights[3] = self.wrd4_slider.value()
        weights[4] = self.wrd5_slider.value()
        weights[5] = self.wrd6_slider.value()

        self.canvas.plot(*weights)
        self.canvas.draw()

    def value_change1(self, weights):
        weights[0] = self.obj1_slider.value()
        weights[1] = self.obj2_slider.value()
        weights[2] = self.obj3_slider.value()

        self.canvas1.plot(*weights)
        self.canvas1.draw()

    def tab2_UI(self):
        tab2 = QWidget()
        outer_layout = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()
        top_layout = QFormLayout()
        energy_slider_values = [0, impact_max, impact_min, energy_mean]

        self.successive_diff = QCheckBox("different successive target stimuli", self)
        self.successive_diff.toggle()
        self.successive_diff.setChecked(diff_successive)
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
        self.continuous_energy.setChecked(isEnergy_linear)
        self.continuous_energy.setToolTip('Positive and negative impacts to energy \n '
                                          'will be equal to the maximum value \n'
                                            'at all levels of player energy.')

        self.starting_energy_slider = QSlider(Qt.Horizontal, self)
        self.starting_energy_slider.setValue(energy)
        self.starting_energy_slider.setMinimum(0)
        self.starting_energy_slider.setMaximum(99)
        self.starting_energy_slider.setToolTip("set the user's starting energy level")

        self.starting_energy_value_label = QLineEdit('0', self)
        self.starting_energy_value_label.setMinimumWidth(80)
        self.starting_energy_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.starting_energy_value_label.setText(str(energy))
        starting_energy_validator = QIntValidator(0,100)
        self.starting_energy_value_label.setValidator(starting_energy_validator)

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
        stick_point_validator = QIntValidator(1,99)
        self.stick_point_value_label.setValidator(stick_point_validator)

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
        min_impact_validator = QIntValidator(1,15)
        self.min_impact_value_label.setValidator(min_impact_validator)

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
        max_impact_validator = QIntValidator(5,20)
        self.max_impact_value_label.setValidator(max_impact_validator)

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
        self.tally_theshold_slider.setValue(thresh)

        self.tally_theshold_value_label = QLineEdit('0', self)
        self.tally_theshold_value_label.setMinimumWidth(80)
        self.tally_theshold_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.tally_theshold_value_label.setText(str(thresh))
        tally_theshold_validator = QIntValidator(0,100)
        self.tally_theshold_value_label.setValidator(tally_theshold_validator)

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
        # style sheets


        # value change functions for graphs
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

    def tab4_UI(self):
        tab4 = QWidget()
        outer_layout = QVBoxLayout()
        gridlay = QGridLayout()

        # CheckBox Widgets

        self.feedback_check = QCheckBox(" feedback sounds ", self)
        self.feedback_check.toggle()
        self.feedback_check.setChecked(isFeedback)
        #self.feedback_check.setLayoutDirection()
        self.feedback_check.setToolTip("turn on feedback sound effects (correct or incorrect) \n"
                                       "that play after the user clicks a response object.")


        self.energy_overlay_check = QCheckBox(" low-health vignette overlay  ", self)
        self.energy_overlay_check.toggle()
        self.energy_overlay_check.setChecked(isEnergy_overlay)
        self.energy_overlay_check.setEnabled(False)

        self.label_audio_check = QCheckBox(" play audio for stimulus ", self)
        self.label_audio_check.toggle()
        self.label_audio_check.setChecked(isLabel_audio)
        self.label_audio_check.setToolTip("turn on the audio that reads the label \n"
                                          "of each newly displayed target object.")

        self.energy_animate_check = QCheckBox(" animate energy bar ", self)
        self.energy_animate_check.toggle()
        self.energy_animate_check.setChecked(isAnimate_energy)
        self.energy_animate_check.setEnabled(False)

        self.increase_scroll_check = QCheckBox(" gradually increase scroll speed ", self)
        self.increase_scroll_check.toggle()
        self.increase_scroll_check.setChecked(increase_scroll)
        self.increase_scroll_check.setToolTip("incrementally speed up the scrolling each time \n" 
                                              "the player crosses the threshold for correct \n"
                                              "responses relating to an object.")


        # Feedback delay widgets

        feedback_delay_label = QLabel('feedback delay', self)
        feedback_delay_label.setAlignment(Qt.AlignCenter)
        feedback_delay_label.adjustSize()
        feedback_delay_label.setToolTip("")

        self.feedback_delay_slider = QSlider(Qt.Horizontal, self)
        self.feedback_delay_slider.setMinimum(0)
        self.feedback_delay_slider.setMaximum(100)
        self.feedback_delay_slider.setValue(feedback_delay_value)
        self.feedback_delay_slider.setEnabled(False)
        self.feedback_delay_slider.setToolTip("adjust the length of the delay between the response \n"
                                       "click and the feedback sound effect for that click.")


        self.feedback_delay_v_label = QLineEdit('0', self)
        self.feedback_delay_v_label.setMaximumWidth(30)
        self.feedback_delay_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.feedback_delay_v_label.setText(str(feedback_delay_value))
        self.feedback_delay_v_label.setEnabled(False)

        feedback_delay_validator = QIntValidator(0,100)
        self.feedback_delay_v_label.setValidator(feedback_delay_validator)

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
        self.feedback_random_slider.setValue(feedback_random_value)
        self.feedback_random_slider.setToolTip("set how often the feedback sound effects (correct/incorrect) \n"
                                               "will be swapped around.")

        self.feedback_random_v_label = QLineEdit('0', self)
        self.feedback_random_v_label.setMaximumWidth(30)
        self.feedback_random_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.feedback_random_v_label.setText(str(feedback_random_value))

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
        self.scroll_speed_slider.setValue(scroll_speed_value)
        self.scroll_speed_slider.setToolTip("set the speed of the vertical scrolling in the game.")

        self.scroll_speed_v_label = QLineEdit('0', self)
        self.scroll_speed_v_label.setMaximumWidth(30)
        self.scroll_speed_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.scroll_speed_v_label.setText(str(scroll_speed_value))

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
        self.max_fps_slider.setValue(fps)
        self.max_fps_slider.setToolTip("set the animation frame rate (FPS). A higher \n"
                                       "FPS makes the game run more smoothly but \n"
                                       "requires more computer resources")

        self.max_fps_v_label = QLineEdit('0', self)
        self.max_fps_v_label.setMaximumWidth(30)
        self.max_fps_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.max_fps_v_label.setText(str(fps))

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

    def tab3_UI(self):
        tab3 = QWidget()
        outer_layout = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()

        check_values = output_checkboxes['boolean_value']
        check_variables = output_checkboxes['description']
        self.checkbox_list = QListWidget()
        list_items = list(range(len(output_checkboxes['variable_name'])))
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
        self.mouse_export.setChecked(isMousetrack)
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

    @pyqtSlot()
    def on_click(self, save_file_path, isExit):
        global export_settings_glob
        export_settings_glob = self.setting_export.isChecked()

        for j in range(len(output_checkboxes['variable_name'])):
            if self.checkbox_list.item(j).checkState() == Qt.Checked:
                output_checkboxes.at[j, 'boolean_value'] = True
            else:
                output_checkboxes.at[j, 'boolean_value'] = False



        # save settings to pkl
        word_slider_values[0] = self.wrd1_slider.value()
        word_slider_values[1] = self.wrd2_slider.value()
        word_slider_values[2] = self.wrd3_slider.value()
        word_slider_values[3] = self.wrd4_slider.value()
        word_slider_values[4] = self.wrd5_slider.value()
        word_slider_values[5] = self.wrd6_slider.value()

        object_slider_values[0] = self.obj1_slider.value()
        object_slider_values[1] = self.obj2_slider.value()
        object_slider_values[2] = self.obj3_slider.value()

        bg_matchingness = self.bg_match_slider.value()

        #energy_slider_values: empty, max, min, stick-point
        impact_max = self.max_impact_slider.value()
        impact_min = self.min_impact_slider.value()
        energy_mean = self.stick_point_slider.value()

        scroll_speed_value = self.scroll_speed_slider.value()
        id_name = self.IDtextbox.text()
        energy = self.starting_energy_slider.value()
        starting_vocabulary = self.start_vocab_slider.value()
        thresh = self.tally_theshold_slider.value()
        fps = self.max_fps_slider.value()


        lives = -1
        if int(self.LivesBox.text()) > 0:
            lives = int(self.LivesBox.text())
        load_previous = self.prior_word_set_box.isChecked()
        isMousetrack = self.mouse_export.isChecked()
        rareness = self.rareness_ordering.isChecked()
        isFixed = self.fixed_labels_box.isChecked()
        isEnergy_linear = self.continuous_energy.isChecked()
        diff_successive = self.successive_diff.isChecked()
        feedback_random_value = self.feedback_random_slider.value()
        isFeedback = self.feedback_check.isChecked()

        # Export settings to pkl for main program
        with open(save_file_path, 'wb') as f:
            pickle.dump([word_slider_values,
                         object_slider_values,
                         energy_mean,
                         impact_max,
                         impact_min,
                         output_checkboxes,
                         id_name,
                         lives,
                         starting_vocabulary,
                         bg_matchingness,
                         energy,
                         thresh,
                         isEnergy_linear,
                         load_previous,
                         isMousetrack,
                         rareness,
                         fps,
                         increase_scroll,
                         isFixed,
                         scroll_speed_value,
                         diff_successive,
                         isLabel_audio,
                         feedback_random_value,
                         isFeedback
                         ], f)
        if isExit:
            global exit_application_glob
            exit_application_glob = False
            self.close()


class Canvas(FigureCanvas):
    @pyqtSlot()
    def __init__(self, *weights, parent=None, width=8, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi = dpi, facecolor='#E1E1E1')
        FigureCanvas.__init__(self, fig)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setParent(parent)
        self.plot(*weights)

    def plot(self, *weights):
        self.figure.clear()
        if len(weights) > 1:

            columns = []
            for i in range(len(weights)):
                label = 'v' + str(int(i)+1)
                columns.append(label)

            df = pd.DataFrame([weights], columns=columns)

            word_slider_colours = ["blue", "red", "yellow", "pink", "orange", "green"]
            self.figure.clear()
            self.ax = self.figure.subplots()

            df.plot.barh(stacked=True, ax=self.ax, legend=False, edgecolor='black', color=word_slider_colours)
            self.ax.axis("off")
            #self.ax.margins(x=0, y=0)
            #self.ax.patch.set_facecolor('none')


class PlotCanvas(FigureCanvas):
    @pyqtSlot()
    def __init__(self, *weights, parent = None, width = 5, height = 5, dpi = 100):
        fig = Figure(figsize=(width, height), dpi = dpi, facecolor='#E1E1E1')
        #self.axes = fig.add_subplot(111)
        #self.axes, fig = plt.subplots()
        FigureCanvas.__init__(self, fig)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setParent(parent)
        self.plot(weights)

    def adjust_spines(self, ax, spines):
        for loc, spine in ax.spines.items():
            if loc in spines:
                spine.set_position(('outward', 10))  # outward by 10 points
            else:
                spine.set_color('none')  # don't draw spine

        # turn off ticks where there is no spine
        if 'left' in spines:
            ax.yaxis.set_ticks_position('left')
        else:
            # no yaxis ticks
            ax.yaxis.set_ticks([])

        if 'bottom' in spines:
            ax.xaxis.set_ticks_position('bottom')
        else:
            # no xaxis ticks
            ax.xaxis.set_ticks([])

    def plot(self, *weights):
        self.figure.clear()

        a = impact_max
        b = impact_min
        c = energy_mean/100
        if len(weights) > 1:
            a = int(weights[1])
            b = int(weights[2])
            c = int(weights[3])/100

        # 100 linearly spaced numbers
        x = np.linspace(-2, 2, 100)
        ax = self.figure.add_subplot(1, 1, 1)


        if a >= b:
            if c >= .5:
                y = np.divide(a-b,10) * np.divide(np.exp(2*np.divide(a,b-a) * (np.divide(x,c)-1)) - 1, np.exp(2*np.divide(a,b-a) * (np.divide(x,c)-1)) + 1)
            else:
                y = np.divide(a-b,10) * np.divide(1 - np.exp(2*np.divide(a,b-a)*(np.divide(1-x,1-c)-1)), 1 + np.exp(2*np.divide(a,b-a)*(np.divide(1-x,1-c)-1)))

            #y = -1 * np.divide((a - b), (1 + np.power((2 * b * (a - b)), (-1*x)))) + np.divide((a - b), 2)
            #x = np.divide((np.divide(np.divide(y, (a-b)) - (1 -np.divide((a-b),b)) * (((-1 * (np.divide(c, 1 +np.power(10, x)))) + np.divide((c+1), 2)) * (np.divide(y,(a-b))))),(1- np.divide((a-b), b)*((-1 * (np.divide(c, (1+np.power(10, x)))))+np.divide((c+1), 2)) - 2 * (1-np.divide((a-b), b))*((-1(np.divide(w, 1+np.power(10,x))))+ np.divide((w+1,2)))*np.sqrt(np.power(np.divide(y,(a-b)),2))+1)),(np.divide(c,1 + np.power(10,-x) - np.divide((c+1), 2), 2) +2 -np.divide(3+np.sqrt(np.power(c, 2)),4)))+c

            ax.spines['left'].set_position('center')
            ax.spines['bottom'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            ax.yaxis.set_ticks([])
            ax.xaxis.set_ticks([])
            self.adjust_spines(ax,['left', 'bottom'])
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
            ax.set_xlim([-.5, 1.5])
            ax.set_ylim([-3, 3])
            #ax.axis("off")
            ax.set_xlabel("Player Energy (0 --> 100)")
            ax.set_ylabel("Relative Ability to Gain Energy")
            # plot the function
            ax.plot(x, y)
            #ax.legend(loc='upper left')
        else:
            y = x*0 + np.divide(b,2)
            ax.plot(x, y, label='Minimum must not exceed maximum')
            ax.axis("off")
            ax.legend(loc='center')
            ax.set_xlim([0, 1])
            ax.set_ylim([-20, 20])


# run settings
if not isSurvey:
    while True:
        exit_code = 1
        if __name__ == '__main__':
            app = QApplication(sys.argv)
            window = App()
            window.show()
            exit_code = app.exec_()


        if exit_code == App.EXIT_CODE_REBOOT:
            print('restarting settings window')
            sip.delete(app)
            del app

        else:
            break


        try:
            with open(settings_default_path, 'rb') as f:
                word_slider_values, object_slider_values, energy_mean, impact_max, impact_min, \
                output_checkboxes, id_name, lives, starting_vocabulary, bg_matchingness, energy, \
                thresh, isEnergy_linear, load_previous, isMousetrack, rareness, fps, increase_scroll, isFixed, scroll_speed_value, \
                diff_successive, isLabel_audio, feedback_random_value, isFeedback = pickle.load(f)

            print("saved settings found")
        except IOError:
            print("could not load new settings")

# load current settings after settings window is exited
try:
    with open(settings_default_path, 'rb') as f:
        word_slider_values, object_slider_values, energy_mean, impact_max, impact_min, \
        output_checkboxes, id_name, lives, starting_vocabulary, bg_matchingness, energy, \
        thresh, isEnergy_linear, load_previous, isMousetrack, rareness, fps, increase_scroll, isFixed, scroll_speed_value, \
        diff_successive, isLabel_audio, feedback_random_value, isFeedback = pickle.load(f)

except IOError:
    print("could not load new settings")


#export settings for data survey file
if export_settings_glob:
    pickle_save_settings(survey_settings_path)

#loads settings in survey application
if isSurvey:
    with open(survey_settings_path, 'rb') as f:
        word_slider_values, object_slider_values, energy_mean, impact_max, impact_min, \
        output_checkboxes, id_name, lives, starting_vocabulary, bg_matchingness, energy, \
        thresh, isEnergy_linear, load_previous, isMousetrack, rareness, fps, increase_scroll, isFixed, scroll_speed_value, \
        diff_successive, isLabel_audio, feedback_random_value, isFeedback = pickle.load(f)

    if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = Enter_Name()
        window.show()
        exit_code = app.exec_()

# exits program if 'x' is pressed for settings window
if exit_application_glob:
    sys.exit()

#session commencing times
now = datetime.now()
start_time_date = now.strftime("%Y%m%d-%H%M%S")

# mouse tracking paths
if isMousetrack:
    id_folder = '/' + "id_%s" % id_name
    session_folder = '/' + "session_%s" % str(now.strftime("%Y%m%d-%H%M%S"))
    current_tracking_dir = str(outputs_path) + '/mouse_tracking' + str(id_folder) + str(session_folder)
    correct_path = os.path.join(current_tracking_dir, "correct/")
    incorrect_path = os.path.join(current_tracking_dir, "incorrect/")

    if not os.path.exists(correct_path):
        os.makedirs(correct_path)
        print("directory created at " + correct_path)

    if not os.path.exists(incorrect_path):
        os.makedirs(incorrect_path)
        print("directory created at " + incorrect_path)


#create new dataframe from 'output_checkboxes' data frame, adding 'output_variable' column for csv
output_dataframe = output_checkboxes
sLength = len(output_dataframe['variable_name'])
s1 = []
for i in range(sLength):
   s1.append('N/A')
output_dataframe['output_variable'] = pd.Series(s1, index=output_dataframe.index)


# initialise pygame
pygame.init()

# create game window
WINDOW_SIZE = [800, 600]
game_window = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))

# Game over text
game_over_font = pygame.font.Font(font_location, 70)

# background

background = pygame.image.load(os.path.join(data_path, "grass.png"))
backgroundY = 0

# set game parameters and data dictionary
objectDict = {'ID_numeric':[], 'fixed_name':[], 'filepath':[], 'loadImg':[], 'type_score':[], 'label':[], 'label_complexity':[], 'is_monster':[]}
objects_on_screen = 5
increase_objects_on_screen = False
object_type = []
objectY = []
objectX = []
start_time = []
objectY_change = scroll_speed_value / (fps / 30)
new_start_time = 0
weight_by_complexity = []
score_value = 0

# set repeat stimulus checking variables
target_type_previous = -1
isRepeat = 0

# variable for recording if target image is displayed
isTarget_img = 1

# labels
def labels_shuffle(list1, list2, list3, list4, list5, list6, weights, length):
    #weightslist = random.choices([1,2,3,4,5,6], weights=weights, k=length)
    newlist1 = random.sample(list1, weights[0])
    newlist2 = random.sample(list2, weights[1])
    newlist3 = random.sample(list3, weights[2])
    newlist4 = random.sample(list4, weights[3])
    newlist5 = random.sample(list5, weights[4])
    newlist6 = random.sample(list6, weights[5])
    returnlist = newlist1 + newlist2 + newlist3 + newlist4 + newlist5 + newlist6
    random.shuffle(returnlist)
    return returnlist

def objects_shuffle1(pd_data, categories, object_category_weights, length):
    returnlist = []
    for i in categories:
        shufflelist = pd_data[["animal_ID", "ID_numeric"]].loc[pd_data["is_monster"] == i].values.tolist() #[0:object_category_weights[i]]
        appendlist = random.sample(shufflelist, object_category_weights[i])
        for element in appendlist:
            returnlist.append(element)

    return returnlist

def return_max_sample_size(starting_weights, *args):
    size_list = []
    for arg in args:
        size_list.append(len(arg))


    weight_as_quotient = np.divide(starting_weights, np.sum(starting_weights))
    quotient_size_list = np.divide(size_list, sum(size_list))
    difference = np.subtract(quotient_size_list, weight_as_quotient)
    index_min = np.argmin(difference)
    ideal_size = np.multiply(weight_as_quotient, np.sum(size_list))
    final_count = np.floor(np.multiply(np.divide(np.floor(ideal_size), ideal_size[index_min]), size_list[index_min]))
    return int(np.sum(final_count)), np.floor(final_count).astype('int')

def return_max_sample_size1(starting_weights, size_list): #starts with size list
    sum_weights = []
    for i in range(len(starting_weights)):
        if size_list[i] != 0:
            sum_weights.append(starting_weights[i])
        else:
            sum_weights.append(0)



    weight_as_quotient = np.divide(starting_weights, np.sum(sum_weights)).astype("float32")
    quotient_size_list = np.divide(size_list, sum(size_list)).astype("float32")
    ideal_size = np.multiply(weight_as_quotient, np.sum(size_list))

    difference = np.subtract(quotient_size_list, weight_as_quotient).astype("float32")
    find_min = []

    for i in range(len(difference)):
        if size_list[i] != 0:
            find_min.append(difference[i])
        else:
            find_min.append(10000)


    index_min = np.argmin(find_min)
    final_count = np.floor(np.multiply(np.divide(np.floor(ideal_size), ideal_size[index_min]), np.floor(size_list[index_min])))
    final_count_with_zeros = []

    for i in range(len(final_count)):
        if size_list[i] == 0:
            final_count_with_zeros.append(0)
        else:
            final_count_with_zeros.append(final_count[i])

    return int(np.sum(final_count_with_zeros)), np.floor(final_count_with_zeros).astype('int')

def sort_with_error(list_to_sort, error):
    errorsList = []
    for i in range(len(list_to_sort)):
        item, meanWeight = combined_word_list[i]
        errorsList.append(random.normalvariate(float(meanWeight), float(error)))
    newSorted = list(zip(list_to_sort, errorsList))
    newList = sorted(newSorted, key=lambda l:l[1])
    returnList, junkList = list(zip(*newList))
    return returnList

def write_line_to_csv_array(from_dataframe, df_column_name, to_csv_array, full_csv_array):
    new_line = []
    new_line_full = []
    for i in range(len(from_dataframe)):
        append_element = from_dataframe.at[i, df_column_name]
        new_line_full.append(append_element)
        if from_dataframe.at[i, 'boolean_value']:
            new_line.append(append_element)
    to_csv_array.append(new_line)
    full_csv_array.append(new_line_full)
    return to_csv_array, full_csv_array

saved_state = os.path.join(data_path, "saved_game_states/", str(id_name) + '_' + 'object_label_data.csv')
if load_previous and os.path.exists(saved_state):
    try:
        prev_data = pd.read_csv(saved_state)
        animalDict_range = len(list(prev_data))
        for i in range(animalDict_range):
            objectDict["filepath"].append(prev_data["filepath"][i])
            objectDict['ID_numeric'].append(prev_data["ID_numeric"][i])
            objectDict['fixed_name'].append(prev_data['fixed_name'][i])
            objectImg_path = str(objectDict["filepath"][i])
            objectDict['loadImg'].append(pygame.image.load(objectImg_path))
            objectDict['type_score'].append(0)
            objectDict['is_monster'].append(prev_data['is_monster'][i])
            objectDict['label'].append(prev_data['label'][i])
            objectDict["label_complexity"].append(prev_data['label_complexity'][i])
    except OSError():
        print("Cannot find previous settings, running using defaults")

else:


    # combine word lists and complexity from input data
    labels_cat1 = list(inputData['two_letter_words'][0:inputData['two_letter_words'].count()])
    labels_cat2 = list(inputData['one_syllable_words'][0:inputData['one_syllable_words'].count()])
    labels_cat3 = list(inputData['two_syllable_simple'][0:inputData['two_syllable_simple'].count()])
    labels_cat4 = list(inputData['two_syllable_long'][0:inputData['two_syllable_long'].count()])
    labels_cat5 = list(inputData['three_syllable_words'][0:inputData['three_syllable_words'].count()])
    labels_cat6 = list(inputData['four_plus_syllable_words'][0:inputData['four_plus_syllable_words'].count()])

    for i in range(len(labels_cat1)):
        labels_cat1[i] = labels_cat1[i], 1
    for i in range(len(labels_cat2)):
        labels_cat2[i] = labels_cat2[i], 2
    for i in range(len(labels_cat3)):
        labels_cat3[i] = labels_cat3[i], 3
    for i in range(len(labels_cat4)):
        labels_cat4[i] = labels_cat4[i], 4
    for i in range(len(labels_cat5)):
        labels_cat5[i] = labels_cat5[i], 5
    for i in range(len(labels_cat6)):
        labels_cat6[i] = labels_cat6[i], 6

    ########Set max possible vocabulary size (called animalDict_range) for weighted random ######
    #get max size based on object category
    obj_cat_list = list(inputData['is_monster'])
    obj_cat_uniq = list(set(obj_cat_list))
    obj_check_weights = []
    category_amounts = []

    for i in range(len(object_slider_values)):
        category_amounts.append(obj_cat_list.count(i))
        #obj_check_weights.append(object_slider_values[i])

    #check useful sliders aren't zero
    valid_weights = []
    for i in obj_cat_uniq:
        valid_weights.append(object_slider_values[i])
    if sum(valid_weights) == 0:
        object_slider_values = [1] * 3

    #get max size based on objects
    len_obj_list, rounded_obj_weights = return_max_sample_size1(object_slider_values, category_amounts)




    # get maximum size based on labels
    if sum(word_slider_values) == 0:
        word_slider_values = [1] * 6
    len_label_list, rounded_label_weights = return_max_sample_size(word_slider_values,
                                            labels_cat1, labels_cat2,
                                            labels_cat3, labels_cat4,
                                            labels_cat5, labels_cat6)

    #choose smallest
    if len_obj_list <= len_label_list:
        animalDict_range = len_obj_list
    else:
        animalDict_range = len_label_list

    print("possible objects to learn: " + str(animalDict_range))

    # 1.weights words according to settings, 2. sifts list with simple words at front (with normal error)

    combined_word_list = labels_shuffle(labels_cat1,
                                        labels_cat2,
                                        labels_cat3,
                                        labels_cat4,
                                        labels_cat5,
                                        labels_cat6,
                                        rounded_label_weights, animalDict_range)
    if rareness:
        wordlist_category_weights = sort_with_error(combined_word_list, 2)
    else:
        wordlist_category_weights = sort_with_error(combined_word_list, 100)

    # load animal information to lists from input data
    animal_weighted_list = objects_shuffle1(inputData, obj_cat_uniq, rounded_obj_weights, animalDict_range)  #potential issue with sliders not always refering to equivalent category? Check this
    animal_randomiser = random.sample(range(animalDict_range), animalDict_range) #creates a shuffled list with every integer between a range appearing once

    # create animal dictionary from lists
    for i in animal_randomiser:
        loadName, loadID = animal_weighted_list[i]
        objectImg_path = os.path.join(data_path, "obj_images/", str(loadName) + ".png")
        objectDict["filepath"].append(objectImg_path)
        objectDict['ID_numeric'].append(loadID)
        objectDict['fixed_name'].append(loadName)
        objectDict['loadImg'].append(pygame.image.load(objectImg_path))
        objectDict['type_score'].append(0)
        objectDict['is_monster'].append(inputData['is_monster'][loadID])
        if isFixed:
            objectDict['label'].append(loadName)
            objectDict["label_complexity"].append(1)


    # apply labels to animals in animal dictionary
    if not isFixed:
        for i in range(len(animal_randomiser)):
            label, word_complexity = wordlist_category_weights[i]
            objectDict['label'].append(label)
            objectDict["label_complexity"].append(word_complexity)


if starting_vocabulary <= animalDict_range:
    current_vocab_size = starting_vocabulary - 1
else:
    current_vocab_size = animalDict_range - 1

# assign animal parameters to on screen array

for i in range(objects_on_screen):
    object_type.append(random.randint(0, current_vocab_size))
    objectX.append(1)
    objectY.append(1)
    start_time.append(0)


# draw target animal parameters
# animal_label = []
labelX = 320
labelY = 550

# score
font = pygame.font.Font(font_location, 32)
livesX = 10
livesY = 40

# player energy
energy_counter = 0
energy_counter_interval = 120 # number of frames until energy drops a little
score_linear = False

textX = 10
textY = 10

# target animal
starting_objects = []
for i in range(objects_on_screen):
    starting_objects.append(object_type[i])

target_type = random.choice(starting_objects)
targetX = 720
targetY = 520

 #sound mixer
mixer.init()
mixer.music.set_volume(0.7)
audio_library = os.path.join(data_path, 'audio/')
silence = pygame.mixer.Sound(audio_library + 'silence.wav')
wait = 0.5
delay = wait * fps
scheduler = True

# csv array and header
full_csv = []
csv_output = []
csv_output, full_csv = write_line_to_csv_array(output_dataframe, 'variable_name', csv_output, full_csv)

# mouse coordinate data
mouse_tracking = []
mouse_tracking_header = ["x_pos", "y_pos", "time_stamp"]
mouse_tracking.append(mouse_tracking_header)
mouse_tracking_file_number = 0

epoch_start = time.time()

def game_over_text():
    over_text = game_over_font.render("GAME OVER ", True, (255, 255, 255))
    game_window.blit(over_text, (200, 250))

def isClicked(animalX,animalY, clickX, clickY):
    distance = math.sqrt((math.pow((animalX+32) - clickX, 2)) + (math.pow((animalY+32) - clickY, 2)))
    if distance < 32:
        return True
    else:
        return False

def weighted_type_select(varietyRange, target_number, generate_target):
    weights = list(objectDict["label_complexity"][0:varietyRange])
    population = list(range(varietyRange))
    min_weights = min(weights)
    max_weights = max(weights)
    weights = np.add(weights, -min_weights + 1)
    weights = np.divide(weights, max_weights)
    weights = np.add(1.1, -weights)
    if rareness:
        if diff_successive and generate_target:
            new_type = target_number
            while new_type == target_number:
                new_type_list = random.choices(population=population, weights=weights, k=1)
                new_type = new_type_list[0]
        else:
            new_type_list = random.choices(population=population, weights=weights, k=1)
            new_type = new_type_list[0]
    else:
        if diff_successive and generate_target:
            new_type = target_number
            while new_type == target_number:
                new_type = random.choice(range(0, varietyRange))
        else:
            new_type = random.choice(range(0, varietyRange))
    return new_type

def draw_object_name(x, y, i):
    level = font.render(" name : " + str(objectDict["label"][i]), True, (255, 255, 255))
    game_window.blit(level, (x, y))

def draw_object(x, y, i):
    game_window.blit(objectDict['loadImg'][object_type[i]], (x, y))

def target_object(x, y, i):
    game_window.blit(objectDict['loadImg'][i], (x, y))

def show_score(x,y):
    score = font.render("score : " + str(score_value), True, (255, 255, 255))
    game_window.blit(score, (x, y))

def show_lives(x,y):
    score = font.render("lives : " + str(lives), True, (255, 255, 255))
    game_window.blit(score, (x, y))

def write_csv(csv_array, full_csv_array, timedate):
    output_file_name = str(id_name) + '_' + timedate + "_clicktimes_" + ".csv"
    with open(outputs_path + output_file_name,'w') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(csv_array)
    if isMousetrack:
        output_file_name = str(id_name) + '_' + timedate + "_clicktimes_full" + ".csv"
        with open(current_tracking_dir + '/' + output_file_name, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(full_csv_array)

def write_mouse_epoch(correct, filename, track_arr):

    if correct:
        with open(correct_path + filename, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(track_arr)
    else:
        with open(incorrect_path + filename, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(track_arr)

def save_obj_labels(object_dict):
    csv_file = str(id_name) + '_' + "object_label_data.csv"
    # header = ['ID_numeric','filepath', 'loadImg','type_score', 'label', 'label_complexity', 'is_monster']
    try:
        with open(previous_data_sets_path + csv_file, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(object_dict.keys())
            writer.writerows(zip(*object_dict.values()))

    except IOError:
        print("I/O error")

def draw_background(y):
    game_window.blit(background, (0, y))
    game_window.blit(background, (0, (y - 1200)))

def calculate_energy(energy_level, mean, continuous, max_impact, min_impact):
    if continuous:
        energy_level = energy_level + max_impact
    else:
        if max_impact <= 0 and energy_level >= mean:
            energy_level = energy_level + min_impact + ((max_impact - min_impact) * ((math.sin(((energy_level - mean) * math.pi)/(100 - mean)) / 2) + 1))
        if max_impact > 0 and energy_level < mean:
            energy_level = energy_level + min_impact + ((max_impact - min_impact) * ((math.sin((energy_level * math.pi) / mean) / 2) + 1))
        else:
            energy_level = energy_level + (abs(min_impact) * (max_impact / abs(max_impact)))

    if energy_level >= 100:
        energy_level = 100
    if energy_level <= 0:
        energy_level = 0

    return energy_level

def draw_energy(energy_level):
    if energy_level < 20:
        colour = "red"
    elif energy_level < 40:
        colour = "orange"
    elif energy_level < 60:
        colour = "yellow"
    elif energy_level < 80:
        colour = "green"
    elif energy_level < 100:
        colour = "blue"
    else:
        colour = "purple"

    pygame.draw.rect(game_window, [255,255,255], pygame.Rect(30, WINDOW_SIZE[1] - 230, 60, 210), 4, 10 )
    pygame.draw.rect(game_window, colour, pygame.Rect(35, WINDOW_SIZE[1] - 25 - energy_level*2, 50, energy_level*2), 0, 6)

# x, y positions that dont overlap
def get_new_randXY(range_i):
    x = random.randint(32, 768)
    y = random.randint(-100, 10)
    # check for overlap
    i_int = 0
    while i_int < range_i:
        distance = math.sqrt((math.pow((objectX[i_int] + 32) - (x + 32), 2)) + (math.pow((objectY[i_int] + 32) - (y + 32), 2)))
        if distance < 50:
            x = random.randint(32, 768)
            y = random.randint(-100, 10)
            i_int = 0
        else:
            i_int += 1

    return x, y

def playsounds(audio):
    audio = pygame.mixer.Sound(audio_library + audio)
    audio.play()
    scheduler = False
    return scheduler, wait * fps

def play_feedback_sounds(true_false):
    weights = [100, feedback_random_value]
    isSwap = random.choices(population=[1, -1], weights=weights, k=1)
    chooser = true_false * isSwap[0]
    if chooser == 1:
        audio = pygame.mixer.Sound(audio_library + "feedback/correct.wav")
        isCorrect_sound = 1
    else:
        audio = pygame.mixer.Sound(audio_library + "feedback/incorrect.wav")
        isCorrect_sound = -1
    audio.play()
    return isCorrect_sound


# new array positions that dont overlap
for i in range(objects_on_screen):
    objectX[i], objectY[i] = get_new_randXY(objects_on_screen)

new_start_time  = time.time() #sets stimulus time
last_recorded_click_time = new_start_time
clicked = False
last_output_click = -1
feedback_sound = 0 #zero means no sound played

# Game loop
running = True


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            write_csv(csv_output, full_csv, start_time_date)
            save_obj_labels(objectDict)
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            for i in range(objects_on_screen):
                clicked = isClicked(objectX[i], objectY[i], *pos)
                if clicked:
                    #save states of variables at time of click for output.csv
                    clicked_type = object_type[i]
                    saved_target_type = target_type
                    saved_x = objectX[i]
                    saved_energy = energy
                    clicked_time = time.time()

                    # if correct animal increase score, print to CSV and change target type and respawn animal
                    if object_type[i] == target_type:
                        isCorrect = True
                        energy = calculate_energy(energy, energy_mean, isEnergy_linear, impact_max, impact_min)
                        score_value += 1

                        # respawn clicked object and create new target
                        object_type[i] = weighted_type_select(current_vocab_size, target_type, False)
                        target_type_previous = target_type #note target type before changing
                        target_type = weighted_type_select(current_vocab_size, target_type_previous, True)

                        # record if the target type is the same as the last one
                        if target_type == target_type_previous:
                            isRepeat = 1
                        else:
                            isRepeat = 0


                        #make sure new target is already/soon displayed as falling animal
                        isTarget_displayed = False
                        in_range_objects = [] #empty list appends object types that are in selected range of screen
                        for j in range(objects_on_screen):
                            if objectY[j] >= 0 and objectY[j] <= 300:  # check if displayed in top part (selected range) of screen
                                in_range_objects.append(object_type[j])
                                if object_type[j] == target_type:
                                    isTarget_displayed = True
                                    start_time[i] = new_start_time #all spawning objects carry the date they were created
                        if isTarget_displayed == False:
                            if diff_successive:
                                object_type[i] = target_type #makes replacement for clicked object equal to target type
                            else:
                                target_type = random.choice(in_range_objects) #makes target equal to object on screen (preferred)


                        # location respawn with no overlap coordinates
                        objectX[i], objectY[i] = get_new_randXY(objects_on_screen)
                        # animalY[i] = 0
                        # score for particular type increases
                        objectDict['type_score'][target_type] += 1

                        # check score for level-up (speeds up y change)
                        if score_value % 20 == 0:
                            if increase_scroll:
                                objectY_change += 0.1
                            # makes more animals on screen


                        # check threshold for type for level up
                        if objectDict['type_score'][target_type] == thresh:
                            # increase animal types shown(only if within array size)
                            if current_vocab_size < (animalDict_range - 1):
                                current_vocab_size += 1
                            if objects_on_screen < animalDict_range:
                                increase_objects_on_screen = True

                        scheduler = True #set count down to play stimulus audio after pause
                        if isFeedback:
                            feedback_sound = play_feedback_sounds(1) #play true/false sound and return code for sound played

                    else:

                        lives -= 1
                        energy = calculate_energy(energy, energy_mean, isEnergy_linear, -impact_max, -impact_min) # change energy level
                        isCorrect = False
                        if isFeedback:
                            feedback_sound = play_feedback_sounds(-1)


                    #if start_time[i] != 0:
                    #    # output to CSV
                    if isCorrect or i != last_output_click or last_recorded_click_time - clicked_time > 2: #makes sure there's nothing recorded when player repeatedly clicks the same wrong answer
                        last_output_click = i

                        if isCorrect:
                            letter_append = '_C'
                        else:
                            letter_append = '_I'
                        mouse_coord_file = id_name + '_' + str(mouse_tracking_file_number).zfill(6) + letter_append + ".csv"

                        #save output data to dataframe
                        output_dataframe = output_dataframe.set_index(['variable_name']) #set index to variable name
                        output_dataframe.at['since_stimulus', 'output_variable'] = round(clicked_time - new_start_time, 4)
                        output_dataframe.at['isMatch', 'output_variable'] = int(isCorrect)
                        output_dataframe.at['target_label', 'output_variable'] = str(objectDict["label"][saved_target_type])
                        output_dataframe.at['score_for_target', 'output_variable'] = objectDict["type_score"][saved_target_type]
                        output_dataframe.at['target_word_category', 'output_variable'] = objectDict["label_complexity"][saved_target_type]
                        output_dataframe.at['target_object_category', 'output_variable'] = objectDict["is_monster"][saved_target_type]
                        output_dataframe.at['clicked_label', 'output_variable'] = str(objectDict["label"][clicked_type])
                        output_dataframe.at['score_for_clicked', 'output_variable'] = objectDict["type_score"][clicked_type]
                        output_dataframe.at['clicked_word_category', 'output_variable'] = objectDict["label_complexity"][clicked_type]
                        output_dataframe.at['clicked_object_category', 'output_variable'] = objectDict["is_monster"][clicked_type]
                        output_dataframe.at['isRepeat', 'output_variable'] = isRepeat
                        output_dataframe.at['isDisplayed', 'output_variable'] = isTarget_img
                        output_dataframe.at['x_position', 'output_variable'] = (WINDOW_SIZE[0] / 2 - saved_x)
                        output_dataframe.at['vocab_size', 'output_variable'] = current_vocab_size
                        output_dataframe.at['player_energy', 'output_variable'] = round(saved_energy, 1)
                        output_dataframe.at['click_time', 'output_variable'] = clicked_time
                        output_dataframe.at['since_last_click', 'output_variable'] = last_recorded_click_time - clicked_time
                        output_dataframe.at['user_ID', 'output_variable'] = id_name
                        output_dataframe.at['time_date', 'output_variable'] = start_time_date
                        output_dataframe.at['target_img', 'output_variable'] = objectDict['fixed_name'][target_type]
                        output_dataframe.at['clicked_img', 'output_variable'] = objectDict['fixed_name'][clicked_type]
                        output_dataframe.at['feedback_type', 'output_variable'] = feedback_sound
                        output_dataframe.at['coord_file_name', 'output_variable'] = mouse_coord_file
                        output_dataframe.at['objects_on_screen', 'output_variable'] = objects_on_screen
                        output_dataframe.at['scroll_speed', 'output_variable'] = int(fps * math.floor(objectY_change))
                        output_dataframe = output_dataframe.reset_index() #reset index

                        last_recorded_click_time = clicked_time


                        #write to to csv array
                        csv_output, full_csv = write_line_to_csv_array(output_dataframe, 'output_variable', csv_output, full_csv)


                        if isCorrect:
                            new_start_time = time.time()

                        if isMousetrack:
                            write_mouse_epoch(isCorrect, mouse_coord_file, mouse_tracking)
                        mouse_tracking_file_number = mouse_tracking_file_number + 1
                        mouse_tracking.clear()

                    clicked = False
                    isCorrect = False


                    # resets the time marking presentation of stimulus


    # Background
    backgroundY = backgroundY + objectY_change
    draw_background(backgroundY)
    if backgroundY >= 1200:
        backgroundY = 0

    # draw animals
    for i in range(objects_on_screen):
        draw_object(objectX[i], objectY[i], i)
        objectY[i] += objectY_change
        #animal goes off bottom of screen
        if objectY[i] >= 600:
            object_type[i] = weighted_type_select(current_vocab_size, target_type, False)
            objectX[i], objectY[i] = get_new_randXY(objects_on_screen)
            start_time[i] = 0
        if objectY[i] >= -5 and objectY[i] < 5:
            if object_type[i] == target_type:
                start_time[i] = new_start_time  #all spawning objects carry time of last stimulus?..not sure if useful

        # play audio of name after delay
    sound_file = str(objectDict["label"][target_type] + '.wav')
    if scheduler:
        delay = delay - 1
        if delay <= 0:
            try:
                scheduler, delay = playsounds(sound_file)
            except IOError:
                print('no audio file')
                scheduler = False

    # Game over
    if lives == 0 or energy <= 0:
        for j in range(objects_on_screen):
            objectY[j] = 2000
        game_over_text()
        #break

    # show score
    show_score(textX, textY)
    if lives > 0:
        show_lives(livesX, livesY)

    # draw target animal
    if objectDict['type_score'][target_type] <= thresh:
        target_object(targetX, targetY, target_type)
        isTarget_img = 1
    else:
        isTarget_img = 0
    draw_object_name(labelX, labelY, target_type)

    # draw energy bar
    draw_energy(energy)

    # energy dropping over time
    energy_counter += 1
    if energy_counter >= energy_counter_interval:
        energy = calculate_energy(energy, energy_mean, isEnergy_linear, -3, -1)
        energy_counter = 0

    if increase_objects_on_screen: #only inscrease size of array after updating
        new_x, new_y = get_new_randXY(objects_on_screen)
        new_type = weighted_type_select(current_vocab_size, target_type, False)
        objectX.append(new_x)
        objectY.append(new_y)
        object_type.append(new_type)
        start_time.append(time.time())
        objects_on_screen += 1
        increase_objects_on_screen = False

    # required for screen updating, screen movement etc
    pygame.display.update()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_data_newline = [mouse_x, mouse_y, (time.time() - epoch_start)]
    mouse_tracking.append(mouse_data_newline)
    clock.tick(fps)