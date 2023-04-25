# Paper-to-Pad-Image-Processing
![Demo Drawing](https://github.com/lennart-rth/Paper_to_Pad_Image_Processing/blob/master/test.png)

The Pen-to-Mouse Tracker is an open-source Python project that uses image processing techniques to track the movement of a pen on paper and transfer it to the mouse. It can be used to draw and write on online collaborative drawing tools or image editing software like GIMP just like using an Tablet.
Benefits and Caveats

## Benefits:
- Allows users to see their drawing on analog paper while also digitalizing it live.
- By uploading a video, one can digitalize their drawing/writing at a later time. (e.g. write notes and listen to a lecture and the digitize later when at home.)
- detailed Settings for fineTuning int the `config.py` file

## Caveats:
- Only works with one color pen that is visually different from the paper color.
- Automated mouse movement is not supported on Ubuntu Wayland.

## How to Use
1. Clone the repository to your local machine.
2. Install dependencies by running `pip install -r requirements.txt`
3. Connect your camera and ensure that it is being detected.
4. Run the pen_to_mouse.py script.
5. If using a video stream, uncomment and edit the line "capture = cv2.VideoCapture("http://192.168.178.54:4747/video")" to add your stream.
6. If using a prerecorded video, uncomment and edit the line "capture = cv2.VideoCapture("test.MOV")" to add your file.
7. Calibrate the pen by hovering over it with the mouse and pressing the "a" key. You can adjust the sliders on the bottom of the window until the outline of the pen is detected correctly.
8. Mark the edges of the paper by hovering over a corner with the mouse and pressing the "c" key. The order is not importand.
9. Reset the paper calibration by pressing the "r" key if needed.
10. Tweak mouse_sensitivity slider to match desired sensitivity in pen-to-mouse movement.
11. Start tracking the pen tip and transferring movement to the mouse by pressing the "alt" key.
12. "Lift and drop" the pen onto the paper by pressing the "space" key to click the mouse down or up.
13. Quit the program by pressing the "q" key.


## Key Bindings
- "a": Calibrate the pen.
- "c": Mark the edges of the paper. The order is not importand.
- "r": Reset the paper calibration.
- "alt": Start tracking the pen tip and transferring movement to the mouse.
- "space": "Lift and drop" the pen onto the paper by clicking the mouse down or up.
- "q": Quit the program.

## Dependencies
1.  mouse==0.7.1
2.  numpy==1.23.4
3.  opencv_python==4.6.0.66
4.  pynput==1.7.6
5.  scipy==1.10.1
