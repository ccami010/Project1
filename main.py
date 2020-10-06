#Website design
import streamlit as st
import pandas as pd
import numpy as np
from pandas import DataFrame

#Creating json file
import requests
import ReadWriteJson

#Formatting API
import nltk
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.probability import FreqDist
from nltk.corpus import stopwords

#Making the wordcloud
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from pprint import pprint

#All of the actual Python code will be in functions found near the beginning of the page
#The Streamlit code will be found after all the functions

#Generates URL
def url_generator(input,days):
    nytKey = ReadWriteJson.read_from_file("NytKey.json")
    nytKey = nytKey["nyt_key"]
    if days == "":
        return "https://api.nytimes.com/svc/topstories/v2/" + input + ".json?api-key=" + nytKey
    else:
        return "https://api.nytimes.com/svc/mostpopular/v2/" + input + "/" + days + ".json?api-key=" + nytKey

#Collects articles from URL and returns key words
def key_words(input,days):
    url = url_generator(input,days)
    url_response = requests.get(url).json()
    if days == "":
        ReadWriteJson.save_to_file(url_response, "userDataTop.json")
        articles = ReadWriteJson.read_from_file("userDataTop.json")
    else:
        ReadWriteJson.save_to_file(url_response, "userDataPopular.json")
        articles = ReadWriteJson.read_from_file("userDataPopular.json")

    results_text = articles["results"]
    abstract_text = ""
    for i in results_text:
        abstract_text = abstract_text + i["abstract"]

    not_important_words = stopwords.words("english")
    important_words = []

    for w in word_tokenize(abstract_text):
        # Makes sure each word is a proper word, and not punctuation
        if w.isalpha():
            # Makes sure each word is one that is relevant to the topic being discussed
            if w.lower() not in not_important_words:
                important_words.append(w.lower())
    return important_words

#Generates frequency distribution
def chart_data(words):
    freq_dist = FreqDist(words)
    x_list = []
    y_list = []

    for i,j in freq_dist.most_common(10):
        x_list.append(i)
        y_list.append(j)

    chart_data = pd.DataFrame(
        np.array(y_list),x_list,
        columns=["Terms"]
    )

    return chart_data

#Creates wordcloud
def wordcloud_generator(list_of_words):
    string_of_words = ""
    for w in list_of_words:
        string_of_words = string_of_words + " " + w

    cloud_image = WordCloud().generate(string_of_words)
    return cloud_image

#Mainly streamlit code below
st.title("New York Times API Project\n")
st.subheader("Part A: Top Stories")

nameInput = st.text_input("What is your name")

"Select one of the options to see the most popular content related to it:"
topic_input = st.selectbox(
    'Select option',
    ("", "Arts", "Automobiles", "Books", "Business", "Fashion", "Food",
     "Health", "Home", "Insider", "Magazine", "Movies", "NY Region", "Obituaries",
     "Opinion", "Politics", "Real Estate", "Science", "Sports", "Sunday Review",
     "Technology", "Theater", "T-magazine", "Travel", "Upshot", "US", "World")
)

if nameInput=="" or topic_input=="":
    "Please select both options."
else:
    "Hello "+nameInput + ". You selected the " + topic_input + " topic."

topic_input = topic_input.lower().replace(" ", "")

if topic_input == "":
    ""
else:
    top_words = key_words(topic_input,"")

    #Frequency distribution for common terms
    freq_check = st.checkbox("Click here to see the 10 most common terms found in New York Times articles.")
    if freq_check:
        st.line_chart(chart_data(top_words))

    #Wordcloud for common terms
    cloud_check = st.checkbox("Click here to see a word cloud of common terms.")
    if cloud_check:
        st.pyplot(
            plt.figure(figsize=(12,12)),
            plt.imshow(wordcloud_generator(top_words))
        )

st.subheader("Part B: Most Popular Articles")
"Select if you want to see the most shared, emailed, or viewed articles."

media = st.selectbox("Select option",
             ("","Shared","Emailed","Viewed")
)

days = st.selectbox("How recent is the article in days?",
                ("","1","7","30")
)

media = media.lower()

if media == "" or days == "":
    "Please select both options."
else:
    popular_words = key_words(media,days)

    st.pyplot(
        plt.figure(figsize=(12,12)),
        plt.imshow(wordcloud_generator(popular_words))
    )

