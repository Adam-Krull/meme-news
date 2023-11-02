import re
import requests
import openai
import datetime
import os
import time
import json

from env import API_KEY, OPENAI_API_KEY, MEME_KEY

openai.api_key = OPENAI_API_KEY

host = "ronreiter-meme-generator.p.rapidapi.com"

gen_headers = {
    'X-RapidAPI-Key': MEME_KEY,
    'X-RapidAPI-Host': host
    }

today = datetime.date.today().strftime('%Y-%m-%d')

descriptions = os.path.join(today, 'descriptions.json')


def make_folder(day=today):
    
    os.mkdir(day)
    
    print(f'Folder created for today: {day}.')
    
    
def save_headlines(headlines, date=today):
    
    filename = 'headlines.json'
    
    path = os.path.join(date, filename)
    
    with open(path, 'w') as f:
        
        json.dump(headlines, f)
        
    print(f'Headline retrieval complete! Retrieved and stored {len(headlines)} headlines.')    


def get_headlines(key=API_KEY):
    
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


def extract(text):
    
    regexp = r"^.*?:\s(.*)"
    
    return re.search(regexp, text).groups()[0]


def clean_content(content):
    
    clean_content = re.sub(r"[^a-zA-Z0-9':\s\.]", "", content)
    
    clean_content = re.sub(r"Donald Trump", "a man made of oranges", clean_content)
    
    try:
        
        image, top, bottom = clean_content.split('\n\n')
    
        clean_dict = {'image': extract(image), 'top': extract(top), 'bottom': extract(bottom)}
                  
        return clean_dict
    
    except:
        
        return None


def get_meme_desc(titles, day=today):
    
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
            
            continue
            
        if (i + 1) % 5 == 0:
        
            print(f'{i + 1} descriptions retrieved.')
            
    save_headlines(app_titles)         
        
    return descs


def get_meme_image(prompt):
    
    new_prompt = 'Use a dark background to create an image according to the following prompt: ' + prompt
    
    try:
    
        gen_image = openai.Image.create(prompt=new_prompt, n=1, size="512x512")

        image_url = gen_image['data'][0]['url']

        return requests.get(image_url).content
    
    except:
        
        print(f'The following prompt was rejected: {prompt}.')
        
        return None


def save_image(image, num, date=today):
    
    now = round(time.time())
    
    filename = f'{now}-{num}.jpg'
    
    path = os.path.join(date, filename)
    
    with open(path, 'wb') as f:
        
        f.write(image)
        
    return path    


def upload_image(path, headers=gen_headers):
    
    upload_url = "https://ronreiter-meme-generator.p.rapidapi.com/images"
    
    image = open(path, 'rb')

    files = {'image': image}
    
    response = requests.post(upload_url, files=files, headers=headers)
    
    print(f'Post request received {response.status_code} status code.')
    
    if response.status_code == 200:
    
        return response.json()['name']
    
    else:
        
        return None


def generate_meme(image, top, bottom, headers=gen_headers):
    
    gen_url = "https://ronreiter-meme-generator.p.rapidapi.com/meme"
    
    querystring = {"top": top, "bottom": bottom, "meme": image}
    
    response = requests.get(gen_url, headers=headers, params=querystring)
    
    return response.content
    
    
def save_meme(image, num, date=today):
    
    now = round(time.time())
    
    filename = f'{now}-{num}-meme.jpg'
    
    path = os.path.join(date, filename)
    
    with open(path, 'wb') as f:
        
        f.write(image)
        
    return path    

        
def meme_button(desc=descriptions):
    
    make_folder()
    
    titles = get_headlines()
    
    if os.path.exists(desc):
        
        with open(desc, 'r') as f:
            
            descriptions = json.load(f)
            
    else:        
    
        descriptions = get_meme_desc(titles)
    
    for i, desc in enumerate(descriptions):
        
        if (i + 1) % 5 == 0:
            
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
        
        
def main():
    
    meme_button()
    
    
if __name__ == '__main__':
    
    main()