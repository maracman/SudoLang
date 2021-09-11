import pygame
from pygame import mixer

import random
import math
import time
import csv
import pickle
import sys
import pandas as pd
from tkinter import *
clock = pygame.time.Clock()
import numpy as np

import re
import os
import platform
from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QMainWindow, QWidget, \
    QApplication, QWidget, QPushButton, QMessageBox, QHBoxLayout, \
    QAction, QTabWidget, QLineEdit, QSlider, QLabel, QCheckBox, QGridLayout, \
    QListWidget, QListWidgetItem
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import pyqtSlot, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure



# default settings
word_slider_values = [0, 50, 50, 25, 10, 10]
object_slider_values = [50, 50, 50]


output_checkboxes = pd.DataFrame(
    [['click_time', True, "'click_time': Timestamp for click"], ['since_last_click', True, "'since_last_click': Time since last response click "],
     ['since_stimulus', True, "'since_stimulus': Time since last matching response"], ['target_ref', True, "'object_ref': Reference name for target object"],
     ['score_for_clicked', True, "'score_for_clicked': No. of prior matches for target object"], ['response_ref', True, "'response_ref': Reference name for response object"],
     ['word_category', True, "'word_category': Category of the target label"], ['isRepeat', True, "'isRepeat': Was the same target shown for the prior stimulus",],
     ['isTarget_img', True, "'isMatch': Did the response match the target"], ['x_position', True, "'x_position': Horizontal position of the response click "],
     ['player_energy', True, "'player_energy': player's energy at time of response"], ['user_ID', True, "'user_ID': Tag each response with the user_ID"],
     ['isDisplayed', True, "'isDisplayed': is target object image represented as stimulus"], ['clicked_label', True, "clicked_label: The label for the object clicked"],
     ['clicked_object', True, "'clicked_object': The image for the object clicked"],['target_object', True, "'target_object': The image of the target object"],
     ['vocab_size', True, "'vocab_size': size of concurrent vocabulary"], ['time_date', False, "'time_date': time stamp of the start of the session"]],
    columns=pd.Index(['variable_name', 'value', 'label'])
)

# legacy attributes (two_letter, two_syl etc)
two_letter_weight = word_slider_values[0]
one_syl_weight = word_slider_values[1]
two_syl_weight = word_slider_values[2]
two_syl_long_weight = word_slider_values[3]
three_syl_weight = word_slider_values[4]
four_syl_weight = word_slider_values[5]

id_name = '_'

energy = 50

impact_max = 6 #now in energy_slider_values
impact_min = 1  #now in energy_slider_values
energy_mean = 30 #now in energy_slider_values "stick-point"
energy_slider_values = [0, impact_max, impact_min, energy_mean]  # empty, max, min, stick-point

isEnergy_linear = False


mon_ani_ratio = 50
load_previous = False
rareness = True
diff_successive = True
increase_scroll = True
thresh = 10
starting_vocabulary = 3
isSurvey = False
fps = 30
isLabel_audio = True
isEnergy_overlay = False
isAnimate_energy = False
scroll_speed_value = 3
feedback_delay_value = 10
isFeedback = True
feedback_random_value = 0
bg_matchingness = 0
isMousetrack = False
export_settings_glob = False
lives = -1



#Legacy Globals
#load_previous_glob = False
#energy_mean_glob = 30 #now in energy_slider_values "stick-point"
#energy_glob = 50
#impact_max_glob = 6 #now in energy_slider_values
#impact_min_glob = 1  #now in energy_slider_values
#isEnergy_linear_glob = False
#thresh_glob = 10 #Threshold for correct animals clicked at which the image is no longer displayed with the label
#id_name_glob = '_'



operating_system = sys.platform
if operating_system == "darwin":
    dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
else:
    dir_path = os.getcwd()

# PyQt window



class App(QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setWindowTitle("Game Settings")
        self.resize(470, 500)
        # Create a top-level layout


        button_action = QAction("&Your button", self)
        button_action.setStatusTip("This is your button")
        button_action.setCheckable(True)


        self.main_widget = QWidget(self)
        self.layout = QVBoxLayout(self.main_widget)



        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(self.tab1_UI(), "Object Labels")
        tabs.addTab(self.tab2_UI(), "Gameplay")
        tabs.addTab(self.tab4_UI(), "Audio/Display")
        tabs.addTab(self.tab3_UI(), "Outputs")

        self.layout.addWidget(tabs)
        hlayout = QHBoxLayout()

        # Create a button in the window
        button = QPushButton('Continue', self)
        button.clicked.connect(self.on_click)
        load_previous = False
        self.setting_export = QCheckBox("   Export these settings\n    for survey application", self)
        self.setting_export.toggle()
        self.setting_export.setChecked(load_previous)

        open_action = QAction("open settings", self)
        open_action.triggered.connect(self.open_settings)
        save_action = QAction("save settings", self)
        save_action.triggered.connect(self.save_settings)


        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)

        hlayout.addWidget(self.setting_export)
        hlayout.addWidget(button)
        self.layout.addLayout(hlayout)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

    def open_settings(self):
        path = QFileDialog.getOpenFileName(self, 'Open a file', '',
                                        'All Files (*.*)')
        if path != ('', ''):
            print("File path : "+ path[0])

    def save_settings(self):
        name, _ = QFileDialog.getSaveFileName(self, 'Save File')
        if name != '':
            file = open(name,'w')
            text = self.textEdit.toPlainText()
            file.write(text)
            file.close()

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

        self.rareness_ordering = QCheckBox("  creature rareness \n according to label complexity", self)
        self.rareness_ordering.toggle()
        self.rareness_ordering.setChecked(rareness)
        self.rareness_ordering.setToolTip('Creatures that have have been attributed more complex names \n'
                                            'will appear and be chosen as the target less often. \n'
                                            'The player will also be more likely to encounter creatures \n '
                                                'with simpler labels at the start of the game.')

        self.prior_word_set_box = QCheckBox("  load creatures and labels \n  from (user ID's) previous session", self)
        self.prior_word_set_box.toggle()
        self.prior_word_set_box.setChecked(load_previous)
        self.prior_word_set_box.setToolTip("Creatures and their labels will be taken \n"
                                           "from the player's previous game. \n"
                                            'Settings for word weights will be ignored ')

        self.fixed_labels_box = QCheckBox("  use fixed object labels ", self)
        self.fixed_labels_box.toggle()
        self.fixed_labels_box.setChecked(load_previous)
        self.fixed_labels_box.setToolTip(" ")

        self.wrd1_slider = QSlider(Qt.Horizontal, self)
        self.wrd1_slider.setValue(word_slider_values[0])
        self.wrd1_slider.setMinimum(0)
        self.wrd1_slider.setMaximum(100)

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

        self.obj1_slider = QSlider(Qt.Horizontal, self)
        self.obj1_slider.setValue(object_slider_values[0])
        self.obj1_slider.setMinimum(0)
        self.obj1_slider.setMaximum(100)

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

        bg_match_v_label = QLabel('0', self)
        bg_match_v_label.setMinimumWidth(80)
        bg_match_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        bg_match_v_label.setText(str(bg_matchingness))

        bg_match_label = QLabel('object/background \n matchingness', self)
        bg_match_label.setAlignment(Qt.AlignCenter)
        bg_match_label.adjustSize()
        bg_match_label.setToolTip("")

        self.start_vocab_slider = QSlider(Qt.Horizontal, self)
        self.start_vocab_slider.setValue(starting_vocabulary)
        self.start_vocab_slider.setMinimum(2)
        self.start_vocab_slider.setMaximum(10)

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

        self.successive_diff = QCheckBox("always use different successive targets", self)
        self.successive_diff.toggle()
        self.successive_diff.setChecked(diff_successive)

        self.LivesBox = QLineEdit(self)
        self.onlyInt = QIntValidator()
        self.LivesBox.setValidator(self.onlyInt)
        self.LivesBox.setText('0')


        self.canvas3 = PlotCanvas(self, *energy_slider_values, width=0, height=0)
        self.canvas3.setStyleSheet("""QWidget {background-color:   grey}""")
        self.canvas3.setMinimumHeight(80)
        self.canvas3.setMaximumHeight(150)

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

        starting_energy_value_label = QLabel('0', self)
        starting_energy_value_label.setMinimumWidth(80)
        starting_energy_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        starting_energy_value_label.setText(str(energy))

        starting_energy_label = QLabel('Starting energy', self)
        starting_energy_label.setAlignment(Qt.AlignCenter)
        starting_energy_label.adjustSize()

        self.stick_point_slider = QSlider(Qt.Horizontal, self)
        self.stick_point_slider.setValue(energy_slider_values[3])
        self.stick_point_slider.setMinimum(0)
        self.stick_point_slider.setMaximum(99)


        stick_point_value_label = QLabel('0', self)
        stick_point_value_label.setMinimumWidth(80)
        stick_point_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        stick_point_value_label.setText(str(energy_slider_values[3]))

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

        min_impact_value_label = QLabel('0', self)
        min_impact_value_label.setMinimumWidth(80)
        min_impact_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        min_impact_value_label.setText(str(energy_slider_values[2]))

        min_impact_label = QLabel('Minimum energy impact', self)
        min_impact_label.setAlignment(Qt.AlignCenter)
        min_impact_label.adjustSize()

        self.max_impact_slider = QSlider(Qt.Horizontal, self)
        self.max_impact_slider.setMinimum(5)
        self.max_impact_slider.setMaximum(20)
        self.max_impact_slider.setValue(energy_slider_values[1])


        max_impact_value_label = QLabel('0', self)
        max_impact_value_label.setMinimumWidth(80)
        max_impact_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        max_impact_value_label.setText(str(energy_slider_values[1]))

        max_impact_label = QLabel('Maximum energy impact', self)
        max_impact_label.setAlignment(Qt.AlignCenter)
        max_impact_label.adjustSize()

        self.tally_theshold_slider = QSlider(Qt.Horizontal, self)
        self.tally_theshold_slider.setMinimum(0)
        self.tally_theshold_slider.setMaximum(100)
        self.tally_theshold_slider.setValue(thresh)


        tally_theshold_value_label = QLabel('0', self)
        tally_theshold_value_label.setMinimumWidth(80)
        tally_theshold_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        tally_theshold_value_label.setText(str(thresh))

        tally_theshold_label = QLabel('threshold for target image', self)
        tally_theshold_label.setAlignment(Qt.AlignCenter)
        tally_theshold_label.adjustSize()
        tally_theshold_label.setToolTip('when the tally for individual creature types exceed \n '
                                              'this value the target image will not accompany \n'
                                        'the target label for that creature.')
        # style sheets


        # value change functions
        self.starting_energy_slider.valueChanged.connect(lambda: starting_energy_value_label.setText(str(self.starting_energy_slider.value())))
        self.stick_point_slider.valueChanged.connect(lambda: stick_point_value_label.setText(str(energy_slider_values[3])))
        self.stick_point_slider.valueChanged.connect(lambda: self.draw_plot(energy_slider_values))
        self.min_impact_slider.valueChanged.connect(lambda: min_impact_value_label.setText(str(energy_slider_values[2])))
        self.min_impact_slider.valueChanged.connect(lambda: self.draw_plot(energy_slider_values))
        self.max_impact_slider.valueChanged.connect(lambda: max_impact_value_label.setText(str(energy_slider_values[1])))
        self.max_impact_slider.valueChanged.connect(lambda: self.draw_plot(energy_slider_values))
        self.tally_theshold_slider.valueChanged.connect(lambda: tally_theshold_value_label.setText(str(self.tally_theshold_slider.value())))

        top_layout.addRow("Number of Lives:", self.LivesBox)

        outer_layout.addWidget(self.canvas3)

        vbox1.addWidget(starting_energy_label)
        vbox1.addWidget(self.starting_energy_slider)
        vbox1.addWidget(starting_energy_value_label)

        vbox1.addWidget(stick_point_label)
        vbox1.addWidget(self.stick_point_slider)
        vbox1.addWidget(stick_point_value_label)

        vbox2.addWidget(min_impact_label)
        vbox2.addWidget(self.min_impact_slider)
        vbox2.addWidget(min_impact_value_label)

        vbox2.addWidget(max_impact_label)
        vbox2.addWidget(self.max_impact_slider)
        vbox2.addWidget(max_impact_value_label)

        vbox2.addWidget(tally_theshold_label)
        vbox2.addWidget(self.tally_theshold_slider)
        vbox2.addWidget(tally_theshold_value_label)

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

        self.energy_overlay_check = QCheckBox(" low-health vignette overlay  ", self)
        self.energy_overlay_check.toggle()
        self.energy_overlay_check.setChecked(isEnergy_overlay)

        self.label_audio_check = QCheckBox(" play audio for stimulus ", self)
        self.label_audio_check.toggle()
        self.label_audio_check.setChecked(isLabel_audio)

        self.energy_animate_check = QCheckBox(" animate energy bar ", self)
        self.energy_animate_check.toggle()
        self.energy_animate_check.setChecked(isAnimate_energy)

        self.increase_scroll_check = QCheckBox(" gradually increase scroll speed ", self)
        self.increase_scroll_check.toggle()
        self.increase_scroll_check.setChecked(increase_scroll)


        # Feedback delay widgets

        feedback_delay_label = QLabel('feedback delay', self)
        feedback_delay_label.setAlignment(Qt.AlignCenter)
        feedback_delay_label.adjustSize()
        feedback_delay_label.setToolTip("")

        self.feedback_delay_slider = QSlider(Qt.Horizontal, self)
        self.feedback_delay_slider.setMinimum(0)
        self.feedback_delay_slider.setMaximum(100)
        self.feedback_delay_slider.setValue(feedback_delay_value)

        self.feedback_delay_v_label = QLineEdit('0', self)
        self.feedback_delay_v_label.setMaximumWidth(30)
        self.feedback_delay_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.feedback_delay_v_label.setText(str(feedback_delay_value))

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
        feedback_random_label.setToolTip("")

        self.feedback_random_slider = QSlider(Qt.Horizontal, self)
        self.feedback_random_slider.setMinimum(0)
        self.feedback_random_slider.setMaximum(100)
        self.feedback_random_slider.setValue(feedback_random_value)

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
        scroll_speed_label.setToolTip("")

        self.scroll_speed_slider = QSlider(Qt.Horizontal, self)
        self.scroll_speed_slider.setMinimum(0)
        self.scroll_speed_slider.setMaximum(10)
        self.scroll_speed_slider.setValue(scroll_speed_value)

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
        max_fps_label.setToolTip("")

        self.max_fps_slider = QSlider(Qt.Horizontal, self)
        self.max_fps_slider.setMinimum(15)
        self.max_fps_slider.setMaximum(100)
        self.max_fps_slider.setValue(fps)

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

        #vbox1.addWidget(feedback_delay_label)
        #vbox1.addWidget(self.feedback_delay_slider)
        #vbox1.addWidget(self.feedback_delay_v_label)

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

        check_values = output_checkboxes['value']
        check_variables = output_checkboxes['label']
        self.checkbox_list = QListWidget()
        for i in range(len(check_variables)):
            list_item = QListWidgetItem(check_variables[i])
            list_item.setFlags(list_item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            if check_values[i]:
                list_item.setCheckState(Qt.Checked)
            else:
                list_item.setCheckState(Qt.Unchecked)
            self.checkbox_list.addItem(list_item)


        self.checkbox_list.setMaximumHeight(400)


        self.mouse_export = QCheckBox("   Export mouse tracking", self)
        self.mouse_export.toggle()
        self.mouse_export.setChecked(isMousetrack)

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
    def on_click(self):
        global export_settings_glob
        global accepted_glob
        accepted_glob = True
        export_settings_glob = self.setting_export.isChecked()

        global mon_ani_ratio
        mon_ani_ratio = self.obj1_slider.value()

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
            print(lives)
        load_previous = self.prior_word_set_box.isChecked()
        isMousetrack = self.mouse_export.isChecked()
        rareness = self.rareness_ordering.isChecked()
        isFixed = self.prior_word_set_box.isChecked()
        isEnergy_linear = self.continuous_energy.isChecked()


        # Export settings to pkl for main program
        with open(os.path.join(dir_path, 'data/current_settings.pkl'), 'wb') as f:
            pickle.dump([word_slider_values,
                         energy_slider_values,
                         object_slider_values,
                         energy_mean,
                         impact_max,
                         impact_min,
                         output_checkboxes,
                         object_slider_values,
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
                         ], f)

        self.close()


class Canvas(FigureCanvas):
    def __init__(self, *weights, parent=None, width=8, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi = dpi, facecolor='#E1E1E1')
        #self.axes = fig.add_subplot(111)
        #fig = plt.subplots()
        FigureCanvas.__init__(self, fig)
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
    def __init__(self, *weights, parent = None, width = 5, height = 5, dpi = 100):
        fig = Figure(figsize=(width, height), dpi = dpi, facecolor='#E1E1E1')
        #self.axes = fig.add_subplot(111)
        #self.axes, fig = plt.subplots()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        self.plot(weights)

    def plot(self, *weights):
        #print(weights)
        a = 10
        b = 4
        if len(weights) > 1:
            a = int(weights[1])
            b = int(weights[2])
            c = int(weights[3])

        #else:
        #    a = 6
        #    b = 3
        #    c = 50


        self.figure.clear()
        #self.ax = self.figure.subplots()
        #df = pd.DataFrame({"1":[v1],"2": [v2],"3":[v3]})
        #df.plot(kind="barh", stacked=True, ax=self.ax)


        # 100 linearly spaced numbers
        x = np.linspace(-2, 2, 100)
        ax = self.figure.add_subplot(1, 1, 1)
        if a >= b:
            y = -1 * np.divide((a - b), (1 + np.power((2 * b * (a - b)), (-1*x)))) + np.divide((a - b), 2)

            ax.spines['left'].set_position('center')
            ax.spines['bottom'].set_position('zero')
            ax.spines['right'].set_color('none')
            ax.spines['top'].set_color('none')
            ax.xaxis.set_ticks_position('bottom')
            ax.yaxis.set_ticks_position('left')
            ax.set_xlim([-1, 1])
            ax.set_ylim([-20, 20])
            ax.axis("off")
            # plot the function
            ax.plot(x, y)
            #ax.legend(loc='upper left')
        else:
            y = x*0 + np.divide(b,2)
            ax.plot(x, y, label='Minimum must not exceed maximum')
            ax.axis("off")
            ax.legend(loc='center')
            ax.set_xlim([-1, 1])
            ax.set_ylim([-20, 20])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    ex = App()
    window.show()
    app.exec_()

with open(os.path.join(dir_path, 'data/current_settings.pkl'), 'rb') as f:
    word_slider_values, energy_slider_values, object_slider_values, energy_mean, impact_max, impact_min, \
    output_checkboxes, object_slider_values, id_name, lives, starting_vocabulary, bg_matchingness, energy, \
    thresh, isEnergy_linear, load_previous, isMousetrack, rareness, fps, increase_scroll, isFixed, scroll_speed_value = pickle.load(f)

#export settings for data survey file
if export_settings_glob:
    with open(os.path.join(dir_path, 'data/survey_settings.pkl'), 'wb') as f:
        pickle.dump([word_slider_values,
                     fps,
                     energy_slider_values,
                     object_slider_values,
                     energy_mean,
                     impact_max,
                     impact_min,
                     output_checkboxes,
                     object_slider_values,
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
                     increase_scroll,
                     isFixed,
                     scroll_speed_value,
                     ], f)


if isSurvey:
    with open(os.path.join(dir_path, 'data/survey_settings.pkl'), 'rb') as f:
        word_slider_values, energy_slider_values, object_slider_values, energy_mean, impact_max, impact_min, output_checkboxes, \
        object_slider_values, id_name, lives, starting_vocabulary, bg_matchingness, energy, thresh, isEnergy_linear, \
        load_previous, isMousetrack, rareness, increase_scroll, fps, isFixed, scroll_speed_value = pickle.load(
            f)

#quit on 'x' in settings
if 'accepted_glob' in locals():
    running = accepted_glob
else:
    sys.exit()


# load input CSV
inputData = pd.read_csv(os.path.join(dir_path, 'data/game_input_data.csv'))

# initialise pygame
pygame.init()

# create game window
WINDOW_SIZE = [800, 600]
game_window = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))

# Game over text
game_over_font = pygame.font.Font('freesansbold.ttf', 70)

# background

background = pygame.image.load(os.path.join(dir_path, "data/grass.png"))
backgroundY = 0

# animal parameters
objectDict = {'ID_numeric':[], 'filepath':[], 'loadImg':[], 'type_score':[], 'label':[], 'label_complexity':[], 'is_monster':[]}
max_animals = 10 #total array size
objects_on_screen = 5
object_type = []
objectY = []
objectX = []
start_time = []
objectY_change = scroll_speed_value / (fps / 30)
current_vocab_size = starting_vocabulary
new_start_time = 0
weight_by_complexity = []


score_value = 0

# check for repeated target variables
target_type_old = 0
isRepeat = 0

# variable for recording if target image is displayed
isTarget_img = 1

# animal labels
def labels_shuffle(list1, list2, list3, list4, list5, list6, weight1, weight2, weight3, weight4, weight5, weight6, length):
    weightslist = random.choices([1,2,3,4,5,6], weights=(weight1, weight2, weight3, weight4, weight5, weight6), k=length)
    newlist1 = random.sample(list1, weightslist.count(1))
    newlist2 = random.sample(list2, weightslist.count(2))
    newlist3 = random.sample(list3, weightslist.count(3))
    newlist4 = random.sample(list4, weightslist.count(4))
    newlist5 = random.sample(list5, weightslist.count(5))
    newlist6 = random.sample(list6, weightslist.count(6))
    returnlist = newlist1 + newlist2 + newlist3 + newlist4 + newlist5 + newlist6
    random.shuffle(returnlist)
    return returnlist

def objects_shuffle1(pd_data, categories, object_category_weights, length):
    returnlist = []
    weights = []
    for i in categories:
        weights.append(object_category_weights[i])

    weightslist = random.choices(categories, weights=weights, k=length)
    for i in categories:
        shufflelist = pd_data[["animal_ID", "ID_numeric"]].loc[pd_data["is_monster"] == i][0:length].values.tolist()
        appendlist = random.sample(shufflelist, weightslist.count(i))
        for element in appendlist:
            returnlist.append(element)

    return returnlist

#def objects_shuffle(list1, list2, weight1, length):
#    weight2 = 100 - weight1
#    weightslist = random.choices([1,2], weights=(weight1, weight2), k=length)
#    newlist1 = random.sample(list1, weightslist.count(1))
#    newlist2 = random.sample(list2, weightslist.count(2))
#    returnlist = newlist1 + newlist2
#    random.shuffle(returnlist)
#    return returnlist

def sort_with_error(list_to_sort, error):
    errorsList = []
    for i in range(len(list_to_sort)):
        item, meanWeight = combined_word_list[i]
        errorsList.append(random.normalvariate(float(meanWeight), float(error)))
    newSorted = list(zip(list_to_sort, errorsList))
    newList = sorted(newSorted, key=lambda l:l[1])
    returnList, junkList = list(zip(*newList))
    return returnList

if load_previous:
    try:
        prev_data = pd.read_csv(os.path.join(dir_path, "data/saved_game_states/", str(id_name) + '_' + 'object_label_data.csv'))
        for i in range(len(list(prev_data))):
            objectDict["filepath"].append(prev_data["filepath"][i])
            objectDict['ID_numeric'].append(prev_data["ID_numeric"][i])
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

    # 1.weights words according to settings, 2. sifts list with simple words at front (with normal error)
    combined_word_list = labels_shuffle(labels_cat1,
                                        labels_cat2,
                                        labels_cat3,
                                        labels_cat4,
                                        labels_cat5,
                                        labels_cat6,
                                        word_slider_values[0],
                                        word_slider_values[1],
                                        word_slider_values[2],
                                        word_slider_values[3],
                                        word_slider_values[4],
                                        word_slider_values[5], max_animals)
    if rareness:
        wordlist_category_weights = sort_with_error(combined_word_list, 2)
    else:
        random.shuffle(combined_word_list)
        wordlist_category_weights = combined_word_list

    # load animal information to lists from input data
    obj_cat_list = list(inputData['is_monster'])
    obj_cat_uniq = list(set(obj_cat_list))
    obj_cat_num_uniq = len(set(obj_cat_list))
    obj_cat_least_item = min(set(obj_cat_list))
    animalDict_range = obj_cat_list.count(obj_cat_least_item) # maximum list length that will allow for random shuffle



    #isMonster_count = list(inputData['is_monster'])
    #if isMonster_count.count(0) <= isMonster_count.count(1): # maximum list length that will allow for random shuffle
    #    animalDict_range = isMonster_count.count(0)
    #else:
    #    animalDict_range = isMonster_count.count(1)


    #print(type(inputData))

    #monsters_index_no = obj_cat_list.count(1)
    #animals_index_no = obj_cat_list.count(0)
    #earthAnimals_names = inputData['animal_ID'][0:animals_index_no].tolist()
    #earthAnimals_numbers = inputData['ID_numeric'][0:animals_index_no].tolist()
    #earthAnimals = list(zip(earthAnimals_names, earthAnimals_numbers))
    #monsterAnimals_names = inputData['animal_ID'][animals_index_no:monsters_index_no].tolist()
    #monsterAnimals_numbers = inputData['ID_numeric'][animals_index_no:monsters_index_no].tolist()
    #monsterAnimals = list(zip(monsterAnimals_names, monsterAnimals_numbers))

    #animal_weighted_list = objects_shuffle(earthAnimals, monsterAnimals, mon_ani_ratio, animals_index_no)
    animal_weighted_list = objects_shuffle1(inputData, obj_cat_uniq, object_slider_values, animalDict_range)

    animal_randomiser = random.sample(range(animalDict_range), animalDict_range) #creates a shuffled list with every integer between a range appearing once

    # create animal dictionary from lists
    for i in animal_randomiser:
         loadName, loadID = animal_weighted_list[i]
         objectImg_path = os.path.join(dir_path, "data/animals/", str(loadName) + ".png")
         objectDict["filepath"].append(objectImg_path)
         objectDict['ID_numeric'].append(loadID)
         objectDict['loadImg'].append(pygame.image.load(objectImg_path))
         objectDict['type_score'].append(0)
         objectDict['is_monster'].append(inputData['is_monster'][loadID])

    # apply labels to animals in animal dictionary
    for i in range(len(animal_randomiser)):
        label, word_complexity = wordlist_category_weights[i]
        objectDict['label'].append(label)
        objectDict["label_complexity"].append(word_complexity)


print(objectDict)

# assign animal parameters to on screen array

for i in range(max_animals):
    object_type.append(random.randint(0, current_vocab_size))
    objectX.append(1)
    objectY.append(1)
    start_time.append(0)


# draw target animal parameters
# animal_label = []
labelX = 320
labelY = 550

# score
font = pygame.font.Font('freesansbold.ttf', 32)
livesX = 10
livesY = 40

# player energy


energy_counter = 0
energy_counter_interval = 120 # number of frames until energy drops a little
score_linear = False


textX = 10
textY = 10



# target animal
target_type = object_type[random.randint(0, objects_on_screen)]
targetX = 720
targetY = 520

#fps
#fps = 60

 #sound mixer
mixer.init()
mixer.music.set_volume(0.7)
audio_library = 'data/audio/'
silence = pygame.mixer.Sound(audio_library + 'silence.wav')
wait = 0.5
delay = wait * fps
scheduler = True


# csv array and elements
csv_output = []
csv_new_line = ["click_time",
                "animal_type",
                "score_for_type",
                "word_complexity",
                "isRepeat",
                "isTarget_img",
                "x_position",
                "player_energy"]  # column labels for .csv header
csv_output.append(csv_new_line)

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

def weighted_type_select(varietyRange):
    if rareness:
        isNew_object = False
        while isNew_object == False:
            random_selector = random.randint(1,varietyRange)
            randomThresh = random.randint(0,6)
            if randomThresh - objectDict["label_complexity"][random_selector] >= 0:
                new_object = random_selector
                isNew_object = True
        return new_object
    else:
        return random.randint(1, varietyRange)

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

def write_csv(csv_array):
    output_file_name = str(id_name) + "_clicktimes_" + str(time.strftime("%Y%m%d-%H%M%S")) + ".csv"
    with open('data/outputs/' + output_file_name,'w') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(csv_array)

def write_mouse_epoch(correct, username, epoch_number, track_arr):
    filename_number = str(epoch_number)

    if correct:
        letter_append = '_C'
        output_file_name = username + '_' + filename_number.zfill(6) + letter_append + ".csv"
        with open('data/outputs/mouse_coords/correct/' + output_file_name, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(track_arr)
    else:
        letter_append = '_I'
        output_file_name = username + '_' + filename_number.zfill(6) + letter_append + ".csv"
        with open('data/outputs/mouse_coords/incorrect/' + output_file_name, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(track_arr)

def save_obj_labels(object_dict):
    print(object_dict)
    csv_file = str(id_name) + '_' + "object_label_data.csv"
    # header = ['ID_numeric','filepath', 'loadImg','type_score', 'label', 'label_complexity', 'is_monster']
    try:
        with open("data/saved_game_states/" + csv_file, 'w') as file:
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


# new array positions that dont overlap
for i in range(max_animals):
    objectX[i], objectY[i] = get_new_randXY(max_animals)



# Game loop



while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            write_csv(csv_output)
            save_obj_labels(objectDict)
            print(csv_output)
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            for i in range(objects_on_screen):
                clicked = isClicked(objectX[i], objectY[i], *pos)
                if clicked:
                    # if correct animal increase score, print to CSV and change target type and respawn animal
                    if object_type[i] == target_type:
                        isCorrect = True

                        energy = calculate_energy(energy, energy_mean, isEnergy_linear, impact_max, impact_min)

                        # record how long the clicked target had been displayed since target was last established
                        new_start_time = time.time()
                        if start_time[i] != 0:
                            print(time.time() - start_time[i])

                            # output to CSV
                            csv_new_line = [round(time.time() - start_time[i], 4),
                                            str(objectDict["label"][target_type]),
                                            objectDict['type_score'][target_type],
                                            objectDict["label_complexity"][target_type],
                                            isRepeat, isTarget_img,
                                            (WINDOW_SIZE[0] / 2 - objectX[i]),
                                            round(energy, 1)]
                            csv_output.append(csv_new_line)

                        score_value +=1
                        object_type[i] = weighted_type_select(current_vocab_size)
                        target_type_old = target_type
                        target_type = weighted_type_select(current_vocab_size)
                        # record if the target type is the same as the last one
                        if target_type == target_type_old:
                            isRepeat = 1
                        else:
                            isRepeat = 0


                        #make sure new target is already/soon displayed as falling animal
                        isTarget_displayed = False
                        for j in range(objects_on_screen):
                            if object_type[j] == target_type:
                                if objectY[j] >= 0 and objectY[j] <= 300:  # check if displayed in obvious part of screen
                                        isTarget_displayed = True
                                        start_time[i] = new_start_time
                        if isTarget_displayed == False:
                            object_type[i] = target_type


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
                            if objects_on_screen < max_animals:
                                objects_on_screen += 1

                        # check threshold for type for level up
                        if objectDict['type_score'][target_type] == thresh:
                            # increase animal types shown(only if within array size)
                            if current_vocab_size < (inputData["animal_ID"].count() - 1):
                                current_vocab_size += 1

                        scheduler = True

                    else:

                        lives -= 1
                        energy = calculate_energy(energy, energy_mean, isEnergy_linear, -impact_max, -impact_min) # change energy level
                        isCorrect = False

                    if isMousetrack:
                        write_mouse_epoch(isCorrect, id_name, mouse_tracking_file_number, mouse_tracking)
                    mouse_tracking_file_number = mouse_tracking_file_number + 1
                    mouse_tracking.clear()


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
            object_type[i] = weighted_type_select(current_vocab_size)
            objectX[i], objectY[i] = get_new_randXY(objects_on_screen)
            start_time[i] = 0
        if objectY[i] >= -5 and objectY[i] < 5:
            if object_type[i] == target_type:
                start_time[i] = new_start_time

        # play audio of name after delay
    sound_file = str(objectDict["label"][target_type] + '.wav')
    if scheduler:
        delay = delay - 1
        if delay <= 0:
            scheduler, delay = playsounds(sound_file)

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

    # required for screen updating, screen movement etc
    pygame.display.update()
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_data_newline = [mouse_x, mouse_y, (time.time() - epoch_start)]
    mouse_tracking.append(mouse_data_newline)
    clock.tick(fps)