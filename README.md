# chatbot
Retrieval based chatbot for assisting with (online) college life.

## Features
1.  search_wikipedia:
    * Searches the word indicated by the user in Wikipedia.
    *  If user input input is in the format "search ___(noun phrase)_____ .. wikipedia", then the noun phrase created from everything between "search" and "wikipedia" is searched.
    * If user input is in other format, the noun right before "wikipedia" is searched.
    * Returns the first 3 sentences from the indicated wikipedia page.
2. zoom_link:
    * Retrives the zoom link indicated by the user if it is already in the database.
    * If the zoom link does not exist, then it stores the link.
3. open_tab:
    * Open tabs for the indicated tag.
    * If the tag does not exist, the url is stored. 
    * If tag already exist but url is added, then the tag will store multiple urls.
4. timezone:
    * converts the time of the user's location to Pacific Standard Time.
5. response:
    * If none of the above functions are called, then the chat bot responds using its database.

## Files
* chatapp.py... functions for the chat bot is stored.
* train_chatbot.py... trains the chatbot with intents.json.
* intents.json... database of predefined responses.
* tab.json... database for tabs (used in open_tab function).
* zoom.json... database for zoom links (used in zoom_link function).

## How to use
1. Train the chatbot
    * Run train_chatbot.py
2. Run chatapp.py


