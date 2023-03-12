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


encoder_model = load_model("models/encoder_model.h5")
decoder_model = load_model("models/decoder_model.h5")
# read vocab_size
with open("models/vocab_size.txt", "r") as f:
    VOCABULARY_SIZE = int(f.read())
dense = Dense(VOCABULARY_SIZE, activation="softmax")
# load tokenizer with pickle
with open("models/tokenizer.pickle", "rb") as f:
    tokenizer = pickle.load(f)




print("##############################\n#   Michelle-Kauan-Chatbot   #\n##############################")

# Eingabe des Benutzers
user_input = input("You: ")

while user_input != "quit":
    # Vorbereitung
    user_input = dh.cleanLine(user_input)
    user_input_list = [user_input]

    # Eingabe in ganzzahlige Werte konvertieren
    text = []
    for input_list in user_input_list:
        word_list = []
        for word in input_list.split():
            try:
                word_list.append(tokenizer.word_index[word])
            except:
                word_list.append(tokenizer.word_index["<OUT>"])
        text.append(word_list)

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
        decoder_concatination_input = dense(decoder_ouputs)

        # Index des Wortes mit der höchsten Wahrscheinlichkeit
        sampled_word_index = np.argmax(decoder_concatination_input[0, -1, :])

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