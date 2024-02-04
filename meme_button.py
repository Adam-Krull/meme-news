#Imports
import re
import requests
import openai
import datetime
import os
import time
import json

#Import keys from my environment file
from env import API_KEY, OPENAI_API_KEY, MEME_KEY

#Set the openai key
openai.api_key = OPENAI_API_KEY

#Declare the host of the meme generation api
host = "ronreiter-meme-generator.p.rapidapi.com"

#Set the headers for requests
gen_headers = {
    'X-RapidAPI-Key': MEME_KEY,
    'X-RapidAPI-Host': host
    }

#Get today's date and format as year-month-day
today = datetime.date.today().strftime('%Y-%m-%d')

#Declare the filepath for meme descriptions
#Not included in the program yet
descriptions = os.path.join(today, 'descriptions.json')


#Make a new folder for today's date
def make_folder(day=today):
    
    """Creates a folder using today's date."""
    
    os.mkdir(day)
    
    print(f'Folder created for today: {day}.')
    

#Save the list of headlines
def save_headlines(headlines, date=today):
    
    """Saves the breaking news headlines to a JSON file.
    
    The filename will be a combination of today's date and 'headlines.json'.
    
    Prints out how many headlines were successfully used to generate prompts and stored."""
    
    filename = 'headlines.json'
    
    path = os.path.join(date, filename)
    
    with open(path, 'w') as f:
        
        json.dump(headlines, f)
        
    print(f'Meme descriptions complete! Stored {len(headlines)} headlines.')    


#Retrieve a list of headlines from the news api
def get_headlines(key=API_KEY):
    
    """Retrieves the latest breaking news headlines from the news api.
    
    Uses regex to remove the source from the end of the headline.
    
    Returns a list of headlines to be fed into ChatGPT for meme creation."""
    
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={key}"
    
    response = requests.get(url)
    
    titles = []
    
    regexp = r"^(.*?)\s\-\s.{0,25}$"
    
    for article in response.json()['articles']:
        
        try:
        
            titles.append(re.search(regexp, article['title']).groups()[0])
            
        except:
            
            print('Article removed. Continuing.')
            
            continue
            
    print('All headlines retrieved! Moving on to descriptions..')        
        
    return titles


#Extract the image description, top text, and bottom text from ChatGPT's response
def extract(text):
    
    """Extracts text based on the format of the response from ChatGPT."""
    
    regexp = r"^.*?:\s(.*)"
    
    return re.search(regexp, text).groups()[0]


#Use regex to clean and extract text from ChatGPT's response
def clean_content(content):
    
    """Uses regex to clean the text and substitute Donald Trump to avoid safety filters.
    
    Returns a dictionary containing: the image description, the top text, and the bottom text."""
    
    clean_content = re.sub(r"[^a-zA-Z0-9':\s\.!]", "", content)
    
    clean_content = re.sub(r"Donald Trump", "a man made of oranges", clean_content)
    
    try:
        
        image, top, bottom = clean_content.split('\n\n')
    
        clean_dict = {'image': extract(image), 'top': extract(top), 'bottom': extract(bottom)}
                  
        return clean_dict
    
    except:
        
        return None


#Generate meme descriptions from breaking headlines
def get_meme_desc(titles, day=today):
    
    """Asks ChatGPT to describe a meme.
    
    Includes try/except logic in case the response is unexpected.
    
    Returns a list of dictionaries, each dictionary containing the image description, top text, and bottom text."""
    
    model = 'gpt-3.5-turbo'
    
    app_titles = []
    
    descs = []
    
    for i, title in enumerate(titles):
        
        user_content = f"""Come up with a funny and concise meme about the following headline: {title}.

                           Format your response like this:
                   
                           Image:
                           Text at the top:
                           Text at the bottom:
                        """
        
        try:
            
            response = openai.ChatCompletion.create(model=model,
                                                messages=[{'role': 'user', 'content': user_content}])
        
            response_content = response['choices'][0]['message']['content']
            
        except:
            
            print('No response received from OpenAI. Continuing to the next headline.')
            
            continue
        
        content = clean_content(response_content)
        
        if content:
            
            app_titles.append(title)
        
            descs.append(content)
            
        else:
              
            print(f'Unable to generate meme for the following title: {title}.')

            print('Response content looked like this:')

            print(response_content)
            
            continue
            
        if (i + 1) % 5 == 0:
        
            print(f'{i + 1} descriptions retrieved.')
            
    save_headlines(app_titles)         
        
    return descs


#Generate a meme image using DALL-E
def get_meme_image(prompt):
    
    """Feeds the image description to the DALL-E model.
    
    Returns the image if one was created, otherwise None."""
    
    new_prompt = 'Create an image with a darker background according to this prompt: ' + prompt
    
    try:
    
        gen_image = openai.Image.create(prompt=new_prompt, n=1, size="512x512")

        image_url = gen_image['data'][0]['url']

        return requests.get(image_url).content
    
    except:
        
        print(f'The following prompt was rejected: {prompt}.')
        
        return None


#Save the generated image    
def save_image(image, num, date=today):
    
    """Saves the DALL-E image to the local filesystem."""
    
    now = round(time.time())
    
    filename = f'{now}-{num}.jpg'
    
    path = os.path.join(date, filename)
    
    with open(path, 'wb') as f:
        
        f.write(image)
        
    return path    


#Upload the generated image to the meme generation api
def upload_image(path, headers=gen_headers):
    
    """Uploads the generated image to the meme generation API.
    
    Returns the name of the image if the upload was successful, otherwise None."""
    
    upload_url = "https://ronreiter-meme-generator.p.rapidapi.com/images"
    
    image = open(path, 'rb')

    files = {'image': image}
    
    response = requests.post(upload_url, files=files, headers=headers)
    
    print(f'Post request received {response.status_code} status code.')
    
    if response.status_code == 200:
    
        return response.json()['name']
    
    else:
        
        return None


#Generate a meme using the text and uploaded image    
def generate_meme(image, top, bottom, headers=gen_headers):
    
    """Generates a meme using the meme generation API.
    
    Returns the generated meme."""
    
    gen_url = "https://ronreiter-meme-generator.p.rapidapi.com/meme"
    
    querystring = {"top": top, "bottom": bottom, "meme": image}
    
    response = requests.get(gen_url, headers=headers, params=querystring)
    
    return response.content
    

#Save the meme    
def save_meme(image, num, date=today):
    
    """Saves the image to a unique filename.
    
    Returns the path to the file."""
    
    now = round(time.time())
    
    filename = f'{now}-{num}-meme.jpg'
    
    path = os.path.join(date, filename)
    
    with open(path, 'wb') as f:
        
        f.write(image)
        
    return path    


#Execute the pipeline from folder to meme creation
def meme_button(desc=descriptions):
    
    """Pipeline function that calls all other functions in this document.
    
    Begins by creating a folder unique to the current day.
    
    Ends by saving each successfully generated meme to the folder."""
    
    make_folder()
    
    titles = get_headlines()
    
    if os.path.exists(desc):
        
        with open(desc, 'r') as f:
            
            descriptions = json.load(f)
            
    else:        
    
        descriptions = get_meme_desc(titles)
    
    for i, desc in enumerate(descriptions):
        
        if i % 5 == 0:
            
            print(f'Feeling sleepy.')
            
            time.sleep(66)
        
        image = get_meme_image(desc['image'])
              
        if image:
        
            image_path = save_image(image, i + 1)

            image_name = upload_image(image_path)
            
            if image_name:

                meme = generate_meme(image_name, desc['top'], desc['bottom'])

                meme_path = save_meme(meme, i + 1)

                print(f'Meme created and saved at {meme_path}.')
                
            else:
                
                print('Something went wrong with the meme generation API. Continuing.')
                
                continue
              
        else:
              
            continue

    print('Meme generation complete!')    
        

#Not sure why I did this lol        
def main():
    
    """xddd"""
    
    meme_button()
    

#Script    
if __name__ == '__main__':
    
    main()