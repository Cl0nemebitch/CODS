import numpy as np
from PIL import Image
import tensorflow as tf


MODEL_PATH = "model/camouflage_classifier.h5"
IMG_SIZE = (128, 128)
CLASS_NAMES_PATH = "model/class_names.txt"
CAMOUFLAGE_THRESHOLD = 0.5
UNCERTAIN_MARGIN = 0.1


def load_model():
    return tf.keras.models.load_model(MODEL_PATH)


def load_class_names():
    try:
        with open(CLASS_NAMES_PATH, "r", encoding="utf-8") as f:
            names = [line.strip() for line in f if line.strip()]
        if len(names) >= 2:
            return names
    except FileNotFoundError:
        pass
    # Fallback class order used in training
    return ["normal", "camouflage"]


def preprocess_image(image):
    image = image.convert("RGB")
    image = image.resize(IMG_SIZE, Image.Resampling.LANCZOS)
    image_array = np.array(image, dtype=np.float32) / 255.0
    image_array = np.expand_dims(image_array, axis=0)
    return image_array


def predict_image(
    image,
    model=None,
    threshold=CAMOUFLAGE_THRESHOLD,
    margin=UNCERTAIN_MARGIN,
):
    if model is None:
        model = load_model()
    class_names = load_class_names()

    image_array = preprocess_image(image)
    probability_class1 = float(model.predict(image_array, verbose=0)[0][0])
    class1_name = class_names[1].lower()
    camouflage_probability = (
        probability_class1 if class1_name == "camouflage" else 1.0 - probability_class1
    )

    lower = threshold - (margin / 2)
    upper = threshold + (margin / 2)

    if lower <= camouflage_probability <= upper:
        label = "Uncertain (near threshold)"
        confidence = max(camouflage_probability, 1.0 - camouflage_probability) * 100
    elif camouflage_probability > threshold:
        label = "Camouflage Detected"
        confidence = camouflage_probability * 100
    else:
        label = "No Camouflage"
        confidence = (1 - camouflage_probability) * 100

    return label, confidence, camouflage_probability
