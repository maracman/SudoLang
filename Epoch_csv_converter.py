import os
import sys
import numpy as np
import matplotlib.pyplot as plt

operating_system = sys.platform
if operating_system == "darwin":
    dir_path = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
else:
    dir_path = os.getcwd()

incorrect_location = os.path.join(dir_path,'data/outputs/mouse_coords/incorrect/')
correct_location = os.path.join(dir_path, 'data/outputs/mouse_coords/correct/')




for root,dirs,files in os.walk(correct_location):
    for file in files:
        print(os.path.join(root, file))
        if file.endswith(".csv"):
            print(file)
            column_names = ["x_pos", "y_pos", "time_stamp"]
            f=open(os.path.join(correct_location, file), 'r')
            file_info = np.loadtxt(f, delimiter=",", skiprows=1)

            #print(file_info)
            pix_array = np.zeros((600, 800, 3), dtype=np.uint8)
            number = file_info[0][0]
            print(number)

            for i in range(len(file_info)):
                pix_array[int(file_info[i,1]), int(file_info[i,0]) ] = [254, 254, 254]


            plt.imshow(pix_array)
            plt.show()


            #f.close()
