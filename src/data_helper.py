

def readDataToLines(filename_lines, filename_conversations): 
    #read files into memory  
    movie_lines = open("data/movie_lines.txt", encoding="utf-8", errors="ignore").read()
    movie_conversations = open("data/movie_conversations.txt", encoding="utf-8", errors="ignore").read()
    #split files at "\n" (linebreak chracter), tranforms into array of lines
    movie_lines = movie_lines.split("\n")
    movie_conversations = movie_conversations.split("\n")
    
    return movie_lines, movie_conversations