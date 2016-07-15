# A script that removes background noise from 2D images of C. elegans
# @Author: Othman Alikhan
# @Date: 2016 - 07 - 15

import numpy as np
import cv2
import os

def generateImagePath():
    """
    Generates the path absolute path to the first frame of the worm images.
    :return: A string of the absolute path to a worm image.
    """
    return os.path.abspath(os.path.join("..", "assets", "images_2d", "frame_000001.png"))


# Load a colour image in grayscale
path = generateImagePath()

img = cv2.imread(path, 0)

cv2.imshow("image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()


