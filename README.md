I put this Chat-GPT bot together in an hour thanks to Chat-GPT.

## Requirements:
- A shared spotify playlist to base insults

## Set up:
- Follow Step 1 in the following instructions to set up a slack bot in your slack workspace:
https://medium.com/applied-data-science/how-to-build-you-own-slack-bot-714283fd16e5#:~:text=Step%201%3A%20Setting%20up%20the%20bot

- Get Spotify and OpenAI API tokens and add them to the `.env` file
- Fill out the other settings in `.env`
- Install python packages:

```sh
pip install -r requirements.txt
```

## Run:
```sh
export $(cat .env | xargs)
python main.py
```

Enjoy a daily dose of sarcastic GLaDOS comments.

Example output:
> Ah, engineers and their taste in music. Let's see what we have here. I must admit, this playlist is quite... interesting. It's like a symphony of mediocrity. But fear not, dear engineers, for I have the perfect song recommendation for you.
> 
> Instead of subjecting yourselves to this rather mundane playlist, I suggest you indulge in a song that matches your exceptional level of creativity and innovation. May I recommend "Bohemian Rhapsody" by Queen? Its intricate composition and unpredictable nature will surely resonate with your brilliant engineering minds. Enjoy
