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
from operator import is_


divide_resolution = 1
framerate = 60
acc_curve = 8
line_width = 6
accel_channels = 2
HSV = False
click_batch = 1
direction_segments = 8 #must be greater than 2

def get_path():
    operating_system = sys.platform
    if operating_system == "darwin":
        dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])

    else:
        dir_path = os.getcwd()

    return_path = os.path.join(dir_path, 'outputs/mouse_coords/')
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

def create_profile(folder_location): #(batch_size, sample_size, folder_location, random=False): #scope can be player or session
    for root,dirs,files in os.walk(folder_location):
        #print(root)
        sessions = []
        file_counts = []
        if re.match(r'.*/id_\w+(?!\/)+$', str(root)):
            user_path = root
            for dir in dirs:
                print(dir)
                if dir.startswith('session_'):
                    print(dir)
                    file_count = 0
                    for file in files:
                        print(file)
                        file_count += 1

                        if file.endswith('.csv'):
                            print('yay')
                            file_count += 1
                    sessions.append(str(dir))
                    file_counts.append(int(file_count))

        session_counts = list(zip(file_counts, sessions))
    return sessions



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
         'direction_best': direction_best,
         })

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


def convert_to_png(folder_loc, max_vel):

    for root,dirs,files in os.walk(folder_loc):
        for file in files:

            if file.endswith(".csv"):
                try:
                    #print(os.path.join(folder_loc, file))
                    f=open(os.path.join(folder_loc, file), 'r')
                    file_info = np.loadtxt(f, delimiter=",", skiprows=1, dtype=[('x_pos', 'int'), ('y_pos', 'int'), ('time', 'float32')])

                    pix_array = np.zeros((round(600/divide_resolution)+1, round(800/divide_resolution)+1, 3), dtype=np.uint8)
                    countdown_array = countdown_convert(file_info['time'])
                    velocity, acceleration, epoch, means = acc_vel_array(file_info, acc_curve)

                    print(epoch[['direction_loose_8', 'direction_slice_8', 'velocity']])
                    print(means)

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
                    new_path = os.path.join(folder_loc, day_today + "_PNGconvert")
                    Path(new_path).mkdir(parents=True, exist_ok=True)
                    filename = file.strip(".csv")

                    #save pixel array as png
                    im = Image.fromarray(pix_array)
                    im.save(new_path + '/' + filename + '.png')

                    plt.imshow(pix_array)  #unhash to review png's while processing
                    plt.show()             #unhash to review png's while processing
                except StopIteration:
                    print("empty file encountered: " + str(file))

                f.close()

# run program
maximum_velocity_total = 100
directory = get_path()
#maximum_velocity_incorrect, mean_vel_incorrect = calculate_max_vel(directory + "incorrect")

#maximum_velocity_correct, mean_vel_correct = calculate_max_vel(directory + "correct")
#maximum_velocity_total = maximum_velocity_correct if maximum_velocity_correct > maximum_velocity_incorrect else maximum_velocity_incorrect
#print(maximum_velocity_total)
#print("velocity mean incorrect " + str(mean_vel_incorrect))
#print("velocity mean correct " + str(mean_vel_correct))

#incorrect_location = directory + "incorrect"
#correct_location = directory + "correct"
#convert_to_png(correct_location, maximum_velocity_total)
#convert_to_png(incorrect_location, maximum_velocity_total)
folders = create_profile(str(directory + 'id_Marcus_collect' ))
print(folders)