from app import app
from flask import render_template
from flask import request
from inout.facerecognition.VideoCamera import VideoCamera
from flask import Flask, render_template, Response
import face_recognition
import cv2
from flask import Blueprint, current_app, send_file, url_for, jsonify
from flask import Flask, render_template, Response, jsonify, request
import numpy as np
import os
import sys
import qrcode
from qrcode import QRCode
from base64 import urlsafe_b64encode, urlsafe_b64decode
from mimetypes import types_map
from io import BytesIO
import cStringIO


video_camera = None
global_frame = None
face_rep = None
constituency = None
face_rep_times = 0

@app.route('/')
@app.route('/index')
def index():
    return render_template('landing.html')

# Register
@app.route('/preparation_registeration', methods=['GET'])
def preparation_registeration():
    return render_template('preparation_registeration.html')

@app.route('/register', methods=['GET'])
def register():
    global video_camera
    global face_rep_times
    global face_rep

    face_rep = None
    face_rep_times = 0

    if video_camera == None:
        video_camera = VideoCamera()
    face_rep_times = 0

    return render_template('register.html')

def qrcode_image(url):
    """The endpoint for generated QRCode image."""
    
    try:
        url = urlsafe_b64decode(url.encode('ascii'))
    except (ValueError, UnicodeEncodeError):
        return jsonify(r=False, error='invalid_data'), 404

    image = make_qrcode_image(url, border=0)
    response = make_image_response(image, kind='png')
    return response

def make_qrcode_image(data, **kwargs):
    """Creates a QRCode image from given data."""
    qrcode = QRCode(**kwargs)
    qrcode.add_data(data)
    return qrcode.make_image()


def make_image_response(image, kind):
    """Creates a cacheable response from given image."""
    mimetype = types_map['.' + kind.lower()]
    io = BytesIO()
    image.save(io, kind.upper())
    io.seek(0)
    return send_file(io, mimetype=mimetype, conditional=True)

def stringifynumpy(p):
    stringify = ""
    shape = p.shape
    for i in range(shape[0]):
        for j in range(shape[1]-1):
            stringify = stringify + str(p[i][j]) + ","
        stringify = stringify + str(p[i][j]) +";"

    print(stringify)

    return stringify

@app.route('/qr_gen', methods=['GET'])
def qr_gen():
    global face_rep
    global constituency
    global name
    global ids
    import numpy as np
    import io

    content = stringifynumpy(face_rep)

    content = ids+"&"+name + "&" + constituency + "&" + content
    image = make_qrcode_image(content, border=0)
    response = qrcode_image(image, kind='png')

    return response

@app.route('/complete_registeration', methods=['POST'])
def complete_registeration():
    global face_rep
    global ids
    global constituency
    global name

    ids = request.form['ido']
    constituency = request.form.get('constituency')
    name = request.form['name']

    # POST DATA ONTO BLOCKCHAIN
    return render_template('complete_registeration.html', idi = str(ids))

# Vote
@app.route('/preparation_vote', methods=['GET'])
def preparation_vote():
    return render_template('preparation_vote.html')

@app.route('/vote', methods=['GET'])
def vote():
    global video_camera
    global face_rep_times

    if video_camera == None:
        video_camera = VideoCamera()
    face_rep_times = 0

    return render_template('vote.html')

@app.route('/complete_vote', methods=['POST'])
def complete_vote():
    # Return Success Page or Fail Page
    return render_template('complete_vote.html')

def video_stream():
    global video_camera 
    global global_frame
    global face_rep
    global face_rep_times
        
    while face_rep_times < 50 and video_camera!= None:
        frame = video_camera.get_frame()
        # Initialize some variables
        face_locations = []
        face_encodings = []
        face_names = []
        process_this_frame = True

        # while True:
        #     # Grab a single frame of video
        #     ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(small_frame)
            face_encodings = face_recognition.face_encodings(small_frame, face_locations)

            face_names = []

            for face_encoding in face_encodings:

                # See if the face is a match for the known face(s)
                # match = face_recognition.compare_faces([obama_face_encoding], face_encoding)
                

                # if match[0]:
                #     name = "Joydeep"
                face_rep = face_encoding

                face_rep_times = face_rep_times + 1

                if face_rep_times < 45:
                  name = "Keep on Looking " + str(50 - face_rep_times)
                else:
                  name = "Done"
                face_names.append(name)

                break


        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if face_rep_times < 45:
              # Draw a box around the face
              cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

              # Draw a label with a name below the face
              cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
              font = cv2.FONT_HERSHEY_DUPLEX
              cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
              cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

              # Draw a label with a name below the face
              cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), -1)
              font = cv2.FONT_HERSHEY_DUPLEX
              cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            break

        ret, jpeg = cv2.imencode('.jpg', frame)

        if frame != None:
            global_frame = frame
            ret, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        else:
            ret, jpeg = cv2.imencode('.jpg', global_frame)
            yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + global_frame.tobytes() + b'\r\n\r\n')
    video_camera.__del__()
    video_camera = None
    yield True

@app.route('/video_viewer')
def video_viewer():
    view = video_stream()
    if view == True:
      pass
    else:
      return Response(view,
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/record_status', methods=['POST'])
def record_status():
    global video_camera 
    if video_camera == None:
        video_camera = VideoCamera()

    json = request.get_json()

    status = json['status']

    if status == "true":
        video_camera.start_record()
        return jsonify(result="started")
    else:
        video_camera.stop_record()
        return jsonify(result="stopped")

# # Vote
# @app.route('/vote', methods=['GET'])
# def register():
#     return render_template('vote.html',title='Assignment 1&2: Information Retrieval',answer=books,debug=query)

# # Check Vote
# @app.route('/vote', methods=['POST'])
# def register():
#     return render_template('success.html',title='Assignment 1&2: Information Retrieval',answer=books,debug=query)

# # Tally
# @app.route('/tally', methods=['GET'])
# def register():
#     return render_template('index.html',title='Assignment 1&2: Information Retrieval',answer=books,debug=query)