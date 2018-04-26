"""
###############################################################################
# A script to read a series of worm images, apply some filters, and then      #
# attempt to display the results real-time using pyqtgraph                    #
#                                                                             #
# __author__ = "Othman Alikhan"                                               #
# __email__ =  "sc14omsa@leeds.ac.uk"                                         #
# __date__ = "2016-07-15"                                                     #
###############################################################################
"""
import os
import sys
import time

import cv2
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui, dockarea

import pyqtgraph.examples
#pyqtgraph.examples.run()

from data import ImageHandler
from prerender import AnimationPreRenderer
from filter import ImageFilter
from gui import ImageDisplay


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
        self.imageHandler = ImageHandler()
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


if __name__ == "__main__":

    param = \
    {
        "fStart":           1,
        "fEnd":             100,
        "fInterval":        500,   # milliseconds
        "fDiff":            1,
        "fSpeedFactor":     1,
        "dataDate":         "2016_06_15",
        "cameraNum":        "1",
    }

    # Pre-render animation (generating images to be graphed in advance)
    # imageHandler = ImageHandler(param["dataDate"], param["cameraNum"])
    # preRenderer = AnimationPreRenderer(imageHandler)
    # preRenderer.generateWormTrackingImages(param["fStart"],
    #                                       param["fEnd"],
    #                                       param["fDiff"])
    # preRenderer.generateDifferenceImages(param["fStart"],
    #                                        param["fEnd"],
    #                                        param["fDiff"])
    # preRenderer.generateOtsuImages(param["fStart"],
    #                                param["fEnd"])

    # Display animation
    imageController = ImageController(param)
    imageController.preRenderAllAnimation()
    imageController.runAnimation()
