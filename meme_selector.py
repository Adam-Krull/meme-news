#Imports
import re
import datetime
import os
import json

from PIL import Image

#Establish today's date
today = datetime.date.today().strftime('%Y-%m-%d')

#Create a list of all files in the folder with today's date
today_memes = os.listdir(today)

#Establish path to headlines
headlines = os.path.join(today, 'headlines.json')

#Load in headlines
with open(headlines, 'r') as f:
    headline_text = json.load(f)

#Extract meme filenames
def extract_memes(file_list):

    """Loads the list of files created today and isolates the meme image filenames.
    
    Returns a list of the filenames."""

    meme_list = [] 

    for file in file_list:

        if 'meme' in file:

            meme_list.append(file)

        else:

            continue

    return meme_list

#Display the meme image in a new window
def display_image(filepath):

    """Displays the image located at the specified filepath."""

    img = Image.open(filepath)

    img.show()

#Asks the user to answer a yes/no question
def approved():

    """Asks the user if they approve of the meme.
    
    Returns True if they do, else False."""

    while True:

        print()

        response = input('Do you approve of this meme? Y/N ')

        if response.strip().lower() == 'y':

            return True
        
        elif response.strip().lower() == 'n':

            return False
        
        else:

            print('Something went wrong.. try again.')



#Extract index position for headline
def extract_index(meme_file):

    """Takes in the name of a meme file.
    
    Uses regex to extract the number of the meme.
    
    Returns the number as an integer."""

    regexp = r"-\d+-"

    return int(re.findall(regexp, meme_file)[0].strip('-')) - 1

#Saves the final JSON object to today's folder
def save_approved(day, approved):

    filename = 'approved.json'

    filepath = os.path.join(day, filename)

    with open(filepath, 'w') as f:
        json.dump(approved, f)

    print(f'JSON object of approved memes saved here: {filepath}.')    

#Pipeline function
def judge_memes(file_list=today_memes, day=today, headlines=headline_text):

    """Ingests a list of filenames and a JSON object containing breaking headlines.
    
    Identifies the meme images and asks the user for approval.
    
    Outputs a JSON object with approved meme filepaths and headlines."""

    meme_list = extract_memes(file_list)

    approved_list = []

    for meme in meme_list:

        meme_path = os.path.join(day, meme)

        display_image(meme_path)

        if approved():

            headline_index = extract_index(meme)

            headline = headlines[headline_index]

            entry = {'headline': headline, 'image': meme_path}

            approved_list.append(entry)

        else:

            print('Meme rejected. Continuing.')

            continue

    save_approved(day, approved_list)

#Script
if __name__ == '__main__':
    judge_memes()