from flask import Flask, render_template, Response,jsonify,request,session
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange
import os
import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import random
from YOLO_Video import video_detection
import threading
import time
import requests

app = Flask(__name__)

app.config['SECRET_KEY'] = '0607bkhanhhoang'
app.config['UPLOAD_FOLDER'] = 'static/files'

data_buffer = {
    "channel_1": [],
    "channel_2": [],
    "channel_3": [],
    "channel_4": [],
    "channel_5": [],
    "channel_6": []
}

@app.route('/data', methods=['POST'])

def generate_data():
    global data_buffer

    # Generate random values for line charts
    new_type1 = random.randint(10, 100)
    new_type2 = random.uniform(20, 80)
    new_type3 = random.uniform(5, 50)
    new_type4 = random.randint(10, 100)
    new_type5 = random.uniform(20, 80)
    new_type6 = random.uniform(5, 50)

    # Update the buffers for line charts
    data_buffer["channel_1"].append(new_type1)
    data_buffer["channel_2"].append(new_type2)
    data_buffer["channel_3"].append(new_type3)
    data_buffer["channel_4"].append(new_type4)
    data_buffer["channel_5"].append(new_type5)
    data_buffer["channel_6"].append(new_type6)
    print("Generated new data for all channels.")

    # Keep only the last 20 values in the buffer
    data_buffer["channel_1"] = data_buffer["channel_1"][-20:]
    data_buffer["channel_2"] = data_buffer["channel_2"][-20:]
    data_buffer["channel_3"] = data_buffer["channel_3"][-20:]
    data_buffer["channel_4"] = data_buffer["channel_4"][-20:]
    data_buffer["channel_5"] = data_buffer["channel_5"][-20:]
    data_buffer["channel_6"] = data_buffer["channel_6"][-20:]

    # Create post_data dictionary
    post_data = {
        "channel_1": new_type1,
        "channel_2": new_type2,
        "channel_3": new_type3,
        "channel_4": new_type4,
        "channel_5": new_type5,
        "channel_6": new_type6
    }

    try:
        # Convert dictionary to JSON string
        data_json = json.dumps(post_data)

        # Parse JSON string back to a Python dictionary
        data = json.loads(data_json)

        # Access values from the dictionary
        channel_1 = data.get("channel_1")
        channel_2 = data.get("channel_2")
        channel_3 = data.get("channel_3")
        channel_4 = data.get("channel_4")
        channel_5 = data.get("channel_5")
        channel_6 = data.get("channel_6")

        # Print the received data
        print(f"Received: channel_1={channel_1}, channel_2={channel_2}, "
              f"channel_3={channel_3}, channel_4={channel_4}, "
              f"channel_5={channel_5}, channel_6={channel_6}")

        # Simulate a response
        response = {"message": "Data received successfully"}
        return response

    except json.JSONDecodeError:
        # Handle JSON parsing error
        print("Error: Invalid JSON data")
        return {"error": "Invalid JSON data"}

    except Exception as e:
        # Catch-all for any other errors
        print(f"Error processing data: {str(e)}")
        return {"error": "An error occurred"}

    

def random_data_generator():
    while True:
        generate_data()
        print("Random data generated and updated in buffer.")
        time.sleep(10)  # Sleep for 1 second before generating new data

# # Define the request handler
# class MyRequestHandler(BaseHTTPRequestHandler):
#     def do_POST(self):
        # # Read the content length to get the size of the incoming data
        # content_length = int(self.headers['Content-Length'])
        # post_data = self.rfile.read(content_length)  # Read the incoming data

        # try:
        #     # Parse the JSON data
        #     data = json.loads(post_data)
        #     channel_1 = data.get("channel_1")
        #     channel_2 = data.get("channel_2")
        #     channel_3 = data.get("channel_3")

        #     # Print the received data
        #     print(f"Received: channel_1={channel_1}, channel_2={channel_2}, channel_3={channel_3}")

        #     # Send a response
        #     self.send_response(200)
        #     self.send_header('Content-Type', 'application/json')
        #     self.end_headers()
        #     response = {"message": "Data received successfully"}
        #     self.wfile.write(json.dumps(response).encode('utf-8'))

        # except json.JSONDecodeError:
        #     # Handle JSON parsing error
        #     self.send_response(400)
        #     self.send_header('Content-Type', 'application/json')
        #     self.end_headers()
        #     response = {"error": "Invalid JSON data"}
        #     self.wfile.write(json.dumps(response).encode('utf-8'))


class UploadFileForm(FlaskForm):
    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Run")

def generate_frames(path_x = ''):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')


# def generate_frames_web(path_x):
#     yolo_output = video_detection(path_x)
#     for detection_ in yolo_output:
#         ref,buffer=cv2.imencode('.jpg',detection_)

#         frame=buffer.tobytes()
#         yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

import cv2

def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)  # Generator producing detected frames

    for detection_ in yolo_output:
        if detection_ is None:
            print("Received an invalid frame. Skipping...")
            continue

        # Encode the frame as JPEG
        success, buffer = cv2.imencode('.jpg', detection_)
        if not success:
            print("Failed to encode frame. Skipping...")
            continue

        # Convert buffer to bytes and yield as an HTTP frame
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/', methods=['GET','POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    session.clear()
    return render_template('indexproject.html')


@app.route("/webcam", methods=['GET','POST'])

def webcam():
    session.clear()
    return render_template('ui.html')

# @app.route('/charts', methods=['GET','POST'])
# def charts():
#     return render_template('charts.html')

# Route for receiving POST data
# @app.route('/receive', methods=['POST'])
# def receive_data():
#     try:
#         # Parse incoming JSON data
#     #     data = request.json
#     #     if not data:
#     #         return jsonify({"error": "No data received"}), 400

        
#     #     channel_1 = data.get("channel_1")
#     #     channel_2 = data.get("channel_2")
#     #     channel_3 = data.get("channel_3")

        
#     #     print(f"Received data: channel_1={channel_1}, channel_2={channel_2}, channel_3={channel_3}")

#     #     return jsonify({"message": "Data received successfully"}), 200
#     # except Exception as e:
#     #     return jsonify({"error": str(e)}), 500
#         # Generate random values for channels
#         channel_1 = random.randint(0, 100)  # Random integer between 0 and 100
#         channel_2 = random.uniform(0, 50)  # Random float between 0 and 50
#         channel_3 = random.uniform(0, 1)   # Random float between 0 and 1

#         # Log generated data
#         print(f"Generated data: channel_1={channel_1}, channel_2={channel_2}, channel_3={channel_3}")

#         # Return the generated values in JSON format
#         return jsonify({
#             "channel_1": channel_1,
#             "channel_2": channel_2,
#             "channel_3": channel_3,
#             "message": "Random data generated successfully"
#         }), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# Function to generate random data and update the buffer


# Route to serve the generated data
@app.route('/data', methods=['GET'])
def receive_data():
    try:
        # Generate new random data and update the buffer
        generate_data()
        print("Updated Data Buffer:", data_buffer)
        return jsonify(data_buffer)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route for the HTML page
@app.route('/charts', methods=['GET'])
def charts():
    if request.method == 'GET':
        # Serve the charts HTML page
        return render_template('charts.html')
    elif request.method == 'POST':
        try:
            generate_data()
            print("Updated Data Buffer:", data_buffer)
            return jsonify(data_buffer)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return render_template('charts.html')

@app.route('/FrontPage', methods=['GET','POST'])
def front():
    # Upload File Form: Create an instance for the Upload File Form
    form = UploadFileForm()
    if form.validate_on_submit():
        # Our uploaded video file path is saved here
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))  # Then save the file
        # Use session storage to save video file path
        session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                                             secure_filename(file.filename))
    return render_template('videoprojectnew.html', form=form)
@app.route('/video')
def video():
    
    return Response(generate_frames(path_x = session.get('video_path', None)),mimetype='multipart/x-mixed-replace; boundary=frame')

# To display the Output Video on Webcam page
@app.route('/webapp')
def webapp():
   
    return Response(generate_frames_web(path_x=0), mimetype='multipart/x-mixed-replace; boundary=frame')

def run_flaskweb():
    app.run(debug=True, use_reloader=False)


if __name__ == "__main__":
    # Create and start the Flask thread
    flask_thread = threading.Thread(target=run_flaskweb)
    flask_thread.start()

    # Start the random data generator thread
    data_thread = threading.Thread(target=random_data_generator)
    data_thread.start()
