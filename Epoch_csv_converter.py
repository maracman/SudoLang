import os
import sys
import numpy as np
import math
from datetime import date
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt

divide_resolution = 10
acc_curve = 8

def get_path():
    operating_system = sys.platform
    if operating_system == "darwin":
        dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])

    else:
        dir_path = os.getcwd()

    return_path = os.path.join(dir_path, 'data/outputs/mouse_coords/')
    return return_path



def convert_to_gb(c):
    c = c * 100000 #colours loop back roughly every 10 seconds
    g = math.floor(c / 256) % 256
    b = c % 256
    return g,b

def convert_to_rgb(c): #convert time information into unique RGB data
    c = c * 1000000 #colours loop back roughly every 100 seconds
    r = math.floor(c / (256 * 256))
    g = math.floor(c / 256) % 256
    b = c % 256
    return r,g,b

def countdown_convert(mouse_timing): #creates rgb consistent relative to final click (significant improvements to models)
    max_time = mouse_timing[len(mouse_timing)-1]
    countdown_array = []
    for i in range(len(mouse_timing)):
        new_time = max_time - mouse_timing[i]
        countdown_array.append(new_time)
    return countdown_array

def acc_vel_array(xy_pos, curve):
    xy_pos_diff = np.roll(xy_pos, curve)
    vel_x = (xy_pos['x_pos'] - xy_pos_diff['x_pos'])/curve
    vel_y = (xy_pos['y_pos'] - xy_pos_diff['y_pos'])/curve
    vel_list = []
    for i in range(len(vel_x)):
        distance = float(math.sqrt(vel_x[i]**2 + vel_y[i]**2))
        vel_list.append(distance)
    vel = np.array(vel_list)
    acc = np.diff(vel)
    return vel, acc

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
    if not inplace:
        return mat if not transpose else mat.T

def convert_to_png(folder_loc):

    for root,dirs,files in os.walk(folder_loc):
        for file in files:

            if file.endswith(".csv"):
                try:
                    #print(os.path.join(folder_loc, file))
                    f=open(os.path.join(folder_loc, file), 'r')
                    file_info = np.loadtxt(f, delimiter=",", skiprows=1, dtype=[('x_pos', 'int'), ('y_pos', 'int'), ('time', 'float32')])

                    pix_array = np.zeros((round(600/divide_resolution)+1, round(800/divide_resolution)+1, 3), dtype=np.uint8)
                    countdown_array = countdown_convert(file_info['time'])
                    velocity, acceleration = acc_vel_array(file_info, acc_curve)

                    #print(countdown_array)

                    for i in range(acc_curve, len(file_info), 1):
                        #colour_r, colour_g, colour_b = convert_to_rgb(countdown_array[i]) #time to rgb



                        colour_g, colour_b = convert_to_gb(countdown_array[i]) #time to green/blue
                        #colour_g = 150
                        #colour_b = 150
                        colour_r = velocity_to_r(velocity[i]) #velocity to red

                        x_coord = round(int(file_info[i][1])/divide_resolution)
                        y_coord = round(int(file_info[i][0])/divide_resolution)
                        if i < len(file_info) - 1:
                            x_next = round(int(file_info[i+1][1])/divide_resolution)
                            y_next = round(int(file_info[i+1][0])/divide_resolution)

                        trace_between_array = draw_line(
                            np.zeros((round(600 / divide_resolution) + 1, round(800 / divide_resolution) + 1)), x_coord,
                            y_coord, x_next, y_next)


                        line_coords = np.argwhere(trace_between_array == 1)
                        #print(line_coords)


                        for j in range(len(line_coords)):
                            if np.nonzero(line_coords[j]):
                                print(line_coords[j])
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

                    #plt.imshow(pix_array)  #unhash to review png's while processing
                    #plt.show()             #unhash to review png's while processing
                except StopIteration:
                    print("empty file encountered: " + str(file))

                f.close()

# run program
directory = get_path()

incorrect_location = directory + "incorrect"
correct_location = directory + "correct"
convert_to_png(correct_location)
convert_to_png(incorrect_location)