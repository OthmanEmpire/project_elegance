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
import math

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
        Initializes the GUI.

        :param fStart: The number of first frame of the animation.
        :param fEnd: The number of the last frame of the animation.
        :param fInterval: The delay in milliseconds between adjacent frames.
        :param fSpeedFactor: Integer times the speed of the animation
        :param imageHandler: An instantiated ImageHandler object that is
        responsible for reading and writing to the correct directories.
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
        #self.dockArea.addDock(self.rawDock, "top")
        self.dockArea.addDock(self.heatDock, "bottom")
        #self.dockArea.addDock(self.roiDock, "right", self.heatDock)

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
        Initializes the timer responsible for tracking animation timing.

        :param fStart: The number of first frame of the animation.
        :param fEnd: The number of the last frame of the animation.
        :param fInterval: The delay in milliseconds between adjacent frames.
        :param fSpeedFactor: Integer times the speed of the animation
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
        track = self.imageHandler.readFrame(frame, "heat")
        self.heatImageView.setImage(track,
                                    autoLevels=False,
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

    def generateTestTrackImages(self, fStart, fEnd):
        """
        Generates some mock track images to test tracking algorithms on. The
        images generated is essentially a sequence of white images where a
        black circle is following a circular trajectory.

        :param fStart: The number of first frame.
        :param fEnd: The number of the last frame.
        """
        print(">>> PRE-RENDERING TRACK TEST IMAGES STARTING <<<")

        # Creating a blank white image
        imgSize = (height, width) = (2048, 2048)
        blank = np.zeros(imgSize, dtype="uint16")
        blank = cv2.bitwise_not(blank)  # Making image white

        # Initializing the moving circle
        movRadius = 100
        movColour = (0, 150, 0)
        isMovFill = -1     # Negative numbers imply filling

        # Initializing the circular trajectory
        trajAngle = 0
        trajRadius = height / 3     # Hoping that height == width
        trajOrigin = (width / 2, height / 2)

        numRevolutions = 2
        totalMoves = (2 * math.pi * trajRadius) * numRevolutions
        movePerStep = totalMoves / (fEnd - fStart)
        anglePerStep = (movePerStep / trajRadius)

        for f, step in enumerate(range(fStart, fEnd+1), start=1):
            print("Test track images rendering progress: %d/%d frames"
                  % (f, fEnd))
            img = blank.copy()

            trajAngle += anglePerStep
            movX = trajRadius * math.cos(trajAngle) + trajOrigin[0]
            movY = trajRadius * math.sin(trajAngle) + trajOrigin[1]
            cv2.circle(img, (int(movX), int(movY)),
                       movRadius, movColour, isMovFill)

            self.imageHandler.writeImage(f, "track", img)

        print(">>> PRE-RENDERING TRACK TEST IMAGES COMPLETE <<<")

    #TODO: WORKING ! !
    # 1. The white background slowly fades to darkness due to summation of
    # small evils
    # 2. Wierd colour adding/changing on the moving black circle
    def generateHeatImages(self, fStart, fEnd):
        """
        Builds a heat map of the worm locomotion activity via averaging out a
        sequence of images produced by the worm tracking algorithm.

        :param fStart: The number of first frame.
        :param fEnd: The number of the last frame.
        """
        print(">>> PRE-RENDERING HEAT MAP IMAGES STARTING <<<")

        # Initializing heat map
        img = self.imageHandler.readFrame(1, "track")
        height, width, _ = img.shape
        heat = np.zeros((height, width), dtype="uint8")

        for f in range(fStart, fEnd+1):
            print("Heat map rendering progress: %d/%d frames" % (f, fEnd))
            img = self.imageHandler.readFrame(f, "track")
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            heat += cv2.add(img, heat)
            print(heat)

            self.imageHandler.writeImage(f, "heat", heat)

        print(">>> PRE-RENDERING HEAT MAP IMAGES COMPLETE <<<")

    def generateWormTrackingImages(self, fStart, fEnd, fDiff):
        """
        Generates and saves the images that show worm tracking algorithm.

        :param fStart: The number of first frame.
        :param fEnd: The number of the last frame.
        :param fDiff: The difference range between two consecutive frames.
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
        Generates and saves the images that show the absolute difference
        between consecutive images.

        :param fStart: The number of first frame.
        :param fEnd: The number of the last frame.
        :param fDiff: The difference range between two consecutive frames.

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
        Generates and saves the images that show Otsu's thresholding.

        :param fStart: The number of first f.
        :param fEnd: The number of the last f.
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

    def computeWormTrackingAlgorithm(self, img1, img2):
        """
        By using various image analysis techniques, attempts to image track
        the worm for the first image in the given images.

        :param img1: The first worm image.
        :param img2: The second worm image to be differenced from.
        """
        estimateData = self.estimateWormPosition(img1, img2)
        return estimateData["image"]

    #TODO: Improve worm tracking algorithm so that it memorizes worm location
    def estimateWormPosition(self, img1, img2):
        """
        Estimates the worm position on a 2D image and bounds it by a circle.

        This is done via down sizing two images using linear interpolation,
        taking their absolute difference, thresholding to remove background
        noise, dillating the resultant image to connect worm segments, then
        finding the contours of the worm.

        :param img1: The first worm image.
        :param img2: The second worm image to be differenced from.
        :return: A dictionary containing the image with the worm bounded,
        the radius of the circle, and the center of the circle.
        """
        # Magic Parameters
        radiusError = 1
        sizeFactor = 10
        threshold = 25
        dilationIter = 10
        contourMinArea = 1000       # worm ~200x10 pixels^2
        height, width, _ = img1.shape
        downSize = (height/sizeFactor, width/sizeFactor)

        # Initializing a blank image
        blank = np.zeros(img1.shape, dtype=img1.dtype)
        blank = cv2.bitwise_not(blank, blank)
        cv2.circle(blank, (height/2, width/2), (height/2), (255, 0, 0), 2)

        # Downsize images
        #img1 = cv2.resize(img1, downSize, img1)
        #img2 = cv2.resize(img2, downSize, img2)

        # Computes the absolute difference
        diff = cv2.absdiff(img1, img2)
        diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # Applies global threshold and converts to binary
        _, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

        # Dilates image to fill all worm gaps and finds all contours
        dillation = cv2.dilate(thresh, None, iterations=dilationIter)
        _, contours, _ = cv2.findContours(dillation,
                                         cv2.RETR_TREE,
                                         cv2.CHAIN_APPROX_SIMPLE)

        radius = 0
        center = 0

        # Bounding only sufficiently large contours by a circle
        for c in contours:
            break
            if cv2.contourArea(c) < contourMinArea / sizeFactor**2:
                print("Contour Area Ignored: %d " % cv2.contourArea(c))
                continue

            # Rescaling circle parameters to map onto original image
            (x, y), radius = cv2.minEnclosingCircle(c)
            center = (int(x * sizeFactor), int(y * sizeFactor))
            radius = int(radius * sizeFactor/2 * radiusError)
            #cv2.circle(blank, center, radius, (0, 0, 100), -1)

        cv2.drawContours(blank, contours, -1, (0, 0, 100))


        estimateData = \
            {
                "image":    blank,
                "radius":   radius,
                "center":   center
            }

        return estimateData

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

    availableTypes = ["raw", "otsu", "difference", "track", "heat"]

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
        :param fType: The choices are in the class variable availabeTypes
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

        :param fType: The choices are in the class variable availabeTypes
        :return: A string of the absolute path to a worm image.
        """
        path = ["..", "..", "assets", "images", self.date, self.camera, fType]
        relPath = os.path.join(*path)
        absPath = os.path.abspath(relPath)

        # Attempts to create missing directories
        if not os.path.exists(absPath) and fType in ImageHandler.availableTypes:
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
        "fEnd":             1000,
        "fInterval":        100,   # milliseconds
        "fDiff":            20,
        "fSpeedFactor":     1,
        "dataDate":         "9999_99_99",   #"2016_06_15",
        "cameraNum":        "1",
    }

    # Pre-render animation
    imageHandler = ImageHandler(param["dataDate"], param["cameraNum"])
    #preRenderer = AnimationPreRenderer(imageHandler)
    #preRenderer.generateWormTrackingImages(param["fStart"],
    #                                       param["fEnd"],
    #                                       param["fDiff"])
    #preRenderer.generateTestTrackImages(1, 1000)
    #preRenderer.generateHeatImages(param["fStart"], param["fEnd"])


    # Display animation
    imageController = ImageController(param)
    imageController.runAnimation()
