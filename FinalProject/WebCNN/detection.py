import os
import cv2
import numpy as np
import tensorflow as tf
from keras import backend
from keras.preprocessing import image
from keras.models import load_model
from FinalProject.settings import BASE_DIR, RESULT_ROOT, detection_model_path, emotion_model_path, gender_model_path, \
    emotion_labels, gender_labels


def load_image(image_path, grayscale=False, target_size=None):
    pil_image = image.load_img(image_path, grayscale, target_size)
    return image.img_to_array(pil_image)


def load_detection_model(model_path):
    detection_model = cv2.CascadeClassifier(model_path)
    return detection_model


def detect_faces(detection_model, gray_image_array):
    return detection_model.detectMultiScale(gray_image_array, 1.3, 5)


def draw_bounding_box(face_coordinates, image_array, color):
    x, y, w, h = face_coordinates
    cv2.rectangle(image_array, (x, y), (x + w, y + h), color, 2)


def apply_offsets(face_coordinates, offsets):
    x, y, width, height = face_coordinates
    x_off, y_off = offsets
    return (x - x_off, x + width + x_off, y - y_off, y + height + y_off)


def draw_text(coordinates, image_array, text, color, x_offset=0, y_offset=0,
              font_scale=2, thickness=2):
    x, y = coordinates[:2]
    cv2.putText(image_array, text, (x + x_offset, y + y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, color, thickness, cv2.LINE_AA)


def preprocess_input(x, v2=True):
    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x


backend.clear_session()
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
gender_classifier = load_model(gender_model_path, compile=False)
graph = tf.get_default_graph()


def prediction(image_path, write_path):
    with graph.as_default():
        font = cv2.FONT_HERSHEY_SIMPLEX
        gender_offsets = (10, 10)
        emotion_offsets = (0, 0)

        image_path1 = BASE_DIR.replace(os.path.sep, '/') + str(image_path)
        write_path1 = os.path.join(RESULT_ROOT, write_path)

        # getting input model shapes for inference
        emotion_target_size = emotion_classifier.input_shape[1:3]
        gender_target_size = gender_classifier.input_shape[1:3]

        # loading images
        rgb_image = load_image(image_path1, grayscale=False)
        gray_image = load_image(image_path1, grayscale=True)
        gray_image = np.squeeze(gray_image)
        gray_image = gray_image.astype('uint8')

        faces = detect_faces(face_detection, gray_image)
        for face_coordinates in faces:
            x1, x2, y1, y2 = apply_offsets(face_coordinates, gender_offsets)
            rgb_face = rgb_image[y1:y2, x1:x2]

            x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
            gray_face = gray_image[y1:y2, x1:x2]

            try:
                rgb_face = cv2.resize(rgb_face, (gender_target_size))
                gray_face = cv2.resize(gray_face, (emotion_target_size))
            except:
                continue

            rgb_face = preprocess_input(rgb_face, False)
            rgb_face = np.expand_dims(rgb_face, 0)
            gender_prediction = gender_classifier.predict(rgb_face)
            gender_label_arg = np.argmax(gender_prediction)
            gender_text = gender_labels[gender_label_arg]

            gray_face = preprocess_input(gray_face, True)
            gray_face = np.expand_dims(gray_face, 0)
            gray_face = np.expand_dims(gray_face, -1)
            emotion_label_arg = np.argmax(emotion_classifier.predict(gray_face))
            emotion_text = emotion_labels[emotion_label_arg]

            if gender_text == gender_labels[0]:
                color = (0, 0, 255)
            else:
                color = (255, 0, 0)
            draw_bounding_box(face_coordinates, rgb_image, color)
            draw_text(face_coordinates, rgb_image, gender_text, color, 0, -20, 1, 2)
            draw_text(face_coordinates, rgb_image, emotion_text, color, 0, -50, 1, 2)
        bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(write_path1, bgr_image)
