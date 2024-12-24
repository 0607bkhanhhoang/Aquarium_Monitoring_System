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
    # new_type1 = random.randint(10, 100)
    # new_type2 = random.uniform(20, 80)
    # new_type3 = random.uniform(5, 50)
    
    # # Update the buffers for line charts
    # data_buffer["channel_1"].append(new_type1)
    # data_buffer["channel_2"].append(new_type2)
    # data_buffer["channel_3"].append(new_type3)
    # print("Generated new data 1")
    
    # # Keep only the last 10 values
    # data_buffer["channel_1"] = data_buffer["channel_1"][-10:]
    # data_buffer["channel_2"] = data_buffer["channel_2"][-10:]
    # data_buffer["channel_3"] = data_buffer["channel_3"][-10:]
    # print("Generated new data 2")
    
    # # Generate random values for pie charts
    # data_buffer["channel_4"] = [random.randint(1, 50) for _ in range(10)]
    # data_buffer["channel_5"] = [random.randint(1, 50) for _ in range(10)]
    # data_buffer["channel_6"] = [random.randint(1, 50) for _ in range(10)]
    # print("Generated new data 3")

    # Read the content length to get the size of the incoming data
    # content_length = int(self.headers['Content-Length'])
    # print("Captured the content length")
    # post_data = self.rfile.read(content_length)  # Read the incoming data

    # try:
    #     # Parse the JSON data
    #     data = json.loads(post_data)
    #     channel_1 = data.get("channel_1")
    #     channel_2 = data.get("channel_2")
    #     channel_3 = data.get("channel_3")
    #     channel_4 = data.get("channel_4") 
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
    # Validate the API key from headers
    api_key = request.headers.get('API-Key')
    if not api_key or not safe_str_cmp(api_key, API_KEY):
        app.logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized"}), 401

    # Process the incoming JSON payload
    try:
        data = request.json
        if not data:
            raise ValueError("No JSON data provided")
        app.logger.info(f"Received data: {data}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        app.logger.error(f"Error processing data: {str(e)}")
        return jsonify({"error": "Invalid data"}), 400
    

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


def generate_frames_web(path_x):
    yolo_output = video_detection(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')


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
