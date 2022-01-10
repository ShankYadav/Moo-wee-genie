import streamlit as st
import pickle
import pandas as pd
import requests
import random

movie_dict = pickle.load(open('/Users/LENOVO/Desktop/Recommender/movies.pkl','rb'))
movies = pd.DataFrame(movie_dict)

movie_db = pd.read_csv('/Users/LENOVO/Desktop/Recommender/tmdb_5000_movies.csv')
movie_db = movie_db[['id','title','tagline','overview','runtime','revenue','release_date','vote_average']]


similarity = pickle.load(open('/Users/LENOVO/Desktop/Recommender/similarity.pkl','rb'))

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distance = similarity[movie_index]
    movie_list = sorted(list(enumerate(distance)),reverse = True,key = lambda x:x[1])[1:6]
    return movie_list

def distances(movie_list):
    dist = []
    ret_list = []
    for movie in movie_list:
        dist.append(movie[1])
    ret_list.append(min(dist))
    ret_list.append(max(dist))
    return ret_list

def similarity_index(dist,dist_list):
    new_dist = (((dist - dist_list[0])/(dist_list[1] - dist_list[0])) * 4) + 95
    return new_dist

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

st.title('The Moo-wee Genie :ox:')

menu = ['Movie Details','Movie Recommender','Random Movie Recommender']
choice = st.sidebar.selectbox("Menu",menu)

if choice == 'Movie Details':
    option = st.selectbox('Select the movie name for details : ',(movies['title'].values))
    if st.button('Search'):
        summary = movie_db.loc[movie_db['title'] == option, 'overview'].iloc[0]
        length = int(movie_db.loc[movie_db['title'] == option, 'runtime'].iloc[0])
        revenue = movie_db.loc[movie_db['title'] == option, 'revenue'].iloc[0]
        date = str(movie_db.loc[movie_db['title'] == option, 'release_date'].iloc[0])[0:4]
        col1,col2 = st.columns([7,3])
        with col1:
            st.subheader(option)
            if (str(movie_db.loc[movie_db['title'] == option, 'tagline'].iloc[0]) != 'nan'):
                st.write(movie_db.loc[movie_db['title'] == option, 'tagline'].iloc[0])
            st.write('Overview : ')
            st.write(summary)
            st.write('Released in :',date)
            st.write('Duration :',str(length),'min')
            if revenue != 0:
                st.write('Collection : $',str(round(revenue,-6)))
        with col2:
            mid = movie_db.loc[movie_db['title'] == option, 'id'].iloc[0]
            st.write('TMDB Rating : ', movie_db.loc[movie_db['title'] == option, 'vote_average'].iloc[0])
            st.image(fetch_poster(mid))

if choice == 'Movie Recommender':
    option = st.selectbox('Select the movie name for recommendations : ',(movies['title'].values))
    movie_list = recommend(option)
    dist = distances(movie_list)
    if st.button('Recommend'):
        st.write("The recommendations for",option," are : ")
        count = 1
        col1, col2, col3, col4, col5 = st.columns(5)
        col_list = [col1, col2, col3, col4, col5]
        for movie in movie_list:
            with col_list[count-1]:
                movie = list(movie)
                movie[1] = similarity_index(movie[1],dist)
                date = str(movies.iloc[movie[0]].release_date)
                date = '('+ date[0:4] +')'
                string1 = str(count)+'\. '+str(round(movie[1]))+'%'+' similar!' 
                st.subheader(string1)
                st.image(fetch_poster(movies.iloc[movie[0]].movie_id))
                st.write(movies.iloc[movie[0]].title,date)
            count += 1

if choice == 'Random Movie Recommender':
    st.write('Click generate for a random movie suggestion!')
    mov_id = random.choice(movie_db['id'])
    if st.button('Generate'):
        summary = movie_db.loc[movie_db['id'] == mov_id, 'overview'].iloc[0]
        length = int(movie_db.loc[movie_db['id'] == mov_id, 'runtime'].iloc[0])
        revenue = movie_db.loc[movie_db['id'] == mov_id, 'revenue'].iloc[0]
        date = str(movie_db.loc[movie_db['id'] == mov_id, 'release_date'].iloc[0])[0:4]
        col1,col2 = st.columns([8,4])
        with col1:
            st.subheader(movie_db.loc[movie_db['id'] == mov_id, 'title'].iloc[0])
            if (str(movie_db.loc[movie_db['id'] == mov_id, 'tagline'].iloc[0]) != 'nan'):
                st.write(movie_db.loc[movie_db['id'] == mov_id, 'tagline'].iloc[0])
            st.write('Overview : ')
            st.write(summary)
            st.write('Released in :',date)
            st.write('Duration :',str(length),'min')
            if revenue != 0:    
                st.write('Collection : $',str(round(revenue,-6)))
        with col2:
            st.write('TMDB Rating : ', movie_db.loc[movie_db['id'] == mov_id, 'vote_average'].iloc[0])
            st.image(fetch_poster(mov_id))