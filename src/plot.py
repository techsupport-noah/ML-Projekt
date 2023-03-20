import matplotlib.pyplot as plt
import numpy as np 

# Listen, welche extrahiert werden sollen
time = []
loss = []
accuracy = []

# Durchgehen der Daten in der Textdatei
i = 0
with open("../lernkurve.txt") as file:
    for line in file:
        if i%2 == 1:
            split_line = line.split(" - ")
            # Speichern der EInträge in den Listen
            time.append(split_line[1])
            loss.append(split_line[2].split()[1])
            accuracy.append(split_line[3].split()[1])
        i+=1

 # Umwandeln der Strings in Floats
loss = list(map(float, loss))
accuracy = list(map(float, accuracy))

# Erstellen einer Liste für die x-Achse
epochs = list(range(1, len(accuracy)+1))

plt.plot(epochs, accuracy)
plt.xlabel('Epochen')
plt.ylabel('Accuracy')
plt.show()

plt.plot(epochs, loss)
plt.xlabel('Epochen')
plt.ylabel('Verlust')
plt.show()