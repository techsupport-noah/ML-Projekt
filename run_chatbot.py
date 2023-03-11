import numpy as np
from pathlib import Path
import sys

from tensorflow.keras.layers import Dense, Embedding, LSTM, Input
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences


module_path = str(Path.cwd() / "src")
if module_path not in sys.path:
    sys.path.append(module_path)

import src.data_helper as dh

outputDimension = 50 
lstm_units = 256
max_sentence_length = 32

"""
Laden der benötigten Daten
"""
# Laden der beiden Vokabulare
index2word = np.load('./data/index2word.dict.npy',allow_pickle='TRUE').item()
word2index = np.load('./data/word2index.dict.npy',allow_pickle='TRUE').item()

# Laden der Layer
w_embedding = np.load('./models/embeddingEncoderLayer.npz', allow_pickle=True)
w_encoder_lstm = np.load('./models/lstmEncoderLayer.npz', allow_pickle=True)
w_decoder_lstm = np.load('./models/lstmDecoderLayer.npz', allow_pickle=True)
w_dense = np.load('./models/denseLayer.npz', allow_pickle=True)

"""
Erstellen des Trainingsmodelles
Genauere Ausführungen sind in dem Hauptdokument zu finden
"""
# Eingabe-Platzhalter für Encoder und Decoder erstellen
encoder_input_placeholder = Input(shape=(max_sentence_length, ))
decoder_input_placeholder = Input(shape=(max_sentence_length, ))
# Embedding-Layer erstellen
VOCABULARY_SIZE = len(index2word)
embedding = Embedding(VOCABULARY_SIZE+1, output_dim=50, input_length=13, trainable=True)
# Encoder-Eingabe dem Emebdding-Layer übergeben
encoder_embedding = embedding(encoder_input_placeholder)
# Encoder-LSTM-Layer erstellen
encoder_lstm = LSTM(lstm_units, return_sequences=True, return_state=True)
# Encoder-Embedding-Ausgabe dem Encoder-LSTM-Layer übergeben
encoder_output, h, c = encoder_lstm(encoder_embedding)
encoder_states = [h, c]
# Decoder-LSTM-Layer erstellen
decoder_embedding = embedding(decoder_input_placeholder)
decoder_lstm = LSTM(lstm_units, return_sequences=True, return_state=True)
decoder_output, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
# Erstellen des Dense-Layers
dense = Dense(VOCABULARY_SIZE, activation="softmax")
# Decoder-Ausgabe dem Dense-Layer übergeben, um Dense-Ausgabe zu erhalten
dense_output = dense(decoder_output)
loaded_model = Model([encoder_input_placeholder, decoder_input_placeholder], dense_output)

# loaded_model.summary()

"""
Anwenden der geladenen Layer auf das neue Modell
"""
loaded_model.layers[2].set_weights(w_embedding['arr_0'])
loaded_model.layers[3].set_weights(w_encoder_lstm['arr_0'])
loaded_model.layers[4].set_weights(w_decoder_lstm['arr_0'])
loaded_model.layers[5].set_weights(w_dense['arr_0'])

"""
Erstellen des Interferenz-Modells
Genauere Ausführungen sind in dem Hauptdokument zu finden
"""
# Encoder-Modell erstellen
encoder_model = Model([encoder_input_placeholder], encoder_states)
# Decoder Eingaben erstellen
decoder_state_input_h_placeholder = Input(shape=(lstm_units, ))
decoder_state_input_c_placeholder = Input(shape=(lstm_units, ))
decoder_state_inputs_placeholder = [decoder_state_input_h_placeholder, decoder_state_input_c_placeholder]
decoder_ouputs, state_h, state_c = decoder_lstm(decoder_embedding, initial_state=decoder_state_inputs_placeholder)
decoder_states = [state_h, state_c]
# Decoder-Modell erstellen
decoder_model = Model([decoder_input_placeholder] + decoder_state_inputs_placeholder, [decoder_ouputs] + decoder_states)

"""
Ausführung des interaktiven Chatbots
"""
print("##############################\n#   Chatbot   #\n##############################")

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
                word_list.append(word2index[word])
            except:
                word_list.append(word2index["<UNK>"])
        text.append(word_list)

    # Länge 13 festlegen
    text = pad_sequences(text, max_sentence_length, padding="post")

    states = encoder_model.predict(text)

    empty_target_sequence = np.zeros((1, 1))
    empty_target_sequence[0,0] = word2index["<S>"]

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
        sampled_word = index2word[sampled_word_index] + " "

        # Wort als Chatbot-Antwort speichern
        if sampled_word != "<E> ":
            answer += sampled_word

        # Antwort beenden falls <END>-Token oder maximale Länge erreicht
        if sampled_word == "<E> " or len(answer.split()) > max_sentence_length:
            stop_condition = True

        # Werte zurücksetzen
        empty_target_sequence = np.zeros((1, 1))
        empty_target_sequence[0, 0] = sampled_word_index
        states = [h, c]

    print("Chatbot: ", answer, "\n==============================")
    # Hier nächste Ei
    # ngabe des Benutzers, um die Abbruchbedingung reichtzeiH