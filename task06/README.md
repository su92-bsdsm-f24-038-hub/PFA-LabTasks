ANIMAL HERD DETECTION SYSTEM

This project detects animals in images and videos using YOLO and OpenCV.

SETUP INSTRUCTIONS:

1. Install requirements:
   pip install -r requirements.txt

2. Download YOLO weights and config:
   - Download yolov3.weights from: https://pjreddie.com/media/files/yolov3.weights
   - Download yolov3.cfg from: https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg
   - Place both files in the 'models' folder

3. Run the application:
   python app.py

4. Open browser and go to:
   http://localhost:5000

FEATURES:
- Upload images or videos
- Detect animals using YOLO
- Mark locations on OpenStreetMap
- Get geolocation alerts
- Support for multiple animal classes

TESTED WITH:
- Python 3.8+
- Flask 2.3.0
- OpenCV 4.8.0

PROJECT STRUCTURE:
task06/
├── app.py                 (Flask application)
├── detect.py              (Detection logic)
├── requirements.txt       (Dependencies)
├── models/
│   ├── coco.names        (YOLO class names)
│   ├── yolov3.cfg        (Download required)
│   └── yolov3.weights    (Download required)
├── static/
│   ├── uploads/          (Uploaded files)
│   └── results/          (Detection results)
└── templates/
    ├── index.html        (Upload page)
    └── result.html       (Results page)

NOTES:
- Make sure to download YOLO weights before running
- The system detects: birds, cats, dogs, horses, sheep, cows, elephants, bears, zebras, and giraffes
- Map integration uses OpenStreetMap (free API)
