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
from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QMainWindow, QWidget, \
    QApplication, QWidget, QPushButton, QLineEdit, QMessageBox, QHBoxLayout, \
    QAction, QTabWidget, QLineEdit, QSlider, QLabel, QCheckBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSlot, Qt



# default settings
two_letter_weight = 0
one_syl_weight = 50
two_syl_weight = 50
two_syl_long_weight = 25
three_syl_weight = 10
four_syl_weight = 5
mon_ani_ratio = 50
load_previous = False
rareness = True

energy_mean = 30
energy = 50
impact_max = 6
impact_min = 1
Energy_isContinuous = False

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


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Settings")
        self.resize(470, 500)
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create the tab widget with two tabs
        tabs = QTabWidget()
        tabs.addTab(self.tab1_UI(), "Labels")
        tabs.addTab(self.tab2_UI(), "Scoring")
        tabs.addTab(self.tab3_UI(), "Export")

        layout.addWidget(tabs)
        hlayout = QHBoxLayout()

        # Create a button in the window
        button = QPushButton('Continue', self)
        button.clicked.connect(self.on_click)
        load_previous = False
        self.setting_export = QCheckBox("   Export these settings\n    for survey application", self)
        self.setting_export.toggle()
        self.setting_export.setChecked(load_previous)

        hlayout.addWidget(self.setting_export)
        hlayout.addWidget(button)
        layout.addLayout(hlayout)

    def tab1_UI(self):

        # define layouts
        tab1 = QWidget()
        outer_layout = QVBoxLayout()
        top_layout = QFormLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox3 = QVBoxLayout()
        hbox2 = QHBoxLayout()
        vbox4 = QVBoxLayout()

        #Default Values
        two_letter_value = two_letter_weight
        one_syl_value = one_syl_weight
        two_syl_value = two_syl_weight
        two_syl_long_value = two_syl_weight
        three_syl_value = three_syl_weight
        four_syl_value = four_syl_weight
        mon_ani_value = mon_ani_ratio

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

        self.two_letter_slider = QSlider(Qt.Horizontal, self)
        self.two_letter_slider.setValue(two_letter_value)
        self.two_letter_slider.setMinimum(0)
        self.two_letter_slider.setMaximum(100)

        two_letter_value_label = QLabel('0', self)
        two_letter_value_label.setMinimumWidth(80)
        two_letter_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        two_letter_value_label.setText(str(two_letter_value))

        two_letter_label = QLabel('Two letter weight', self)
        two_letter_label.setAlignment(Qt.AlignCenter)
        two_letter_label.adjustSize()

        self.one_syl_slider = QSlider(Qt.Horizontal, self)
        self.one_syl_slider.setValue(one_syl_value)
        self.one_syl_slider.setMinimum(0)
        self.one_syl_slider.setMaximum(100)

        one_syl_value_label = QLabel('0', self)
        one_syl_value_label.setMinimumWidth(80)
        one_syl_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        one_syl_value_label.setText(str(one_syl_value))

        one_syl_label = QLabel('One syllable weight', self)
        one_syl_label.setAlignment(Qt.AlignCenter)
        one_syl_label.adjustSize()

        self.two_syl_slider = QSlider(Qt.Horizontal, self)
        self.two_syl_slider.setValue(two_syl_value)
        self.two_syl_slider.setMinimum(0)
        self.two_syl_slider.setMaximum(100)

        two_syl_value_label = QLabel('0', self)
        two_syl_value_label.setMinimumWidth(80)
        two_syl_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        two_syl_value_label.setText(str(two_syl_value))

        two_syl_label = QLabel('Two syllable weight', self)
        two_syl_label.setAlignment(Qt.AlignCenter)
        two_syl_label.adjustSize()

        self.two_syl_long_slider = QSlider(Qt.Horizontal, self)
        self.two_syl_long_slider.setValue(two_syl_long_value)
        self.two_syl_long_slider.setMinimum(0)
        self.two_syl_long_slider.setMaximum(100)

        two_syl_long_value_label = QLabel('0', self)
        two_syl_long_value_label.setMinimumWidth(80)
        two_syl_long_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        two_syl_long_value_label.setText(str(two_syl_long_value))

        two_syl_long_label = QLabel('Two syllable (long) weight', self)
        two_syl_long_label.setAlignment(Qt.AlignCenter)
        two_syl_long_label.adjustSize()

        self.three_syl_slider = QSlider(Qt.Horizontal, self)
        self.three_syl_slider.setValue(three_syl_value)
        self.three_syl_slider.setMinimum(0)
        self.three_syl_slider.setMaximum(100)

        three_syl_value_label = QLabel('0', self)
        three_syl_value_label.setMinimumWidth(80)
        three_syl_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        three_syl_value_label.setText(str(three_syl_value))

        three_syl_label = QLabel('Three syllable weight', self)
        three_syl_label.setAlignment(Qt.AlignCenter)
        three_syl_label.adjustSize()

        self.four_syl_slider = QSlider(Qt.Horizontal, self)
        self.four_syl_slider.setValue(four_syl_value)
        self.four_syl_slider.setMinimum(0)
        self.four_syl_slider.setMaximum(100)

        four_syl_value_label = QLabel('0', self)
        four_syl_value_label.setMinimumWidth(80)
        four_syl_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        four_syl_value_label.setText(str(four_syl_value))

        four_syl_label = QLabel('Four syllable weight', self)
        four_syl_label.setAlignment(Qt.AlignCenter)
        four_syl_label.adjustSize()

        self.mon_ani_slider = QSlider(Qt.Horizontal, self)
        self.mon_ani_slider.setValue(mon_ani_value)
        self.mon_ani_slider.setMinimum(0)
        self.mon_ani_slider.setMaximum(100)

        mon_ani_value_label = QLabel('0', self)
        mon_ani_value_label.setMinimumWidth(80)
        mon_ani_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        mon_ani_value_label.setText(str(mon_ani_value))

        mon_ani_label = QLabel('Animal to monster ratio', self)
        mon_ani_label.setAlignment(Qt.AlignCenter)
        mon_ani_label.adjustSize()
        mon_ani_label.setToolTip("Sets the percentage of earth-animals shown to the player. \n"
                                 "The remaining percentage represents monsters/aliens.")

        # Add widgets to layouts
        top_layout.addRow("User ID:", self.IDtextbox)

        vbox1.addSpacing(15)
        vbox1.addWidget(two_letter_label)
        vbox1.addWidget(self.two_letter_slider)
        vbox1.addWidget(two_letter_value_label)
        vbox1.addSpacing(15)

        vbox1.addWidget(one_syl_label)
        vbox1.addWidget(self.one_syl_slider)
        vbox1.addWidget(one_syl_value_label)
        vbox1.addSpacing(15)

        vbox1.addWidget(two_syl_label)
        vbox1.addWidget(self.two_syl_slider)
        vbox1.addWidget(two_syl_value_label)
        vbox1.addSpacing(15)

        vbox2.addSpacing(15)
        vbox2.addWidget(two_syl_long_label)
        vbox2.addWidget(self.two_syl_long_slider)
        vbox2.addWidget(two_syl_long_value_label)
        vbox2.addSpacing(15)

        vbox2.addWidget(three_syl_label)
        vbox2.addWidget(self.three_syl_slider)
        vbox2.addWidget(three_syl_value_label)
        vbox2.addSpacing(15)

        vbox2.addWidget(four_syl_label)
        vbox2.addWidget(self.four_syl_slider)
        vbox2.addWidget(four_syl_value_label)
        vbox2.addSpacing(15)

        vbox3.addWidget(mon_ani_label)
        vbox3.addWidget(self.mon_ani_slider)
        vbox3.addWidget(mon_ani_value_label)
        vbox3.addSpacing(15)

        vbox4.addWidget(self.rareness_ordering)
        vbox3.addSpacing(15)
        vbox4.addWidget(self.load_creature_bank)

        #functions for slider value changes
        self.two_letter_slider.valueChanged.connect(lambda: two_letter_value_label.setText(str(self.two_letter_slider.value())))
        self.one_syl_slider.valueChanged.connect(
            lambda: one_syl_value_label.setText(str(self.one_syl_slider.value())))
        self.two_syl_slider.valueChanged.connect(
            lambda: two_syl_value_label.setText(str(self.two_syl_slider.value())))
        self.two_syl_long_slider.valueChanged.connect(
            lambda: two_syl_long_value_label.setText(str(self.two_syl_long_slider.value())))
        self.three_syl_slider.valueChanged.connect(
            lambda: three_syl_value_label.setText(str(self.three_syl_slider.value())))
        self.four_syl_slider.valueChanged.connect(
            lambda: four_syl_value_label.setText(str(self.four_syl_slider.value())))
        self.mon_ani_slider.valueChanged.connect(
            lambda: mon_ani_value_label.setText(str(self.mon_ani_slider.value())))

        # nest layouts
        outer_layout.addLayout(top_layout)
        outer_layout.addLayout(hbox1)
        hbox1.addLayout(vbox1)
        hbox1.addLayout(vbox2)
        outer_layout.addLayout(hbox2)
        hbox2.addLayout(vbox3)
        hbox2.addSpacing(30)
        hbox2.addLayout(vbox4)
        tab1.setLayout(outer_layout)
        return tab1

    def tab2_UI(self):
        tab2 = QWidget()
        outer_layout = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()

        starting_energy_value = energy
        stick_point_value = energy_mean
        min_impact_value = impact_min
        max_impact_value = impact_max
        tally_threshold_value = thresh1

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
        self.stick_point_slider.setValue(stick_point_value)
        self.stick_point_slider.setMinimum(0)
        self.stick_point_slider.setMaximum(99)


        stick_point_value_label = QLabel('0', self)
        stick_point_value_label.setMinimumWidth(80)
        stick_point_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        stick_point_value_label.setText(str(stick_point_value))

        stick_point_label = QLabel('Energy stick point', self)
        stick_point_label.setAlignment(Qt.AlignCenter)
        stick_point_label.adjustSize()
        stick_point_label.setToolTip('Negative impact to energy will approach the minimum value \n'
                                           'as player energy decreases below this point, whilst positive  \n'
                                           'impact to energy will decrease to the minimum value as  \n'
                                           'player energy exceeds this point. ')

        self.min_impact_slider = QSlider(Qt.Horizontal, self)
        self.min_impact_slider.setMinimum(0)
        self.min_impact_slider.setMaximum(5)
        self.min_impact_slider.setValue(min_impact_value)


        min_impact_value_label = QLabel('0', self)
        min_impact_value_label.setMinimumWidth(80)
        min_impact_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        min_impact_value_label.setText(str(min_impact_value))

        min_impact_label = QLabel('Minimum energy impact', self)
        min_impact_label.setAlignment(Qt.AlignCenter)
        min_impact_label.adjustSize()

        self.max_impact_slider = QSlider(Qt.Horizontal, self)
        self.max_impact_slider.setMinimum(5)
        self.max_impact_slider.setMaximum(20)
        self.max_impact_slider.setValue(max_impact_value)


        max_impact_value_label = QLabel('0', self)
        max_impact_value_label.setMinimumWidth(80)
        max_impact_value_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        max_impact_value_label.setText(str(max_impact_value))

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

        self.starting_energy_slider.valueChanged.connect(lambda: starting_energy_value_label.setText(str(self.starting_energy_slider.value())))
        self.stick_point_slider.valueChanged.connect(lambda: stick_point_value_label.setText(str(self.stick_point_slider.value())))
        self.min_impact_slider.valueChanged.connect(lambda: min_impact_value_label.setText(str(self.min_impact_slider.value())))
        self.max_impact_slider.valueChanged.connect(lambda: max_impact_value_label.setText(str(self.max_impact_slider.value())))
        self.tally_theshold_slider.valueChanged.connect(lambda: tally_theshold_value_label.setText(str(self.tally_theshold_slider.value())))


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

        vbox3.addSpacing(100)

        outer_layout.addLayout(hbox1)
        hbox1.addLayout(vbox1)
        hbox1.addLayout(vbox2)
        outer_layout.addLayout(vbox3)
        tab2.setLayout(outer_layout)
        return tab2

    def tab3_UI(self):
        tab3 = QWidget()
        outer_layout = QVBoxLayout()
        hbox1 = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()

        isMousetrack = False
        self.mouse_export = QCheckBox("   Export mouse tracking", self)
        self.mouse_export.toggle()
        self.mouse_export.setChecked(isMousetrack)

        hbox1.addWidget(self.mouse_export)

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
        two_letter_weight = self.two_syl_long_slider.value()
        one_syl_weight = self.one_syl_slider.value()
        two_syl_weight = self.two_syl_slider.value()
        two_syl_long_weight = self.two_syl_long_slider.value()
        three_syl_weight = self.three_syl_slider.value()
        four_syl_weight = self.four_syl_slider.value()
        mon_ani_ratio = self.mon_ani_slider.value()
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

print(id_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    ex = App()
    window.show()
    app.exec_()