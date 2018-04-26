"""
Module that contains the computer vision algorithms of project elegancc.
"""


import cv2
import time


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
