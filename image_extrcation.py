import cv2
import easyocr

# Load pre-trained model
reader = easyocr.Reader(['en'])

# Read the image
image = cv2.imread("2.png")

# Perform text detection and recognition
result = reader.readtext(image)

# Draw bounding boxes around the detected text and print the recognized text
for detection in result:
    bbox = detection[0]
    text = detection[1]
    cv2.rectangle(image, (int(bbox[0][0]), int(bbox[0][1])), (int(bbox[2][0]), int(bbox[2][1])), (0, 255, 0), 2)
    cv2.putText(image, text, (int(bbox[0][0]), int(bbox[0][1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    print("Detected text:", text)

# Save the output image
cv2.imwrite("output_image_with_text.jpg", image)

print("Text detection and recognition completed.")
print("Output saved as output_image_with_text.jpg")
