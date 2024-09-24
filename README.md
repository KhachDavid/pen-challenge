# Pen Challenge

This project used:
- Realsense Camera d435i 
- OpenCV 
- Pincher 100x robot

After finding the coordinates of the pen using the camera, they are transformed into pincher 100x's coordinate system.

The robot received an instruction to go to that location and grab the pen.

The transformation is made possible due to an initial calibration where the transformation matrix is found.

Calibration can be run using the following command:
```
python3 main.py -c
```
More setup instructions can be found in the **Who Stole My Pen_.pdf** file

# Demo

[Demo](demo.mp4)