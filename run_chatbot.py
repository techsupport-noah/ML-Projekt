import tensorflow as tf
import random 
import re #re = regular expressions
import os
import numpy as np 
from collections import Counter
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.layers import Dense, Embedding, LSTM, Input
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.utils import to_categorical
from matplotlib import pyplot as plt
import src.data_helper as dh
import pickle


# read vocab_size
with open("models/vocab_size.txt", "r") as f:
    VOCABULARY_SIZE = int(f.read())
dense = Dense(VOCABULARY_SIZE, activation="softmax")
# load tokenizer with pickle
with open("models/tokenizer.pickle", "rb") as f:
    tokenizer = pickle.load(f)

outputDimension = 50
lstm_units = 256

# load training model
embedding = tf.keras.layers.Embedding(VOCABULARY_SIZE, output_dim = outputDimension, trainable=True)
# input tensor for the encoder, shape of each vector is determined by max_length which was also used to pad the data
inputEncoderTensor = tf.keras.Input(shape=(None, ))

# embedding layer of the encoder, the input is the input tensor, the output is the embedding tensor
encoderEmbedding = embedding(inputEncoderTensor)

# LSTM layer of the encoder, the input is the embedding tensor, the output is the output tensor and the hidden state of the encoder
encoderLSTM = tf.keras.layers.LSTM(lstm_units, return_sequences=True, return_state = True)
encoderOutput, encoderHiddenState, encoderCellState = encoderLSTM(encoderEmbedding)
encoderStates = [encoderHiddenState, encoderCellState]
# input tensor for the decoder, shape of each vector is determined by max_length which was also used to pad the data
inputDecoderTensor = tf.keras.Input(shape=(None, ))

# embedding layer of the decoder, the input is the input tensor, the output is the embedding tensor
decoderEmbedding = embedding(inputDecoderTensor)

# LSTM layer of the decoder, the input is the embedding tensor and the state of the previous lstm layer, the output is the output tensor and the hidden state of the decoder
decoderLSTM = tf.keras.layers.LSTM(lstm_units, return_state = True, return_sequences=True)
decoderOutput, _, _ = decoderLSTM(decoderEmbedding, initial_state = encoderStates)

# dense layer of the decoder, the input is the output tensor of the lstm layer, the output is the output tensor of the dense layer
# the dense layer has the same number of units as the number of words in the dictionary because the output of the dense layer is a vector with a probability for each word in the dictionary
decoderDense = tf.keras.layers.Dense(VOCABULARY_SIZE, activation = "softmax")
outputDense = decoderDense(decoderOutput)
# Define the model 
model = tf.keras.models.Model([inputEncoderTensor, inputDecoderTensor], outputDense)

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# apply saved weights
model.load_weights("models/weights.h5")

# interference model
# Encoder-Modell erstellen
encoder_model = Model([inputEncoderTensor], encoderStates)
# Decoder Eingaben erstellen
decoder_state_input_h_placeholder = Input(shape=(lstm_units, ))
decoder_state_input_c_placeholder = Input(shape=(lstm_units, ))
decoder_state_inputs_placeholder = [decoder_state_input_h_placeholder, decoder_state_input_c_placeholder]
decoder_ouputs, state_h, state_c = decoderLSTM(decoderEmbedding, initial_state=decoder_state_inputs_placeholder)
decoder_states = [state_h, state_c]
# Decoder-Modell erstellen
decoder_model = Model([inputDecoderTensor] + decoder_state_inputs_placeholder, [decoder_ouputs] + decoder_states)




print("##############################\n#   Chatbot   #\n##############################")

user_input = ""

while user_input != "quit":

    # Eingabe des Benutzers
    user_input = input("You: ")

    if user_input == "": 
        continue

    # Vorbereitung
    user_input = dh.cleanLine(user_input)
    user_input_list = [user_input]

    # Eingabe in ganzzahlige Werte konvertieren
    # text = []
    # for input_list in user_input_list:
    #     word_list = []
    #     for word in input_list.split():
    #         try:
    #             word_list.append(tokenizer.word_index[word])
    #         except:
    #             word_list.append(tokenizer.word_index["<OUT>"])
    #     text.append(word_list)

    text = tokenizer.texts_to_sequences(user_input_list)

    # check if text only contains <OUT> tokens
    if len(text[0]) == 1:
        print("Chatbot: Sorry, I don't understand this word/those words.", "\n==============================")
        continue

    # Länge 13 festlegen
    #text = pad_sequences(text, 13, padding="post")

    states = encoder_model.predict(text)

    empty_target_sequence = np.zeros((1, 1))
    empty_target_sequence[0,0] = tokenizer.word_index["<S>"]

    # Dauerschleife bis Ende des Strings oder maximale Länge erreicht
    stop_condition = False
    answer = ""

    while not stop_condition:

        decoder_ouputs, h, c = decoder_model.predict([empty_target_sequence] + states)

        # Dense mit Softmax-Aktivierung
        decoder_concatination_input = decoderDense(decoder_ouputs)

        # Index des Wortes mit der höchsten Wahrscheinlichkeit
        sampled_word_index = np.argmax(decoder_concatination_input[0, -1, :])

        # Index des Wortes mit der zweit höchsten Wahrscheinlichkeit
        # sampled_word_index = np.argsort(decoder_concatination_input[0, -1, :])[-2]
        
        if sampled_word_index == 0:
            sampled_word_index = np.argsort(decoder_concatination_input[0, -1, :])[-2]

        # Wort über invertiertes Vokabular finden
        sampled_word = tokenizer.index_word[sampled_word_index] + " "

        # Wort als Chatbot-Antwort speichern
        if sampled_word != "<E> ":
            answer += sampled_word

        # Antwort beenden falls <END>-Token oder maximale Länge erreicht
        if sampled_word == "<E> " or len(answer.split()) > 13:
            stop_condition = True

        # Werte zurücksetzen
        empty_target_sequence = np.zeros((1, 1))
        empty_target_sequence[0, 0] = sampled_word_index
        states = [h, c]

    print("Chatbot: ", answer, "\n==============================")
    # Hier nächste Eingabe des Benutzers, um die Abbruchbedingung reichtzeiH