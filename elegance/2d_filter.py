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
        :return: A list containing all the AxesImages to be animated.
        """
        fDiff = args[0]

        self._updatePerformanceMeasuring()

        axes = \
        [
            self.updateRawAnimation(fNum),
#            self.updateRawHistAnimation(fNum),
            self.updateDifferenceAnimation(fNum, fDiff),
#            self.updateDifferenceHistAnimation(fNum, fDiff),
#            self.updateOtsuAnimation(fNum),
#            self.updateOtsuHistAnimation(fNum),
        ]
        return axes

    def updateOtsuAnimation(self, fNum):
        """
        Updates the animation that is responsible for showing Otsu's
        Thresholding.

        :param fNum: The frame number of the first image to be subtracted.
        :return: The Axes to be updated.
        """
        img = self.readFrame(fNum, 0)
        retval, threshold = cv2.threshold(img, 127, 255, cv2.THRESH_TRUNC)
        self.axesOtsuImg.set_data(threshold)
        return self.axesOtsuImg

    def updateOtsuHistAnimation(self, fNum):
        """
        Updates the animation that is responsible for showing the
        histogram of Otsu's Thresholding.

        :param fNum: The frame number of the first image to be subtracted.
        :return: The Axes to be updated.
        """
        img = self.readFrame(fNum, 0)
        retval, threshold = cv2.threshold(img, 127, 255, cv2.THRESH_TRUNC)
        self.axesOtsuHist.cla()
        self.axesOtsuHist.autoscale(enable=False, axis='both')
        self.axesOtsuHist.hist(threshold.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')
        return self.axesOtsuHist

    def updateDifferenceAnimation(self, fNum, fDiff):
        """
        Updates the animation that is responsible for showing the OpenCV
        difference (and not OpenCV subtract!) between two frames.

        :param fNum: The frame number of the first image to be subtracted.
        :param fDiff: The difference between the first and next frame.
        :return: The Axes to be updated.
        """
        img = self.computeDifferenceAlgorithm(fNum, fNum + fDiff)
        self.axesDifImg.set_data(img)
        return self.axesDifImg

    def updateDifferenceHistAnimation(self, fNum, fDiff):
        """
        Updates the animation that is responsible for showing the histogram
        of the OpenCV difference (and not OpenCV subtract!) between two frames.

        :param fNum: The frame number of the first image to be subtracted.
        :param fDiff: The difference between the first and next frame.
        :return: The Axes to be updated.
        """
        img = self.computeDifferenceAlgorithm(fNum, fNum + fDiff)
        self.axesDifHist.cla()
        self.axesDifHist.autoscale(enable=False, axis='both')
        self.axesDifHist.hist(img.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')
        return self.axesDifHist

    def updateRawAnimation(self, fNum):
        """
        Updates the animation that is responsible for showing the raw frames.

        :param fNum: The frame number to be shown.
        :return: The Axes to be updated.
        """
        img = self.readFrame(fNum)
        self.axesRawImg.set_data(img)
        return self.axesRawImg

    def updateRawHistAnimation(self, fNum):
        """
        Updates the animation that is responsible for showing the histogram
        of the raw frames.

        :param fNum: The frame number to be shown.
        :return: The Axes to be updated.
        """
        img = self.readFrame(fNum)
        self.axesRawHist.cla()
        self.axesRawHist.autoscale(enable=False, axis='both')
        self.axesRawHist.hist(img.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')
        return self.axesRawHist

    def initializeAllAnimation(self):
        """
        Initializes all animations.

        :return: A list containing all the AxesImages to be initialized.
        """
        axes = \
        [
            self.initializeRawAnimation(1),
#            self.initializeRawHistAnimation(2),
            self.initializeDifferenceAnimation(3),
#            self.initializeDifferenceHistAnimation(4),
#            self.initializeOtsuAnimation(5),
#            self.initializeOtsuHistAnimation(6),
        ]
        return axes

    def initializeOtsuAnimation(self, location):
        """
        Initializes the animation for showing Otsu's thresholding.

        :param location: The location of the subplot.
        :return: The axes to be initialized
        """
        otsuArgs = (127, 255, cv2.THRESH_TRUNC)
        retval, threshold = self.computeOtsuAlgorithm(self.fStart, *otsuArgs)

        self.axesOtsu = self.fig.add_subplot(2, 2, location)
        self.axesOtsu.set_title("Image Otsu's Thresholding")
        self.axesOtsuImg = self.axesOtsu.imshow(threshold)
        return self.axesOtsuImg

    def initializeOtsuHistAnimation(self, location):
        """
        Initializes the animation for the histogram of Otsu's thresholding.

        :param location: The location of the subplot.
        :return: The axes to be initialized
        """
        otsuArgs = (127, 255, cv2.THRESH_TRUNC)
        retval, threshold = self.computeOtsuAlgorithm(self.fStart, *otsuArgs)

        self.axesOtsuHist = self.fig.add_subplot(2, 2, location)
        self.axesOtsuHist.set_title("Intensity Otsu's Thresholding")
        self.axesOtsuHist.set_xlim([-10, 300])
        self.axesOtsuHist.set_ylim([0, 1])
        self.axesOtsuHist.hist(threshold.ravel(),
                               normed=True,
                               bins=256,
                               fc='k',
                               ec='k')

        return self.axesOtsuImg

    def initializeDifferenceAnimation(self, location):
        """
        Initializes the animation for the difference of images.

        :param location: The location of the subplot.
        :return: The axes to be initialized
        """
        self.axesDif = self.fig.add_subplot(2, 2, location)
        self.axesDif.set_title("Image Difference")

        img = self.computeDifferenceAlgorithm(self.fStart,
                                              self.fStart + self.fDiff)
        self.axesDifImg = self.axesDif.imshow(img, cmap="gray")
        return self.axesDifImg

    def initializeDifferenceHistAnimation(self, location):
        """
        Initializes the animation for the histogram of the difference of
        images.

        :param location: The location of the subplot.
        :return: The axes to be initialized
        """
        img = self.computeDifferenceAlgorithm(self.fStart, self.fStart + self.fDiff)
        self.axesDifHist = self.fig.add_subplot(2, 2, location)
        self.axesDifHist.set_title("Intensity Difference Histogram")
        self.axesDifHist.set_xlim([-10, 300])
        self.axesDifHist.set_ylim([0, 1])
        self.axesDifHist.hist(img.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')
        return self.axesDifImg

    def initializeRawAnimation(self, location):
        """
        Initializes the animation for the raw images.

        :param location: The location of the subplot.
        :return: A list containing all the Axes to be initialized.
        """
        self.axesRaw = self.fig.add_subplot(2, 2, location)
        self.axesRaw.set_title("Image Raw")

        img = self.readFrame(self.fStart)
        self.axesRawImg = self.axesRaw.imshow(img)
        return self.axesRawImg

    def initializeRawHistAnimation(self, location):
        """
        Initializes the animation for histogram of the raw images.

        :param location: The location of the subplot.
        :return: A list containing all the Axes to be initialized.
        """
        img = self.readFrame(self.fStart)
        self.axesRawHist = self.fig.add_subplot(2, 2, location)
        self.axesRawHist.set_title("Intensity Raw")
        self.axesRawHist.set_xlim([-10, 300])
        self.axesRawHist.set_ylim([0, 1])
        self.axesRawHist.hist(img.ravel(),
                              normed=True,
                              bins=256,
                              fc='k',
                              ec='k')
        return self.axesRawImg

    def computeOtsuAlgorithm(self, fNum, *args):
        """
        Wrapper function that runs the opencv otsu's thresholding algorithm
        on a specified frame number.

        :param fNum: the frame number to perform operations on.
        :param args: Any argument that can be passed to the OpenCV thresholding
        function.
        :return: The outputs of the OpenCV thresholding function.
        """
        img = self.readFrame(fNum, 0)
        return cv2.threshold(img, *args)

    def computeDifferenceAlgorithm(self, fOne, fDiff):
        """
        Blurs two images, takes their absolute difference, applies a local
        gaussian threshold, then attempts to find contours of the worm and
        draws a rectangle around it.

        :param fOne: Integer number of the first frame.
        :param fDiff: How many frames ahead the next image is.
        :return: The difference of two images in OpenCV format.
        """
        img1 = cv2.imread(self._generateFramePath(fOne))
        img2 = cv2.imread(self._generateFramePath(fOne + fDiff))

        # Blurs the images
        img1 = cv2.blur(img1, (3, 3))
        img2 = cv2.blur(img2, (3, 3))

        # Computes the absolute difference
        diff = cv2.absdiff(img1, img2)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Applies local gaussian thresholding to binary
        thresh = cv2.adaptiveThreshold(diff, 255,
                                       cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY_INV,
                                       3, 6)

        # Dilates image to fill gaps and finding all contours
        thresh = cv2.dilate(thresh, None, iterations=3)
        (contours, _) = cv2.findContours(thresh.copy(),
                                         cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)

        # Extracting only sufficiently large contours and drawing a
        # rectangle around them
        for c in contours:
            if cv2.contourArea(c) < 1000:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            print("Contours Rectangle at: (%d %d) (%d %d)" % (x, y, w, h))
            cv2.rectangle(thresh, (x, y), (x+w, y+h), (255, 255, 255), 2)

        return thresh

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
