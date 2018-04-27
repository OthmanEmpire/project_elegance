"""
Module that contains the computer vision algorithms of project elegancc.
"""


import os
import cv2


class ImageHandler:
    """
    Responsible for handling image reading and writing.
    """

    def readFrame(self, fNum, fType, flag=1):
        """
        Reads a worm image for the given frame number and image type using
        OpenCV read.

        The frames must be named chronologically using the form
        "frame_0000XY", where six digits (can be leading zeros) are
        present after the frame prefix.

        :param fNum: The frame number to be read.
        :param fType: The choices can be from ["raw", "difference", "heat"].
        :param flag: The flag for the OpenCV image read method.
        :return: An image in OpenCV format.
        """
        dir = self._generateDirPath(fType)
        jFrame = "frame_%06d.jpeg" % fNum
        jPath = os.path.join(dir, jFrame)

        pFrame = "frame_%06d.png" % fNum
        pPath = os.path.join(dir, pFrame)

        if os.path.exists(jPath):
            return cv2.imread(jPath, flag)
        elif os.path.exists(pPath):
            return cv2.imread(pPath, flag)
        else:
            raise NameError("Could not find the input images in an existing "
                            "directory!\n%s\n%s" % (pPath, jPath))

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
        frame = "frame_%06d.jpeg" % fNum
        fPath = os.path.join(dir, frame)
        cv2.imwrite(fPath, image, args)

    def _generateDirPath(self, fType):
        """
        Generates the absolute path to a directory that hosts the the images
        for given type of frame. This requires a specific folder structure to
        work correctly.

        :param fType: A choice of ("raw", "heat", "difference")
        :param dirPath: A path to the directory hosting the data.
        :return: A string of the absolute path to a worm image.
        """
        path = ["..", "data", "images", fType]
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

