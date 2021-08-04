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
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# default settings
word_slider_values = [0, 50, 50, 25, 10, 10]

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
        #tabs.setStyleSheet("""background: #E1DFE1""")
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

        #Default Values
        mon_ani_value = mon_ani_ratio

        self.canvas = Canvas(self, *word_slider_values, width=0, height=0)
        self.canvas.setStyleSheet("""QWidget {background-color:   grey}""")
        self.canvas.setMinimumHeight(30)
        self.canvas.setMaximumHeight(40)


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

        hbox_top.addWidget(self.canvas)

        vbox1.addSpacing(15)
        vbox1.addWidget(wrd1_label)
        vbox1.addWidget(self.wrd1_slider)
        vbox1.addWidget(wrd1_v_label)
        vbox1.addSpacing(15)

        vbox1.addWidget(wrd2_label)
        vbox1.addWidget(self.wrd2_slider)
        vbox1.addWidget(wrd2_v_label)
        vbox1.addSpacing(15)

        vbox1.addWidget(wrd3_label)
        vbox1.addWidget(self.wrd3_slider)
        vbox1.addWidget(wrd3_v_label)
        vbox1.addSpacing(15)

        vbox2.addSpacing(15)
        vbox2.addWidget(wrd4_label)
        vbox2.addWidget(self.wrd4_slider)
        vbox2.addWidget(wrd4_v_label)
        vbox2.addSpacing(15)

        vbox2.addWidget(wrd5_label)
        vbox2.addWidget(self.wrd5_slider)
        vbox2.addWidget(wrd5_v_label)
        vbox2.addSpacing(15)

        vbox2.addWidget(wrd6_label)
        vbox2.addWidget(self.wrd6_slider)
        vbox2.addWidget(wrd6_v_label)
        vbox2.addSpacing(15)

        vbox3.addWidget(mon_ani_label)
        vbox3.addWidget(self.mon_ani_slider)
        vbox3.addWidget(mon_ani_value_label)
        vbox3.addSpacing(15)

        vbox4.addWidget(self.rareness_ordering)
        vbox3.addSpacing(15)
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
        self.mon_ani_slider.valueChanged.connect(
            lambda: mon_ani_value_label.setText(str(self.mon_ani_slider.value())))






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

        self.canvas.plot(weights)
        self.canvas.draw()

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
        # style sheets


        # value change functions
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

    def redraw(self, weights):
        self.canvas.plot(weights)

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




class Canvas(FigureCanvas):
    def __init__(self, *weights, parent=None, width=8, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi = dpi, facecolor='#E1E1E1')
        #self.axes = fig.add_subplot(111)
        #fig = plt.subplots()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        self.plot(weights)




    def plot(self, weights):
        self.figure.clear()
        if len(weights) > 1:

            v1 = weights[0]
            v2 = weights[1]
            v3 = weights[2]
            v4 = weights[3]
            v5 = weights[4]
            v6 = weights[5]
            word_slider_colours = ["blue", "red", "yellow", "pink", "orange", "green"]
            self.figure.clear()
            self.ax = self.figure.subplots()
            df = pd.DataFrame({"1": [v1], "2": [v2], "3": [v3], "4": [v4], "5": [v5], "6": [v6]})
            df.plot.barh(stacked=True, ax=self.ax, legend=False, edgecolor='black', color=word_slider_colours)
            self.ax.axis("off")
            self.ax.margins(x=0, y=0)
            self.ax.patch.set_facecolor('none')



print(id_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    ex = App()
    window.show()
    app.exec_()