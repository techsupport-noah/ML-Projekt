import random


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

    # shuffle the list of conversations to get better training results
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