"""
 chatapp.py
 ... a Python scropt in which the users can easily interact with
    the bot.
"""
import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np

from keras.models import load_model
model = load_model('Ren2021.h5')
import json
import random
import requests
import textblob
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import webbrowser

intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))

allChat = []
def clean_up_sentence(sentence):
    """tokenize each word in sentence (lower-case)
       return an array of words
    """
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # lower-case
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def bagOfWords(sentence_words, words, show_details=True):
    """if a word in words exist in sentence, --> 1
       otherwise --> 0
       inputs:
            sentence... input sentence
            words... a list of unique lemmatized words from dataset
       return: bag of words array (0 or 1)
    """
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0]*len(words)
    for s in sentence_words:
        for index,word in enumerate(words):
            if word == s:
                # assign 1 if current word is in the vocabulary position
                bag[index] = 1
                if show_details:
                    print ("found in bag: %s" % word)
    return(np.array(bag))

def predict_class(sentence, model):
    """
    """
    # tokenize pattern
    sentence_words = clean_up_sentence(sentence)

    ERROR_THRESHOLD = 0.25
    # filter out predictions below a threshold
    bow = bagOfWords(sentence_words, words, show_details=False)
    all_results = model.predict(np.array([bow]))[0]
    results = [[i,pred] for i,pred in enumerate(all_results) if pred > ERROR_THRESHOLD]

    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    #print(return_list)
    return return_list

def getResponse(predicted, intents_json):
    try:
        tag = predicted[0]['intent']
        list_of_intents = intents_json['intents']
        for i in list_of_intents:
            if(i['tag']== tag):
                result = random.choice(i['responses'])
                break
    except:
        result = "I don't understand.."
    
    return result

def search_wikipedia(message):
    """ search in wikipedia
            If user input input is in the format "search ___(noun phrase)_____ .. wikipedia",
                then the noun phrase created from everything between "search" and "wikipedia"
                is searched.
            If user input is in other format, the noun right before "wikipedia" is searched.
        
        returns... the first three sentences from the indicated wikipedia page.
    """
    nouns = [word for (word, pos) in nltk.pos_tag(message) if pos[0] == 'N']
    #print(nouns) 
    wiki_index = nouns.index("wikipedia")
    if "search" in nouns:
        search_index = nouns.index("search")
        lookup = nouns[search_index+1:wiki_index]
        lookup = "_".join(lookup)
        #print(lookup)
    else:
        lookup = nouns[wiki_index-1]

    wikipedia_url = "http://en.wikipedia.org/wiki/" + lookup
    # print(wikipedia_url)
    response = requests.get(wikipedia_url)

    if response.status_code == 404:                 # page not found
        return "There was a problem with searching in wikipedia"
        
    data_from_url = response.text                   # the HTML text from the page
    soup = BeautifulSoup(data_from_url,"lxml")

    AllDivs = soup.find(id = "content").find_all("p")
    description = ""
    for i in range(min(5, len(AllDivs))):
        description += AllDivs[i].text
        tokenized = nltk.word_tokenize(description.lower())

    descBlob = textblob.TextBlob(description)
    if len(descBlob.sentences) > 3:
        first3 = 0
        for i in range(3):
            first3 += len(descBlob.sentences[i])
        result = description[:first3+1]
    else:
        result = description
    return result

def zoom_link(message):
    """ gets the zoom link if it already has it, stores the link if
        it doesn't.
    """
    result = ""
    not_found = ""
    # if user is looking for a zoom link
    if "zoom.us" not in message:
        try:
            with open('zoom.json') as dbfile:
                zoomLinks = json.loads(dbfile.read())
            for link in zoomLinks['zoom links']:
                if message == link['tag']:
                    result = link['url']
                    break
                else:
                    not_found += link['tag'] + "\n"
        except:
            pass  # zoom.json is empty
        if result == "":  # message not found in key
            result = message + " not found. Below is the list of keys I have.\n"
            result += "If you want to insert additional link, input in the following format: \n"
            result += "__(key name)__: __(URL)__"
            result += "existing keys: " + not_found
    # user wants to input a new URL
    elif "zoom.us" in message:
        semicolon_index = message.index(":")
        key = message[:semicolon_index]
        url = message[semicolon_index+2:]  # excluding ": "
        newLink = {"tag": key, "url": url}
        
        with open('zoom.json') as dbfile:
            zoomLinks = json.loads(dbfile.read())
        existed = False
        for link in zoomLinks['zoom links']:
            if key == link['tag']:  # if tag did exist
                link['url'] = url
                existed = True
                break
        if existed == False:  # if tag did not exist
            zoomLinks["zoom links"].append(newLink)
        with open('zoom.json', 'w') as dbfile:
            json.dump(zoomLinks, dbfile, indent=4)
        result = "New link successfully saved."
    return result

def open_tab(message):
    """ open tabs for the indicated tag. If the tag does not exist,
       the url is stored. If tag already exist but url is added,
       then the tag will store multiple urls.
    """
    result = ""
    not_found = ""

    # to open in Chrome
    chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

    # if user wants to open tab(s)
    if "open" in message:
        try:
            message = clean_up_sentence(message)
            message = message[1] # don't need 'open'
            with open('tab.json') as dbfile:
                tabLinks =  json.loads(dbfile.read())
            for link in tabLinks['tab links']:
                if message == link['tag']:
                    result = link['url']
                    break
                else:
                    not_found += link['tag'] + "\n"
        except:
            pass
        if result == "":  # message not found in key
            result = message + " not found."
            result += "If you want to insert additional link, input in the following format: \n"
            result += "__(key name)__: __(URL)__\n"
            result += "existing keys: \n" + not_found
            return result

        # open tab(s)
        for url in result:
            webbrowser.get(chrome_path).open(url)
        return "tab(s) opened"

    # if user wants to store a new link
    else:
        space_index = message.index(" ")
        key = message[:space_index-1]
        url = message[space_index+1:]  # excluding ": "
        newLink = {"tag": key, "url": [url]}

        with open('tab.json') as dbfile:
            tabLinks = json.loads(dbfile.read())
        existed = False
        for link in tabLinks['tab links']:
            if key == link['tag']:  # if the tag did exist
                link['url'].append(url) # adds the link
                existed = True
                break
        if existed == False: # if the tag did not exist
            tabLinks["tab links"].append(newLink) # adds the tag&link
        with open('tab.json', 'w') as dbfile:
            json.dump(tabLinks, dbfile, indent=4)
        result = "New link successfully saved."
        return result

def timezone(message):
    """ timezone conversion
    """
    current_time = datetime.now()
    fmt = "%Y-%m-%d %H:%M"
    response = "It's "
    if "claremont" in message:  # returns current time in Claremont
        pacific_tzinfo = pytz.timezone("US/Pacific")
        pacific_time = current_time.astimezone(pacific_tzinfo)
        response += pacific_time.strftime(fmt)
        return response
    else:
        response += current_time.strftime(fmt)
        return response

def chatbot_response(message):
    """
    """
    lowered = message.lower()
    message_index = allChat.index(lowered)
    tokenized_message = clean_up_sentence(message)

    predicted = predict_class(message, model)
    response = getResponse(predicted, intents)

    # wikipedia
    if "wikipedia" in tokenized_message:
        # print("wikipedia")
        response = search_wikipedia(tokenized_message)

    # zoom
    if "zoom link" in message.lower():
        # print("zoom")
        response = "Please indicate which zoom link you want"

    if len(allChat) > 1 and "zoom link" in allChat[message_index-1]:  # if "zoom" was in the previous user input
        response = zoom_link(message)

    if "zoom.us" in message:
        response = zoom_link(message)
    
    # open tab(s)
    if "open" in message.lower():
        # print("tab")
        response = open_tab(message)
    if "open" in allChat[message_index-1] and "https" in message:
        response = open_tab(message)

    # timezone
    if "what time" in message.lower():
        response = timezone(tokenized_message)

    return response

#Creating GUI with tkinter
import tkinter
from tkinter import *

def send():
    message = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0",END)

    if message != '':
        lowered = message.lower()
        allChat.append(lowered) # keeping record of every chat
        # print(allChat) # debugging

        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + message + '\n\n')
        ChatLog.config(foreground="#0C2D48", font=("Verdana", 12 ))
    
        response = chatbot_response(message)
        ChatLog.insert(END, "Ren: " + response + '\n\n')
            
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)

base = Tk()
base.title("Ren - chatbot")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

#Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Verdana",)

ChatLog.config(state=DISABLED)

#Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

#Create Button to send message
SendButton = Button(base, font=("Verdana",12,'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#2E8BC0", activebackground="#145DA0",fg='#ffffff',
                    command= send )

#Create the box to enter message
EntryBox = Text(base, bd=0, bg="white",width="29", height="5", font="Verdana")



#Place all components on the screen
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

base.mainloop()
