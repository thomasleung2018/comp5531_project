# import the necessary packages
from imutils.video import VideoStream
from flask import Response, request
from flask import Flask
from flask import render_template
from flask import send_from_directory
import threading
import argparse
import time
import cv2
import pyautogui
import pydirectinput
import win32api, win32con, win32gui

code2key = {
    '27': 'esc',
    '14': 'backspace',
    '8': 'backspace',
    '13': 'enter',
    '32': 'space',
    '37': 'left',
    '38': 'up',
    '39': 'right',
    '40': 'down',
    '45': 'insert',
    '46': 'delete',
    '65': 'a',
    '68': 'd',
    '82': 'r',
    '83': 's',
    '87': 'w',
    '90': 'z',
}

from window_capture import WindowCapture
#wincap = WindowCapture("League of Legends (TM) Client")
wincap = WindowCapture("Baba is You")

outputFrame = None
lock = threading.Lock()

app = Flask(__name__, template_folder='')

vs = VideoStream(src=0).start()
time.sleep(2.0)

@app.route("/")
def index():
    return render_template("index.html")


def cap_video(frameCount):
    global vs, outputFrame, lock
    while True:
        frame = wincap.get_screenshot()

        with lock:
            outputFrame = frame.copy()


def generate():
    global outputFrame, lock

    while True:
        with lock:
            if outputFrame is None:
                continue

            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            if not flag:
                continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/video_feed")
def video_feed():
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/control", methods=['GET', 'POST'])
def control():
    key = request.args.get('key')
    if key in code2key:
        pydirectinput.press(code2key[key])
    else:
        return "no this key"
    return key

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())

    t = threading.Thread(target=cap_video, args=(
        args["frame_count"],))
    t.daemon = True
    t.start()

    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)

vs.stop()
