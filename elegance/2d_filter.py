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
from pyqtgraph import QtCore, QtGui, dockarea

import pyqtgraph.examples
#pyqtgraph.examples.run()


class ImageController:
    """
    Responsible for coordinating the GUI with the core image processing
    algorithms.
    """

    def __init__(self, args):
        """
        A simple constructor.

        :args param: A dictionary containing all the control parameters.
        """
        self.args = args
        self.imageHandler = ImageHandler(self.args["dataDate"],
                                         self.args["cameraNum"])
        self.initializeGUI()

    def initializeGUI(self):
        """
        Initializes the Qt GUI framework and application.
        """
        self.app = QtGui.QApplication(sys.argv)
        self.imageDisplay = ImageDisplay(self.args["fStart"],
                                         self.args["fEnd"],
                                         self.args["fInterval"],
                                         self.args["fSpeedFactor"],
                                         self.imageHandler)

    def preRenderAllAnimation(self):
        """
        Generates the images for all possible animations.
        """
        preRenderer = AnimationPreRenderer(self.imageHandler)
        preRenderer.generateOtsuImages(self.args["fStart"], self.args["fEnd"])
        preRenderer.generateDifferenceImages(self.args["fStart"],
                                             self.args["fEnd"],
                                             self.args["fDiff"])
        preRenderer.generateWormTrackingImages(self.args["fStart"],
                                               self.args["fEnd"],
                                               self.args["fDiff"])

    def runAnimation(self):
        """
        Runs the GUI worm images animation.
        """
        self.imageDisplay.animationTimer.start()
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

    def __init__(self, fStart, fEnd, fInterval, fSpeedFactor, imageHandler):
        """
        :param fStart: The number of first frame of the animation.
        :param fEnd: The number of the last frame of the animation.
        :param fInterval: The delay in milliseconds between adjacent frames.
        :param fSpeedFactor: Integer times the speed of the animation
        :param imageHandler: An instantiated ImageHandler object that is
        responsible for reading and writing to the correct directories.

        Initializes the GUI.
        """
        # Initialize super class and instance variables
        super(self.__class__, self).__init__()
        self.imageHandler = imageHandler

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
        self.initializeTimer(fStart, fEnd, fInterval, fSpeedFactor)

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
        self.dockArea = pg.dockarea.DockArea()
        self.dockArea.setContentsMargins(0, 0, 0, 0)

        # Raw image dock
        self.rawDock = pg.dockarea.Dock("Raw Image", size=(200, 400))
        self.rawDock.setContentsMargins(0, 0, 0, 0)

        # Heat map dock
        self.heatDock = pg.dockarea.Dock("Heat Map", size=(200, 400))
        self.heatDock.setContentsMargins(0, 0, 0, 0)

        # Region of interest dock
        self.roiDock = pg.dockarea.Dock("ROI (Tracking)", size=(200, 400))
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

    def initializeTimer(self, fStart, fEnd, fInterval, fSpeedFactor):
        """
        :param fStart: The number of first frame of the animation.
        :param fEnd: The number of the last frame of the animation.
        :param fInterval: The delay in milliseconds between adjacent frames.
        :param fSpeedFactor: Integer times the speed of the animation

        Initializes the timer responsible for tracking animation timing.
        """
        duration = fSpeedFactor * fInterval * (fEnd - fStart)
        self.animationTimer = QtCore.QTimeLine()
        self.animationTimer.setFrameRange(fStart, fEnd)
        self.animationTimer.setUpdateInterval(fInterval)
        self.animationTimer.setDuration(duration)
        self.animationTimer.valueChanged.connect(self.updateAnimation)

    def updateAnimation(self):
        """
        Updates the animation displayed by changing the worm frame
        being displayed.
        """
        frame = self.animationTimer.currentFrame()
        time = self.animationTimer.currentTime()
        print("Frame: %d, Time: %.3f seconds" % (frame, time/1000.0))

        # Update raw animation
        #raw = self.imageHandler.readFrame(frame, "raw")
        #raw = cv2.resize(raw, (512, 512), raw)
        #self.rawImageView.setImage(raw,
        #                           autoRange=False,
        #                           autoLevels=False,
        #                           autoHistogramRange=False)

        # Update tracking animation
        track = self.imageHandler.readFrame(frame, "track")
        self.heatImageView.setImage(track,
                                    autoRange=False,
                                    autoHistogramRange=False)

        # Update difference animation
        #diff = self.imageHandler.readFrame(frame, "difference")
        #self.heatImageView.setImage(diff,
        #                            autoRange=False,
        #                            autoHistogramRange=False)

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
        responsible for reading and writing to the correct directories.
        """
        self.imageHandler = imageHandler
        self.imageFilter = ImageFilter()

    def generateWormTrackingImages(self, fStart, fEnd, fDiff):
        """
        :param fStart: The number of first frame.
        :param fEnd: The number of the last frame.
        :param fDiff: The difference range between two consecutive frames.

        Generates and saves the images that show worm tracking algorithm.
        """
        print(">>> PRE-RENDERING WORM TRACKING IMAGES STARTING <<<")

        for f in range(fStart, fEnd+1):
            print("Worm tracking rendering progress: %d/%d frames" % (f, fEnd))
            img1 = self.imageHandler.readFrame(f, "raw")
            img2 = self.imageHandler.readFrame(f+ fDiff, "raw")
            track = self.imageFilter.computeWormTrackingAlgorithm(img1, img2)
            self.imageHandler.writeImage(f, "track", track)

        print(">>> PRE-RENDERING WORM TRACKING IMAGES COMPLETE <<<")

    def generateDifferenceImages(self, fStart, fEnd, fDiff):
        """
        :param fStart: The number of first frame.
        :param fEnd: The number of the last frame.
        :param fDiff: The difference range between two consecutive frames.

        Generates and saves the images that show the absolute difference
        between consecutive images.
        """
        print(">>> PRE-RENDERING DIFFERENCE IMAGES STARTING <<<")

        for f in range(fStart, fEnd+1):
            print("Difference rendering progress: %d/%d frames" % (f, fEnd))
            img1 = self.imageHandler.readFrame(f, "raw")
            img2 = self.imageHandler.readFrame(f + fDiff, "raw")
            diff = self.imageFilter.computeDifferenceAlgorithm(img1, img2)
            self.imageHandler.writeImage(f, "difference", diff)

        print(">>> PRE-RENDERING DIFFERENCE IMAGES COMPLETE <<<")

    def generateOtsuImages(self, fStart, fEnd):
        """
        :param fStart: The number of first f.
        :param fEnd: The number of the last f.

        Generates and saves the images that show Otsu's thresholding.
        """
        print(">>> PRE-RENDERING OTSU IMAGES STARTING <<<")

        for f in range(fStart, fEnd+1):
            print("Otsu rendering progress: %d/%d frames" % (f, fEnd))
            img = self.imageHandler.readFrame(f, "raw")
            args = (img, 127, 255, cv2.THRESH_BINARY)
            _, thresh = self.imageFilter.computeOtsuAlgorithm(*args)
            self.imageHandler.writeImage(f, "otsu", thresh)

        print(">>> PRE-RENDERING OTSU IMAGES COMPLETE <<<")


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
    def computeWormTrackingAlgorithm(self, img1, img2):
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

        # worm ~200x10 pixels^2
        contourMinArea = 1000

        img = img1.copy()

        # Downsize images
        #img1 = cv2.resize(img1, downSize, img1)
        #img2 = cv2.resize(img2, downSize, img2)

        # Computes the absolute difference
        diff = cv2.absdiff(img1, img2)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Applies global thresholding to binary
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

        # Dilates image to fill gaps and finding all contours
        dillation = cv2.dilate(thresh, None, iterations=dilationIter)
        _, contours, _ = cv2.findContours(dillation.copy(),
                                         cv2.RETR_TREE,
                                         cv2.CHAIN_APPROX_SIMPLE)

        #cv2.drawContours(img, contours, -1, (0,255,0), 3)

        # Extracting only sufficiently large contours and drawing a
        # rectangle around them
        for c in contours:
            if cv2.contourArea(c) < contourMinArea:
                continue

            (x, y, w, h) = cv2.boundingRect(c)
            #print("Contours Rectangle at: (%d %d) (%d %d)" % (x, y, w, h))
            #print("Contours Area: %d " % cv2.contourArea(c))
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 170), 2)


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
        availableTypes = ["raw", "otsu", "difference", "track", "heat"]
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
        "fStart":           1,
        "fEnd":             50,
        "fInterval":        1000,   # milliseconds
        "fDiff":            20,
        "fSpeedFactor":     1,
        "dataDate":         "2016_06_15",
        "cameraNum":        "1",
    }

    # Pre-render animation
    imageHandler = ImageHandler(param["dataDate"], param["cameraNum"])
    preRenderer = AnimationPreRenderer(imageHandler)
    #preRenderer.generateWormTrackingImages(param["fStart"],
    #                                       param["fEnd"],
    #                                       param["fDiff"])

    # Display animation
    imageController = ImageController(param)
    imageController.runAnimation()
