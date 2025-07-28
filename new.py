import json
import pickle
import random
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.callbacks import EarlyStopping # <--- Import EarlyStopping

nltk.download('punkt')
lemmatizer = WordNetLemmatizer()

# Load intents
intents = json.loads(open('intents.json').read())

words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
words = sorted(set(words))

classes = sorted(set(classes))

# Save words and classes
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# Training data
training = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    word_patterns = [lemmatizer.lemmatize(w.lower()) for w in doc[0]]
    for w in words:
        bag.append(1) if w in word_patterns else bag.append(0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

random.shuffle(training)
training = np.array(training, dtype=object)

train_x = list(training[:, 0])
train_y = list(training[:, 1])

# Define model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

# Compile
sgd = SGD(learning_rate=0.01, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# <--- Add EarlyStopping callback
early_stopping = EarlyStopping(
    monitor='val_loss', # Monitor validation loss
    patience=20,        # Stop if val_loss doesn't improve for 20 epochs
    restore_best_weights=True # Restore weights from the epoch with best val_loss
)

# Train and save
print("\nStarting model training...")
history = model.fit(
    np.array(train_x),
    np.array(train_y),
    epochs=200,          # Max epochs
    batch_size=5,
    verbose=1,
    validation_split=0.2, # Use 20% of data for validation
    callbacks=[early_stopping] # <--- Add the callback here
)
model.save('chatbot_simplelearnmodel.h5')
print("Training finished and model saved.")
print(f"Final training accuracy: {history.history['accuracy'][-1]:.4f}")
if 'val_accuracy' in history.history:
    print(f"Final validation accuracy: {history.history['val_accuracy'][-1]:.4f}")
print("Executed")
