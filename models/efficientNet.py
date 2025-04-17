import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.applications.efficientnet_v2 import EfficientNetV2B0, preprocess_input

# Parameters
dataset_path = "/root/butterfly/SOUTH FL Butterflies NEW"
img_size = (224, 224)
batch_size = 32
epochs = 30
seed = 42

# Data augmentation
data_augmentation = tf.keras.Sequential([
    tf.keras.layers.RandomFlip("horizontal"),
    tf.keras.layers.RandomRotation(0.1),
    tf.keras.layers.RandomZoom(0.1),
    tf.keras.layers.RandomContrast(0.1)
])

# Load dataset
full_dataset = tf.keras.utils.image_dataset_from_directory(
    dataset_path,
    image_size=img_size,
    batch_size=batch_size,
    label_mode='categorical',
    shuffle=True,
    seed=seed
)

# Class names
class_names = full_dataset.class_names
num_classes = len(class_names)
print(f"Using {num_classes} classes: {class_names}")

# Preprocessing
full_dataset = full_dataset.map(lambda x, y: (preprocess_input(x), y))

# Shuffle and split
dataset_batches = full_dataset.cardinality().numpy()
full_dataset = full_dataset.shuffle(buffer_size=dataset_batches, seed=seed)

train_size = int(0.7 * dataset_batches)
val_size = int(0.2 * dataset_batches)

train_ds = full_dataset.take(train_size)
remaining = full_dataset.skip(train_size)
val_ds = remaining.take(val_size)
test_ds = remaining.skip(val_size)

# Augment training
train_ds = train_ds.map(lambda x, y: (data_augmentation(x, training=True), y))

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)
test_ds = test_ds.cache().prefetch(buffer_size=AUTOTUNE)

# Base model
base_model = EfficientNetV2B0(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet',
    pooling=None
)
base_model.trainable = True
for layer in base_model.layers[:-40]:
    layer.trainable = False

# Build model
model = tf.keras.Sequential([
    base_model,
    tf.keras.layers.GlobalAveragePooling2D(),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(num_classes, activation='softmax')
])

# Compile
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks
callbacks = [
    tf.keras.callbacks.EarlyStopping(patience=5, restore_best_weights=True),
    tf.keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=2, verbose=1)
]

# Train
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs,
    callbacks=callbacks
)

# Evaluate
test_loss, test_accuracy = model.evaluate(test_ds)
print(f"Test accuracy: {test_accuracy:.4f}")
print(f"Test loss: {test_loss:.4f}")

# Save the model as a .keras file
model_path = "/root/butterfly/butterfly_classifier.keras"
model.save(model_path)
print(f"Model saved to: {model_path}")

# Classification report
y_true = []
y_pred = []

for images, labels in test_ds:
    preds = model.predict(images)
    y_true.extend(np.argmax(labels.numpy(), axis=1))
    y_pred.extend(np.argmax(preds, axis=1))

report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
report_df = pd.DataFrame(report).transpose()

# Save report
report_path = "/root/butterfly/classification_report.csv"
report_df.to_csv(report_path)
print(f"Classification report saved to: {report_path}")

# Confusion matrix
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, xticklabels=class_names, yticklabels=class_names, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.tight_layout()

# Save CM
cm_path = "/root/butterfly/confusion_matrix.png"
plt.savefig(cm_path)
print(f"Confusion matrix saved to: {cm_path}")