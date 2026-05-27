# Camouflaged Image Classification (Binary CNN)

## Objective
This project is a simple deep learning classification app that predicts:
- `camouflage`
- `normal`

The user uploads an image in a local Streamlit app, and the model predicts whether camouflage is present or not.

This is a **binary image classification** project (not segmentation).
No masks, outlines, YOLO, or U-Net are used.

## Dataset Structure
Keep your dataset in this format:

```text
dataset/
  Train/
    camouflage/
    normal/
```

Each folder should contain class images.

## Project Files
- `train.py` -> trains CNN using TensorFlow/Keras and saves model
- `predict.py` -> loads model and predicts from an image
- `app.py` -> Streamlit interface for image upload and prediction
- `requirements.txt` -> required Python packages

## Setup and Run
Install dependencies:

```bash
pip install -r requirements.txt
```

Train the model:

```bash
python train.py
```

Run Streamlit app:

```bash
streamlit run app.py
```

## Optional: Auto-Prepare Dataset From Two Sources
If you have one source folder for camouflage images and one source folder for normal images:

```bash
python prepare_dataset.py --camouflage-source "path_to_camouflage_images" --normal-source "path_to_normal_images" --clean-output
```

Example:

```bash
python prepare_dataset.py --camouflage-source "CAMO-V.1.0-CVIU2019/Images/Train" --normal-source "animal-categories-90-masters-of-survival" --clean-output --max-per-class 2000
```

## Model Details
- Input size: `128x128x3`
- Layers used:
  - `Conv2D`
  - `MaxPooling2D`
  - `Flatten`
  - `Dense`
- Final layer: `Dense(1, activation="sigmoid")`
- Loss: `binary_crossentropy`
- Output model file: `model/camouflage_classifier.h5`

## Prediction Logic
- If predicted probability > 0.5: **Camouflage Detected**
- Else: **No Camouflage**
- Confidence percentage is also shown in the app.

## Viva-Friendly Explanation
1. We load images from two folders (`camouflage`, `normal`) using `image_dataset_from_directory`.
2. All images are resized to `128x128` and normalized to `[0,1]`.
3. A simple CNN learns visual patterns from training images.
4. Since there are only two classes, we use:
   - sigmoid output
   - binary crossentropy loss
5. The trained model is saved and reused in Streamlit for live prediction.
6. The app is local, simple, and suitable for beginner-level college deep learning demonstration.
