import os
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models


# Project settings
DATASET_DIR = "dataset/Train"
IMG_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 13
MODEL_PATH = "model/camouflage_classifier.h5"
PLOT_PATH = "model/training_plot.png"
CLASS_NAMES_PATH = "model/class_names.txt"
CLASS_ORDER = ["normal", "camouflage"]


def validate_dataset_labels():
    checks = [
        ("camouflage", "normal_"),
        ("normal", "camouflage_"),
    ]
    mismatches = []

    for folder, wrong_prefix in checks:
        folder_path = os.path.join(DATASET_DIR, folder)
        if not os.path.isdir(folder_path):
            continue
        for name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, name)
            if os.path.isfile(file_path) and name.lower().startswith(wrong_prefix):
                mismatches.append(file_path)

    if mismatches:
        preview = "\n".join(mismatches[:10])
        raise ValueError(
            "Found likely mislabeled files (filename prefix does not match folder).\n"
            "Fix these before training to avoid false predictions.\n"
            f"Examples:\n{preview}"
        )


def load_datasets():
    if not os.path.isdir(DATASET_DIR):
        raise FileNotFoundError(
            f"Dataset folder not found: '{DATASET_DIR}'. "
            "Expected structure: dataset/Train/camouflage and dataset/Train/normal"
        )

    class_dirs = [
        d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))
    ]
    if len(class_dirs) < 2:
        raise ValueError(
            f"Found only {len(class_dirs)} class folder(s) in '{DATASET_DIR}'. "
            "Binary classification needs 2 folders: 'camouflage' and 'normal'."
        )

    train_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=0.2,
        subset="training",
        seed=42,
        class_names=CLASS_ORDER,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="binary",
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        DATASET_DIR,
        validation_split=0.2,
        subset="validation",
        seed=42,
        class_names=CLASS_ORDER,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        label_mode="binary",
    )
    class_names = train_ds.class_names

    # Normalize pixel values from [0,255] to [0,1]
    normalization_layer = layers.Rescaling(1.0 / 255.0)
    train_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
    val_ds = val_ds.map(lambda x, y: (normalization_layer(x), y))

    # Improve performance
    train_ds = train_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=tf.data.AUTOTUNE)

    return train_ds, val_ds, class_names


def build_model():
    data_augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.1),
            layers.RandomZoom(0.1),
        ],
        name="data_augmentation",
    )

    model = models.Sequential(
        [
            layers.Input(shape=(128, 128, 3)),
            data_augmentation,
            layers.Conv2D(32, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    return model


def save_training_plot(history):
    os.makedirs("model", exist_ok=True)

    plt.figure(figsize=(10, 4))

    plt.subplot(1, 2, 1)
    plt.plot(history.history["accuracy"], label="Train Accuracy")
    plt.plot(history.history["val_accuracy"], label="Val Accuracy")
    plt.title("Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.plot(history.history["loss"], label="Train Loss")
    plt.plot(history.history["val_loss"], label="Val Loss")
    plt.title("Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend()

    plt.tight_layout()
    plt.savefig(PLOT_PATH)
    plt.close()


def main():
    print("Loading dataset...")
    validate_dataset_labels()
    train_ds, val_ds, class_names = load_datasets()
    print(f"Detected class order: {class_names}")

    print("Building model...")
    model = build_model()
    model.summary()

    print("Training model...")
    os.makedirs("model", exist_ok=True)

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=EPOCHS
    )

    model.save(MODEL_PATH)
    print(f"Model saved successfully at: {MODEL_PATH}")

    with open(CLASS_NAMES_PATH, "w", encoding="utf-8") as f:
        for name in class_names:
            f.write(name + "\n")
    print(f"Class names saved at: {CLASS_NAMES_PATH}")

    save_training_plot(history)
    print(f"Training plot saved at: {PLOT_PATH}")


if __name__ == "__main__":
    main()
