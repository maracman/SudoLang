import pygame
import random
import math
import time
import csv
import pickle
import pandas as pd
clock = pygame.time.Clock()
import re
from PyQt5 import QtWidgets
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import os

dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])


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
isSurvey = True

id_name = '_'

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Session ID'
        self.left = 10
        self.top = 10
        self.width = 400
        self.height = 140
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

≈

        # Create textbox
        self.textbox = QLineEdit(self)
        self.textbox.move(20, 20)
        self.textbox.resize(280, 40)

        # Create a button in the window
        self.button = QPushButton('Continue', self)
        self.button.move(20, 80)

        # connect button to function on_click
        self.button.clicked.connect(self.on_click)
        self.show()

    @pyqtSlot()
    def on_click(self):
        global id_name
        textboxValue = self.textbox.text()
        id_name = textboxValue
        self.close()

print(id_name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    app.exec_()


#export settings for data survey file
if export_settings:
    with open(os.path.join(dir_path, 'data/survey_settings.pkl'), 'wb') as f:
        pickle.dump([two_syl_weight, one_syl_weight, two_syl_weight, two_syl_long_weight, three_syl_weight, four_syl_weight, mon_ani_ratio, load_previous, rareness, energy_mean, energy, impact_max, impact_min, Energy_isContinuous, thresh1], f)

if isSurvey:
    with open(os.path.join(dir_path, 'data/survey_settings.pkl'), 'rb') as f:
        two_syl_weight, one_syl_weight, two_syl_weight, two_syl_long_weight, three_syl_weight, four_syl_weight, mon_ani_ratio, load_previous, rareness, energy_mean, energy, impact_max, impact_min, Energy_isContinuous, thresh1 = pickle.load(f)



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
    combined_word_list = weighted_sample(animalNames1, animalNames2, animalNames3, animalNames4, animalNames5, animalNames6, two_letter_weight, one_syl_weight, two_syl_weight, two_syl_long_weight, three_syl_weight, four_syl_weight, max_animals)
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
csv_new_line = ["click_time", "animal_type", "score_for_type", "word_complexity", "isRepeat", "isTarget_img", "x_position", "player_energy"]  # column labels for .csv header
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
    output_file_name = os.path.join(dir_path, str(id_name)) + "_clicktimes_" + str(time.strftime("%Y%m%d-%H%M%S")) + ".csv"
    with open(os.path.join(dir_path, 'data/outputs/', output_file_name), 'w') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(csv_array)

def write_animalDict(animal_dict):
    print(animal_dict)
    csv_file = os.path.join(dir_path, str(id_name), '_', "animal_word_data.csv")
    # header = ['ID_numeric','filepath', 'loadImg','type_score', 'label', 'label_complexity', 'is_monster']
    try:
        with open(os.path.join(dir_path, "data/saved_game_states/", csv_file), 'w') as file:
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
                            csv_new_line = [round(time.time() - start_time[i], 4), str(animalDict["label"][target_type]), animalDict['type_score'][target_type], animalDict["label_complexity"][target_type], isRepeat, isTarget_img, (WINDOW_SIZE[0]/2 - animalX[i]), round(energy, 1)]
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