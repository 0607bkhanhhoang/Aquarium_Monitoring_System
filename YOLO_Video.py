from ultralytics import YOLO
import cv2
import math

def video_detection(path_x):
    video_capture = path_x

    # Create a Webcam Object
    cap = cv2.VideoCapture(video_capture)
    if not cap.isOpened():
        raise ValueError("Unable to open video capture device. Check the path or webcam index.")

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    model = YOLO("/Users/buikh/workspace/MILESTONE_2_HK241/Aquarium_Monitoring_System/YOLO-Weights/fish.pt")
    classNames = [
        'Acanthuridae -Surgeonfishes', 'Carangidae -Jacks', 'Labridae -Snappers', 
        'Scaridae -Parrrotfishes', 'Scombridae -Tunas-', 'Serranidae -Groupers', 
        'Shark -Selachimorpha', 'Zanclidae -Moorish Idol'
    ]

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read from the video capture device.")
            break

        results = model(img, stream=True)
        for r in results:
            boxes = r.boxes
            for box in boxes:
                # Extract bounding box coordinates
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                conf = math.ceil((box.conf[0] * 100)) / 100  # Confidence level

                # Extract class index
                cls = int(box.cls[0])
                if cls < 0 or cls >= len(classNames):
                    print(f"Invalid class index {cls}. Skipping...")
                    continue

                class_name = classNames[cls]
                label = f'{class_name} {conf}'
                t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
                c2 = x1 + t_size[0], y1 - t_size[1] - 8

                # Define colors based on the class
                color_map = {
                    "Labridae -Snappers": (0, 204, 255),
                    "Carangidae -Jacks": (222, 82, 175),
                    "Acanthuridae -Surgeonfishes": (0, 149, 255),
                    "Scaridae -Parrrotfishes": (0, 19, 255),
                    "Scombridae -Tunas-": (0, 109, 255),
                    "Serranidae -Groupers": (0, 80, 255),
                    "Shark -Selachimorpha": (0, 255, 19),
                    "Zanclidae -Moorish Idol": (0, 135, 245)
                }
                color = color_map.get(class_name, (85, 45, 255))  # Default color

                # Draw bounding boxes and labels
                if conf > 0.5:
                    cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
                    cv2.rectangle(img, (x1, y1), c2, color, -1, cv2.LINE_AA)  # Filled box for label
                    cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

        yield img  # Yield the processed frame

    cap.release()
    cv2.destroyAllWindows()


# def video_detection(path_x):
#     video_capture = path_x

#     # Create a Webcam Object
#     cap = cv2.VideoCapture(video_capture)
#     frame_width = int(cap.get(3))
#     frame_height = int(cap.get(4))

#     model = YOLO("YOLO-Weights/fish.pt")
#     classNames = ['Acanthuridae -Surgeonfishes', 'Carangidae -Jacks', 'Labridae -Snappers', 
#                   'Scaridae -Parrrotfishes', 'Scombridae -Tunas-', 'Serranidae -Groupers', 
#                   'Shark -Selachimorpha', 'Zanclidae -Moorish Idol']
    
#     while True:
#         success, img = cap.read()
#         if not success:
#             print("Failed to read from the video capture device.")
#             break

#         results = model(img, stream=True)
#         for r in results:
#             boxes = r.boxes
#             for box in boxes:
#                 x1, y1, x2, y2 = box.xyxy[0]
#                 x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
#                 conf = math.ceil((box.conf[0] * 100)) / 100
#                 cls = int(box.cls[0])

#                 # Validate class index
#                 if cls < 0 or cls >= len(classNames):
#                     print(f"Invalid class index {cls}. Skipping...")
#                     continue

#                 class_name = classNames[cls]
#                 label = f'{class_name} {conf}'
#                 t_size = cv2.getTextSize(label, 0, fontScale=1, thickness=2)[0]
#                 c2 = x1 + t_size[0], y1 - t_size[1] - 8

#                 # Define colors based on the class
#                 color_map = {
#                     "Labridae -Snappers": (0, 204, 255),
#                     "Carangidae -Jacks": (222, 82, 175),
#                     "Acanthuridae -Surgeonfishes": (0, 149, 255),
#                     "Scaridae -Parrrotfishes": (0, 19, 255),
#                     "Scombridae -Tunas-": (0, 109, 255),
#                     "Serranidae -Groupers": (0, 80, 255),
#                     "Shark -Selachimorpha": (0, 255, 19),
#                     "Zanclidae -Moorish Idol": (0, 135, 245)
#                 }
#                 color = color_map.get(class_name, (85, 45, 255))  # Default color

#                 if conf > 0.5:
#                     cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
#                     cv2.rectangle(img, (x1, y1), c2, color, -1, cv2.LINE_AA)  # filled
#                     cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=1, lineType=cv2.LINE_AA)

#         yield img

#     cap.release()
#     cv2.destroyAllWindows()
