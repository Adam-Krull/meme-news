# Meme news

This project automates the generation of memes from recent news headlines. A future iteration of the project will automatically post the memes, along with the associated headlines, to an X account on a daily basis. The project relies on a number of APIs to accomplish these tasks.

### APIs

1. [News API](https://newsapi.org/): used to retrieve recent headlines.
2. [OpenAI API](https://openai.com/blog/openai-api): used to generate meme content and images.
3. [Meme API](https://rapidapi.com/meme-generator-api-meme-generator-api-default/api/meme-generator): used to create the memes, using the text and image supplied by OpenAI.

### Dependencies

1. Re: used regex to clean text data.
2. Requests: made get and post requests to the APIs.
3. Openai: used ChatGPT and DALL-E to generate content.
4. Datetime: retrieved today's date for folder and file naming conventions.
5. Os: created filepaths.
6. Time: retrieved the current time in unix timestamp for unique file names.
7. Json: read and wrote headlines to json files.
8. An env file in the same working directory as the script with the following variables:
    - API_KEY: for the News API.
    - OPENAI_API_KEY: for the openai API.
    - MEME_KEY: for the meme generation API.