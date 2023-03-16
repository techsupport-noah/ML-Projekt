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

print("(1) General/Base Model\n")
print("(2) Romance Model\n")
print("(3) Action Model\n")


#Eingabe Genre
genreInput = input("Choose Genre (by number): ")

if(genreInput == "1"):
    genre = "all"
if(genreInput == "2"):
    genre = "romance"
if(genreInput == "3"):
    genre = "action"
#if genreInput was not 1, 2 or 3, the program will exit
if(genreInput != "1" and genreInput != "2" and genreInput != "3"):
    print("Please choose a valid number")
    exit()

# load tokenizer with pickle
with open(f"models/tokenizer_{genre}.pickle", "rb") as f:
    tokenizer = pickle.load(f)

VOCABULARY_SIZE = len(tokenizer.word_index) + 1
# print("Size: ", VOCABULARY_SIZE)

padding_index = tokenizer.word_index["<P>"]
# print("Padding index: ", padding_index)

# read vocab_size
# with open("models/vocab_size.txt", "r") as f:
    # VOCABULARY_SIZE = int(f.read())
dense = Dense(VOCABULARY_SIZE, activation="softmax")

# parameters

outputDimension = 50
lstm_units = 400
max_sentence_length = 12 

# load model

embedding = tf.keras.layers.Embedding(VOCABULARY_SIZE, output_dim = outputDimension, trainable=True)
inputEncoderTensor = tf.keras.Input(shape=(None, ))
encoderEmbedding = embedding(inputEncoderTensor)
encoderLSTM = tf.keras.layers.LSTM(lstm_units, return_sequences=True, return_state = True)
encoderOutput, encoderHiddenState, encoderCellState = encoderLSTM(encoderEmbedding)
encoderStates = [encoderHiddenState, encoderCellState]
inputDecoderTensor = tf.keras.Input(shape=(None, ))
decoderEmbedding = embedding(inputDecoderTensor)
decoderLSTM = tf.keras.layers.LSTM(lstm_units, return_state = True, return_sequences=True)
decoderOutput, _, _ = decoderLSTM(decoderEmbedding, initial_state = encoderStates)
decoderDense = tf.keras.layers.Dense(VOCABULARY_SIZE, activation = "softmax")
outputDense = decoderDense(decoderOutput)

model = tf.keras.models.Model([inputEncoderTensor, inputDecoderTensor], outputDense)

# compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# apply saved weights
model.load_weights(f"models/weights_{genre}.h5")

# create interference model

# encoder
encoder_model = Model([inputEncoderTensor], encoderStates)
# decoder
decoder_state_input_h = Input(shape=(lstm_units, ))
decoder_state_input_c = Input(shape=(lstm_units, ))
decoder_state_inputs = [decoder_state_input_h, decoder_state_input_c]
decoder_ouputs, state_h, state_c = decoderLSTM(decoderEmbedding, initial_state=decoder_state_inputs)
decoder_states = [state_h, state_c]
decoder_model = Model([inputDecoderTensor] + decoder_state_inputs, [decoder_ouputs] + decoder_states)




print("\n   Chatbot-Interactive Input   \n")

userInput = ""

while userInput != "exit":

    # Eingabe des Benutzers
    userInput = input("You: ")

    # skip empty input
    if userInput == "": 
        continue

    userInput = dh.cleanLine(userInput)
    userInput_list = [userInput]

    # tokenize input
    text = tokenizer.texts_to_sequences(userInput_list)

    # check if only unknown input was given
    if all(word == 1 for word in text):
        print("Chatbot: Sorry, I don't understand this.", "\n")
        continue
    
    # pad input to same length as in training
    text = pad_sequences(text, padding="post", maxlen=max_sentence_length, truncating="post", value=padding_index)
    states = encoder_model.predict(text, verbose=0)

    empty_target_sequence = np.zeros((1, 1))
    empty_target_sequence[0,0] = tokenizer.word_index["<S>"] # start answer with start token

    stop_condition = False
    answer = ""

    while not stop_condition:

        decoder_ouputs, h, c = decoder_model.predict([empty_target_sequence] + states, verbose=0)

        decoder_concatination_input = decoderDense(decoder_ouputs)

        # get index of word with highest probability
        sampled_word_index = np.argmax(decoder_concatination_input[0, -1, :])
        
        if sampled_word_index == 0:
            stop_condition = True
            sampled_word_index = np.argsort(decoder_concatination_input[0, -1, :])[-2]

        # find associated word
        sampled_word = tokenizer.index_word[sampled_word_index] + " "

        if sampled_word != "<E> ":
            answer += sampled_word

        # end if end token is reached or answer is too long
        if sampled_word == "<E> " or len(answer.split()) > 20:
            stop_condition = True

        empty_target_sequence = np.zeros((1, 1))
        empty_target_sequence[0, 0] = sampled_word_index
        states = [h, c]

    print("Chatbot: ", answer, "\n")