import os
import json
import tweepy
import streamlit as st
import pandas as pd
from textblob import TextBlob
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import sqlite3
import networkx as nx

conn = sqlite3.connect(os.getcwd() + '/twitter-example/db/cached.db')

path = os.path.join(os.path.expanduser('~'), '.twitter', 'twitter.json')
with open(path) as f:
    api = json.loads(f.read())

auth = tweepy.AppAuthHandler(api['Key'], api['Secret'])
api = tweepy.API(auth)

st.sidebar.title('Twitter Sentiment')
btn = st.sidebar.button('Search')
btn2 = st.sidebar.button('Rate Limit')
usr = st.sidebar.text_input("User:")
btn3 = st.sidebar.button('Cache user friends')
btn4 = st.sidebar.button('Friend List')
if btn:
    tweets = api.search(q=':)', result_type='recent', lang='pt', count=100,
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
    st.write(rate_limit)
if btn3:
    cursor = conn.cursor()
    cursor.execute(
        "select count(name) from sqlite_master where type='table' and name='network_edges'"
    )
    if cursor.fetchone()[0]:
        df_old = pd.read_sql_query("select * from network_edges", conn)
        new_usr = usr not in df_old['from'].values
    else:
        df_old = pd.DataFrame()
        new_usr = True
    if new_usr:
        friends = []
        for friend in tweepy.Cursor(api.friends, usr, count=200).items():
            friends.append((usr, friend.screen_name))
        df = pd.DataFrame()
        df['from'] = [a for a, b in friends]
        df['to'] = [b for a, b in friends]
        df = pd.concat([df_old, df])
        df.to_sql('network_edges', conn, if_exists='replace', index=False)
        st.write("Cached successfully!")
    else:
        st.write("User already in cache")
if btn4:
    df = pd.read_sql_query("select * from network_edges", conn)
    G = nx.from_pandas_edgelist(df, "from", "to")

    l = {node: node for node in G.nodes() if node in df['from'].values}
    fig, ax = plt.subplots()
    pos = nx.spring_layout(G, k=0.1)
    nx.draw(G, pos, with_labels=False, node_color='lightblue', node_size=10, width=0.2)
    nx.draw_networkx_labels(G, pos, l, font_size=10, \
        font_family='Gentium Book Basic', font_color="red")
    st.pyplot(fig)
    st.write(df.head())

conn.close()