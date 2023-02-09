import random
import re
import numpy


def readDataToLines(filename_lines, filename_conversations): 
    #read files into memory  
    movie_lines = open(filename_lines, encoding="utf-8", errors="ignore").read()
    movie_conversations = open(filename_conversations, encoding="utf-8", errors="ignore").read()
    #split files at "\n" (linebreak chracter), tranforms into array of lines
    movie_lines = movie_lines.split("\n")
    movie_conversations = movie_conversations.split("\n")
    
    return movie_lines, movie_conversations

def readConversationsToList(movie_conversations): 
    #create empty list
    conversation_lists = []

    # iterate over the list of conversations
    for conversation in movie_conversations:
        
        # get the list of the utterances that make the conversation (last element of the split)
        temp = conversation.split(" +++$+++ ")[-1]

        # remove the square brackets
        temp = temp[1:-1]

        # remove the single quotes
        temp = temp.replace("'","")

        # remove the commas
        temp = temp.replace(",","")

        #print(temp + "\n")

        # split the string into a list of utterances
        temp = temp.split()

        #print(temp)
        
        # append the list of utterances to the list of conversations
        conversation_lists.append(temp);

    # shuffle the list of conversations one dimensionally (not the utterances)
    random.shuffle(conversation_lists)

    return conversation_lists

def readLinesToDict(movie_lines):
    #create empty dictionary
    lines_dict = {}

    # iterate over the list of lines
    for line in movie_lines:
        
        # split the line into its components
        temp = line.split(" +++$+++ ")
        
        # if the line has the correct number of components
        if len(temp) == 5:
            
            # get the id of the line
            line_id = temp[0]
            
            # get the text of the line
            line_text = temp[4]
            
            # add the line to the dictionary
            lines_dict[line_id] = line_text

    return lines_dict

def cleanLines(lines_dict):
    #create empty dictionary
    cleaned_lines_dict = {}
    
    # iterate over the lines
    for line_id, line_text in lines_dict.items():
        
        # convert to lowercase
        line_text = line_text.lower()

        # remove punctuation
        line_text = re.sub(r"'m", " am", line_text)
        line_text = re.sub(r"'s", " is", line_text)
        line_text = re.sub(r"'ve", " have", line_text)
        line_text = re.sub(r"'d", " would", line_text)
        line_text = re.sub(r"won't", "will not", line_text)
        line_text = re.sub(r"weren't", "were not", line_text)
        line_text = re.sub(r"'ll", " will", line_text)
        line_text = re.sub(r"'re", " are", line_text)
        line_text = re.sub(r"can't", "can not", line_text)

        # remove every not word character
        line_text = re.sub(r"[^\w\s]", "", line_text)

        # replace the newline character with a space
        line_text = line_text.replace("\n", " ")
        
        # replace the tab character with a space
        line_text = line_text.replace("\t", " ")

        # replace the double space with a single space
        line_text = line_text.replace("  ", " ")
        
        # add the cleaned line to the dictionary
        cleaned_lines_dict[line_id] = line_text
        
    return cleaned_lines_dict

def splitConversationsToRequestAndResponse(conversations_list, lines_dict):
    #create empty list for requests
    requests = []
    #create empty list for responses
    responses = []
    
    # iterate over the list of conversations
    for conversation in conversations_list:
        
        # iterate over the list of utterances in the conversation
        for i in range(len(conversation) - 1):
            
            # get the input
            request = lines_dict[conversation[i]]
            
            # get the response
            response = lines_dict[conversation[i+1]]
            
            # append the question to the list of questions
            requests.append(request)
            
            # append the answer to the list of answers
            responses.append(response)
            
    return requests, responses

def getWord2Count(requests, responses):
    #create empty dictionary
    word2count = {}
    
    # iterate over the requests
    for request in requests:
        
        # iterate over the words in the request
        for word in request.split():
            
            # if the word is not in the dictionary
            if word not in word2count:
                
                # add the word to the dictionary with the count 1
                word2count[word] = 1
                
            # if the word is already in the dictionary
            else:
                
                # increase the count by 1
                word2count[word] += 1
                
    # iterate over the responses
    for response in responses:
        
        # iterate over the words in the response
        for word in response.split():
            
            # if the word is not in the dictionary
            if word not in word2count:
                
                # add the word to the dictionary with the count 1
                word2count[word] = 1
                
            # if the word is already in the dictionary
            else:
                
                # increase the count by 1
                word2count[word] += 1
                
    return word2count

def encapsuleWithTokens(input, startseq, endseq):
    input_encapsuled = []

    # iterate over the requests
    for i in range(len(input)):
        
        # add the start token to the beginning and the end token to the end of the request
        input_encapsuled.append(startseq + " " + input[i] + " " + endseq)
    
    return input_encapsuled

def saveDictionary(dictionary, filename):
    # save the dictionary with numpy
    numpy.save(filename, dictionary)

def translateToNumeric(list, dictionary, nulltoken):
    # create empty list
    numeric_list = []
    
    # iterate over the list
    for item in list:
        
        # create empty string for the numeric item
        numeric_item = []
        
        # iterate over the words in the item
        for word in item.split():
            
            # if the word is in the dictionary
            if word in dictionary:
                
                # append the word to the list
                numeric_item.append(dictionary[word])
                
            # if the word is not in the dictionary
            else:
                
                # append the unknown token to the list
                numeric_item.append(dictionary[nulltoken])
                
        # convert the list back to a string and add to the list
        numeric_list.append(numeric_item)
        
    return numeric_list
    
def removeLongSequences(inputRequest, inputResponse, max_words):
    # create empty list for the input encoder
    inputRequestRemoved = []
    # create empty list for the input decoder
    inputResponseRemoved = []
    
    # iterate over the input
    for i in range(len(inputRequest)):
        
        # if the length of the input encoder and input decoder is less than the max words + 2 (for the start and end tokens)
        if len(inputRequest[i]) <= max_words + 2 and len(inputResponse[i]) <= max_words + 2:
            
            # append the input encoder to the list
            inputRequestRemoved.append(inputRequest[i])
            
            # append the input decoder to the list
            inputResponseRemoved.append(inputResponse[i])
            
    return inputRequestRemoved, inputResponseRemoved

def removeStartToken(input):
    # create empty list
    inputRemoved = []
    
    # iterate over the input
    for item in input:
        
        # remove the start token from the beginning of the item
        item = item[1:]
        
        # append the item to the list
        inputRemoved.append(item)
        
    return inputRemoved