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
import time


class ImageFilter:
    """
    Responsible for filtering out noise from the 2D images of C. Elegans.
    """

    def __init__(self, fStart, fEnd, fDiff, dataType):
        """
        A simple constructor.

        :param fStart: The first frame of the worm images.
        :param fEnd: The last frame of the worm images.
        :param fDiff: Number of frames apart the two subtracted frames are.
        :param dataType: A string consisting of two characters where the
        first character denotes which directory (alphabetical) and the second
        character denotes camera number.
        """
        # Initializing instance variables
        self.fStart = fStart
        self.fEnd = fEnd
        self.fDiff = fDiff
        self.fPause = fPause
        self.dataType = dataType

        # Initializing matplotlib figure
        self.fig = plt.figure()
        self.fig.set_size_inches(18.5, 10.5, forward=True)
        self.fig.canvas.set_window_title("I See Elegance?")

    def runAnimation(self):
        """
        Runs all the worm animations which are based in the animate function.
        """
        self._startPerformanceMeasuring()

        ani = animation.FuncAnimation(self.fig,
                                      self.updateAllAnimation,
                                      init_func=self.initializeAllAnimation,
                                      frames=np.arange(self.fStart, self.fEnd),
                                      fargs=(fDiff,),
                                      interval=self.fPause,
                                      repeat=False,
                                      blit=True,
                                      save_count=0)
        plt.show()

    def updateAllAnimation(self, fNum, *args):
        """
        Updates all animations.

        :param fNum: The current frame to be animated.
        :param args: Contains the 'fDiff' parameter for the difference
        animation. This is how many frames apart the subtraction should be.
        :return: A tuple containing all the AxesImages to be animated.
        """
        self._updatePerformanceMeasuring()

        fDiff = args[0]
        rawAxes = self.updateRawAnimation(fNum)
#        difAxes = self.updateDifferenceAnimation(fNum, fDiff)
        otsuAxes = self.updateOtsuAnimation(fNum)
        return rawAxes + otsuAxes

    def updateOtsuAnimation(self, fNum):
        """
        Updates the animation that is responsible for Otsu's Thresholding.

        :param fNum: The frame number of the first image to be subtracted.
        :return: A list containing all the Axes to be updated.
        """
        img = self.readFrame(fNum, 0)
        retval, threshold = cv2.threshold(img, 127, 255, cv2.THRESH_TRUNC)

        self.axesOtsuImg.set_data(threshold)
        self.axesOtsuHist.cla()
        self.axesOtsuHist.autoscale(enable=False, axis='both')
        self.axesOtsuHist.hist(threshold.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')

        return [self.axesOtsuImg, self.axesOtsuHist]

    def updateDifferenceAnimation(self, fNum, fDiff):
        """
        Updates the animation that is responsible for computing the OpenCV
        difference (and not OpenCV subtract!) between two frames.

        :param fNum: The frame number of the first image to be subtracted.
        :param fDiff: The difference between the first and next frame.
        :return: A list containing all the Axes to be updated.
        """
        img = self.computeFrameDifference(fNum, fNum+fDiff)
        self.axesDifImg.set_data(img)
        self.axesDifHist.cla()
        self.axesDifHist.autoscale(enable=False, axis='both')
        self.axesDifHist.hist(img.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')

        return [self.axesDifImg, self.axesDifHist]

    def updateRawAnimation(self, fNum):
        """
        Updates the animation that is responsible for showing the raw frames
        and it's historgram.

        :param fNum: The frame number to be shown.
        :return: A list containing all the Axes to be updated.
        """
        img = self.readFrame(fNum)
        self.axesRawImg.set_data(img)
        self.axesRawHist.cla()
        self.axesRawHist.autoscale(enable=False, axis='both')
        self.axesRawHist.hist(img.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')

        return [self.axesRawImg, self.axesRawHist]

    def initializeAllAnimation(self):
        """
        Initializes all animations.

        :return: A tuple containing all the AxesImages to be initialized.
        """
        rawAxes = self.initializeRawAnimation()
#        difAxes = self.initializeDifferenceAnimation()
        otsuAxes = self.initializeOtsuAnimation()
        return rawAxes + otsuAxes

    def initializeOtsuAnimation(self):
        """
        Initializes the animation for the Otsu's thresholding.

        :return: A list containing all the Axes to be initialized.
        """
        img = self.readFrame(self.fStart, 0)
        retval, threshold = cv2.threshold(img, 127, 255, cv2.THRESH_TRUNC)

        self.axesOtsu = self.fig.add_subplot(2, 2, 3)
        self.axesOtsu.set_title("Image Otsu's Thresholding")
        self.axesOtsuImg = self.axesOtsu.imshow(threshold)

        self.axesOtsuHist = self.fig.add_subplot(2, 2, 4)
        self.axesOtsuHist.set_title("Intensity Otsu's Thresholding")
        self.axesOtsuHist.set_xlim([-10, 300])
        self.axesOtsuHist.set_ylim([0, 1])
        self.axesOtsuHist.hist(threshold.ravel(),
                               normed=True,
                               bins=256,
                               fc='k',
                               ec='k')

        return [self.axesOtsuImg, ]

    def initializeDifferenceAnimation(self):
        """
        Initializes the animation for the difference of images.

        :return: A list containing all the Axes to be initialized.
        """
        img = self.computeFrameDifference(self.fStart, self.fStart + self.fDiff)

        self.axesDif = self.fig.add_subplot(2, 2, 3)
        self.axesDif.set_title("Image Difference")
        self.axesDifImg = self.axesDif.imshow(img)

        self.axesDifHist = self.fig.add_subplot(2, 2, 4)
        self.axesDifHist.set_title("Intensity Difference")
        self.axesDifHist.set_xlim([-10, 300])
        self.axesDifHist.set_ylim([0, 1])
        self.axesDifHist.hist(img.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')

        return [self.axesDifImg, ]

    def initializeRawAnimation(self):
        """
        Initializes the animation for the raw images.

        :return: A list containing all the Axes to be initialized.
        """
        img = self.readFrame(self.fStart)

        self.axesRaw = self.fig.add_subplot(2, 2, 1)
        self.axesRaw.set_title("Image Raw")
        self.axesRawImg = self.axesRaw.imshow(img)

        self.axesRawHist = self.fig.add_subplot(2, 2, 2)
        self.axesRawHist.set_title("Intensity Raw")
        self.axesRawHist.set_xlim([-10, 300])
        self.axesRawHist.set_ylim([0, 1])
        self.axesRawHist.hist(img.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')

        return [self.axesRawImg, ]

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

    def readFrame(self, fNum, flag=1):
        """
        Reads the worm image for the given frame number using OpenCV read.

        :param fNum: The frame number to be read.
        :param flag: The flag for the opencv image read method.
        :return: An image in OpenCV format.
        """
        return cv2.imread(self._generateFramePath(fNum), flag)

    def _generateFramePath(self, fNum):
        """
        Generates the absolute path to a given frame number in the 2D images
        directory for C. Elegans. This requires the frames to be named
        chronologically using the form "frame_0000XY.png", where six digits (
        can be leading zeros) are present after the frame prefix.

        :param fNum: The frame number of the 2D image.
        :return: A string of the absolute path to a worm image.
        """
        type = self.dataType[0]
        camera = "cam" + self.dataType[1]
        frame = "frame_%06d.png" % fNum

        path = ["..", "assets", "images", type, camera, frame]

        relPath = os.path.join(*path)
        absPath = os.path.abspath(relPath)

        if os.path.exists(absPath):
            return absPath
        else:
            raise NameError("Could not generate a path frame number %d!" % fNum)

    def _updatePerformanceMeasuring(self):
        """
        Updates the last frame called in the animation and prints the time
        elapsed, and average FPS since the last call to _beginTiming function.
        """
        print("--- PERFORMANCE MEASUREMENTS UPDATING ---")
        self.currentFrame += 1

        dt = time.time() - self.timeStart
        fps = (self.currentFrame / dt)

        print("Time Elapsed: %d seconds" % dt)
        print("Current Frame: %d" % self.currentFrame)
        print("Overall FPS: %.2f" % fps)

    def _startPerformanceMeasuring(self):
        """
        Starts the measuring of time and current frame.
        To be used in conjunction with it's update method.
        """
        print("--- PERFORMANCE MEASUREMENTS STARTING NOW ---")
        self.timeStart = time.time()
        self.currentFrame = 0


if __name__ == "__main__":
    # Control variables
    fStart = 1
    fDiff = 10
    fEnd = 680
    fPause = 1000       # milliseconds
    dataType = "C1"

    imageFilter = ImageFilter(fStart, fEnd, fDiff, dataType)
    imageFilter.runAnimation()
