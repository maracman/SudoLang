import os
import sys
import numpy as np
import math
from datetime import date
from PIL import Image
from pathlib import Path

divide_resolution = 10

def get_path():
    operating_system = sys.platform
    if operating_system == "darwin":
        dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])

    else:
        dir_path = os.getcwd()

    return_path = os.path.join(dir_path, 'data/outputs/mouse_coords/')
    return return_path



def convert_to_rgb(c):
    c = c * 100000
    r = math.floor(c / (256 * 256));
    g = math.floor(c / 256) % 256;
    b = c % 256;
    return(r,g,b)


def convert_to_png(folder_loc):

    for root,dirs,files in os.walk(folder_loc):
        for file in files:

            if file.endswith(".csv"):
                print(os.path.join(folder_loc, file))
                f=open(os.path.join(folder_loc, file), 'r')
                file_info = np.loadtxt(f, delimiter=",", skiprows=1)

                pix_array = np.zeros((round(600/divide_resolution)+1, round(800/divide_resolution)+1, 3), dtype=np.uint8)
                number = file_info[0][0]
                print(number)

                for i in range(len(file_info)):
                    colour_r, colour_g, colour_b = convert_to_rgb(file_info[i,2])
                    pix_array[round(int(file_info[i,1])/divide_resolution), round(int(file_info[i,0])/divide_resolution) ] \
                        = [colour_r, colour_g, colour_b]

                #create file path
                day_today = date.today().strftime("%Y-%m-%d")
                new_path = os.path.join(folder_loc, day_today + "_PNGconvert")
                Path(new_path).mkdir(parents=True, exist_ok=True)
                filename = file.strip(".csv")

                #save pixel array as png
                im = Image.fromarray(pix_array)
                im.save(new_path + '/' + filename + '.png')

                #plt.imshow(pix_array)
                #plt.show()

                f.close()

# run program
directory = get_path()

incorrect_location = directory + "incorrect"
correct_location = directory + "correct"
convert_to_png(correct_location)
convert_to_png(incorrect_location)