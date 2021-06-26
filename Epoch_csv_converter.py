import os
import sys
import numpy as np
import math
import scipy.misc
import matplotlib.pyplot as plt

divide_resolution = 10

operating_system = sys.platform
if operating_system == "darwin":
    dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
else:
    dir_path = os.getcwd()

incorrect_location = os.path.join(dir_path,'data/outputs/mouse_coords/incorrect/')
correct_location = os.path.join(dir_path, 'data/outputs/mouse_coords/correct/')

def convert_to_rgb(c):
    c = c * 100000
    r = math.floor(c / (256 * 256));
    g = math.floor(c / 256) % 256;
    b = c % 256;
    return(r,g,b)



def convert_to_png(folder_loc):

    for root,dirs,files in os.walk(folder_loc):
        for file in files:
            print(os.path.join(root, file))
            if file.endswith(".csv"):
                print(file)
                f=open(os.path.join(folder_loc, file), 'r')
                file_info = np.loadtxt(f, delimiter=",", skiprows=1)
                #print(file_info)
                pix_array = np.zeros((round(600/divide_resolution), round(800/divide_resolution), 3), dtype=np.uint8)
                number = file_info[0][0]
                print(number)

                for i in range(len(file_info)):
                    colour_r, colour_g, colour_b = convert_to_rgb(file_info[i,2])
                    pix_array[round(int(file_info[i,1])/divide_resolution), round(int(file_info[i,0])/divide_resolution) ] \
                        = [colour_r, colour_g, colour_b]

                plt.imshow(pix_array)
                plt.show()
                filename = file.strip(".csv")
                #scipy.misc.toimage(pix_array, cmin=0.0, cmax=...).save(folder_loc + filename + '.png')
                f.close()

convert_to_png(correct_location)
convert_to_png(incorrect_location)