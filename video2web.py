# import the necessary packages
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import argparse
import time
import cv2
import pyautogui
import pydirectinput
import win32api, win32con, win32gui

from window_capture import WindowCapture
#wincap = WindowCapture("League of Legends (TM) Client")
wincap = WindowCapture("Baba is You")

outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to
vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")


def cap_video(frameCount):
    # grab global references to the video stream, output frame, and
    # lock variables
    global vs, outputFrame, lock
    # loop over frames from the video stream
    while True:
        frame = wincap.get_screenshot()

        with lock:
            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/control/r", methods=['GET'])
def r():
    print("r")
    pydirectinput.press('r')
    return 'r'

@app.route("/control/d", methods=['GET'])
def d():
    print("d")
    pydirectinput.press('d')
    return 'd'

@app.route("/control/f", methods=['GET'])
def f():
    print("f")
    pydirectinput.press('f')
    return 'f'

@app.route("/control/up", methods=['GET'])
def up():
    print("up")
    pydirectinput.press('up')
    return 'up'

@app.route("/control/down", methods=['GET'])
def down():
    print("down")
    pydirectinput.press('down')
    return 'down'

@app.route("/control/left", methods=['GET'])
def left():
    print("left")
    pydirectinput.press('left')
    return 'left'

@app.route("/control/right", methods=['GET'])
def right():
    print("right")
    pydirectinput.press('right')
    return 'right'

@app.route("/control/enter", methods=['GET'])
def enter():
    print("enter")
    pydirectinput.press('enter')
    return 'enter'

# check to see if this is the main thread of execution
if __name__ == '__main__':
    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    # start a thread that will perform motion detection
    t = threading.Thread(target=cap_video, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

vs.stop()
