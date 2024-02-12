from flask import Flask, render_template, Response, request
import cv2
import dlib
import numpy as np
import os
import shutil
import logging
import time

app = Flask(__name__)

# Initialize face detector
detector = dlib.get_frontal_face_detector()

# Global variables
camera = cv2.VideoCapture(0)
path_photos_from_camera = "data/data_faces_from_camera/"
existing_faces_cnt = 0

# Function to clear old data
def clear_data():
    global existing_faces_cnt
    folders_rd = os.listdir(path_photos_from_camera)
    for i in range(len(folders_rd)):
        shutil.rmtree(path_photos_from_camera + folders_rd[i])
    if os.path.isfile("data/features_all.csv"):
        os.remove("data/features_all.csv")
    existing_faces_cnt = 0
    return "Face images and `features_all.csv` removed!"

# Function to create face folder
def create_face_folder(input_name_char):
    global existing_faces_cnt
    existing_faces_cnt += 1
    current_face_dir = path_photos_from_camera + "person_" + str(existing_faces_cnt) + "_" + input_name_char
    os.makedirs(current_face_dir)
    return "\"" + current_face_dir + "/\" created!"

# Function to save current face
def save_current_face():
    if current_frame_faces_cnt == 1:
        if not out_of_range_flag:
            ss_cnt = save_current_face.ss_cnt
            # Create blank image according to the size of face detected
            face_ROI_image = np.zeros((int(face_ROI_height * 2), face_ROI_width * 2, 3), np.uint8)
            for ii in range(face_ROI_height * 2):
                for jj in range(face_ROI_width * 2):
                    face_ROI_image[ii][jj] = current_frame[face_ROI_height_start - hh + ii][face_ROI_width_start - ww + jj]
            save_current_face.log_all = "\"" + current_face_dir + "/img_face_" + str(ss_cnt) + ".jpg\"" + " saved!"
            face_ROI_image = cv2.cvtColor(face_ROI_image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(current_face_dir + "/img_face_" + str(ss_cnt) + ".jpg", face_ROI_image)
            return "%s/img_face_%s.jpg" % (current_face_dir, ss_cnt)
        else:
            return "Please do not out of range!"
    else:
        return "No face in current frame!"

# Generator function to stream video frames
def gen_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/')
def index():
    return render_template('indexx.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/register_face', methods=['POST'])
def register_face():
    global current_frame_faces_cnt, face_ROI_width_start, face_ROI_height_start, face_ROI_width, face_ROI_height, hh, ww, out_of_range_flag, current_frame, current_face_dir

    input_name_char = request.form.get('name')
    current_frame_faces_cnt = int(request.form.get('faces_cnt'))
    face_ROI_width_start = int(request.form.get('width_start'))
    face_ROI_height_start = int(request.form.get('height_start'))
    face_ROI_width = int(request.form.get('width'))
    face_ROI_height = int(request.form.get('height'))
    hh = int(face_ROI_height / 2)
    ww = int(face_ROI_width / 2)
    out_of_range_flag = request.form.get('out_of_range') == 'True'
    current_frame = np.fromstring(request.form.get('frame'), dtype=np.uint8).reshape((480, 640, 3))
    current_face_dir = create_face_folder(input_name_char)
    save_current_face.log_all = save_current_face()

    return save_current_face.log_all


if __name__ == '__main__':
    app.run(debug=True)
