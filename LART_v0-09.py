import pygame
import random
import math
import time
import csv
import pickle
import sys
import pandas as pd
import tkinter as tk
from tkinter import *
from tkinter import ttk
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


        self.close()

print(id_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    ex = App()
    window.show()
    app.exec_()






#export settings for data survey file
if export_settings:
    with open(os.path.join(dir_path, 'data/survey_settings.pkl'), 'wb') as f:
        pickle.dump([two_syl_weight,
                     one_syl_weight,
                     two_syl_weight,
                     two_syl_long_weight,
                     three_syl_weight,
                     four_syl_weight,
                     mon_ani_ratio,
                     load_previous,
                     rareness,
                     energy_mean,
                     energy,
                     impact_max,
                     impact_min,
                     Energy_isContinuous,
                     thresh1], f)

if isSurvey:
    with open(os.path.join(dir_path, 'data/survey_settings.pkl'), 'rb') as f:
        two_syl_weight, one_syl_weight, two_syl_weight, two_syl_long_weight, three_syl_weight, \
        four_syl_weight, mon_ani_ratio, load_previous, rareness, energy_mean, energy, impact_max, \
        impact_min, Energy_isContinuous, thresh1 = pickle.load(f)



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
animalDict = {'ID_numeric':[],'filepath':[], 'loadImg':[],'type_score':[], 'label':[], 'label_complexity':[], 'is_monster':[]}
max_animals = 10 #total array size
animals_on_screen = 5
animal_type = []
animalY = []
animalX = []
start_time = []
animalY_change = 1
animal_variety = 2
new_start_time = 0
weight_by_complexity = []

# check for repeated target variables
target_type_old = 0
isRepeat = 0



# variable for recording if target image is displayed
isTarget_img = 1

# animal labels
def weighted_sample(list1, list2, list3, list4, list5, list6, weight1, weight2, weight3, weight4, weight5, weight6, length):
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

def weighted_sample2(list1, list2, weight1, length):
    weight2 = 100 - weight1
    weightslist = random.choices([1,2], weights=(weight1, weight2), k=length)
    newlist1 = random.sample(list1, weightslist.count(1))
    newlist2 = random.sample(list2, weightslist.count(2))
    returnlist = newlist1 + newlist2
    random.shuffle(returnlist)
    return returnlist

def sort_with_error(list_to_sort, error):
    errorsList = []
    for i in range(len(list_to_sort)):
        item, meanWeight = combined_word_list[i]
        errorsList.append(random.normalvariate(float(meanWeight), float(error)))
    newSorted = list(zip(list_to_sort, errorsList))
    newList = sorted(newSorted, key=lambda l:l[1])
    print(newList)
    returnList, junkList = list(zip(*newList))
    return returnList

if load_previous:
    try:
        prev_data = pd.read_csv(os.path.join(dir_path, "data/saved_game_states/", str(id_name) + '_' + 'animal_word_data.csv'))
        for i in range(len(list(prev_data))):
            animalDict["filepath"].append(prev_data["filepath"][i])
            animalDict['ID_numeric'].append(prev_data["ID_numeric"][i])
            animalImg_path = str(animalDict["filepath"][i])
            animalDict['loadImg'].append(pygame.image.load(animalImg_path))
            animalDict['type_score'].append(0)
            animalDict['is_monster'].append(prev_data['is_monster'][i])
            animalDict['label'].append(prev_data['label'][i])
            animalDict["label_complexity"].append(prev_data['label_complexity'][i])
    except OSError():
        print("Cannot find previous settings, running using defaults")

else:
    # combine word lists and complexity from input data
    animalNames1 = list(inputData['two_letter_words'][0:inputData['two_letter_words'].count()])
    animalNames2 = list(inputData['one_syllable_words'][0:inputData['one_syllable_words'].count()])
    animalNames3 = list(inputData['two_syllable_simple'][0:inputData['two_syllable_simple'].count()])
    animalNames4 = list(inputData['two_syllable_long'][0:inputData['two_syllable_long'].count()])
    animalNames5 = list(inputData['three_syllable_words'][0:inputData['three_syllable_words'].count()])
    animalNames6 = list(inputData['four_plus_syllable_words'][0:inputData['four_plus_syllable_words'].count()])

    for i in range(len(animalNames1)):
        animalNames1[i] = animalNames1[i], 1
    for i in range(len(animalNames2)):
        animalNames2[i] = animalNames2[i], 2
    for i in range(len(animalNames3)):
        animalNames3[i] = animalNames3[i], 3
    for i in range(len(animalNames4)):
        animalNames4[i] = animalNames4[i], 4
    for i in range(len(animalNames5)):
        animalNames5[i] = animalNames5[i], 5
    for i in range(len(animalNames6)):
        animalNames6[i] = animalNames6[i], 6

    # 1.weights words according to globals, 2. sifts list with simple words at front (with normal error)
    combined_word_list = weighted_sample(animalNames1,
                                         animalNames2,
                                         animalNames3,
                                         animalNames4,
                                         animalNames5,
                                         animalNames6,
                                         two_letter_weight,
                                         one_syl_weight,
                                         two_syl_weight,
                                         two_syl_long_weight,
                                         three_syl_weight,
                                         four_syl_weight, max_animals)
    if rareness:
        wordlist_complexity_weights = sort_with_error(combined_word_list, 2)
    else:
        random.shuffle(combined_word_list)
        wordlist_complexity_weights = combined_word_list

    # load animal information to lists from input data
    isMonster_count = list(inputData['is_monster'])
    if isMonster_count.count(0) <= isMonster_count.count(1): # maximum list length that will allow for random shuffle
        animalDict_range = isMonster_count.count(0)
    else:
        animalDict_range = isMonster_count.count(1)
    monsters_index_no = isMonster_count.count(1)
    animals_index_no = isMonster_count.count(0)
    earthAnimals_names = inputData['animal_ID'][0:animals_index_no].tolist()
    earthAnimals_numbers = inputData['ID_numeric'][0:animals_index_no].tolist()
    earthAnimals = list(zip(earthAnimals_names, earthAnimals_numbers))
    monsterAnimals_names = inputData['animal_ID'][animals_index_no:monsters_index_no].tolist()
    monsterAnimals_numbers = inputData['ID_numeric'][animals_index_no:monsters_index_no].tolist()
    monsterAnimals = list(zip(monsterAnimals_names, monsterAnimals_numbers))

    animal_weighted_list = weighted_sample2(earthAnimals, monsterAnimals, mon_ani_ratio, animals_index_no)
    animal_randomiser = random.sample(range(animalDict_range), animalDict_range)

    # create animal dictionary from lists
    for i in animal_randomiser:
         loadName, loadID = animal_weighted_list[i]
         animalImg_path = os.path.join(dir_path,"data/animals/", str(loadName) + ".png")
         animalDict["filepath"].append(animalImg_path)
         animalDict['ID_numeric'].append(loadID)
         animalDict['loadImg'].append(pygame.image.load(animalImg_path))
         animalDict['type_score'].append(0)
         animalDict['is_monster'].append(inputData['is_monster'][loadID])

    # apply labels to animals in animal dictionary
    for i in range(len(animal_randomiser)):
        label, word_complexity = wordlist_complexity_weights[i]
        animalDict['label'].append(label)
        animalDict["label_complexity"].append(word_complexity)


print(animalDict)

# assign animal parameters to on screen array

for i in range(max_animals):
    animal_type.append(random.randint(0, animal_variety))
    animalX.append(1)
    animalY.append(1)
    start_time.append(0)


# draw target animal parameters
# animal_label = []
labelX = 320
labelY = 550

# score
font = pygame.font.Font('freesansbold.ttf', 32)
score_value = 0
lives = 20
livesX = 10
livesY = 40

# player energy


energy_counter = 0
energy_counter_interval = 120 # number of frames until energy drops a little
score_linear = False


textX = 10
textY = 10



# target animal
target_type = animal_type[random.randint(0, animals_on_screen)]
targetX = 720
targetY = 520


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
        isNew_animal = False
        while isNew_animal == False:
            random_selector = random.randint(1,varietyRange)
            randomThresh = random.randint(0,6)
            if randomThresh - animalDict["label_complexity"][random_selector] >= 0:
                new_animal_type = random_selector
                isNew_animal = True
        return new_animal_type
    else:
        return random.randint(1, varietyRange)

def animal_name(x,y,i):
    level = font.render("animal name : " + str(animalDict["label"][i]), True, (255, 255, 255))
    game_window.blit(level, (x, y))

def draw_animal(x, y, i):
    game_window.blit(animalDict['loadImg'][animal_type[i]], (x, y))

def target_animal(x, y, i):
    game_window.blit(animalDict['loadImg'][i], (x, y))

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

def write_animalDict(animal_dict):
    print(animal_dict)
    csv_file = str(id_name) + '_' + "animal_word_data.csv"
    # header = ['ID_numeric','filepath', 'loadImg','type_score', 'label', 'label_complexity', 'is_monster']
    try:
        with open("data/saved_game_states/" + csv_file, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(animal_dict.keys())
            writer.writerows(zip(*animal_dict.values()))

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
        distance = math.sqrt((math.pow((animalX[i_int]+32) - (x+32), 2)) + (math.pow((animalY[i_int]+32) - (y+32), 2)))
        if distance < 50:
            x = random.randint(32, 768)
            y = random.randint(-100, 10)
            i_int = 0
        else:
            i_int += 1

    return x, y

# new array positions that dont overlap
for i in range(max_animals):
    animalX[i], animalY[i] = get_new_randXY(max_animals)



# Game loop
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            write_csv(csv_output)
            write_animalDict(animalDict)
            print(csv_output)
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            for i in range(animals_on_screen):
                clicked = isClicked(animalX[i], animalY[i], *pos)
                if clicked:
                    # if correct animal increase score, print to CSV and change target type and respawn animal
                    if animal_type[i] == target_type:

                        energy = calculate_energy(energy, energy_mean, Energy_isContinuous, impact_max, impact_min)

                        # record how long the clicked target had been displayed since target was last established
                        new_start_time = time.time()
                        if start_time[i] != 0:
                            print(time.time() - start_time[i])

                            # output to CSV
                            csv_new_line = [round(time.time() - start_time[i], 4),
                                            str(animalDict["label"][target_type]),
                                            animalDict['type_score'][target_type],
                                            animalDict["label_complexity"][target_type],
                                            isRepeat, isTarget_img,
                                            (WINDOW_SIZE[0]/2 - animalX[i]),
                                            round(energy, 1)]
                            csv_output.append(csv_new_line)

                        score_value +=1
                        animal_type[i] = weighted_type_select(animal_variety)
                        target_type_old = target_type
                        target_type = weighted_type_select(animal_variety)
                        # record if the target type is the same as the last one
                        if target_type == target_type_old:
                            isRepeat = 1
                        else:
                            isRepeat = 0


                        #make sure new target is already/soon displayed as falling animal
                        isTarget_displayed = False
                        for j in range(animals_on_screen):
                            if animal_type[j] == target_type:
                                if animalY[j] >= 0 and animalY[j] <= 300:  # check if displayed in obvious part of screen
                                        isTarget_displayed = True
                                        start_time[i] = new_start_time
                        if isTarget_displayed == False:
                            animal_type[i] = target_type


                        # location respawn with no overlap coordinates
                        animalX[i], animalY[i] = get_new_randXY(animals_on_screen)
                        # animalY[i] = 0
                        # score for particular type increases
                        animalDict['type_score'][target_type] += 1

                        # check score for level-up (speeds up y change)
                        if score_value % 20 == 0:
                            animalY_change += 0.1
                            # makes more animals on screen
                            if animals_on_screen < max_animals:
                                animals_on_screen += 1

                        # check threshold for type for level up
                        if animalDict['type_score'][target_type] == thresh1:
                            # increase animal types shown(only if within array size)
                            if animal_variety < (inputData["animal_ID"].count() - 1):
                                animal_variety += 1

                    else:
                        lives -= 1
                        energy = calculate_energy(energy, energy_mean, Energy_isContinuous, -impact_max, -impact_min) # change energy level

    # Background
    backgroundY = backgroundY + animalY_change
    draw_background(backgroundY)
    if backgroundY >= 1200:
        backgroundY = 0

    # draw animals
    for i in range(animals_on_screen):
        draw_animal(animalX[i], animalY[i], i)
        animalY[i] += animalY_change
        #animal goes off bottom of screen
        if animalY[i] >= 600:
            animal_type[i] = weighted_type_select(animal_variety)
            animalX[i], animalY[i] = get_new_randXY(animals_on_screen)
            start_time[i] = 0
        if animalY[i] >= -5 and animalY[i] < 5:
            if animal_type[i] == target_type:
                start_time[i] = new_start_time

    # Game over
    if lives <= 0 or energy <= 0:
        for j in range(animals_on_screen):
            animalY[j] = 2000
        game_over_text()
        #break

    # show score
    show_score(textX, textY)
    show_lives(livesX, livesY)

    # draw target animal
    if animalDict['type_score'][target_type] < thresh1:
        target_animal(targetX, targetY, target_type)
        isTarget_img = 1
    else:
        isTarget_img = 0
    animal_name(labelX, labelY, target_type)

    # draw energy bar
    draw_energy(energy)

    # energy dropping over time
    energy_counter += 1
    if energy_counter >= energy_counter_interval:
        energy = calculate_energy(energy, energy_mean, Energy_isContinuous, -3, -1)
        energy_counter = 0

    # required for screen updating, screen movement etc
    pygame.display.update()
    clock.tick(60)