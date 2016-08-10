"""
###############################################################################
# A script that suppresses all the information in the 2D images of C. Elegans #
# except the worm itself (i.e. image filtering).                              #
#                                                                             #
#                                                                             #
# Author: Othman Alikhan                                                      #
# Email: sc14omsa@leeds.ac.uk                                                 #
#                                                                             #
# Python Version: 2.7                                                         #
# Date Created: 2016-07-15                                                    #
###############################################################################
"""
import os
import sys
import time

import cv2
import numpy as np

import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import *

import pyqtgraph.examples
#pyqtgraph.examples.run()


class ImageController:
    """
    Responsible for coordinating the GUI with the core image processing
    algorithms.
    """

    def __init__(self, param):
        """
        A simple constructor.

        :param param: A dictionary containing all the control parameters.
        """
        self.param = param
        self.app = QtGui.QApplication(sys.argv)
        self.imageDisplay = ImageDisplay(self.param["fStart"],
                                         self.param["fEnd"],
                                         self.param["fInterval"])

        self.imageHandler = ImageHandler(self.param["dataDate"],
                                         self.param["cameraNum"])

    def run(self):
        """
        Animates the worm algorithm (Algorithm W)
        """
        self.leThread = AnimationPreRenderer(self.imageHandler)
        self.leThread.generateDifferenceImages(1, 100, 20)
        self.exit()

    def exit(self):
        """
        Exits the GUI safely by catching the SystemExit exception
        """
        try:
            sys.exit(self.app.exec_())
        except SystemExit:
            print("Exiting Application!")




class ImageDisplay(QtGui.QWidget):
    """
    Responsible for rendering the images on screen using qt/pyqtgraph.
    """

    def __init__(self, fStart, fEnd, fInterval):
        """
        :param fStart: The number of first frame of the animation.
        :param fEnd: The number of the last frame of the animation.
        :param fInterval: The delay in milliseconds between adjacent frames.

        Initializes the GUI.
        """
        # Initialize super class
        super(self.__class__, self).__init__()

        # Initializing window and docks
        self.initializeWindow()
        self.initializeDocks()

        # Initializing Views
        self.initializeRawView()
        self.initializeHeatView()
        self.initializeRoiView()

        # Adding ImageViews to docks
        self.rawDock.addWidget(self.rawImageView)
        self.heatDock.addWidget(self.heatImageView)
        self.roiDock.addWidget(self.roiImageView)

        # Setting central widget and show
        self.window.setCentralWidget(self.dockArea)
        self.window.show()

        # Begin animation timing
        self.initializeTimer(fStart, fEnd, fInterval)

    def initializeWindow(self):
        """
        Initializes the main GUI window.
        """
        self.window = QtGui.QMainWindow()
        self.window.resize(1200, 800)
        self.window.setWindowTitle("I See Elegance. I C. Elegans")
        self.window.setContentsMargins(0, 0, 0, 0)

    def initializeDocks(self):
        """
        Initializes the dock widgets.
        """
        # Create the docking area
        self.dockArea = DockArea()
        self.dockArea.setContentsMargins(0, 0, 0, 0)

        # Raw image dock
        self.rawDock = Dock("Raw Image", size=(200, 400))
        self.rawDock.setContentsMargins(0, 0, 0, 0)

        # Heat map dock
        self.heatDock = Dock("Heat Map", size=(200, 400))
        self.heatDock.setContentsMargins(0, 0, 0, 0)

        # Region of interest dock
        self.roiDock = Dock("ROI (Tracking)", size=(200, 400))
        self.roiDock.setContentsMargins(0, 0, 0, 0)

        # Place the docks appropriately into the docking area
        self.dockArea.addDock(self.rawDock, "top")
        self.dockArea.addDock(self.heatDock, "bottom")
        self.dockArea.addDock(self.roiDock, "right", self.heatDock)

    def initializeRawView(self):
        """
        Initializes the ImageView responsible for handling the raw images.
        """
        self.rawImageView = self._generateView()

    def initializeHeatView(self):
        """
        Initializes the ImageView responsible for handling the heat images.
        """
        self.heatImageView = self._generateView()

    def initializeRoiView(self):
        """
        Initializes the ImageView responsible for handling the roi images.
        """
        self.roiImageView = self._generateView()

    def initializeTimer(self, fStart, fEnd, fInterval):
        """
        :param fStart: The number of first frame of the animation.
        :param fEnd: The number of the last frame of the animation.
        :param fInterval: The delay in milliseconds between adjacent frames.

        Initializes the timer responsible for tracking animation timing.
        """
        self.animationTimer = QtCore.QTimeLine()
        self.animationTimer.setFrameRange(fStart, fEnd)
        self.animationTimer.setUpdateInterval(fInterval)
        self.animationTimer.setDuration(fEnd*fInterval)
        self.animationTimer.valueChanged.connect(self.triggerAnimate)
        self.animationTimer.start()

    def triggerAnimate(self):
        """
        Emits a signal to indicate that an update to the gui animation
        is needed.
        """
        #TODO: Remove print statement
        print(self.animationTimer.currentFrame(),
              self.animationTimer.currentTime())
        self.emit(QtCore.SIGNAL("ANIMATE"))
        self.animationTimer.emit(QtCore.SIGNAL("ANIMATE"))

    def _generateView(self):
        """
        Generates a generic ImageView.
        """
        imageView = pg.ImageView()
        imageView.setContentsMargins(0, 0, 0, 0)
        return imageView


class AnimationPreRenderer:
    """
    Responsible for pre-rendering the output of the image filtering
    algorithms (otherwise real-time rendering is too slow).
    """

    def __init__(self, imageHandler):
        """
        A simple constructor.

        :param imageHandler: An instantiated ImageHandler object that is
        responsible for reading the correct worm frames.
        """
        self.imageHandler = imageHandler
        self.imageFilter = ImageFilter()

    def generateDifferenceImages(self, fStart, fEnd, fDiff):
        """
        Generates and saves the images responsible for showing the absolute
        difference between consecutive images.
        """
        for frame in range(fStart, fEnd):
            img1 = self.imageHandler.readFrame(frame, "raw")
            img2 = self.imageHandler.readFrame(frame + fDiff, "raw")
            diff = self.imageFilter.computeDifferenceAlgorithm(img1, img2)
            self.imageHandler.writeImage(frame, "difference", diff)



################################################################################


class ImageFilter:
    """
    Responsible for applying filtering algorithms on the images.
    """

    def __init__(self):
        """
        A simple constructor that initializes variables used to crudely
        time algorithms.
        """
        self.currentFrame = 0
        self.timeStart = None

    def computeOtsuAlgorithm(self, img, *args):
        """
        Wrapper function that simply runs the OpenCV Otsu's thresholding.

        :param img: The image to perform the algorithm on.
        :return: The outputs of the OpenCV thresholding function.
        """
        return cv2.threshold(img, *args)

    def computeDifferenceAlgorithm(self, img1, img2):
        """
        Computes the absolute difference between two frames.

        :param img1: The first image to be used in the difference.
        :param img2: The second image to be used in the difference.
        :return: The difference of two images in OpenCV format.
        """
        return cv2.absdiff(img1, img2)

    #TODO: Complete worm tracking algorithm
    def trackWormAlgorithm(self, img1, img2):
        """
        Blurs two images, takes their absolute difference, applies a local
        gaussian threshold, then attempts to find contours of the worm and
        draws a rectangle around it.

        :param fOne: Integer number of the first frame.
        :param fDiff: How many frames ahead the next image is.
        :return: The difference of two images in OpenCV format.
        """
        # Magic Parameters
        downSize = (256, 256)
        threshold = 25
        dilationIter = 10
        contourMinArea = 100   # worm ~ 200 x 10 pixels^2



        img = img1.copy()


        # Downsize images
        img1 = cv2.resize(img1, downSize, img1)
        img2 = cv2.resize(img2, downSize, img2)

        # Computes the absolute difference
        diff = cv2.absdiff(img1, img2)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Applies global thresholding to binary
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

        # Dilates image to fill gaps and finding all contours
        dillation = cv2.dilate(thresh, None, iterations=dilationIter)
        contours = cv2.findContours(dillation.copy(),
                                         cv2.RETR_EXTERNAL,
                                         cv2.CHAIN_APPROX_SIMPLE)


        img = cv2.cvtColor(diff, cv2.COLOR_GRAY2BGR)



        # Extracting only sufficiently large contours and drawing a
        # rectangle around them
        for c in contours:
            if cv2.contourArea(c) < contourMinArea:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
#            print("Contours Rectangle at: (%d %d) (%d %d)" % (x, y, w, h))
#            print("Contours Area: %d " % cv2.contourArea(c))
            cv2.rectangle(img, (x, y), (x+w, y+h), (170, 0, 0), 2)


        return img

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


class ImageHandler:
    """
    Responsible for handling image reading and writing.
    """

    def __init__(self, dataDate, cameraNum):
        """
        A simple constructor.

        :param dataDate: The date the data was recorded (e.g. '2016_02_22').
        :param cameraNum: The camera number that took the images.
        directory.
        """
        self.date = dataDate
        self.camera = "camera_" + str(cameraNum)

    def readFrame(self, fNum, fType, flag=1):
        """
        Reads a worm image for the given frame number and image type using
        OpenCV read.

        The frames must be named chronologically using the form
        "frame_0000XY.png", where six digits (can be leading zeros) are
        present after the frame prefix.

        :param fNum: The frame number to be read.
        :param fType: The choices can be from ["raw", "difference", "heat"].
        :param flag: The flag for the OpenCV image read method.
        :return: An image in OpenCV format.
        """
        dir = self._generateDirPath(fType)
        frame = "frame_%06d.png" % fNum
        fPath = os.path.join(dir, frame)

        if os.path.exists(fPath):
            return cv2.imread(fPath, flag)
        else:
            raise NameError("Could not find images hosted in an existing "
                            "directory! The path %s does not exist" % fPath)

    def writeImage(self, fNum, fType, image, args=None):
        """
        Writes the given image to the appropriate directory type with the
        given frame number.

        :param fNum: The frame number to be read.
        :param fType: The choices can be from ["raw", "difference", "heat"].
        :param image: The image to be saved.
        :param args: Any args that can thrown to OpenCV image write.
        """
        dir = self._generateDirPath(fType)
        frame = "frame_%06d.png" % fNum
        fPath = os.path.join(dir, frame)
        cv2.imwrite(fPath, image, args)

    def _generateDirPath(self, fType):
        """
        Generates the absolute path to a directory that hosts the the images
        for given type of frame. This requires a specific folder structure to
        work correctly.

        :param fType: A choice of ("raw", "heat", "difference")
        :return: A string of the absolute path to a worm image.
        """
        path = ["..", "..", "assets", "images", self.date, self.camera, fType]
        relPath = os.path.join(*path)
        absPath = os.path.abspath(relPath)

        # Attempts to create missing directories
        availableTypes = ["raw", "difference", "heat"]
        if not os.path.exists(absPath) and fType in availableTypes:
            os.makedirs(absPath)

        if os.path.exists(absPath):
            return absPath
        else:
            raise NameError("A directory hosting images seems to be missing! "
                            "The path %s does not exist" % absPath)


if __name__ == "__main__":

    #TODO: Document parameters that can be modified in all called methods
    param = \
    {
        "fStart":       1,
        "fEnd":         500,
        "fInterval":    100,   # milliseconds
        "fDiff":        20,
        "dataDate":     "2016_06_15",
        "cameraNum":    "1",
    }

    # Run
    imageController = ImageController(param)
    imageController.run()
