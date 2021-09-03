import pygame

import random
import math
import csv
import sys
import pandas as pd
clock = pygame.time.Clock()
import re
import os
import platform
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtCore import *

    #QVBoxLayout, QFormLayout, QMainWindow, QWidget, \
    #QApplication, QWidget, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, \
    #QAction, QTabWidget, QLineEdit, QSlider, QLabel, QCheckBox, QScrollArea, \
    #QScrollBar, QListWidget

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtGui import *
from PyQt5.QtCore import pyqtSlot, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


# default settings
word_slider_values = [0, 50, 50, 25, 10, 10]
object_slider_values = [50, 50, 50]
energy_slider_values = [0, 10, 4, 50]  # empty, max, min, stick-point
output_checkboxes = pd.DataFrame(
    [['click_time', True, "'click_time': Timestamp for click"], ['elapsed_time', True, "'elapsed_time': Time since last response "],
     ['elapsed_since_correct', True, "'elapsed_since_correct': Time since last matching response"], ['target_ref', True, "'object_ref': Reference name for target object"],
     ['score_for_clicked', True, "'score_for_clicked': No. of prior matches for target object"], ['response_ref', True, "'response_ref': Reference name for response object"],
     ['word_category', True, "'word_category': Category of the target label"], ['isRepeat', True, "'isRepeat': Was the same target shown for the prior stimulus",],
     ['isTarget_img', True, "'isTarget_img': Did the response match the target"], ['x_position', True, "'x_position': Horizontal position of the response click "],
     ['player_energy', True, "'player_energy': Player's energy at time of response"],['user_ID', True, "'user_ID': Tag each response with the user_ID"]],
    columns=pd.Index(['variable_name', 'value', 'label'])
)

bg_matchingness = 0
mon_ani_ratio = 50
load_previous = False
rareness = True
diff_successive = True
isIncrease_scroll = True

max_fps_value = 30
isLabel_audio = True

isEnergy_overlay = False
isAnimate_energy = False
scroll_speed_value = 3

feedback_delay_value = 10
isFeedback = True
feedback_random_value = 0

energy_mean = 30 #now in energy_slider_values "stick-point"
energy = 50
impact_max = 6 #now in energy_slider_values
impact_min = 1  #now in energy_slider_values
Energy_isContinuous = False

starting_vocabulary = 3

#Threshold for correct animals clicked at which the image is no longer displayed with the label
thresh1 = 10

export_settings = False
isSurvey = False

id_name = '_'

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

        self.load_creature_bank = QCheckBox("  load creatures and labels \n  from (user ID's) previous session", self)
        self.load_creature_bank.toggle()
        self.load_creature_bank.setChecked(load_previous)
        self.load_creature_bank.setToolTip("Creatures and their labels will be taken \n"
                                           "from the player's previous game. \n"
                                            'Settings for word weights will be ignored ')

        self.wrd1_slider = QSlider(Qt.Horizontal, self)
        self.wrd1_slider.setValue(word_slider_values[0])
        self.wrd1_slider.setMinimum(0)
        self.wrd1_slider.setMaximum(100)

        wrd1_v_label = QLabel('0', self)
        wrd1_v_label.setMinimumWidth(80)
        wrd1_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        wrd1_v_label.setText(str(word_slider_values[0]))

        wrd1_label = QLabel('Two letter weight', self)
        wrd1_label.setAlignment(Qt.AlignCenter)
        wrd1_label.adjustSize()

        self.wrd2_slider = QSlider(Qt.Horizontal, self)
        self.wrd2_slider.setValue(word_slider_values[1])
        self.wrd2_slider.setMinimum(0)
        self.wrd2_slider.setMaximum(100)

        wrd2_v_label = QLabel('0', self)
        wrd2_v_label.setMinimumWidth(80)
        wrd2_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        wrd2_v_label.setText(str(word_slider_values[1]))

        wrd2_label = QLabel('One syllable weight', self)
        wrd2_label.setAlignment(Qt.AlignCenter)
        wrd2_label.adjustSize()

        self.wrd3_slider = QSlider(Qt.Horizontal, self)
        self.wrd3_slider.setValue(word_slider_values[2])
        self.wrd3_slider.setMinimum(0)
        self.wrd3_slider.setMaximum(100)

        wrd3_v_label = QLabel('0', self)
        wrd3_v_label.setMinimumWidth(80)
        wrd3_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        wrd3_v_label.setText(str(word_slider_values[2]))

        wrd3_label = QLabel('Two syllable weight', self)
        wrd3_label.setAlignment(Qt.AlignCenter)
        wrd3_label.adjustSize()

        self.wrd4_slider = QSlider(Qt.Horizontal, self)
        self.wrd4_slider.setValue(word_slider_values[3])
        self.wrd4_slider.setMinimum(0)
        self.wrd4_slider.setMaximum(100)

        wrd4_v_label = QLabel('0', self)
        wrd4_v_label.setMinimumWidth(80)
        wrd4_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        wrd4_v_label.setText(str(word_slider_values[3]))

        wrd4_label = QLabel('Two syllable (long) weight', self)
        wrd4_label.setAlignment(Qt.AlignCenter)
        wrd4_label.adjustSize()

        self.wrd5_slider = QSlider(Qt.Horizontal, self)
        self.wrd5_slider.setValue(word_slider_values[4])
        self.wrd5_slider.setMinimum(0)
        self.wrd5_slider.setMaximum(100)

        wrd5_v_label = QLabel('0', self)
        wrd5_v_label.setMinimumWidth(80)
        wrd5_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        wrd5_v_label.setText(str(word_slider_values[4]))

        wrd5_label = QLabel('Three syllable weight', self)
        wrd5_label.setAlignment(Qt.AlignCenter)
        wrd5_label.adjustSize()

        self.wrd6_slider = QSlider(Qt.Horizontal, self)
        self.wrd6_slider.setValue(word_slider_values[5])
        self.wrd6_slider.setMinimum(0)
        self.wrd6_slider.setMaximum(100)

        wrd6_v_label = QLabel('0', self)
        wrd6_v_label.setMinimumWidth(80)
        wrd6_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        wrd6_v_label.setText(str(word_slider_values[5]))

        wrd6_label = QLabel('Four syllable weight', self)
        wrd6_label.setAlignment(Qt.AlignCenter)
        wrd6_label.adjustSize()

        self.obj1_slider = QSlider(Qt.Horizontal, self)
        self.obj1_slider.setValue(object_slider_values[0])
        self.obj1_slider.setMinimum(0)
        self.obj1_slider.setMaximum(100)

        obj1_v_label = QLabel('0', self)
        obj1_v_label.setMinimumWidth(80)
        obj1_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        obj1_v_label.setText(str(object_slider_values[0]))

        obj1_label = QLabel('Object Category One', self)
        obj1_label.setAlignment(Qt.AlignCenter)
        obj1_label.adjustSize()
        obj1_label.setToolTip("")

        self.obj2_slider = QSlider(Qt.Horizontal, self)
        self.obj2_slider.setValue(object_slider_values[1])
        self.obj2_slider.setMinimum(0)
        self.obj2_slider.setMaximum(100)

        obj2_v_label = QLabel('0', self)
        obj2_v_label.setMinimumWidth(80)
        obj2_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        obj2_v_label.setText(str(object_slider_values[1]))

        obj2_label = QLabel('Object Category Two', self)
        obj2_label.setAlignment(Qt.AlignCenter)
        obj2_label.adjustSize()
        obj2_label.setToolTip("")

        self.obj3_slider = QSlider(Qt.Horizontal, self)
        self.obj3_slider.setValue(object_slider_values[2])
        self.obj3_slider.setMinimum(0)
        self.obj3_slider.setMaximum(100)

        obj3_v_label = QLabel('0', self)
        obj3_v_label.setMinimumWidth(80)
        obj3_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        obj3_v_label.setText(str(object_slider_values[2]))

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
        vbox1.addWidget(wrd1_v_label)
        vbox1.addSpacing(10)

        vbox1.addWidget(wrd2_label)
        vbox1.addWidget(self.wrd2_slider)
        vbox1.addWidget(wrd2_v_label)
        vbox1.addSpacing(10)

        vbox1.addWidget(wrd3_label)
        vbox1.addWidget(self.wrd3_slider)
        vbox1.addWidget(wrd3_v_label)
        vbox1.addSpacing(15)

        vbox2.addSpacing(15)
        vbox2.addWidget(wrd4_label)
        vbox2.addWidget(self.wrd4_slider)
        vbox2.addWidget(wrd4_v_label)
        vbox2.addSpacing(10)

        vbox2.addWidget(wrd5_label)
        vbox2.addWidget(self.wrd5_slider)
        vbox2.addWidget(wrd5_v_label)
        vbox2.addSpacing(10)

        vbox2.addWidget(wrd6_label)
        vbox2.addWidget(self.wrd6_slider)
        vbox2.addWidget(wrd6_v_label)
        vbox2.addSpacing(15)

        vbox3.addWidget(self.canvas1)

        vbox3.addWidget(obj1_label)
        vbox3.addWidget(self.obj1_slider)
        vbox3.addWidget(obj1_v_label)
        vbox3.addSpacing(15)

        vbox3.addWidget(obj2_label)
        vbox3.addWidget(self.obj2_slider)
        vbox3.addWidget(obj2_v_label)
        vbox3.addSpacing(15)

        vbox3.addWidget(obj3_label)
        vbox3.addWidget(self.obj3_slider)
        vbox3.addWidget(obj3_v_label)
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

        vbox4.addWidget(self.rareness_ordering)
        vbox4.addSpacing(15)
        vbox4.addWidget(self.load_creature_bank)

        # Set Style Sheets
        #self.wrd1_slider.setStyleSheet("""QSlider::handle:horizontal { background: blue; border-radius: 10px; }""")
        #tab1.setStyleSheet()

        #functions for slider value changes
        self.wrd1_slider.valueChanged.connect(lambda: wrd1_v_label.setText(str(word_slider_values[0])))
        self.wrd1_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))
        self.wrd2_slider.valueChanged.connect(
            lambda: wrd2_v_label.setText(str(word_slider_values[1])))
        self.wrd2_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))
        self.wrd3_slider.valueChanged.connect(
            lambda: wrd3_v_label.setText(str(word_slider_values[2])))
        self.wrd3_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))
        self.wrd4_slider.valueChanged.connect(
            lambda: wrd4_v_label.setText(str(word_slider_values[3])))
        self.wrd4_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))
        self.wrd5_slider.valueChanged.connect(
            lambda: wrd5_v_label.setText(str(word_slider_values[4])))
        self.wrd5_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))
        self.wrd6_slider.valueChanged.connect(
            lambda: wrd6_v_label.setText(str(word_slider_values[5])))
        self.wrd6_slider.valueChanged.connect(lambda: self.value_change(word_slider_values))

        self.obj1_slider.valueChanged.connect(
            lambda: obj1_v_label.setText(str(object_slider_values[0])))
        self.obj1_slider.valueChanged.connect(lambda: self.value_change1(object_slider_values))
        self.obj2_slider.valueChanged.connect(
            lambda: obj2_v_label.setText(str(object_slider_values[1])))
        self.obj2_slider.valueChanged.connect(lambda: self.value_change1(object_slider_values))
        self.obj3_slider.valueChanged.connect(
            lambda: obj3_v_label.setText(str(object_slider_values[2])))
        self.obj3_slider.valueChanged.connect(lambda: self.value_change1(object_slider_values))

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

        starting_energy_value = energy
        tally_threshold_value = thresh1

        self.successive_diff = QCheckBox("always use different successive targets", self)
        self.successive_diff.toggle()
        self.successive_diff.setChecked(diff_successive)

        self.LivesBox = QLineEdit(self)
        self.onlyInt = QIntValidator()
        self.LivesBox.setValidator(self.onlyInt)

        self.canvas3 = PlotCanvas(self, *energy_slider_values, width=0, height=0)
        self.canvas3.setStyleSheet("""QWidget {background-color:   grey}""")
        self.canvas3.setMinimumHeight(80)
        self.canvas3.setMaximumHeight(150)

        self.continuous_energy = QCheckBox(" linear energy impact ", self)
        self.continuous_energy.toggle()
        self.continuous_energy.setChecked(Energy_isContinuous)
        self.continuous_energy.setToolTip('Positive and negative impacts to energy \n '
                                          'will be equal to the maximum value \n'
                                            'at all levels of player energy.')

        self.starting_energy_slider = QSlider(Qt.Horizontal, self)
        self.starting_energy_slider.setValue(starting_energy_value)
        self.starting_energy_slider.setMinimum(0)
        self.starting_energy_slider.setMaximum(99)

        starting_energy_value_label = QLabel('0', self)
        starting_energy_value_label.setMinimumWidth(80)
        starting_energy_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        starting_energy_value_label.setText(str(starting_energy_value))

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
        self.tally_theshold_slider.setValue(tally_threshold_value)


        tally_theshold_value_label = QLabel('0', self)
        tally_theshold_value_label.setMinimumWidth(80)
        tally_theshold_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        tally_theshold_value_label.setText(str(tally_threshold_value))

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
        self.increase_scroll_check.setChecked(isIncrease_scroll)


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
        self.max_fps_slider.setMinimum(20)
        self.max_fps_slider.setMaximum(100)
        self.max_fps_slider.setValue(max_fps_value)

        self.max_fps_v_label = QLineEdit('0', self)
        self.max_fps_v_label.setMaximumWidth(30)
        self.max_fps_v_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.max_fps_v_label.setText(str(max_fps_value))

        self.max_fps_v_label.returnPressed.connect(
            lambda: self.max_fps_slider.setValue(int(self.max_fps_v_label.text())))
        self.max_fps_slider.valueChanged.connect(
            lambda: self.max_fps_v_label.setText(str(self.max_fps_slider.value())))


        gridlay.addWidget(self.feedback_check, 0, 1, 1, 3)

        gridlay.addWidget(feedback_delay_label, 1, 0, 2, 1)
        gridlay.addWidget(self.feedback_delay_v_label, 1, 1, 2, 2)
        gridlay.addWidget(self.feedback_delay_slider, 1, 2, 2, 3)

        gridlay.addWidget(feedback_random_label, 2, 0, 3, 1)
        gridlay.addWidget(self.feedback_random_v_label, 2, 1, 3, 2)
        gridlay.addWidget(self.feedback_random_slider, 2, 2, 3, 3)

        gridlay.addWidget(scroll_speed_label, 3, 0, 4, 1)
        gridlay.addWidget(self.scroll_speed_v_label, 3, 1, 4, 2)
        gridlay.addWidget(self.scroll_speed_slider, 3, 2, 4, 3)

        gridlay.addWidget(max_fps_label, 4, 0, 5, 1)
        gridlay.addWidget(self.max_fps_v_label, 4, 1, 5, 2)
        gridlay.addWidget(self.max_fps_slider, 4, 2, 5, 3)

        gridlay.addWidget(self.energy_overlay_check, 5, 1, 6, 3)
        gridlay.addWidget(self.label_audio_check, 6, 1, 7, 3)
        gridlay.addWidget(self.energy_animate_check, 7, 1, 8, 3)
        gridlay.addWidget(self.increase_scroll_check, 8, 1, 9, 3)

        #vbox1.addWidget(feedback_delay_label)
        #vbox1.addWidget(self.feedback_delay_slider)
        #vbox1.addWidget(self.feedback_delay_v_label)


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

        isMousetrack = False
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
        global two_letter_weight
        global one_syl_weight
        global two_syl_weight
        global two_syl_long_weight
        global three_syl_weight
        global four_syl_weight
        global mon_ani_ratio
        global rareness
        global load_previous
        global id_name
        global energy_mean
        global energy
        global impact_min
        global impact_max
        global Energy_isContinuous
        global thresh1
        global export_settings
        global isMousetrack_glob
        global accepted_glob
        accepted_glob = True
        two_letter_weight = self.wrd4_slider.value()
        one_syl_weight = self.wrd2_slider.value()
        two_syl_weight = self.wrd3_slider.value()
        two_syl_long_weight = self.wrd4_slider.value()
        three_syl_weight = self.wrd5_slider.value()
        four_syl_weight = self.wrd6_slider.value()
        mon_ani_ratio = self.obj1_slider.value()
        rareness = self.rareness_ordering.isChecked()
        id_name = self.IDtextbox.text()

        energy = self.starting_energy_slider.value()
        impact_min = self.min_impact_slider.value()
        impact_max = self.max_impact_slider.value()
        thresh1 = self.tally_theshold_slider.value()
        Energy_isContinuous = self.continuous_energy.isChecked()

        load_previous = self.load_creature_bank.isChecked()
        export_settings = self.setting_export.isChecked()
        isMousetrack_glob = self.mouse_export.isChecked()


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
            y = -1 * np.divide((a - b),( 1 + np.power((2 * b * (a - b)),(-1*x)))) + np.divide((a - b), 2)

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









print(id_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    ex = App()
    window.show()
    app.exec_()