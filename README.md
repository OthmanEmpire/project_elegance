## Project Elegance: Computer Vision with C. Elegans
The aim of this project is to build some tools that would assist in analysing
the behaviour of the worm (Caenorhabditis Elegans) in real-time. The particular
focus is developing an algorithm that can track the worm as it moves in a
three-dimensional environment.

Project Elgance was one of my summer internship projects and was halted due to
a shift in business needs so the algorithm remains incomplete.

![](data/video/tracker.gif)


## Key Features
* Implementation of several image filtering algorithms to track the worm.
* Capability of pre-rendering the 2D images for each tracking algorithm.
* Playing the 2D images as an animation using pyqtgraph.
* Ability to generate test images to study the tracking algorithms.


## Requirements (see requirements.txt)
* Python 3+
  * OpenCV 3.1.0
  * pyqtgraph  0.10.0


## Authors
* Author: Othman Alikhan, oz.alikhan@gmail.com
* Supervisors: Dr. Netta Cohen, Dr. Thomas Ranner, Dr. Robert Holbrook


## Credits
1. Input data (C. elegans movie):
    Movie S1 from Kwon N, Pyo J, Lee S, Je J (2013). "3-D Worm Tracker for
    Freely Moving C. elegans". PLOS ONE. DOI:10.1371/journal.pone.0057484.
    PMID 23437394.
