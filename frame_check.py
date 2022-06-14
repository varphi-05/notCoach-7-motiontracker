import cv2
import numpy as np

def checkpixel(main_colour, check_colour, dx):

    checkpixel_v = 0

    # checks the chosen colour it's R, G and B value respectively,
    # and if it's value is less than 'dx' away from the main colour
    for i in range(3):
        checkpixel_v += main_colour[i] - dx < check_colour[i] < main_colour[i] + dx
    # if the above requirement is met for all three values, returns True, otherwise returns False
    if checkpixel_v == 3:
        return True
    else:
        return False

def checkframe(bottom_left_point,
               up_right_point,
               frame,
               main_colour,
               dx
               ):
    # creates an empty list in which the approved pixels will be stored
    approved_pix = []

    # checks all pixels within the chosen bounds and approves a pixel if checkpixel() returns True
    for x_pix in range(bottom_left_point[0], up_right_point[0]):
        for y_pix in range(bottom_left_point[1], up_right_point[1]):

            if 0<x_pix<frame.shape[1] and 0<y_pix<frame.shape[0]:
                # stores the RGB value of the pixel in question
                pix_colour = (frame[y_pix, x_pix, 2], frame[y_pix, x_pix, 1], frame[y_pix, x_pix, 0])

                if checkpixel(main_colour, pix_colour, dx):
                    approved_pix.append((x_pix, y_pix))
    return approved_pix
