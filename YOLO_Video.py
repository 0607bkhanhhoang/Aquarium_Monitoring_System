from ultralytics import YOLO
import cv2
import math

def video_detection(path_x):
    video_capture = path_x
    
    #Create a Webcam Object
    cap=cv2.VideoCapture(video_capture)
    frame_width=int(cap.get(3))
    frame_height=int(cap.get(4))
    
    model=YOLO("YOLO-Weights/fish.pt")
    classNames = ['Acanthuridae -Surgeonfishes', 'Carangidae -Jacks', 'Labridae -Snappers', 'Scaridae -Parrrotfishes', 'Scombridae -Tunas-', 'Serranidae -Groupers', 'Shark -Selachimorpha', 'Zanclidae -Moorish Idol']
    while True:
        success, img = cap.read()
        results=model(img,stream=True)
        for r in results:
            boxes=r.boxes
            for box in boxes:
                x1,y1,x2,y2=box.xyxy[0]
                x1,y1,x2,y2=int(x1), int(y1), int(x2), int(y2)
                print(x1,y1,x2,y2)
                conf=math.ceil((box.conf[0]*100))/100
                cls=int(box.cls[0])
                class_name=classNames[cls]
                label=f'{class_name}{conf}'
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                print(t_size)
                c2 = x1 + t_size[0], y1 - t_size[1] - 8
                if class_name == "Labridae -Snappers":
                    color=(0, 204, 255)
                elif class_name == "Carangidae -Jacks":
                    color = (222, 82, 175)
                elif class_name == "Acanthuridae -Surgeonfishes":
                    color = (0, 149, 255)
                elif class_name == "Scaridae -Parrrotfishes":
                    color = (0, 19, 255)
                elif class_name == "Scombridae -Tunas-":
                    color = (0, 109, 255)
                elif class_name == "Serranidae -Groupers":
                    color = (0, 80, 255)
                elif class_name == "Shark -Selachimorpha":
                    color = (0, 255, 19)
                elif class_name == "Zanclidae -Moorish Idol":
                    color = (0, 135, 245)
                else:
                    color = (85,45,255)
                if conf>0.5:
                    cv2.rectangle(img, (x1,y1), (x2,y2), color,3)
                    cv2.rectangle(img, (x1,y1), c2, color, -1, cv2.LINE_AA)  # filled
                    cv2.putText(img, label, (x1,y1-2),0, 1,[255,255,255], thickness=1,lineType=cv2.LINE_AA)

        yield img
cv2.destroyAllWindows()