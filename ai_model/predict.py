
import tensorflow as tf
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "waste_model.keras"
CLASS_PATH = BASE_DIR / "class_names.txt"

model = tf.keras.models.load_model(MODEL_PATH)

with open(CLASS_PATH, "r") as file:
    class_names = file.read().splitlines()


def predict_waste(image_path):
    image = tf.keras.utils.load_img(
        image_path,
        target_size=(180, 180)
    )

    image_array = tf.keras.utils.img_to_array(image)
    image_array = np.expand_dims(image_array, axis=0)

    predictions = model.predict(image_array, verbose=0)

    predicted_index = int(np.argmax(predictions[0]))
    confidence = float(predictions[0][predicted_index]) * 100

    return {
        "category": class_names[predicted_index],
        "confidence": round(confidence, 2)
    }


if __name__ == "__main__":
    test_image = input("Enter image path: ")
    result = predict_waste(test_image)

    print("Predicted category:", result["category"])
    print("Confidence:", result["confidence"], "%")
