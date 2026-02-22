from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from detect import detect_animals
import cv2

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['RESULT_FOLDER'] = 'static/results'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'mp4', 'avi'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    location = request.form.get('location', 'Unknown Location')
    
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        result_path, count, coords = detect_animals(filepath, app.config['RESULT_FOLDER'])
        
        latitude = request.form.get('latitude', '31.5204')
        longitude = request.form.get('longitude', '74.3587')
        
        return render_template('result.html', 
                             original=filepath, 
                             result=result_path, 
                             count=count,
                             location=location,
                             lat=latitude,
                             lon=longitude)
    
    return redirect(url_for('index'))

@app.route('/detect_video', methods=['POST'])
def detect_video():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        cap = cv2.VideoCapture(filepath)
        framecount = 0
        detected_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if framecount % 30 == 0:
                temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_frame.jpg')
                cv2.imwrite(temp_path, frame)
                result_path, count, coords = detect_animals(temp_path, app.config['RESULT_FOLDER'])
                if count > 0:
                    detected_frames += 1
            
            framecount = framecount + 1
        
        cap.release()
        
        latitude = request.form.get('latitude', '31.5204')
        longitude = request.form.get('longitude', '74.3587')
        location = request.form.get('location', 'Unknown Location')
        
        return render_template('result.html',
                             original=filepath,
                             result=result_path,
                             count=detected_frames,
                             location=location,
                             lat=latitude,
                             lon=longitude)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)
    app.run(debug=True, port=5000)
