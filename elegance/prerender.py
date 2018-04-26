"""
Module that contains the computer vision algorithms of project elegancc.
"""

import cv2
from filter import ImageFilter


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
            img2 = self.imageHandler.readFrame(f + fDiff, "raw")
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
