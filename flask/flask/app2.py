# Let's write your code here!

from flask import Flask, request, abort
from flask_basicauth import BasicAuth
import json
import pymysql
import os
import math
from collections import defaultdict
from flask_swagger_ui import get_swaggerui_blueprint
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)
app.config.from_file("flask_config.json", load=json.load)
app.config['BASIC_AUTH_FORCE']=True       # Reinforces the security to ask the login and password each time
auth = BasicAuth(app)


@app.route("/movies/<int:movie_id>")
@auth.required
def movie(movie_id):
    """the overall function"""

    def remove_null_fields(obj):
        """The function to remove the null fields in the 'columns of sql"""
        return {k:v for k, v in obj.items() if v is not None}

    db_conn = pymysql.connect(host="localhost", user="root", password = "Alsimar10", database="bechdel",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:   # for movies, changing the names and keeping only the columns we want
        cursor.execute("""SELECT
                            M.movieId,
                            M.originalTitle,
                            M.primaryTitle AS englishTitle,
                            B.rating AS bechdelScore,
                            M.runtimeMinutes,
                            M.startYear AS Year,
                            M.movieType,
                            M.isAdult,
                            case 
                                when B.rating > 2 then 'True'
                                else 'False'
                            end as bechdelTest
                        FROM Movies M
                        JOIN Bechdel B ON B.movieId = M.movieId 
                        WHERE M.movieId=%s""", (movie_id, ))
        movie = cursor.fetchone()
        if not movie:
            abort (404)
        movie = remove_null_fields(movie)  # removing the null values using the function defined above

    with db_conn.cursor() as cursor: # for genre
        cursor.execute("""SELECT * FROM MoviesGenres WHERE movieId=%s""", (movie_id, ))
        genres = cursor.fetchall()
        movie['genres'] = [g['genre'] for g in genres]

    with db_conn.cursor() as cursor:  # for people
        cursor.execute("""SELECT
                            P.personId,
                            P.primaryName AS name,
                            P.birthYear,
                            P.deathYear,
                            MP.job,
                            MP.category AS role
                        FROM MoviesPeople MP
                        JOIN People P on P.personId = MP.personId
                        WHERE MP.movieId=%s""", (movie_id, ))
        people = cursor.fetchall()
        movie['people'] = [remove_null_fields(p) for p in people]
    

    db_conn.close() 

    #movie['bechdelTest']=movie['bechdelScore'].apply(lambda x : True if int(x)>0 else False) # my attempt of doing the boolean test via python

    return movie

PAGE_SIZE = 30  # initialising my variables
MAX_PAGE_SIZE = 30

@app.route("/movies")
@auth.required
def movies():
    """the overall function for the movies per page"""

    def remove_null_fields(obj):
        """The function to remove the null fields in the 'columns of sql"""
        return {k:v for k, v in obj.items() if v is not None}

    page = int(request.args.get('page',1))
    page_size = int(request.args.get('page_size', MAX_PAGE_SIZE))
    page_size = min(page_size, MAX_PAGE_SIZE)

    db_conn = pymysql.connect(host="localhost", user="root", password = "Alsimar10", database="bechdel",
                              cursorclass=pymysql.cursors.DictCursor)

    with db_conn.cursor() as cursor:   # for movies, changing the names and keeping only the columns we want
        cursor.execute("""SELECT
                            M.movieId,
                            M.originalTitle,
                            M.primaryTitle AS englishTitle,
                            B.rating AS bechdelScore,
                            M.runtimeMinutes,
                            M.startYear AS Year,
                            M.movieType,
                            M.isAdult,
                            case 
                                when B.rating > 2 then 'True'
                                else 'False'
                            end as bechdelTest
                        FROM Movies M
                        JOIN Bechdel B ON B.movieId = M.movieId 
                        ORDER BY movieId
                        LIMIT %s # how many per page, kind off
                        OFFSET %s # which page where we start in multiples of limit eg. if limit is 10, then offset 50 means 5th page
                       """, (PAGE_SIZE, (page-1) * PAGE_SIZE))
        movies = cursor.fetchall()
        if not movies:
            abort (404)
        movies = [remove_null_fields(movie) for movie in movies]  # removing the null values using the function defined above
        
    list_movieId = []
    for m in movies:
        test = m['movieId']
        list_movieId.append(test)
    print(list_movieId)


    with db_conn.cursor() as cursor: 
                # Generate placeholders for movie_ids based on the length of the list
        placeholder = ','.join(['%s'] * len(list_movieId))      

    # Execute the SQL query with client_ids as parameters
        cursor.execute(f"select genre, movieId from bechdel.moviesgenres where movieId IN ({placeholder})", tuple(list_movieId))  
        genres = cursor.fetchall()

    genres_dict = defaultdict(list)  # creating the 'empty' dictionary

    for gen in genres:
        genres_dict[gen['movieId']].append(gen['genre'])
    
    with db_conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM Movies")
        total = cursor.fetchone()
        last_page = math.ceil(total['total'] / page_size)

    db_conn.close() 

    for movie in movies:  # filling in movies with the genres
        movieId = movie['movieId']
        movie['genres'] = genres_dict[movieId]

    return {'movies': movies, 
            'next_page': f'/movies?page={page+1}&page_size={page_size}',
              'last_page': f'/movies?page={last_page}&page_size={page_size}',
              'total_results' : f'{total}'
            }


# To make the documentation using swaggerui

swaggerui_blueprint = get_swaggerui_blueprint(
    base_url='/docs',
    api_url='/static/openapi.yaml',
)
app.register_blueprint(swaggerui_blueprint)


# to create a json
response = requests.get("http://localhost:8080/movies?page=50&page_size=3",
                        auth=HTTPBasicAuth(username="ironhack", password="ilovedata"))
response_json = response.json()
response_json['movies']