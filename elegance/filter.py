"""
Module that contains the computer vision algorithms of project elegancc.
"""


import cv2
import time


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)


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

    def computeWormTrackingAlgorithm(self, img):
        """
        Converts the image to grayscale, applies a binary threshold, dilates
        the image, then finds contours. Afterwards, draws contours with
        sufficient area size onto the image.

        :param img: An image.
        :return: An image resulting from applying the algorithm on the input.
        """
        # Magic Parameters
        dilationIter = 3

        # worm ~150x15 = 2250 pixels^2
        contourMinArea = 500
        contourMaxArea = 3000

        # Converts the image to grayscale
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Applies global thresholding to binary
        _, thresh = cv2.threshold(img, 30, 255, cv2.THRESH_BINARY)

        # Erodes the image to improve quality of contours
        # Note: Erodes instead of Dilate because binary image is 'reversed'
        erode = cv2.erode(thresh, None, iterations=dilationIter)
        _, contours, _ = cv2.findContours(erode,
                                          cv2.RETR_TREE,
                                          cv2.CHAIN_APPROX_NONE)

        # Draws all contours
        # track = cv2.drawContours(img, contours, -1, GRAY)

        # Extracting only sufficiently large contours and drawing a
        # rectangle around them (idea is to track the worm)
        for c in contours:
            if contourMaxArea > cv2.contourArea(c) > contourMinArea:
                (x, y, w, h) = cv2.boundingRect(c)
                cv2.rectangle(img, (x, y), (x+w, y+h), WHITE, 2)
                # print("Contours Rectangle at: (%d %d) (%d %d)" % (x, y, w, h))
                # print("Contours Area: %d " % cv2.contourArea(c))

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
            track = self.imageFilter.computeWormTrackingAlgorithm(img1)
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
