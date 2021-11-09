import os
import colorsys
import re
import sys
import numpy as np
import pandas as pd
import math
from datetime import date
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
from scipy.stats import norm, skewnorm
import matplotlib.mlab as mlab

from operator import is_
import random
import itertools

export_to_png = False #export all files in user directory to .png
new_file_name = "epoch_training.csv"
epoch_categories = ["correct", "incorrect"] #folder names for labels
plot_category_1 = "correct"
plot_category_2 = "incorrect"
divide_resolution = 1
stats_csv_columns = ("isDisplayed", "coord_file_name")
framerate = 60
acc_curve = 8
no_in_test_set = 10 #how many to set aside for testing
line_width = 6
res_x = 800
pause_outlier_thresh = 4 #duration beyond which to not count as a pause
res_y = 600
accel_channels = 2
length_include = 1 #only inlclude files this many seconds or longer
user = 'Marcus1'
HSV = False
is_test = False #overlay test epochs on histograms
test_set_label = "correct"
click_batch = 1
decision_point_calculator = acc_curve #sets how tightly to measure when the cursor starts moving toward the response object
profiling_label = user
sample_size = 20 #number of files used to create user profile (recommended 100)
number_of_samples = 100 #batch size for under 100 samples bootstrapping
direction_segments = 8 #must be greater than 2

def get_path():
    operating_system = sys.platform
    if operating_system == "darwin":
        dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])

    else:
        dir_path = os.getcwd()

    return_path = os.path.join(dir_path, 'outputs/mouse_tracking/')
    return return_path

def hsv_to_rgb(h, s, v):
    if s == 0.0: v*=255; return (v, v, v)
    i = int(h*6.) # XXX assume int() truncates!
    f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
    if i == 0: return (v, t, p)
    if i == 1: return (q, v, p)
    if i == 2: return (p, v, t)
    if i == 3: return (p, q, v)
    if i == 4: return (t, p, v)
    if i == 5: return (v, p, q)

def convert_to_gb(c):
    c = c * 100000 #colours loop back roughly every 10 seconds
    g = math.floor(c / 256) % 256
    b = c % 256
    return g,b

def convert_to_rgb(c, vel, max_vel): #convert time information into unique RGB data
    if not HSV:
        if accel_channels == 0:
            c = c * 1000000 #colours loop back roughly every 100 seconds
            r = round(math.floor(c / (256 * 256)))
            g = round(math.floor(c / 256) % 256)
            b = c % 256
        elif accel_channels == 1:
            c = c * 100000  # colours loop back roughly every 10 seconds
            g = round(math.floor(c / 256) % 256)
            b = c % 256
            r = round((vel/max_vel) * 256)
        elif accel_channels == 2:
            vel = vel/max_vel * 256 * 256
            g = round(math.floor(vel / 256) % 256)
            b = vel % 256
            r = c * 50
        else:
            vel = vel * 1000000
            r = round(math.floor(vel / (256 * 256)))
            g = round(math.floor(vel / 256) % 256)
            b = vel % 256
    else:
        h = round(c / 15 * 360) % 360
        s = round(int((vel/max_vel) * 100))
        v = round(int((vel/max_vel) * 100))
        if s < 5:
            s = 5
        if v < 5:
            v = 5
        rgb = colorsys.hsv_to_rgb((h/360.0),(s/100.0),(v/100.0))
        r = rgb[0] * 256
        g = rgb[1] * 256
        b = rgb[2] * 256

    return r,g,b

def countdown_convert(mouse_timing): #creates rgb consistent relative to final click (significant improvements to models)
    max_time = mouse_timing[len(mouse_timing)-1]
    countdown_array = []
    for i in range(len(mouse_timing)):
        new_time = max_time - mouse_timing[i]
        countdown_array.append(new_time)
    return countdown_array

def index_files(folder_location, for_test): #(batch_size, sample_size, folder_location, random=False): #scope can be player or session
    user_path = []
    user_ID = []
    session = []
    label = []
    sequence_no = []
    file_name = []
    epoch_path = []
    stats_csv = pd.DataFrame()

    print('.')
    user_id_path = []
    user_session = []
    for dirs in os.walk(directory):
        print(dirs)

    for roots, dirs, files in os.walk(directory):
        if re.match('/.*id_\w+(?!\/)+$', str(roots)):
            for dir in dirs:
                if dir.startswith('session_'):
                    user_id_path.append(roots)
                    user_session.append(dir)

    #load stats csv
    for path in user_id_path:
        for dir in user_session:
            for file in os.listdir(str(path) + '/' + str(dir)):
                if file.endswith('.csv'):
                    filepath = str(path) + '/' + str(dir) + '/' + str(file)
                    filedir = str(path) + '/' + str(dir)
                    filename = file
                    new_stats_df = pd.read_csv(filepath, usecols=stats_csv_columns)
                    new_stats_df['stats_directory'] = [filedir] * len(new_stats_df)
                    new_stats_df['stats_filename'] = [filename] * len(new_stats_df)
                    stats_csv = stats_csv.append(new_stats_df)
    print(stats_csv["stats_directory"])
    #load epoch csv's and data in dataframe
    for i in range(len(user_id_path)):
        for category in epoch_categories:
            directory2 = str(user_id_path[i]) + '/' + str(user_session[i] + '/' + str(category))
            for roots, dirs, files in os.walk(directory2):
                for file in files:
                    if file.endswith('.csv'):
                        file_name.append(file)
                        user_path.append(user_id_path[i])
                        session.append(user_session[i])
                        file_path = str(directory2) + '/' + str(file)
                        epoch_path.append(file_path)
                        user = str(re.findall("(?<=id_)\w+$", str(user_id_path[i])))
                        sequence = str(re.findall("(?<=%s[_])\d+" %str(user), str(file)))
                        sequence = sequence.lstrip("['").strip("']")
                        sequence = int(sequence)
                        user = user.lstrip("['").strip("']")

                        #add isDisplayed to categories
                        if 1 in stats_csv[(stats_csv["stats_directory"] == str(str(user_id_path[i]) + '/' + str(user_session[i]))) &
                                   (stats_csv["coord_file_name"] == str(file))]["isDisplayed"].values.flatten().tolist():
                            append_category = "displayed"
                        else:
                            append_category = category
                        print(append_category)
                        label.append(append_category)

                        user_ID.append(user)
                        sequence_no.append(sequence)
    #print(stats_csv)
    file_index = pd.DataFrame(
        {"user_path": user_path, 'user_ID': user_ID, 'session': session, 'label': label, 'sequence_no': sequence_no, 'file_path': epoch_path,
        'file_name': file_name, 'test': False})

    #set aside alotted number of each category for test
    categories = file_index["label"].unique()
    for category in categories:
        test_set = file_index[(file_index['label'] == category)].sample(n=for_test, replace=False)
        remainder = file_index.loc[~file_index.index.isin(test_set.index)]
        test_set.loc[:,'test'] = True
        file_index = pd.concat([remainder, test_set])



    return file_index

def is_file_empty_2(file_name):
    """ Check if file is empty by reading first character in it"""
    # open ile in read mode
    with open(file_name, 'r') as read_obj:
        # read first character
        one_char = read_obj.read(1)
        # if not fetched then file is empty
        if not one_char:
           return True
    return False

def is_file_empty(file_path):
    """ Check if file is empty by confirming if its size is 0 bytes"""
    # Check if file exist and it is empty
    return os.path.exists(file_path) and os.path.getsize(file_path) == 0

def user_profile(file_index, user_name, label, sample, batch_id, test = False, return_means = True):
    pause_amounts = []
    pause_durations = []
    curve = acc_curve
    vel_append = []
    heat_map_click = []
    decision_accel_diff_append = []
    direction_best_append = []
    direction_loose_append = []
    x_pos_append = []
    filelist_append = []
    y_pos_append = []
    stutters = []
    time_append = []
    decision_times = []
    valid_files = []
    final_click_pos = []
    distance_from_click = []
    approach_offsets = []
    files = file_index[(file_index["user_ID"] == user_name) & (file_index["label"] == label) & (file_index["test"] == test)]["file_path"].tolist()
    #print(str(len(files)) + ' total' +' "'+ str(label) + '" ' + 'files for ' + str(user_name))

    if sample > len(files):
        sample = len(files)
    files = random.sample(files, sample)

    for file in files:

        try:
            f = open(file, 'r')
            if not is_file_empty(file) and not is_file_empty_2(file):
                xy_pos = np.loadtxt(f, delimiter=",", skiprows=1, dtype=[('x_pos', 'int'), ('y_pos', 'int'), ('time', 'float32')])
            else:
                print("empty file: " + str(file))
                continue
        except IOError:
            print("corrupt file: " + str(file))
            continue

        valid_files.append(file)
        #calculate loose velocity
        xy_pos_rolled = np.roll(xy_pos, curve)
        vel_x = (xy_pos['x_pos'] - xy_pos_rolled['x_pos'])/curve # * (xy_pos_rolled['time'] - xy_pos['time'])
        vel_y = (xy_pos['y_pos'] - xy_pos_rolled['y_pos'])/curve # * (xy_pos_rolled['time'] - xy_pos['time'])

        vel_list = []
        for i in range(len(vel_x)):
            distance = float(math.sqrt(vel_x[i]**2 + vel_y[i]**2))
            vel_list.append(distance)
        vel_append = [*vel_append, *vel_list]


        #caulculate pauses
        pause_list = pause_calculator(vel_list, xy_pos["time"])
        if len(pause_list) != 0:
            pause_durations.append(np.mean(pause_list))
        else:
            pause_durations.append(int(0))


        pause_amounts.append(len(pause_list))

        # last mouse posistion aka click
        click_pos = int(xy_pos['x_pos'][len(xy_pos)-1]), int(xy_pos['y_pos'][len(xy_pos)-1])
        heat_map_click.append(click_pos)
        click_pos_list = [click_pos] * len(xy_pos)
        final_click_pos = [*final_click_pos, *click_pos_list]

        #fix last to first rollover error
        for i in range(curve):
            vel_x[i] = np.subtract(xy_pos['x_pos'], np.roll(xy_pos['x_pos'], i))[i]/i
            vel_y[i] = np.subtract(xy_pos['y_pos'], np.roll(xy_pos['y_pos'], i))[i]/i
        vel_x[0] = 0
        vel_y[0] = 0
    
        x_diff1 = np.roll(np.append(np.diff(xy_pos['x_pos']), 0), 1)
        y_diff1 = np.roll(np.append(np.diff(xy_pos['y_pos']), 0), 1)
        x_diff2 = xy_pos['x_pos'] - np.roll(xy_pos['x_pos'],2)
        y_diff2 = xy_pos['y_pos'] - np.roll(xy_pos['y_pos'],2)
        x_diff2[0:2] = 0
        y_diff2[0:2] = 0
        x_diff3 = xy_pos['x_pos'] - np.roll(xy_pos['x_pos'],3)
        y_diff3 = xy_pos['y_pos'] - np.roll(xy_pos['y_pos'],3)
        x_diff3[0:3] = 0
        y_diff3[0:3] = 0
    
        #determine direction at highest resolution possible
        direction_loose = np.degrees(np.arctan(vel_y/vel_x))
        add_ar_loose = np.where(vel_x < 0, 270, np.where(vel_x > 0, 90, 0))
        direction_loose = np.floor(np.add(add_ar_loose, direction_loose))
        add_ar_tight1 = np.where(x_diff1 < 0, 270, np.where(x_diff1 > 0, 90, 0))
        direction_tight1 = np.degrees(np.arctan(y_diff1 / x_diff1))
        direction_tight1 = np.add(add_ar_tight1, direction_tight1)
        add_ar_tight2 = np.where(x_diff2 < 0, 270, np.where(x_diff2 > 0, 90, 0))
        direction_tight2 = np.degrees(np.arctan(y_diff2 / x_diff2))
        direction_tight2 = np.add(add_ar_tight2, direction_tight2)
        add_ar_tight3 = np.where(x_diff3 < 0, 270, np.where(x_diff3 > 0, 90, 0))
        direction_tight3 = np.degrees(np.arctan(y_diff3 / x_diff3))
        direction_tight3 = np.add(add_ar_tight3, direction_tight3)
        direction_best = np.nan_to_num(direction_tight1, nan=np.nan_to_num(direction_tight2, nan= np.nan_to_num(direction_tight3, nan = direction_loose)))

        direction_best_append = [*direction_best_append, *direction_best]
        direction_loose_append = [*direction_loose_append, *direction_loose]
        x_pos_append = [*x_pos_append, *xy_pos['x_pos']]
        y_pos_append = [*y_pos_append, *xy_pos['y_pos']]
        time_append = [*time_append, *xy_pos['time']]

        #calculate stutter
        stutter = np.sum(np.abs((np.subtract(np.nan_to_num(direction_loose, 0), np.nan_to_num(direction_best, 0)))))/len(direction_loose)
        stutters.append(stutter)

        #distance at each point from destination click
        new_distance_from_click = np.sqrt(np.power(xy_pos["x_pos"] - click_pos[0], 2) + np.power(xy_pos["y_pos"] - click_pos[1], 2))
        distance_from_click = [*distance_from_click, *new_distance_from_click]

        #calculate decision point from distance
        decision_time = 0
        decision_time_point = 0
        check_distance = 0
        decision_xy = [round(res_x/2), round(res_y/2)]
        for i in range(len(new_distance_from_click)):
            index = decision_point_calculator + (i * decision_point_calculator)
            if index < len(new_distance_from_click):
                if check_distance < new_distance_from_click[len(new_distance_from_click) - index]:
                    decision_time = xy_pos["time"][len(xy_pos)-1] - xy_pos["time"][len(xy_pos) - index]
                    decision_time_point = xy_pos["time"][len(xy_pos) - index] #used to calculate discrepency between max acceleration and decision
                    check_distance = new_distance_from_click[len(new_distance_from_click) - index]
                    decision_xy = [xy_pos['x_pos'][len(xy_pos) - index], xy_pos['y_pos'][len(xy_pos) - index]]
                else:
                    break
            else:
                break

        #decision_time_list = [decision_time] * len(xy_pos)
        decision_times.append(decision_time)

        #calculate discrepency between decision and max acceleration
        accel = np.roll(np.append(np.diff(vel_list), 0),1) #appends 0 to start of vel diff
        max_accel_index = np.argmax(accel)

        if decision_time_point > 0:
            decision_accel_diff = decision_time_point - xy_pos["time"][max_accel_index]
        else:
            decision_accel_diff = 0
        decision_accel_diff_append.append(decision_accel_diff)

        #calculate appraoch offset
        if click_pos[0] - decision_xy[0] > 0: # --> todo: substitute for function
            justify_angle = 90
        elif click_pos[0] - decision_xy[0] < 0:
            justify_angle = 270
        else:
            justify_angle = 0

        if click_pos[0] - res_x/2 > 0: # --> todo: substitute for function
            justify_angle2 = 90
        elif click_pos[0] - res_x/2 < 0:
            justify_angle2 = 270
        else:
            justify_angle2 = 0

        approach_angle = np.degrees(np.arctan(click_pos[1] - decision_xy[1]/click_pos[0] - decision_xy[0])) - justify_angle
        angle_from_center = np.degrees(np.arctan(click_pos[1] - res_y/2/click_pos[0] - res_x/2)) - justify_angle2
        approach_offset = abs(approach_angle - angle_from_center) % 180
        approach_offsets.append(approach_offset)

        #link to file destination
        filelist = [file] * len(xy_pos)
        filelist_append = [*filelist_append, *filelist]



    #save useful info to dataframe
    stats_per_timeframe = pd.DataFrame(
        {'x_pos': x_pos_append,
         'y_pos': y_pos_append,
         'time': time_append,
         'velocity': vel_append,
         'direction_loose'+ '_' + str(curve): direction_loose_append,
         'direction_best': direction_best_append,
         'click_position': final_click_pos,
         'distance_from_click': distance_from_click,
         'file': filelist_append
         })

    #create direction categories
    category_splits = [0, 360/direction_segments]
    category_names = [1]
    for i in range(direction_segments-1):
        new_category = category_splits[i+1] + 360/direction_segments
        category_splits.append(new_category)
        category_names.append(i+2)

        direction_cat_name = 'direction_slice_' + str(direction_segments)
        stats_per_timeframe[str(direction_cat_name)] = pd.cut(stats_per_timeframe['direction_loose'+ '_' + str(curve)], category_splits, labels=category_names)

    direction_means_stats_df = []
    for file in valid_files:
        filestats = stats_per_timeframe[(stats_per_timeframe["file"] == file)]
        new_direction_mean = filestats[['velocity', str(direction_cat_name)]].groupby(str(direction_cat_name)).mean().values.flatten().tolist()
        direction_means_stats_df.append(new_direction_mean)

    stats_per_epoch = pd.DataFrame(
        {'file': pd.unique(filelist_append),
         'decision_time': decision_times,
         'direction_velocities': direction_means_stats_df,
         'approach_offset': approach_offsets,
         'directional_stutter': stutters,
         'mean_pause_length': pause_durations,
         'mean_pause_number': pause_amounts,
         'max_accel_v_decision': decision_accel_diff_append,
         'batch_number': batch_id,
         'label': label
         })

    direction_means = stats_per_timeframe[['velocity', str(direction_cat_name)]].groupby(str(direction_cat_name)).mean()
    mean_decision_time = np.mean(stats_per_epoch["decision_time"])
    mean_approach_offset = np.mean(stats_per_epoch["approach_offset"])
    mean_stutters = np.mean(stats_per_epoch["directional_stutter"])
    mean_pause_duration = np.mean(np.trim_zeros(stats_per_epoch['mean_pause_length']))
    mean_pause_amount = np.mean(stats_per_epoch['mean_pause_number'])
    mean_decision_accel = np.mean(stats_per_epoch['max_accel_v_decision'])

    if return_means:
        return heat_map_click, stats_per_epoch, stats_per_timeframe

def draw_profile(incorrect_vel, correct_vel, heat_map_correct, heat_map_incorrect):
    x_list = []
    y_list = []
    x1_list = []
    y1_list = []
    for i in range(0,direction_segments):
        angle = (i * 360/direction_segments) + (360/direction_segments/2)
        angle = np.radians(angle)
        y_list.append(np.cos(angle) * incorrect_vel[i])
        x_list.append(np.sin(angle) * incorrect_vel[i])


    x_list = [*x_list, x_list[0]]
    y_list = [*y_list, y_list[0]]


    for i in range(direction_segments):
        angle = (i * 360 / direction_segments) + (360 / direction_segments / 2)
        angle = np.radians(angle)
        y1_list.append(np.cos(angle) * correct_vel[i])
        x1_list.append(np.sin(angle) * correct_vel[i])


    x1_list = [*x1_list, x1_list[0]]
    y1_list = [*y1_list, y1_list[0]]

    plt.plot(x1_list, y1_list, color='blue', label="correct")
    plt.plot(x_list, y_list, color='red', label="incorrect")

    plt.show()
    i_x_heat, i_y_heat = zip(*heat_map_incorrect)
    plt.plot(i_x_heat,i_y_heat, 'ro', color='red')
    c_x_heat, c_y_heat = zip(*heat_map_correct)
    plt.plot(c_x_heat,c_y_heat, 'ro', color='blue')
    plt.show()

def pause_calculator(velocities, time):
    pauses = []
    pause_time = 0
    initial_time = 0
    for i in range(len(velocities)-1):
        if velocities[i+1] == 0 and velocities[i] != 0:
            initial_time = time[i+1]
        elif velocities[i+1] != 0 and velocities[i] == 0:
            pause_time = (time[i+1] - initial_time)
            if pause_time > 0 and pause_time < pause_outlier_thresh:
                pauses.append(pause_time)
                pause_time = 0
        else:
            pass
    return pauses

def draw_histograms(title, x_label, test_x_positions=None, use_test=False,  **kwargs):
    colours = ("red", "blue",  "green", "yellow", "purple", "orange", "pink")
    colour_index = 0
    max = []
    min = []
    for stats in kwargs.values():
        max.append(np.max(stats))
        min.append(np.min(stats))

    max = np.max(max)
    min = np.min(min)

    # test overlays
    if use_test:
        test_x_positions = test_x_positions.values.tolist()
        max = np.max(test_x_positions) if max < np.max(test_x_positions) else max
        min = np.min(test_x_positions) if min > np.min(test_x_positions) else min
        for i in range(len(test_x_positions)):
            use_colour = colours[(len(kwargs)) + 1 + i] if ((len(kwargs)) + 1 + i) < 7 else list(
                np.random.choice(range(256), size=3))
            x = test_x_positions[i]
            plt.axvline(x, label=i, color=use_colour)

    for name, values in kwargs.items():
        plt.hist(values, color=colours[colour_index], label=name, alpha=0.5, density=True)
        ae, loce, scalee = skewnorm.fit(values)
        domain = np.linspace(min, max, 100)
        p = skewnorm.pdf(domain, ae, loce, scalee)
        plt.plot(domain, p, color=colours[colour_index])
        colour_index = colour_index + 1



    plt.gca().set(title=title, xlabel = x_label)
    plt.legend()
    plt.show()

def acc_vel_array(xy_pos, curve):
    xy_pos_rolled = np.roll(xy_pos, curve)
    vel_x = (xy_pos['x_pos'] - xy_pos_rolled['x_pos'])/curve # * (xy_pos_rolled['time'] - xy_pos['time'])
    vel_y = (xy_pos['y_pos'] - xy_pos_rolled['y_pos'])/curve # * (xy_pos_rolled['time'] - xy_pos['time'])


    #fix last to first rollover error
    for i in range(curve):
        vel_x[i] = np.subtract(xy_pos['x_pos'], np.roll(xy_pos['x_pos'], i))[i]/i
        vel_y[i] = np.subtract(xy_pos['y_pos'], np.roll(xy_pos['y_pos'], i))[i]/i
    vel_x[0] = 0
    vel_y[0] = 0

    x_diff1 = np.roll(np.append(np.diff(xy_pos['x_pos']), 0), 1)
    y_diff1 = np.roll(np.append(np.diff(xy_pos['y_pos']), 0), 1)
    x_diff2 = xy_pos['x_pos'] - np.roll(xy_pos['x_pos'],2)
    y_diff2 = xy_pos['y_pos'] - np.roll(xy_pos['y_pos'],2)
    x_diff2[0:2] = 0
    y_diff2[0:2] = 0
    x_diff3 = xy_pos['x_pos'] - np.roll(xy_pos['x_pos'],3)
    y_diff3 = xy_pos['y_pos'] - np.roll(xy_pos['y_pos'],3)
    x_diff3[0:3] = 0
    y_diff3[0:3] = 0

    #determine direction at highest resolution possible
    direction_loose = np.degrees(np.arctan(vel_y/vel_x))
    add_ar_loose = np.where(vel_x < 0, 270, np.where(vel_x > 0, 90, 0))
    direction_loose = np.floor(np.add(add_ar_loose, direction_loose))
    add_ar_tight1 = np.where(x_diff1 < 0, 270, np.where(x_diff1 > 0, 90, 0))
    direction_tight1 = np.degrees(np.arctan(y_diff1 / x_diff1))
    direction_tight1 = np.add(add_ar_tight1, direction_tight1)
    add_ar_tight2 = np.where(x_diff2 < 0, 270, np.where(x_diff2 > 0, 90, 0))
    direction_tight2 = np.degrees(np.arctan(y_diff2 / x_diff2))
    direction_tight2 = np.add(add_ar_tight2, direction_tight2)
    add_ar_tight3 = np.where(x_diff3 < 0, 270, np.where(x_diff3 > 0, 90, 0))
    direction_tight3 = np.degrees(np.arctan(y_diff3 / x_diff3))
    direction_tight3 = np.add(add_ar_tight3, direction_tight3)
    direction_best = np.nan_to_num(direction_tight1, nan=np.nan_to_num(direction_tight2, nan= np.nan_to_num(direction_tight3, nan = direction_loose)))

    #calculate velocity
    vel_list = []
    for i in range(len(vel_x)):
        distance = float(math.sqrt(vel_x[i]**2 + vel_y[i]**2))
        vel_list.append(distance)
    vel = np.array(vel_list)
    acc = np.roll(np.append(np.diff(vel), 0),1) #appends 0 to start of vel diff

    #create direction categories
    category_splits = [0, 360/direction_segments]
    category_names = [1]
    for i in range(direction_segments-1):
        new_category = category_splits[i+1] + 360/direction_segments
        category_splits.append(new_category)
        category_names.append(i+2)

    #save useful info to dataframe
    epoch_df = pd.DataFrame(
        {'x_pos': xy_pos['x_pos'],
         'y_pos': xy_pos['y_pos'],
         'time': xy_pos['time'],
         'velocity': vel,
         'direction_loose'+ '_' + str(curve): direction_loose,
         'direction_tight1': direction_tight1,
         'direction_tight2': direction_tight2,
         'direction_best': direction_best
         })

    # directions into categories by splitting into buckets
    direction_cat_name = 'direction_slice_' + str(direction_segments)
    epoch_df[str(direction_cat_name)] = pd.cut(epoch_df['direction_loose'+ '_' + str(curve)], category_splits, labels=category_names)
    direction_means = epoch_df[['velocity', str(direction_cat_name)]].groupby(str(direction_cat_name)).mean()

    return vel, acc, epoch_df, direction_means

def velocity_to_r(vel):
        r = vel * 5
        return r

def draw_line(mat, x0, y0, x1, y1, inplace=False):
    if not (0 <= x0 < mat.shape[0] and 0 <= x1 < mat.shape[0] and
            0 <= y0 < mat.shape[1] and 0 <= y1 < mat.shape[1]):
        raise ValueError('Invalid coordinates.')
    if not inplace:
        mat = mat.copy()
    if (x0, y0) == (x1, y1):
        mat[x0, y0] = 2
        return mat if not inplace else None
    # Swap axes if Y slope is smaller than X slope
    transpose = abs(x1 - x0) < abs(y1 - y0)
    if transpose:
        mat = mat.T
        x0, y0, x1, y1 = y0, x0, y1, x1
    # Swap line direction to go left-to-right if necessary
    if x0 > x1:
        x0, y0, x1, y1 = x1, y1, x0, y0
    # Write line ends
    mat[x0, y0] = 2
    mat[x1, y1] = 2
    # Compute intermediate coordinates using line equation
    x = np.arange(x0 + 1, x1)
    y = np.round(((y1 - y0) / (x1 - x0)) * (x - x0) + y0).astype(x.dtype)
    # Write intermediate coordinates
    mat[x, y] = 1

    #draw thickness
    lim1 = line_width / 2
    if line_width % 2 == 0:
        lim2 = lim1
    else:
        lim2 = lim1 - 1
    #thicken points
    for x_inc in range(int(lim1 + lim2)):
        for y_inc in range(int(lim1 + lim2)):
            mat[x0 - x_inc, y0 - y_inc] = 1
            mat[x1 - x_inc, y1 - y_inc] = 1

    #thicken betweens
    for i in range(len(x)):
        for x_inc in range(int(lim1 + lim2)):
            for y_inc in range(int(lim1 + lim2)):
                mat[x[i] - x_inc, y[i] - y_inc] = 1

    if not inplace:
        return mat if not transpose else mat.T


def calculate_max_vel(folder_loc):
    max_vel_arr = []
    mean_vel_array = []

    for root,dirs,files in os.walk(folder_loc):
        for file in files:

            if file.endswith(".csv"):
                try:
                    f=open(os.path.join(folder_loc, file), 'r')
                    file_info = np.loadtxt(f, delimiter=",", skiprows=1, dtype=[('x_pos', 'int'), ('y_pos', 'int'), ('time', 'float32')])
                    velocity, acceleration, epoch_info, means = acc_vel_array(file_info, acc_curve)
                    max_velocity = np.max(velocity)
                    mean_vel = np.mean(velocity[np.nonzero(velocity)])

                    Except = False
                except IOError:
                    print("couldn't load file")
                    Except = True
            if not Except:
                mean_vel_array.append(mean_vel)
                max_vel_arr.append(max_velocity)

    max_velocity = np.max(max_vel_arr)
    total_mean_vel = sum(mean_vel_array)/len(mean_vel_array)
    return max_velocity, total_mean_vel


def convert_to_png(max_vel, folders):
    files = folders["file_path"].values.tolist()
    folders = folders.set_index("file_path")
    #for root,dirs,files in os.walk(folder_loc):
    #    for file in files:

    #        if file.endswith(".csv"):
    for file in files:
        try:
            #print(os.path.join(folder_loc, file))
            f=open(file, 'r')
            file_info = np.loadtxt(f, delimiter=",", skiprows=1, dtype=[('x_pos', 'int'), ('y_pos', 'int'), ('time', 'float32')])

            pix_array = np.zeros((round(600/divide_resolution)+1, round(800/divide_resolution)+1, 3), dtype=np.uint8)
            countdown_array = countdown_convert(file_info['time'])
            velocity, acceleration, epoch, means = acc_vel_array(file_info, acc_curve)

            for i in range(acc_curve, len(file_info), 1):
                colour_r, colour_g, colour_b = convert_to_rgb(countdown_array[i], velocity[i], max_vel) #time to rgb

                x_coord = round(int(file_info[i][1])/divide_resolution)
                y_coord = round(int(file_info[i][0])/divide_resolution)
                if i < len(file_info) - 1:
                    x_next = round(int(file_info[i+1][1])/divide_resolution)
                    y_next = round(int(file_info[i+1][0])/divide_resolution)

                trace_between_array = draw_line(
                    np.zeros((round(600 / divide_resolution) + line_width, round(800 / divide_resolution) + line_width)), x_coord,
                    y_coord, x_next, y_next)

                line_coords = np.argwhere(trace_between_array == 1)
                #print(epoch)

                for j in range(len(line_coords)):
                    if np.nonzero(line_coords[j]):
                        joining_x, joining_y = line_coords[j,0], line_coords[j,1]
                        pix_array[joining_x, joining_y] = [colour_r, colour_g, colour_b]

                pix_array[x_coord, y_coord] = [colour_r, colour_g, colour_b]


            #create png folder
            day_today = date.today().strftime("%Y-%m-%d")
            new_path = str(folders.loc[file]["user_path"]) + '/' + (str(day_today) + "_PNGconvert") + '/' + str(folders.loc[file]["session"]) + '/' + str(folders.loc[file]["label"])


            Path(new_path).mkdir(parents=True, exist_ok=True)
            filename = folders.loc[file]["file_name"].strip(".csv")

            #save pixel array as png
            im = Image.fromarray(pix_array)
            fig = plt.figure()
            ax = plt.axes([0, 0, 1, 1])
            plt.axis("off")

            #im.save(new_path + '/' + filename + '.png')

            plt.imshow(im, interpolation="nearest")  #unhash to review png's while processing

            circle1 = plt.Circle((round(file_info[len(file_info)-1]["x_pos"]/divide_resolution), round(file_info[len(file_info)-1]["y_pos"]/divide_resolution)), 20, color='r', alpha=0.3)
            plt.gca().add_patch(circle1)

            plt.savefig((new_path + '/' + filename + '.png'), bbox_inches='tight', interpolation="nearest")

            plt.show()             #unhash to review png's while processing
        except StopIteration:
            print("empty file encountered: " + str(file))

        f.close()

def save_epoch_dataframe(filepath, dataframe):
    dataframe.to_csv(filepath, index = False, header=True)

# run program
maximum_velocity_total = 100
directory = get_path()
folders = index_files(directory, no_in_test_set)
print(folders["label"])

#test set
_, test_epoch_stats, test_timeframe_stats = user_profile(folders, user, test_set_label, 3, 1, test=True)
print(test_epoch_stats)


#append empties for batch sampling
variable1_velocities = ['nul'] * number_of_samples
heat_map_variable1 = ['nul'] * number_of_samples

variable2_velocities = ['nul'] * number_of_samples
heat_map_variable2 = ['nul'] * number_of_samples

heat_map_variable1 = []
variable1_epoch_stats = pd.DataFrame()
variable1_timeframe_stats = pd.DataFrame()
heat_map_variable2 = []
variable2_epoch_stats = pd.DataFrame()
variable2_timeframe_stats = pd.DataFrame()

for i in range(number_of_samples):
    new_heat_map_variable1, new_epoch_stats_variable1, new_timeframe_stats_variable1 = user_profile(folders, user, plot_category_1, sample_size, i)
    new_heat_map_variable2, new_epoch_stats_variable2, new_timeframe_stats_variable2 = user_profile(folders, user, plot_category_2, sample_size, i)

    #append data frames
    variable1_epoch_stats = variable1_epoch_stats.append(new_epoch_stats_variable1)
    variable1_timeframe_stats = variable1_timeframe_stats.append(new_timeframe_stats_variable1)
    heat_map_variable1.append(new_heat_map_variable1)

    variable2_epoch_stats = variable2_epoch_stats.append(new_epoch_stats_variable2)
    variable2_timeframe_stats = variable2_timeframe_stats.append(new_timeframe_stats_variable2)
    heat_map_variable2.append(new_heat_map_variable2)

    direction_cat_name = 'direction_slice_' + str(direction_segments)
    variable1_velocities[i] = variable1_timeframe_stats[['velocity', str(direction_cat_name)]].groupby(str(direction_cat_name)).mean()
    variable2_velocities[i] = variable2_timeframe_stats[['velocity', str(direction_cat_name)]].groupby(str(direction_cat_name)).mean()


#print(test_correct_epoch_stats["decision_time"])
#bootstrapped and pure distribution histograms
if number_of_samples > 1:
    draw_histograms(
        incorrect = variable2_epoch_stats[["decision_time", "batch_number"]].groupby('batch_number').mean(),
        correct = variable1_epoch_stats[["decision_time", "batch_number"]].groupby('batch_number').mean(),
        title="Time from Decision to Final Click",
        x_label="time in seconds",
        test_x_positions=test_epoch_stats["decision_time"],
        use_test=is_test)
    draw_histograms(
        incorrect = variable2_epoch_stats[['max_accel_v_decision', "batch_number"]].groupby('batch_number').mean(),
        correct = variable1_epoch_stats[['max_accel_v_decision', "batch_number"]].groupby('batch_number').mean(),
        title="Time from Decision to Maximum Accelleration",
        x_label="time in seconds",
        test_x_positions=test_epoch_stats["max_accel_v_decision"],
        use_test=is_test)
    draw_histograms(
        incorrect = variable2_epoch_stats[['mean_pause_number', "batch_number"]][(variable2_epoch_stats['mean_pause_number'] != 0)].groupby('batch_number').mean(),
        correct = variable1_epoch_stats[['mean_pause_number', "batch_number"]][(variable1_epoch_stats['mean_pause_number'] != 0)].groupby('batch_number').mean(),
        title="Mean Number of Pauses per Epoch (excluding zeros)",
        x_label="number of pauses",
        test_x_positions=test_epoch_stats["mean_pause_number"],
        use_test=is_test)
    draw_histograms(
        incorrect = variable2_epoch_stats[['mean_pause_number', "batch_number"]].groupby('batch_number').mean(),
        correct = variable1_epoch_stats[['mean_pause_number', "batch_number"]].groupby('batch_number').mean(),
        title="Mean Number of Pauses per Epoch",
        x_label="number of pauses",
        test_x_positions=test_epoch_stats["mean_pause_number"],
        use_test=is_test)
    draw_histograms(
        incorrect = variable2_epoch_stats[['mean_pause_length', "batch_number"]].groupby('batch_number').mean(),
        correct = variable1_epoch_stats[['mean_pause_length', "batch_number"]].groupby('batch_number').mean(),
        title="Mean Duration of Pause",
        x_label="pause length in seconds",
        test_x_positions=test_epoch_stats["mean_pause_length"],
        use_test=is_test)
    draw_histograms(
        incorrect = variable2_epoch_stats[["directional_stutter", "batch_number"]].groupby('batch_number').mean(),
        correct = variable1_epoch_stats[["directional_stutter", "batch_number"]].groupby('batch_number').mean(),
        title="Amount of Directional Stutter",
        x_label="average of discrepency (in degrees) with overall direction",
        test_x_positions=test_epoch_stats["directional_stutter"],
        use_test=is_test)
    draw_histograms(
        incorrect = variable2_epoch_stats[["approach_offset", "batch_number"]].groupby('batch_number').mean(),
        correct = variable1_epoch_stats[["approach_offset", "batch_number"]].groupby('batch_number').mean(),
        title="Angle of Offset on Approach",
        x_label="discrepency in degrees from center angle",
        test_x_positions=test_epoch_stats["approach_offset"],
        use_test=is_test)
else:
    draw_histograms(
        incorrect=variable2_epoch_stats["decision_time"],
        correct=variable1_epoch_stats["decision_time"],
        title="Time from Decision to Final Click",
        x_label="time in seconds",
        test_x_positions = test_epoch_stats["decision_time"],
        use_test=is_test)
    draw_histograms(
        incorrect=variable2_epoch_stats['max_accel_v_decision'],
        correct=variable1_epoch_stats['max_accel_v_decision'],
        title="Time from Decision to Maximum Accelleration",
        x_label="time in seconds",
        test_x_positions=test_epoch_stats["max_accel_v_decision"],
        use_test=is_test)
    draw_histograms(
        incorrect=variable2_epoch_stats['mean_pause_number'][(variable2_epoch_stats['mean_pause_number'] != 0)],
        correct=variable1_epoch_stats['mean_pause_number'][(variable1_epoch_stats['mean_pause_number'] != 0)],
        title="Mean Number of Pauses per Epoch (no zeros)",
        x_label="number of pauses",
        test_x_positions=test_epoch_stats["mean_pause_number"],
        use_test=is_test)
    draw_histograms(
        incorrect=variable2_epoch_stats['mean_pause_number'],
        correct=variable1_epoch_stats['mean_pause_number'],
        title="Mean Number of Pauses per Epoch",
        x_label="number of pauses",
        test_x_positions=test_epoch_stats["mean_pause_number"],
        use_test=is_test)
    draw_histograms(
        incorrect=variable2_epoch_stats['mean_pause_length'],
        correct=variable1_epoch_stats['mean_pause_length'],
        title="Mean Duration of Pause",
        x_label="pause length in seconds",
        test_x_positions=test_epoch_stats["mean_pause_length"],
        use_test=is_test)
    draw_histograms(
        incorrect=variable2_epoch_stats["directional_stutter"],
        correct=variable1_epoch_stats["directional_stutter"],
        title="Amount of Directional Stutter",
        x_label="average of discrepency (in degrees) with overall direction",
        test_x_positions=test_epoch_stats["directional_stutter"],
        use_test=is_test)
    draw_histograms(
        incorrect=variable2_epoch_stats["approach_offset"],
        correct=variable1_epoch_stats["approach_offset"],
        title="Angle of Offset on Approach",
        x_label="discrepency in degrees from center angle",
        test_x_positions=test_epoch_stats["approach_offset"],
        use_test=is_test)

big_heat_map_variable1 = list(itertools.chain.from_iterable(heat_map_variable1))
big_heat_map_variable2 = list(itertools.chain.from_iterable(heat_map_variable2))
mean_variable2_velocities = np.array(np.mean(variable2_velocities, axis=0)).flatten().tolist()
mean_variable1_velocities = np.array(np.mean(variable1_velocities, axis=0)).flatten().tolist()

#correct_example_epoch =  user_profile(folders, user, "incorrect", sample_size)
variable1_velocities[i] = variable1_timeframe_stats[['velocity', str(direction_cat_name)]].groupby(str(direction_cat_name)).mean()
variable2_velocities[i] = variable2_timeframe_stats[['velocity', str(direction_cat_name)]].groupby(str(direction_cat_name)).mean()


draw_profile(mean_variable2_velocities, mean_variable1_velocities, big_heat_map_variable1, big_heat_map_variable2)

export_dataframe = pd.concat([variable1_epoch_stats,variable2_epoch_stats])
save_csv_path = os.path.join(directory, new_file_name)
save_epoch_dataframe(save_csv_path, export_dataframe)

joint_timeframe_stats = pd.concat([variable1_timeframe_stats, variable2_timeframe_stats])
maxvel = joint_timeframe_stats["velocity"].max()
meanvel = joint_timeframe_stats["velocity"].mean()

# convert to image
if export_to_png:
    convert_to_png(maxvel, folders)
