"""
Module that contains the GUI elements of project elegancc.
"""
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui, dockarea

import pyqtgraph.examples
#pyqtgraph.examples.run()


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
        self.heatDock = pg.dockarea.Dock("Difference", size=(200, 400))
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
        raw = self.imageHandler.readFrame(frame, "raw")
        self.rawImageView.setImage(raw,
                                   autoRange=False,
                                   # autoLevels=False,
                                   autoHistogramRange=False)

        # Update tracking animation
        track = self.imageHandler.readFrame(frame, "track")
        self.roiImageView.setImage(track,
                                   autoRange=False,
                                   autoHistogramRange=False)

        # Update difference animation
        diff = self.imageHandler.readFrame(frame, "difference")
        self.heatImageView.setImage(diff,
                                    autoRange=False,
                                    autoHistogramRange=False)

    def _generateView(self):
        """
        Generates a generic ImageView.
        """
        imageView = pg.ImageView()
        imageView.setContentsMargins(0, 0, 0, 0)
        return imageView
