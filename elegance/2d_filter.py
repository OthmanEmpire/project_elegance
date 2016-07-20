"""
###############################################################################
# A script that suppresses all the information in the 2D images of C. Elegans #
# except the worm itself (i.e. image filtering).                              #
#                                                                             #
#                                                                             #
# Author: Othman Alikhan                                                      #
# Email: sc14omsa@leeds.ac.uk                                                 #
#                                                                             #
# Python Version: 2.6.6                                                       #
# Date Created: 2016-07-15                                                    #
###############################################################################
"""

import os
import cv2
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def main():
    """
    Main execution point of the script.
    """
    # Control variables
    frameStart = 1
    frameDiff = 20
    frameEnd = 700
    framePause = 1000          # in milliseconds

    # Initializing the graph
    plt.title("C. Elegans in Action")
    plt.xticks([]), plt.yticks([])
    p = plt.imshow(calculateFrameDifference(frameStart, frameStart + frameDiff))

    # Slideshow of the difference between two frames for all frames
    for frame in range(frameStart, frameEnd):
        p.set_data(calculateFrameDifference(frame, frame + frameDiff))
        plt.pause(framePause/1000)


#TODO:
#    ani = animation.F


def calculateFrameDifference(frameOne, frameTwo):
    """
    Calculates the absolute difference between the given two frames
    numbers of the worm.

    :param frameOne: Integer number of the first frame.
    :param frameTwo: Integer number of the second frame.
    :return: An image in openCV format.
    """
    img1 = cv2.imread(generateFramePath(frameOne))
    img2 = cv2.imread(generateFramePath(frameTwo))
    return cv2.absdiff(img1, img2)

def generateFramePath(frameNum):
    """
    Generates the absolute path to a given frame number in the 2D images
    directory for C. Elegans.

    :param frameNum: The frame number of the 2D image.
    :return: A string of the absolute path to a worm image.
    """
    dir = ["..", "assets", "images_2d"]
    fileName = ["frame_%06d.png" % frameNum]
    path = dir + fileName

    relPath = os.path.join(*path)
    absPath = os.path.abspath(relPath)

    if os.path.exists(absPath):
        return absPath
    else:
        raise NameError("Could not generate a path for the give frame number!")

if __name__ == "__main__":
    main()
