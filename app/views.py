from app import app
from flask import render_template
from flask import request
from inout.facerecognition.VideoCamera import VideoCamera
from flask import Flask, render_template, Response
import face_recognition
import cv2
from flask import Blueprint, current_app, send_file, url_for, jsonify
from flask import Flask, render_template, Response, jsonify, request, redirect
import numpy as np
import os
import requests
import sys
import qrcode
from qrcode import QRCode
from base64 import urlsafe_b64encode, urlsafe_b64decode
from mimetypes import types_map
from io import BytesIO
import cStringIO
# import qrtools

# import zbar
from PIL import Image

# import sys
# sys.settrace

video_camera = None
global_frame = None
face_rep = None
constituency = None
face_rep_times = 0
face_verified = None
frames_seen = 0

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
    print(url)
    # try:
    #     url = urlsafe_b64decode(url.encode('ascii'))
    # except (ValueError, UnicodeEncodeError):
    #     return jsonify(r=False, error='invalid_data'), 404

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
    if len(p.shape) == 1:
        for i in range(shape[0]-1):
            stringify = stringify + str(p[i]) + ","
        stringify = stringify + str(p[i]) +";"
    else:
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
    response = qrcode_image(content)

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
@app.route('/preparation_vote_2', methods=['GET'])
def preparation_vote_2():
    return render_template('preparation_vote_2.html')

@app.route('/preparation_vote', methods=['GET'])
def preparation_vote():
    return render_template('preparation_vote.html')

@app.route('/complete_vote')
def complete_vote():
    global face_verified
    global face_rep_times
    global qrcode_detail

    if qrcode_detail != None:
        face_rep_times = 0

        if face_verified == True:
            # fetch vote
            # POST DATA ONTO BLOCKCHAIN
            return render_template('complete_vote.html',status = True, message = "Please Proceed")
    else:
            return render_template('complete_vote.html',status = False, message = "Failed the Face Verification. Please Retry")

def getConstituency(qrcode_detail):
    try:
        elements = qrcode_detail.split("&")
        return elements[2]
    except Exception as e:
        print(e)
        print(qrcode_detail)
        return None

def getName(qrcode_detail):
    try:
        elements = qrcode_detail.split("&")
        return elements[1]
    except Exception as e:
        print(e)
        print(qrcode_detail)
        return None
    
def getID(qrcode_detail):
    try:
        elements = qrcode_detail.split("&")
        return elements[0]
    except Exception as e:
        print(e)
        print(qrcode_detail)
        return None
    
def getFaceEncoding(qrcode_detail):
    try:
        elements = qrcode_detail.split("&")
        string_numpy = elements[3]

        if string_numpy[-1]==";":
            string_numpy = string_numpy[:-1]

        rows = string_numpy.split(";")
        print(rows)
        num_rows = len(rows)

        if len(rows)>1:
            print("here")
            columns_row1 = rows[0].split(",")
            num_cols = len(columns_row1)
            numpy_array = np.array(np.zeros([num_rows,num_cols]))

            for row in range(len(rows)):
                columns = row.split(",")
                print(columns)
                for column in range(len(columns)):
                    numpy_array[row][column] = float(columns[column])

        else:
            num_rows = len(rows[0].split(","))
            num_cols = 1
            numpy_array = np.array(np.zeros(num_rows))

            rows = rows[0].split(',')
            for row in range(num_rows):
                try:
                    numpy_array[row] = float(rows[row])
                except Exception as e:
                    print(e)
                    print("ye - "+str(rows[row]))
            

        return numpy_array

    except Exception as e:
        print(e)
        print(qrcode_detail)
        return None

@app.route('/vote', methods=['GET'])
def vote():
    global video_camera
    global face_rep_times
    global qrcode_detail
    global face_verified

    if qrcode_detail != None:
        cons = getConstituency(qrcode_detail)
        ids = getID(qrcode_detail)
        name = getName(qrcode_detail)
        if video_camera == None:
            video_camera = VideoCamera()
        face_rep_times = 0
        face_verified = False
        return render_template('vote.html', constituency = cons, ids = ids, name = name)
    else:
        redirect('/preparation_vote')

@app.route('/scan_qr', methods=['GET'])
def scan_qr_get():
    global face_rep_times
    global qrcode_detail
    global frames_seen
    global face_verified

    frames_seen = 0
    qrcode_detail = None
    face_verified = False
    qrcode_detail = None
    return render_template('/scan_qr.html')

@app.route('/scan_qr', methods=['POST'])
def scan_qr_post():
    global face_rep_times
    global qrcode_detail
    global frames_seen
    global face_verified

    frames_seen = 0
    qrcode_detail = None
    face_verified = False

    qrcode_detail = "AC98987878&Sarthak Ahuja&Shalimar Bagh&-0.159224867821,0.0961131304502,0.0806648805737,-0.0190040543675,0.00478628277779,-0.00189683120698,-0.0760209485888,-0.0222772955894,0.12480738014,-0.0947327464819,0.137215003371,0.0406793281436,-0.220997065306,-0.00102177634835,-0.070340000093,0.0954733639956,-0.137289196253,-0.125256210566,-0.0677188187838,-0.138273492455,0.0532022044063,0.043803177774,0.00489089637995,0.0475884824991,-0.137116998434,-0.316078811884,-0.0781381726265,-0.11543083936,-0.0406564325094,-0.0805452466011,0.028474137187,-0.0572183355689,-0.124757274985,0.0444896258414,-0.0289920698851,0.0578845739365,-0.0231432057917,-0.0520578250289,0.194136470556,0.0342295020819,-0.0845594704151,0.00536869000643,0.0336395166814,0.284532248974,0.174878165126,0.0646973848343,0.00684992130846,-0.0530644506216,0.131528690457,-0.28083050251,0.0388191603124,0.190147593617,0.026546234265,0.14211383462,0.0698419585824,-0.0969827473164,0.0510563068092,0.082145281136,-0.125917777419,0.0781889781356,-0.0149715701118,-0.0720971077681,0.00677150953561,-0.0293271094561,0.218069955707,0.101842686534,-0.151010781527,-0.0795929804444,0.0911204144359,-0.195250198245,-0.069269105792,0.0236312001944,-0.087544515729,-0.171684682369,-0.260465472937,0.0995862483978,0.392084568739,0.211553886533,-0.132674798369,0.0294713303447,-0.128424033523,-0.0150609947741,0.0833096504211,0.0616741552949,-0.114379473031,-0.0463977828622,-0.0848779603839,0.0126761011779,0.214710205793,0.0430870726705,-0.0722344741225,0.182654589415,0.0203853882849,0.0773385837674,0.0289880670607,0.0785187035799,-0.131176531315,-0.0361043810844,-0.0844457000494,0.0156937241554,-0.00129470229149,-0.0582292713225,0.00625693053007,0.0664530545473,-0.145363330841,0.146967947483,-0.00600379705429,-0.0319493561983,-0.0105505697429,0.120610244572,-0.162945210934,-0.0516600012779,0.125345110893,-0.224538087845,0.185971796513,0.204392194748,0.0473874993622,0.175246149302,0.11393918097,0.0970177352428,-0.0587824322283,0.00480561330914,-0.0874410569668,-0.0905140191317,0.0157949887216,0.0619117096066,0.0474206395447,0.0474206395447;"
    #qrcode_detail = "ASCNJDNJ&Joydeep Mondal&Punjabi Bagh&-0.0839269310236,0.12945112586,0.0304085426033,-0.0817777514458,-0.0676832050085,0.0144281834364,-0.0459085032344,-0.0849780142307,0.266784399748,-0.105459749699,0.24629278481,0.0293383151293,-0.205893740058,-0.0779131576419,-0.105598807335,0.0674170330167,-0.150210529566,-0.171141564846,-0.0295076221228,-0.0694564580917,0.00294003635645,0.0321683473885,0.0121504440904,0.0690746903419,-0.112860195339,-0.299994826317,-0.0215801224113,-0.0836579352617,0.0305544435978,-0.103548057377,-0.0138551164418,0.028623752296,-0.236025214195,-0.0731510967016,-0.0444226711988,0.168215721846,0.0442672520876,-0.0198362469673,0.17235904932,0.0433496460319,-0.126728013158,-0.083517074585,-0.00554303079844,0.297870635986,0.1374168396,0.00992935337126,0.00220810994506,-0.0883668065071,0.12289750576,-0.222542434931,0.115538835526,0.117748022079,0.165982782841,0.0291853249073,0.0269441381097,-0.170543938875,-0.0326750054955,0.183693274856,-0.162859678268,0.0464849583805,0.0148559324443,-0.0196643993258,-0.0326906368136,-0.0828299224377,0.32918637991,0.124147795141,-0.126922488213,-0.0898699387908,0.164067208767,-0.120629757643,-0.100762546062,0.0546288192272,-0.051092620939,-0.118638239801,-0.32086455822,0.0906050428748,0.419354975224,0.119058899581,-0.161984965205,0.0429138615727,-0.13892506063,-0.0351451560855,-0.00716241262853,0.0550528727472,-0.147305294871,0.112487755716,-0.0940234139562,0.0167062357068,0.200252041221,0.0777082890272,-0.0883498266339,0.160065621138,-0.041999027133,0.0638670474291,0.0527986697853,0.0156255885959,-0.0743653178215,0.0195793882012,-0.152228742838,-0.0158229507506,0.020648483187,-0.0813403129578,-0.0192819200456,0.0889135301113,-0.225633427501,0.0839072093368,0.0185916293412,-0.0566525086761,0.0430916249752,0.0241381619126,-0.103341862559,-0.0768657326698,0.207207083702,-0.328171461821,0.188917949796,0.105696618557,0.0995999574661,0.238834917545,0.105856724083,0.0771142318845,0.0204803738743,-0.0494273379445,-0.10764375329,-0.0624768547714,0.0636158585548,-0.0634630396962,0.138613075018,0.138613075018;"
    # img = Image.open(request.files['file'].stream)
    # # try:
    return redirect('/preparation_vote_2')
    # except Exception as e:
    #     print(e)
    #     qrcode_detail = None
    #     return render_template('/scan_qr.html')

    

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

# @app.route('/video_viewer_qr')
# def video_viewer_qr():
#     view = video_stream_find_qr(True)
#     if view == True:
#       return redirect("/preparation_vote_2")
#     else:
#       return Response(view,
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_viewer_face')
def video_viewer_face():
    view = video_stream_find_face()
    if view == True:
      pass
    else:
      return Response(view,
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def video_stream_find_face():
    global video_camera 
    global global_frame
    global qrcode_detail
    global face_rep_times
    global face_verified
        
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
                face_rep = getFaceEncoding(qrcode_detail)
                name = getName(qrcode_detail)

                if face_rep == None:
                    text = "Invalid QR Mask"
                    face_verified = False
                else:
                    match = face_recognition.compare_faces([face_rep], face_encoding)
                    

                    if match[0]:
                        text = name
                        face_verified = True
                    else:
                        text = "Matching... "+str(50 - face_rep_times)
                        face_verified = False

                    face_rep = face_encoding

                    face_rep_times = face_rep_times + 1

                    face_names.append(text)

                    break


        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), face_name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            if face_name != name:
              # Draw a box around the face
              cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

              # Draw a label with a name below the face
              cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
              font = cv2.FONT_HERSHEY_DUPLEX
              cv2.putText(frame, face_name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            else:
              cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

              # Draw a label with a name below the face
              cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), -1)
              font = cv2.FONT_HERSHEY_DUPLEX
              cv2.putText(frame, face_name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
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

# def video_stream_find_qr(joy=False):
#     global video_camera 
#     global frames_seen
#     global qrcode_detail
    
#     try:
#         while frames_seen < 50 and qrcode_detail== None:
#             frame = video_camera.get_frame()
#             # Initialize some variables
#             face_locations = []
#             face_encodings = []
#             face_names = []
#             process_this_frame = True

#             # while True:
#             #     # Grab a single frame of video
#             #     ret, frame = video_capture.read()

#             # Resize frame of video to 1/4 size for faster face recognition processing
#             # small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

#             # Only process every other frame of video to save time
#             if process_this_frame:
#                 # Find all the faces and face encodings in the current frame of video
#                 # Converts image to grayscale.
#                 gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#                 # Uses PIL to convert the grayscale image into a ndary array that ZBar can understand.
#                 image = Image.fromarray(gray)
#                 width, height = image.size
#                 zbar_image = zbar.Image(width, height, 'Y800', image.tostring())

#                 # Scans the zbar image.
#                 scanner = zbar.ImageScanner()
#                 scanner.scan(zbar_image)

#                 # Prints data from image.
#                 for decoded in zbar_image:
#                     print(decoded.data)
#                     qrcode_detail = decoded.data
#                     break


#             process_this_frame = not process_this_frame
#             frames_seen = frames_seen + 1
#             if frame != None:
#                 global_frame = frame
#                 ret, jpeg = cv2.imencode('.jpg', frame)
#                 yield (b'--frame\r\n'
#                         b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
#             else:
#                 ret, jpeg = cv2.imencode('.jpg', global_frame)
#                 yield (b'--frame\r\n'
#                                 b'Content-Type: image/jpeg\r\n\r\n' + global_frame.tobytes() + b'\r\n\r\n')
        

#         if qrcode_detail == None:
#             # Move to Backup
#             img = cv2.imread('/static/images/qr_gen.png',0)
#             # Uses PIL to convert the grayscale image into a ndary array that ZBar can understand.
#             image = Image.fromarray(img)
#             width, height = image.size
#             zbar_image = zbar.Image(width, height, 'Y800', image.tostring())

#             # Scans the zbar image.
#             scanner = zbar.ImageScanner()
#             scanner.scan(zbar_image)

#             # Prints data from image.
#             for decoded in zbar_image:
#                 # print("FOUND THIS IN BACKUP - ")
#                 # print(decoded.data)
#                 qrcode_detail = decoded.data
#                 break

#             if qrcode_detail == None:
#                 qrcode_detail = "AC98987878&Sarthak Ahuja&Shalimar Bagh&-0.159224867821,0.0961131304502,0.0806648805737,-0.0190040543675,0.00478628277779,-0.00189683120698,-0.0760209485888,-0.0222772955894,0.12480738014,-0.0947327464819,0.137215003371,0.0406793281436,-0.220997065306,-0.00102177634835,-0.070340000093,0.0954733639956,-0.137289196253,-0.125256210566,-0.0677188187838,-0.138273492455,0.0532022044063,0.043803177774,0.00489089637995,0.0475884824991,-0.137116998434,-0.316078811884,-0.0781381726265,-0.11543083936,-0.0406564325094,-0.0805452466011,0.028474137187,-0.0572183355689,-0.124757274985,0.0444896258414,-0.0289920698851,0.0578845739365,-0.0231432057917,-0.0520578250289,0.194136470556,0.0342295020819,-0.0845594704151,0.00536869000643,0.0336395166814,0.284532248974,0.174878165126,0.0646973848343,0.00684992130846,-0.0530644506216,0.131528690457,-0.28083050251,0.0388191603124,0.190147593617,0.026546234265,0.14211383462,0.0698419585824,-0.0969827473164,0.0510563068092,0.082145281136,-0.125917777419,0.0781889781356,-0.0149715701118,-0.0720971077681,0.00677150953561,-0.0293271094561,0.218069955707,0.101842686534,-0.151010781527,-0.0795929804444,0.0911204144359,-0.195250198245,-0.069269105792,0.0236312001944,-0.087544515729,-0.171684682369,-0.260465472937,0.0995862483978,0.392084568739,0.211553886533,-0.132674798369,0.0294713303447,-0.128424033523,-0.0150609947741,0.0833096504211,0.0616741552949,-0.114379473031,-0.0463977828622,-0.0848779603839,0.0126761011779,0.214710205793,0.0430870726705,-0.0722344741225,0.182654589415,0.0203853882849,0.0773385837674,0.0289880670607,0.0785187035799,-0.131176531315,-0.0361043810844,-0.0844457000494,0.0156937241554,-0.00129470229149,-0.0582292713225,0.00625693053007,0.0664530545473,-0.145363330841,0.146967947483,-0.00600379705429,-0.0319493561983,-0.0105505697429,0.120610244572,-0.162945210934,-0.0516600012779,0.125345110893,-0.224538087845,0.185971796513,0.204392194748,0.0473874993622,0.175246149302,0.11393918097,0.0970177352428,-0.0587824322283,0.00480561330914,-0.0874410569668,-0.0905140191317,0.0157949887216,0.0619117096066,0.0474206395447,0.0474206395447;"
#                 print("Went Into Double Backup")
#     except Exception as e:
#         if qrcode_detail == None:
#             if joy:
#                 qrcode_detail = "ASCNJDNJ&Joydeep Mondal&Punjabi Bagh&-0.0839269310236,0.12945112586,0.0304085426033,-0.0817777514458,-0.0676832050085,0.0144281834364,-0.0459085032344,-0.0849780142307,0.266784399748,-0.105459749699,0.24629278481,0.0293383151293,-0.205893740058,-0.0779131576419,-0.105598807335,0.0674170330167,-0.150210529566,-0.171141564846,-0.0295076221228,-0.0694564580917,0.00294003635645,0.0321683473885,0.0121504440904,0.0690746903419,-0.112860195339,-0.299994826317,-0.0215801224113,-0.0836579352617,0.0305544435978,-0.103548057377,-0.0138551164418,0.028623752296,-0.236025214195,-0.0731510967016,-0.0444226711988,0.168215721846,0.0442672520876,-0.0198362469673,0.17235904932,0.0433496460319,-0.126728013158,-0.083517074585,-0.00554303079844,0.297870635986,0.1374168396,0.00992935337126,0.00220810994506,-0.0883668065071,0.12289750576,-0.222542434931,0.115538835526,0.117748022079,0.165982782841,0.0291853249073,0.0269441381097,-0.170543938875,-0.0326750054955,0.183693274856,-0.162859678268,0.0464849583805,0.0148559324443,-0.0196643993258,-0.0326906368136,-0.0828299224377,0.32918637991,0.124147795141,-0.126922488213,-0.0898699387908,0.164067208767,-0.120629757643,-0.100762546062,0.0546288192272,-0.051092620939,-0.118638239801,-0.32086455822,0.0906050428748,0.419354975224,0.119058899581,-0.161984965205,0.0429138615727,-0.13892506063,-0.0351451560855,-0.00716241262853,0.0550528727472,-0.147305294871,0.112487755716,-0.0940234139562,0.0167062357068,0.200252041221,0.0777082890272,-0.0883498266339,0.160065621138,-0.041999027133,0.0638670474291,0.0527986697853,0.0156255885959,-0.0743653178215,0.0195793882012,-0.152228742838,-0.0158229507506,0.020648483187,-0.0813403129578,-0.0192819200456,0.0889135301113,-0.225633427501,0.0839072093368,0.0185916293412,-0.0566525086761,0.0430916249752,0.0241381619126,-0.103341862559,-0.0768657326698,0.207207083702,-0.328171461821,0.188917949796,0.105696618557,0.0995999574661,0.238834917545,0.105856724083,0.0771142318845,0.0204803738743,-0.0494273379445,-0.10764375329,-0.0624768547714,0.0636158585548,-0.0634630396962,0.138613075018,0.138613075018;"
#             else:
#                 qrcode_detail = "AC98987878&Sarthak Ahuja&Shalimar Bagh&-0.159224867821,0.0961131304502,0.0806648805737,-0.0190040543675,0.00478628277779,-0.00189683120698,-0.0760209485888,-0.0222772955894,0.12480738014,-0.0947327464819,0.137215003371,0.0406793281436,-0.220997065306,-0.00102177634835,-0.070340000093,0.0954733639956,-0.137289196253,-0.125256210566,-0.0677188187838,-0.138273492455,0.0532022044063,0.043803177774,0.00489089637995,0.0475884824991,-0.137116998434,-0.316078811884,-0.0781381726265,-0.11543083936,-0.0406564325094,-0.0805452466011,0.028474137187,-0.0572183355689,-0.124757274985,0.0444896258414,-0.0289920698851,0.0578845739365,-0.0231432057917,-0.0520578250289,0.194136470556,0.0342295020819,-0.0845594704151,0.00536869000643,0.0336395166814,0.284532248974,0.174878165126,0.0646973848343,0.00684992130846,-0.0530644506216,0.131528690457,-0.28083050251,0.0388191603124,0.190147593617,0.026546234265,0.14211383462,0.0698419585824,-0.0969827473164,0.0510563068092,0.082145281136,-0.125917777419,0.0781889781356,-0.0149715701118,-0.0720971077681,0.00677150953561,-0.0293271094561,0.218069955707,0.101842686534,-0.151010781527,-0.0795929804444,0.0911204144359,-0.195250198245,-0.069269105792,0.0236312001944,-0.087544515729,-0.171684682369,-0.260465472937,0.0995862483978,0.392084568739,0.211553886533,-0.132674798369,0.0294713303447,-0.128424033523,-0.0150609947741,0.0833096504211,0.0616741552949,-0.114379473031,-0.0463977828622,-0.0848779603839,0.0126761011779,0.214710205793,0.0430870726705,-0.0722344741225,0.182654589415,0.0203853882849,0.0773385837674,0.0289880670607,0.0785187035799,-0.131176531315,-0.0361043810844,-0.0844457000494,0.0156937241554,-0.00129470229149,-0.0582292713225,0.00625693053007,0.0664530545473,-0.145363330841,0.146967947483,-0.00600379705429,-0.0319493561983,-0.0105505697429,0.120610244572,-0.162945210934,-0.0516600012779,0.125345110893,-0.224538087845,0.185971796513,0.204392194748,0.0473874993622,0.175246149302,0.11393918097,0.0970177352428,-0.0587824322283,0.00480561330914,-0.0874410569668,-0.0905140191317,0.0157949887216,0.0619117096066,0.0474206395447,0.0474206395447;"
#             print("Went Into Double Backup")
#     video_camera.__del__()
#     video_camera = None
#     yield True


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