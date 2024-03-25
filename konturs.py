from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import showinfo, askyesno

import os

import numpy as np
from PIL import Image

import requests
import csv
import time
import cv2

coord_file = ''
map_dir = ''
output_dir = ''

# format:
# index,x1,y1,x2,y2,xd,yd
# x1,y1 - bot left
# x2,y2 - top right
# xd,yd - distance in meters
coord_array = []

show_points_on_map = False

output_file = ''

image_size_x = 640
image_size_y = 640


def choose_coord_file():
    Tk().withdraw()
    showinfo("Select tile_coordinates file", "Select tile_coordinates file")
    coord_file = askopenfilename()

    return coord_file
    

def choose_directory():
    Tk().withdraw()
    showinfo("Select folder with processed map tile images", "Select folder with processed map tile images")
    map_dir = askdirectory()

    return map_dir

def choose_output_folder():
    Tk().withdraw()
    showinfo("Select output folder", "Select output folder")
    output_dir = askdirectory()

    return output_dir

def ask_if_show_points():
    Tk().withdraw()
    choice = askyesno("Show points on map?", "Do you want to Show points on map?")

    return choice

def process_coord_file(coord_array):
    with open(coord_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                values = line.split(',')
                coord_array.append(values)
    return

def find_center(filepath):
    image = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    max_area = image_size_x * image_size_y
    min_area = 0.0048828125 * max_area

    res_array = []

    for contour in contours:
        area = cv2.contourArea(contour)

    
        if area > min_area:
            M = cv2.moments(contour)
            centroid_x = int(M["m10"] / M["m00"])
            centroid_y = int(M["m01"] / M["m00"])

            res_array.append((centroid_x, centroid_y, area / max_area))

    return res_array
            

def find_white_pixel_percent(filepath):
    image = Image.open(filepath)
    grayscale_image = image.convert('L')
    np_image = np.array(grayscale_image)

    white_pixels = np.count_nonzero(np_image == 255)
    total_pixels = np_image.size
    white_pixel_percentage = (white_pixels / total_pixels)

    

    return white_pixel_percentage


def process_map_areas(output_file):

    output_array = []

    for filename in os.listdir(map_dir):
        filepath = os.path.join(map_dir, filename)
        
        tile_index, _ = filename.split('-')
        tile_index = int(tile_index)
        white_pixel_percent = find_white_pixel_percent(filepath)

        x1, y1 = float(coord_array[tile_index][1]), float(coord_array[tile_index][2])
        x2, y2 = float(coord_array[tile_index][3]), float(coord_array[tile_index][4])
        
        output_array.append([tile_index,x1,y1,x2,y2,white_pixel_percent])
        
    with open(output_file, 'w') as file:
        for row in output_array:
            for item in row:
                file.write(str(item)+',')
            file.write('\n')

    return


def process_map_points(output_file):

    

    output_array = []

    for filename in os.listdir(map_dir):
        filepath = os.path.join(map_dir, filename)
        
        tile_index, _ = filename.split('-')
        tile_index = int(tile_index)

        array = find_center(filepath)

        for x,y,area in array:

            x1, y1 = float(coord_array[tile_index][1]), float(coord_array[tile_index][2])
            x2, y2 = float(coord_array[tile_index][3]), float(coord_array[tile_index][4])

            x_len = float(coord_array[tile_index][5])
            y_len = float(coord_array[tile_index][6])

            rel_x = x / image_size_x
            rel_y = 1 - y / image_size_y

            map_x = (x2 - x1) * rel_x 
            map_y = (y2 - y1) * rel_y
 
            output_array.append([map_x + x1, map_y + y1, area * x_len * y_len])
        
    with open(output_file, 'w') as file:
        for row in output_array:
            for item in row:
                file.write(str(item)+',')
            file.write('\n')

    return

coord_file = choose_coord_file()
map_dir = choose_directory()
output_dir = choose_output_folder()


#show_points_on_map = ask_if_show_points()


process_coord_file(coord_array)

#if show_points_on_map:
output_file = os.path.join(output_dir, "output_points.txt")
process_map_points(output_file)
#else:
output_file = os.path.join(output_dir, "output_areas.txt")
process_map_areas(output_file)
