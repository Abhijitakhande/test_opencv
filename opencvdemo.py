import cv2

# Load pre-trained model
net = cv2.dnn.readNet("frozen_inference_graph.pb", "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt")

# List of classes detected by the model
classes = []
with open("labels.txt", "r") as f:
    classes = f.read().splitlines()

# Read the image
image = cv2.imread("2.jpg")

# Convert the image to blob format
blob = cv2.dnn.blobFromImage(image, 1.0/127.5, (300, 300), (127.5, 127.5, 127.5), swapRB=True, crop=False)

# Set the input for the network
net.setInput(blob)

# Run forward pass to get detections
detections = net.forward()

# Loop over the detections
for i in range(detections.shape[2]):
    confidence = detections[0, 0, i, 2]

    # Filter out weak detections
    if confidence > 0.5:
        class_id = int(detections[0, 0, i, 1])

        # Get the bounding box coordinates
        box = detections[0, 0, i, 3:7] * [image.shape[1], image.shape[0], image.shape[1], image.shape[0]]
        (startX, startY, endX, endY) = box.astype("int")

        # Draw the bounding box and label on the image
        cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)
        label = f"{classes[class_id]}: {confidence:.2f}"
        cv2.putText(image, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

# Save the output image
cv2.imwrite("output_image.jpg", image)

print("Object detection completed. Output saved as output_image.jpg.")