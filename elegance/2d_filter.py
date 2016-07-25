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
        # Initializing instance variables
        self.fStart = fStart
        self.fEnd = fEnd
        self.fDiff = fDiff
        self.fPause = fPause

        # Initializing matplotlib figure
        self.fig = plt.figure()
        self.fig.canvas.set_window_title("I See Elegance?")

    def runAnimation(self):
        """
        Runs all the worm animations which are based in the animate function.
        """
        ani = animation.FuncAnimation(self.fig,
                                      self.updateAllAnimation,
                                      init_func=self.initializeAllAnimation,
                                      frames=np.arange(self.fStart, self.fEnd),
                                      fargs=(fDiff,),
                                      interval=fPause,
                                      blit=True)
        plt.show()

    def initializeAllAnimation(self):
        """
        Initializes all animations.

        :return: A tuple containing all the AxesImages to be initialized.
        """
        self.initializeRawAnimation()
        self.initializeDifferenceAnimation()
        return self.axesImgRaw, self.axesImgDif

    def initializeRawAnimation(self):
        """
        Initializes the animation for the raw images.
        """
        self.axesRaw = self.fig.add_subplot(2, 2, 1)
        self.axesRaw.set_title("Image Raw")

        img = self.readFrame(self.fStart)
        self.axesImgRaw = self.axesRaw.imshow(img)

    def initializeDifferenceAnimation(self):
        """
        Initializes the animation for the difference of images.
        """
        self.axesDif = self.fig.add_subplot(2, 2, 3)
        self.axesDif.set_title("Image Difference")

        img = self.computeFrameDifference(self.fStart, self.fStart + self.fDiff)
        self.axesImgDif = self.axesDif.imshow(img)

    def updateAllAnimation(self, fNum, *args):
        """
        Updates all animations.

        :param fNum: The current frame to be animated.
        :param args: Contains the 'fDiff' parameter for the difference
        animation. This is how many frames apart the subtraction should be.
        :return: A tuple containing all the AxesImages to be animated.
        """
        fDiff = args[0]
        self.updateRawAnimation(fNum, self.axesImgRaw)
        self.updateDifferenceAnimation(fNum, fDiff, self.axesImgDif)
        return self.axesImgRaw, self.axesImgDif

    def updateRawAnimation(self, fNum, axes):
        """
        Updates the animation that is responsible for showing the raw frames.

        :param fNum: The frame number to be shown.
        :param axes: The matplotlib axes to draw the animation on.
        """
        axes.set_data(self.readFrame(fNum))

    def updateDifferenceAnimation(self, fNum, fDiff, axes):
        """
        Updates the animation that is responsible for computing the OpenCV
        difference (and not OpenCV subtract!) between two frames.

        :param fNum: The frame number of the first image to be subtracted.
        :param fDiff: The difference between the first and next frame.
        :param axes: The matplotlib axes to draw the animation on.
        """
        axes.set_data(self.computeFrameDifference(fNum, fNum + fDiff))

    def computeFrameDifference(self, fOne, fTwo):
        """
        Calculates the absolute difference between the given two frames
        numbers of the worm.

        :param fOne: Integer number of the first frame.
        :param fTwo: Integer number of the second frame.
        :return: The difference of two images in OpenCV format.
        """
        img1 = cv2.imread(self._generateFramePath(fOne))
        img2 = cv2.imread(self._generateFramePath(fTwo))
        return cv2.absdiff(img1, img2)

    def readFrame(self, fNum):
        """
        Reads the worm image for the given frame number using OpenCV read.

        :param f: The frame number to be read.
        :return: An image in OpenCV format.
        """
        return cv2.imread(self._generateFramePath(fNum))

    def _generateFramePath(self, fNum):
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
    fPause = 40      # in milliseconds

    imageFilter = ImageFilter(fStart, fEnd, fDiff, fPause)
    imageFilter.runAnimation()

# TODO:
# 1. Plot the normal animation of the worm next to subtracted frames
# 2. Plot the histogram of intensities next to that as well
