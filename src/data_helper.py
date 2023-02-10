import random
import re
import numpy


def readDataToLines(filename_lines, filename_conversations): 
    """
    1.read files into memory
    2.splits files at \n (linebreak character) 
    3.transforms into array of lines
    """
    movie_lines = open(filename_lines, encoding="utf-8", errors="ignore").read()
    movie_conversations = open(filename_conversations, encoding="utf-8", errors="ignore").read()

    movie_lines = movie_lines.split("\n")
    movie_conversations = movie_conversations.split("\n")
    
    return movie_lines, movie_conversations


def readConversationsToList(movie_conversations): 
    """
    iterate over the list of conversations
        get the list of the utterances that make the conversation (last element of the split)
        remove the square brackets
        remove the single quotes
        remove the commas
        split the string into a list of utterances
        append the list of utterances to the list of conversations
    """
    conversation_lists = []
    for conversation in movie_conversations:
        temp = conversation.split(" +++$+++ ")[-1]
        temp = temp[1:-1]
        temp = temp.replace("'","")
        temp = temp.replace(",","")
        temp = temp.split()
        conversation_lists.append(temp);

    return conversation_lists



def readLinesToDict(movie_lines):
    """
    iterates over the lines:
        splits lines into its components
        if line has correct number of components:
            extract id and text
            add line to a dict

    """
    lines_dict = {}
    for line in movie_lines:
        temp = line.split(" +++$+++ ")
        if len(temp) == 5:
            line_id = temp[0]
            line_text = temp[4]
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


def splitConversationsToRequestAndResponse(conversations_lists, lines_dict):
    """
    iterates over list of conversations
        iterate through utterances of that conversation
            split into request and resonses (question and answer)
    """
    requests = []
    responses = []
    
    for conversation in conversations_lists:
        for i in range(len(conversation) - 1):
            requests.append(lines_dict[conversation[i]])
            responses.append(lines_dict[conversation[i+1]])
    return requests, responses


def getWord2Count(requests, responses):
    """
    iterates over requests/responses
        iterates over every word in current request/respnse
            if word already in dict -> increment count
            else add word to dict 
    """
    word2count = {}
    
    for request in requests:
        for word in request.split():
            if word in word2count:
                word2count[word] += 1
            else:
                word2count[word] = 1
                
    for response in responses:
        for word in response.split():
            if word in word2count:
                word2count[word] += 1
            else:
                word2count[word] = 1
                        
    return word2count



def encapsuleWithTokens(responses, startseq, endseq):
    """
    iterate over the requests/responses 
        add start-/endsequenz to current request/response
    """
    responses = [f"{startseq} {response} {endseq}" for response in responses]
    return responses


def removeStartToken(input):
    """
    removes first token (start token) from every sentence of input
    """
    input = [item[1:] for item in input ]
    return input


def get_maximum_sentence_length(inputEncoder, inputDecoder, test_inputEncoder, test_inputDecoder):
    """
    return maximum length of existing sentence
    """
    # get the maximum length of the requests
    max_length_request = max([len(x) for x in inputEncoder])
    # get the maximum length of the responses
    max_length_response = max([len(x) for x in inputDecoder])
    # get the maximum length of the test requests
    max_length_test_request = max([len(x) for x in test_inputEncoder])
    # get the maximum length of the test responses
    max_length_test_response = max([len(x) for x in test_inputDecoder])
    # get the maximum length of the requests, responses and test requests and responses
    max_length = max(max_length_request, max_length_response, max_length_test_request, max_length_test_response)
    return max_length
