import os
import json
import tweepy
import streamlit as st
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

path = os.path.join(os.path.expanduser('~'), '.twitter', 'twitter.json')
with open(path) as f:
    api = json.loads(f.read())

auth = tweepy.AppAuthHandler(api['Key'], api['Secret'])
api = tweepy.API(auth)

st.sidebar.title('Twitter Sentiment')
btn = st.sidebar.button('Next')
btn2 =st.sidebar.button('Rate Limit')
if btn:
    tweets = api.search(q='brasil', result_type='recent', lang='pt', count=100,
                        tweet_mode='extended')
    df = pd.DataFrame()
    df['tweet'] = [twt.retweeted_status.full_text if 'retweeted_status' in dir(twt) \
        else twt.full_text for twt in tweets]
    get_polarity = lambda x: TextBlob(x).translate(to='en').sentiment.polarity
    get_subjectivity = lambda x: TextBlob(x).translate(to='en').sentiment.subjectivity
    #df['polarity'] = df['tweet'].apply(get_polarity)
    #df['subjectivity'] = df['tweet'].apply(get_subjectivity)

    all_txt = ''.join([t for t in df['tweet']])
    stopwords = set(STOPWORDS)
    stopwords.update(["da", "meu", "em", "você", "de", "ao", "os", "o", "é", "que", \
        "na", "https", "e", "t", ".", "co", "quem", "pra", "isso", "dos", "não", "sim", \
        "um", "uma", "do", "dos", "vai", "foi", "já"])
    wordcloud = WordCloud(stopwords=stopwords, width = 500, height = 500).generate(all_txt)
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.set_axis_off()
    st.pyplot(fig)

    st.table(df)
if btn2:
    rate_limit = api.rate_limit_status()["resources"]
    st.write(rate_limit['search'])
