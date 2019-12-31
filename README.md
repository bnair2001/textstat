# TextStat
## Inspiration
Comments on Youtube videos hold a lot of insight and feedback valuable to the creator but spam spoils the insights. Text response and feedback holds a lot of value but it is hard to comprehend due to its size, but if we can condense it down to numbers and summarize it, it can be made useful
## What it does
It either takes a youtube video URL and gives stats on the comments or takes a twitter profile and gives stats based on the tweets. It also helps to find out all the questions asked in the comment section
## How we built it
We built the backed with flask and TensorFlow serve. We used a sentiment analysis model whose data pipeline also uses a spam filter. The model was built using tf 2.0 and was trained on the IMDB dataset.
## Challenges we ran into
Setting TensorFlow serve for the first time. Learning about tf 2.0.
## Accomplishments that we're proud of
The TensorFlow model and the intuitive UI.
## What we learned
tf2.0
## What's next for Textstat
* Comparison of stats with that of previous videos, tweets, and posts.
* Stats on facebook posts.
* Measuring amount of spam in the comments, tweets, and posts.
* Measuring toxicity in the comments, tweets, and posts.
