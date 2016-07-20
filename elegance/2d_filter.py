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
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


class ImageFilter:
    """
    Responsible for filtering out noise from the 2D images of C. Elegans.
    """

    def __init__(self, fStart, fEnd, fDiff, fPause):
        """
        A simple constructor.

        :param fStart: The first frame of the worm images.
        :param fEnd: The last frame of the worm images.
        :param fDiff: Number of frames apart the two subtracted frames are.
        :param fPause: Number of milliseconds between animated frames.
        """
        # Initializing variables
        self.fStart = fStart
        self.fEnd = fEnd
        self.fDiff = fDiff
        self.fPause = fPause

        # Initializing the animation
        self.fig = plt.figure()
        self.im = plt.imshow(
            self.computeFrameDifference(self.fStart, self.fStart + self.fDiff))

    def runAnimation(self):
        """
        Runs the worm animation that is based on the animate function.
        """
        plt.title("C. Elegans in Action")
        ani = animation.FuncAnimation(self.fig, self.animate,
                                      frames=np.arange(fStart, fEnd),
                                      fargs=(fDiff,),
                                      interval=fPause,
                                      blit=True)
        plt.show()

    def animate(self, frame, *args):
        """
        Used to draw the animation which shows the difference of two frames.
        This is done via matplotlib's animation.FuncAnimation.

        :param frame: The current frame to be animated.
        :param args: Contains the 'fDiff' parameter which dictates how
        many frames apart the two frames to be subtracted are.
        :return: An AxesImage which is to be processed by
        animation.FuncAnimation.
        """
        fDiff = args[0]
        self.im.set_data(self.computeFrameDifference(frame, frame + fDiff))
        return self.im,

    def computeFrameDifference(self, fOne, fTwo):
        """
        Calculates the absolute difference between the given two frames
        numbers of the worm.

        :param fOne: Integer number of the first frame.
        :param fTwo: Integer number of the second frame.
        :return: An image in openCV format.
        """
        img1 = cv2.imread(self.generateFramePath(fOne))
        img2 = cv2.imread(self.generateFramePath(fTwo))
        return cv2.absdiff(img1, img2)

    def generateFramePath(self, fNum):
        """
        Generates the absolute path to a given frame number in the 2D images
        directory for C. Elegans. This requires the frames to be named
        chronologically using the form "frame_0000XY.png", where six digits (
        can be leading zeros) are present after the frame prefix.

        :param fNum: The frame number of the 2D image.
        :return: A string of the absolute path to a worm image.
        """
        dir = ["..", "assets", "images_2d"]
        fileName = ["frame_%06d.png" % fNum]
        path = dir + fileName

        relPath = os.path.join(*path)
        absPath = os.path.abspath(relPath)

        if os.path.exists(absPath):
            return absPath
        else:
            raise NameError("Could not generate a path frame number %d!" % fNum)

if __name__ == "__main__":
    # Control variables
    fStart = 1
    fDiff = 10
    fEnd = 680
    fPause = 1      # in milliseconds

    imageFilter = ImageFilter(fStart, fEnd, fDiff, fPause)
    imageFilter.runAnimation()
