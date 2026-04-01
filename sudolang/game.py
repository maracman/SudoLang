import pygame
from pygame import mixer

import random
import math
import time
import csv
import os
import numpy as np
import pandas as pd
from datetime import datetime

from sudolang.config import (
    data_path, outputs_path, previous_data_sets_path,
    font_location, inputData,
)


# ---------------------------------------------------------------------------
# Sampling / shuffling helpers
# ---------------------------------------------------------------------------

def labels_shuffle(list1, list2, list3, list4, list5, list6, weights, length):
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
        shufflelist = pd_data[["animal_ID", "ID_numeric"]].loc[pd_data["is_monster"] == i].values.tolist()
        appendlist = random.sample(shufflelist, object_category_weights[i])
        for element in appendlist:
            returnlist.append(element)
    return returnlist


def return_max_sample_size(starting_weights, *args):
    size_list = [len(arg) for arg in args]
    weight_as_quotient = np.divide(starting_weights, np.sum(starting_weights))
    quotient_size_list = np.divide(size_list, sum(size_list))
    difference = np.subtract(quotient_size_list, weight_as_quotient)
    index_min = np.argmin(difference)
    ideal_size = np.multiply(weight_as_quotient, np.sum(size_list))
    final_count = np.floor(np.multiply(np.divide(np.floor(ideal_size), ideal_size[index_min]), size_list[index_min]))
    return int(np.sum(final_count)), np.floor(final_count).astype('int')


def return_max_sample_size1(starting_weights, size_list):
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


def sort_with_error(list_to_sort, combined_word_list, error):
    errorsList = []
    for i in range(len(list_to_sort)):
        item, meanWeight = combined_word_list[i]
        errorsList.append(random.normalvariate(float(meanWeight), float(error)))
    newSorted = list(zip(list_to_sort, errorsList))
    newList = sorted(newSorted, key=lambda l: l[1])
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


# ---------------------------------------------------------------------------
# Main game runner
# ---------------------------------------------------------------------------

def run_game(settings):
    """Run the SudoLang game with the given settings."""
    s = settings

    # Session timestamps
    now = datetime.now()
    start_time_date = now.strftime("%Y%m%d-%H%M%S")

    # Mouse tracking paths
    correct_path = None
    incorrect_path = None
    current_tracking_dir = None
    if s.isMousetrack:
        id_folder = '/' + "id_%s" % s.id_name
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

    # Create output dataframe from settings
    output_dataframe = s.output_checkboxes.copy()
    sLength = len(output_dataframe['variable_name'])
    output_dataframe['output_variable'] = pd.Series(['N/A'] * sLength, index=output_dataframe.index)

    # Initialise pygame
    pygame.init()
    clock = pygame.time.Clock()

    WINDOW_SIZE = [800, 600]
    game_window = pygame.display.set_mode((WINDOW_SIZE[0], WINDOW_SIZE[1]))

    game_over_font = pygame.font.Font(font_location, 70)
    font = pygame.font.Font(font_location, 32)

    background = pygame.image.load(os.path.join(data_path, "grass.png"))
    backgroundY = 0

    # Game state
    objectDict = {'ID_numeric': [], 'fixed_name': [], 'filepath': [], 'loadImg': [],
                  'type_score': [], 'label': [], 'label_complexity': [], 'is_monster': []}
    objects_on_screen = 5
    increase_objects_on_screen = False
    object_type = []
    objectY = []
    objectX = []
    start_time = []
    objectY_change = s.scroll_speed_value / (s.fps / 30)
    new_start_time = 0
    score_value = 0

    target_type_previous = -1
    isRepeat = 0
    isTarget_img = 1

    # ---------------------------------------------------------------
    # Build object dictionary (load previous or generate new)
    # ---------------------------------------------------------------
    saved_state = os.path.join(data_path, "saved_game_states/", str(s.id_name) + '_' + 'object_label_data.csv')
    if s.load_previous and os.path.exists(saved_state):
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
        # Combine word lists and complexity from input data
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

        # Set max possible vocabulary size
        obj_cat_list = list(inputData['is_monster'])
        obj_cat_uniq = list(set(obj_cat_list))
        category_amounts = []

        for i in range(len(s.object_slider_values)):
            category_amounts.append(obj_cat_list.count(i))

        valid_weights = [s.object_slider_values[i] for i in obj_cat_uniq]
        if sum(valid_weights) == 0:
            s.object_slider_values = [1] * 3

        len_obj_list, rounded_obj_weights = return_max_sample_size1(s.object_slider_values, category_amounts)

        if sum(s.word_slider_values) == 0:
            s.word_slider_values = [1] * 6
        len_label_list, rounded_label_weights = return_max_sample_size(
            s.word_slider_values,
            labels_cat1, labels_cat2, labels_cat3,
            labels_cat4, labels_cat5, labels_cat6)

        if len_obj_list <= len_label_list:
            animalDict_range = len_obj_list
        else:
            animalDict_range = len_label_list

        print("possible objects to learn: " + str(animalDict_range))

        combined_word_list = labels_shuffle(
            labels_cat1, labels_cat2, labels_cat3,
            labels_cat4, labels_cat5, labels_cat6,
            rounded_label_weights, animalDict_range)

        if s.rareness:
            wordlist_category_weights = sort_with_error(combined_word_list, combined_word_list, 2)
        else:
            wordlist_category_weights = sort_with_error(combined_word_list, combined_word_list, 100)

        animal_weighted_list = objects_shuffle1(inputData, obj_cat_uniq, rounded_obj_weights, animalDict_range)
        animal_randomiser = random.sample(range(animalDict_range), animalDict_range)

        for i in animal_randomiser:
            loadName, loadID = animal_weighted_list[i]
            objectImg_path = os.path.join(data_path, "obj_images/", str(loadName) + ".png")
            objectDict["filepath"].append(objectImg_path)
            objectDict['ID_numeric'].append(loadID)
            objectDict['fixed_name'].append(loadName)
            objectDict['loadImg'].append(pygame.image.load(objectImg_path))
            objectDict['type_score'].append(0)
            objectDict['is_monster'].append(inputData['is_monster'][loadID])
            if s.isFixed:
                objectDict['label'].append(loadName)
                objectDict["label_complexity"].append(1)

        if not s.isFixed:
            for i in range(len(animal_randomiser)):
                label, word_complexity = wordlist_category_weights[i]
                objectDict['label'].append(label)
                objectDict["label_complexity"].append(word_complexity)

    if s.starting_vocabulary <= animalDict_range:
        current_vocab_size = s.starting_vocabulary - 1
    else:
        current_vocab_size = animalDict_range - 1

    for i in range(objects_on_screen):
        object_type.append(random.randint(0, current_vocab_size))
        objectX.append(1)
        objectY.append(1)
        start_time.append(0)

    # Target and score display
    labelX = 320
    labelY = 550
    livesX = 10
    livesY = 40
    textX = 10
    textY = 10
    targetX = 720
    targetY = 520

    energy_counter = 0
    energy_counter_interval = 120

    starting_objects = [object_type[i] for i in range(objects_on_screen)]
    target_type = random.choice(starting_objects)

    # Sound mixer
    mixer.init()
    mixer.music.set_volume(0.7)
    audio_library = os.path.join(data_path, 'audio/')
    silence = pygame.mixer.Sound(audio_library + 'silence.wav')
    wait = 0.5
    delay = wait * s.fps
    scheduler = True

    # CSV output
    full_csv = []
    csv_output = []
    csv_output, full_csv = write_line_to_csv_array(output_dataframe, 'variable_name', csv_output, full_csv)

    # Mouse coordinate data
    mouse_tracking = []
    mouse_tracking_header = ["x_pos", "y_pos", "time_stamp"]
    mouse_tracking.append(mouse_tracking_header)
    mouse_tracking_file_number = 0
    epoch_start = time.time()

    # ---------------------------------------------------------------
    # Local helper functions (closures over game state)
    # ---------------------------------------------------------------

    def game_over_text():
        over_text = game_over_font.render("GAME OVER ", True, (255, 255, 255))
        game_window.blit(over_text, (200, 250))

    def isClicked(animalX, animalY, clickX, clickY):
        distance = math.sqrt((math.pow((animalX + 32) - clickX, 2)) + (math.pow((animalY + 32) - clickY, 2)))
        return distance < 32

    def weighted_type_select(varietyRange, target_number, generate_target):
        weights = list(objectDict["label_complexity"][0:varietyRange])
        population = list(range(varietyRange))
        min_weights = min(weights)
        max_weights = max(weights)
        weights = np.add(weights, -min_weights + 1)
        weights = np.divide(weights, max_weights)
        weights = np.add(1.1, -weights)
        if s.rareness:
            new_type = random.choices(population=population, weights=weights, k=1)
        else:
            new_type = random.choices(population=population, k=1)
        if generate_target:
            if s.diff_successive and new_type[0] == target_number:
                new_type = random.choices(population=population, k=1)
        return new_type[0]

    def draw_object_name(x, y, i):
        label = font.render(str(objectDict["label"][i]), True, (255, 255, 255))
        game_window.blit(label, (x, y))

    def draw_object(x, y, i):
        game_window.blit(objectDict['loadImg'][object_type[i]], (x, y))

    def target_object(x, y, i):
        game_window.blit(objectDict['loadImg'][i], (x, y))

    def show_score(x, y):
        score = font.render("score : " + str(score_value), True, (255, 255, 255))
        game_window.blit(score, (x, y))

    def show_lives(x, y):
        score = font.render("lives : " + str(s.lives), True, (255, 255, 255))
        game_window.blit(score, (x, y))

    def write_csv_out(csv_array, full_csv_array, timedate):
        output_file_name = str(s.id_name) + '_' + timedate + "_clicktimes_" + ".csv"
        with open(outputs_path + output_file_name, 'w') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(csv_array)
        if s.isMousetrack:
            output_file_name = str(s.id_name) + '_' + timedate + "_clicktimes_full" + ".csv"
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
        csv_file = str(s.id_name) + '_' + "object_label_data.csv"
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
                energy_level = energy_level + min_impact + ((max_impact - min_impact) * ((math.sin(((energy_level - mean) * math.pi) / (100 - mean)) / 2) + 1))
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
        pygame.draw.rect(game_window, [255, 255, 255], pygame.Rect(30, WINDOW_SIZE[1] - 230, 60, 210), 4, 10)
        pygame.draw.rect(game_window, colour, pygame.Rect(35, WINDOW_SIZE[1] - 25 - energy_level * 2, 50, energy_level * 2), 0, 6)

    def get_new_randXY(range_i):
        x = random.randint(32, 768)
        y = random.randint(-100, 10)
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

    def playsounds(audio_name):
        audio = pygame.mixer.Sound(audio_library + audio_name)
        audio.play()
        return False, wait * s.fps

    def play_feedback_sounds(true_false):
        weights = [100, s.feedback_random_value]
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

    # ---------------------------------------------------------------
    # Initial object positions
    # ---------------------------------------------------------------
    for i in range(objects_on_screen):
        objectX[i], objectY[i] = get_new_randXY(objects_on_screen)

    new_start_time = time.time()
    last_recorded_click_time = new_start_time
    clicked = False
    last_output_click = -1
    feedback_sound = 0

    # ---------------------------------------------------------------
    # Game loop
    # ---------------------------------------------------------------
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                write_csv_out(csv_output, full_csv, start_time_date)
                save_obj_labels(objectDict)
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()

                for i in range(objects_on_screen):
                    clicked = isClicked(objectX[i], objectY[i], *pos)
                    if clicked:
                        clicked_type = object_type[i]
                        saved_target_type = target_type
                        saved_x = objectX[i]
                        saved_energy = s.energy
                        clicked_time = time.time()

                        if object_type[i] == target_type:
                            isCorrect = True
                            s.energy = calculate_energy(s.energy, s.energy_mean, s.isEnergy_linear, s.impact_max, s.impact_min)
                            score_value += 1

                            object_type[i] = weighted_type_select(current_vocab_size, target_type, False)
                            target_type_previous = target_type
                            target_type = weighted_type_select(current_vocab_size, target_type_previous, True)

                            if target_type == target_type_previous:
                                isRepeat = 1
                            else:
                                isRepeat = 0

                            isTarget_displayed = False
                            in_range_objects = []
                            for j in range(objects_on_screen):
                                if objectY[j] >= 0 and objectY[j] <= 300:
                                    in_range_objects.append(object_type[j])
                                    if object_type[j] == target_type:
                                        isTarget_displayed = True
                                        start_time[i] = new_start_time
                            if not isTarget_displayed:
                                if s.diff_successive:
                                    object_type[i] = target_type
                                else:
                                    target_type = random.choice(in_range_objects)

                            objectX[i], objectY[i] = get_new_randXY(objects_on_screen)
                            objectDict['type_score'][target_type] += 1

                            if score_value % 20 == 0:
                                if s.increase_scroll:
                                    objectY_change += 0.1

                            if objectDict['type_score'][target_type] == s.thresh:
                                if current_vocab_size < (animalDict_range - 1):
                                    current_vocab_size += 1
                                if objects_on_screen < animalDict_range:
                                    increase_objects_on_screen = True

                            scheduler = True
                            if s.isFeedback:
                                feedback_sound = play_feedback_sounds(1)

                        else:
                            s.lives -= 1
                            s.energy = calculate_energy(s.energy, s.energy_mean, s.isEnergy_linear, -s.impact_max, -s.impact_min)
                            isCorrect = False
                            if s.isFeedback:
                                feedback_sound = play_feedback_sounds(-1)

                        if isCorrect or i != last_output_click or last_recorded_click_time - clicked_time > 2:
                            last_output_click = i

                            if isCorrect:
                                letter_append = '_C'
                            else:
                                letter_append = '_I'
                            mouse_coord_file = s.id_name + '_' + str(mouse_tracking_file_number).zfill(6) + letter_append + ".csv"

                            output_dataframe = output_dataframe.set_index(['variable_name'])
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
                            output_dataframe.at['user_ID', 'output_variable'] = s.id_name
                            output_dataframe.at['time_date', 'output_variable'] = start_time_date
                            output_dataframe.at['target_img', 'output_variable'] = objectDict['fixed_name'][target_type]
                            output_dataframe.at['clicked_img', 'output_variable'] = objectDict['fixed_name'][clicked_type]
                            output_dataframe.at['feedback_type', 'output_variable'] = feedback_sound
                            output_dataframe.at['coord_file_name', 'output_variable'] = mouse_coord_file
                            output_dataframe.at['objects_on_screen', 'output_variable'] = objects_on_screen
                            output_dataframe.at['scroll_speed', 'output_variable'] = int(s.fps * math.floor(objectY_change))
                            output_dataframe = output_dataframe.reset_index()

                            last_recorded_click_time = clicked_time
                            csv_output, full_csv = write_line_to_csv_array(output_dataframe, 'output_variable', csv_output, full_csv)

                            if isCorrect:
                                new_start_time = time.time()

                            if s.isMousetrack:
                                write_mouse_epoch(isCorrect, mouse_coord_file, mouse_tracking)
                            mouse_tracking_file_number = mouse_tracking_file_number + 1
                            mouse_tracking.clear()

                        clicked = False
                        isCorrect = False

        # Background
        backgroundY = backgroundY + objectY_change
        draw_background(backgroundY)
        if backgroundY >= 1200:
            backgroundY = 0

        # Draw objects
        for i in range(objects_on_screen):
            draw_object(objectX[i], objectY[i], i)
            objectY[i] += objectY_change
            if objectY[i] >= 600:
                object_type[i] = weighted_type_select(current_vocab_size, target_type, False)
                objectX[i], objectY[i] = get_new_randXY(objects_on_screen)
                start_time[i] = 0
            if objectY[i] >= -5 and objectY[i] < 5:
                if object_type[i] == target_type:
                    start_time[i] = new_start_time

        # Play audio of name after delay
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
        if s.lives == 0 or s.energy <= 0:
            for j in range(objects_on_screen):
                objectY[j] = 2000
            game_over_text()

        # Show score
        show_score(textX, textY)
        if s.lives > 0:
            show_lives(livesX, livesY)

        # Draw target animal
        if objectDict['type_score'][target_type] <= s.thresh:
            target_object(targetX, targetY, target_type)
            isTarget_img = 1
        else:
            isTarget_img = 0
        draw_object_name(labelX, labelY, target_type)

        # Draw energy bar
        draw_energy(s.energy)

        # Energy dropping over time
        energy_counter += 1
        if energy_counter >= energy_counter_interval:
            s.energy = calculate_energy(s.energy, s.energy_mean, s.isEnergy_linear, -3, -1)
            energy_counter = 0

        if increase_objects_on_screen:
            new_x, new_y = get_new_randXY(objects_on_screen)
            new_type = weighted_type_select(current_vocab_size, target_type, False)
            objectX.append(new_x)
            objectY.append(new_y)
            object_type.append(new_type)
            start_time.append(time.time())
            objects_on_screen += 1
            increase_objects_on_screen = False

        pygame.display.update()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_data_newline = [mouse_x, mouse_y, (time.time() - epoch_start)]
        mouse_tracking.append(mouse_data_newline)
        clock.tick(s.fps)
