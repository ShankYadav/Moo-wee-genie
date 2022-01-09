"""Content Based Movie Recommender System"""

import numpy as np 
import pandas as pd 
import ast
from sklearn.feature_extraction.text import CountVectorizer 
from nltk.stem.porter import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

#Creating the dataframe from the datasets.
movies = pd.read_csv('/Users/LENOVO/Desktop/Recommender/tmdb_5000_movies.csv')
credits = pd.read_csv('/Users/LENOVO/Desktop/Recommender/tmdb_5000_credits.csv')
df = movies.merge(credits,on = 'title')
df = df[['movie_id','title','genres','overview','keywords','cast','crew','release_date']]

#Preproccessing of the data
def tags(obj):
    ret_list =[]
    #literal_eval to convert string into list
    for i in ast.literal_eval(obj):
        ret_list.append(i['name'])
    return ret_list

def cast_tags(obj):
    ret_list =[]
    count = 0
    #literal_eval to convert string into list
    for i in ast.literal_eval(obj):
        if(count<3):
            ret_list.append(i['name'])
            count += 1
        else: 
            break
    return ret_list

def dir_tags(obj):
    ret_list =[]
    #literal_eval to convert string into list
    for i in ast.literal_eval(obj):
        if(i['job']=='Director'):
            ret_list.append(i['name'])
            break
    return ret_list

def merge(objects):
    for obj in objects:
        df[obj] = df[obj].apply(lambda x:[i.replace(" ","") for i in x])

df.dropna(inplace=True)
df['genres'] = df['genres'].apply(tags)
df['keywords'] = df['keywords'].apply(tags)
df['cast'] = df['cast'].apply(cast_tags)
df['crew'] = df['crew'].apply(dir_tags)
df['overview'] = df['overview'].apply(lambda x:x.split())

merge(['genres','keywords','cast','crew'])

df['tags'] = df['genres'] + df['keywords'] + df['cast'] + df['crew'] + df['overview']
df['tags'] = df['tags'].apply(lambda x:" ".join(x))
df['tags'] = df['tags'].apply(lambda x:x.lower())
df = df[['movie_id','title','tags','release_date']]

#Vectorzation of the movies by using bag of words
def stemmer(text):
    ret_list = []
    for i in text.split():
        ret_list.append(ps.stem(i))
    return " ".join(ret_list)

cv = CountVectorizer(max_features=5000,stop_words='english')
vectors = cv.fit_transform(df['tags']).toarray()

ps = PorterStemmer()
df['tags'] = df['tags'].apply(stemmer)

similarity = cosine_similarity(vectors)

#Recommender
def recommend(movie):
    movie_index = df[df['title'] == movie].index[0]
    distance = similarity[movie_index]
    movie_list = sorted(list(enumerate(distance)),reverse = True,key = lambda x:x[1])[1:6]
    return movie_list

movie = input('Enter movie name to recommend movies :')
movie_list = recommend(movie)

def distances(movie_list):
    dist = []
    ret_list = []
    for movie in movie_list:
        dist.append(movie[1])
    ret_list.append(min(dist))
    ret_list.append(max(dist))
    return ret_list

dist = distances(movie_list)

#Scaling the similarity between the movies
def similarity_index(dist,dist_list):
    new_dist = (((dist - dist_list[0])/(dist_list[1] - dist_list[0])) * 4) + 95
    return new_dist

#Printing the recommended movies
def print_mov(movie_list):
    count = 1
    for movie in movie_list:
        movie = list(movie)
        movie[1] = similarity_index(movie[1],dist)
        date = str(df.iloc[movie[0]].release_date)
        print(count,end = '.\n')
        print(df.iloc[movie[0]].title,' (',date[0:4],')',sep = '')
        print(round(movie[1]),'%',' similar! \n',sep = '')
        count += 1

print_mov(movie_list)
pickle.dump(df.to_dict(),open('/Users/LENOVO/Desktop/Recommender/movies.pkl','wb'))
pickle.dump(similarity,open('/Users/LENOVO/Desktop/Recommender/similarity.pkl','wb'))