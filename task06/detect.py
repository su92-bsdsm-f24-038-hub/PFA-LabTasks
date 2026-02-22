import cv2
import numpy as np
import os

def detect_animals(image_path, output_folder):
    image = cv2.imread(image_path)
    height, width = image.shape[:2]
    
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (416, 416), swapRB=True, crop=False)
    
    net = cv2.dnn.readNet('models/yolov3.weights', 'models/yolov3.cfg')
    
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
    
    net.setInput(blob)
    outputs = net.forward(output_layers)
    
    boxes = []
    confidences = []
    class_ids = []
    
    with open('models/coco.names', 'r') as f:
        classes = [line.strip() for line in f.readlines()]
    
    animal_classes = ['bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']
    
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            
            if confidence > 0.5 and classes[class_id] in animal_classes:
                centerx = int(detection[0] * width)
                centery = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                
                x = int(centerx - w / 2)
                y = int(centery - h / 2)
                
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)
    
    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    
    font = cv2.FONT_HERSHEY_PLAIN
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    
    detected_coords = []
    
    if len(indexes) > 0:
        for i in indexes.flatten():
            x, y, w, h = boxes[i]
            label = str(classes[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            color = colors[class_ids[i]]
            
            cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            cv2.putText(image, label + " " + confidence, (x, y - 5), font, 1, color, 2)
            
            detected_coords.append([x, y, w, h])
    
    result_filename = 'result_' + os.path.basename(image_path)
    result_path = os.path.join(output_folder, result_filename)
    cv2.imwrite(result_path, image)
    
    return result_path, len(indexes) if len(indexes) > 0 else 0, detected_coords

def detect_with_haar(image_path, output_folder):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    cascade = cv2.CascadeClassifier(cascade_path)
    
    detections = cascade.detectMultiScale(gray, 1.1, 4)
    
    for (x, y, w, h) in detections:
        cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
    
    result_filename = 'haar_result_' + os.path.basename(image_path)
    result_path = os.path.join(output_folder, result_filename)
    cv2.imwrite(result_path, image)
    
    return result_path, len(detections), []
