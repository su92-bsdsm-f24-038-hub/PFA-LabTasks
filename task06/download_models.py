import urllib.request
import os

print("Downloading YOLOv3 weights...")

weights_url = "https://pjreddie.com/media/files/yolov3.weights"
cfg_url = "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg"

models_dir = "models"
os.makedirs(models_dir, exist_ok=True)

weights_path = os.path.join(models_dir, "yolov3.weights")
cfg_path = os.path.join(models_dir, "yolov3.cfg")

if not os.path.exists(weights_path):
    print("Downloading yolov3.weights (this may take a while)...")
    urllib.request.urlretrieve(weights_url, weights_path)
    print("Downloaded yolov3.weights")
else:
    print("yolov3.weights already exists")

if not os.path.exists(cfg_path):
    print("Downloading yolov3.cfg...")
    urllib.request.urlretrieve(cfg_url, cfg_path)
    print("Downloaded yolov3.cfg")
else:
    print("yolov3.cfg already exists")

print("Download complete! You can now run: python app.py")
