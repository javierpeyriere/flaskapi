# Let's write your code here!

from flask import Flask, request, abort
from flask_basicauth import BasicAuth
import json
import pymysql
import os
import math

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

    page = int(request.args.get('page',0))
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
                        WHERE M.movieId=%s
                        ORDER BY movieId
                        LIMIT %s
                        OFFSET %s
                       """, (movie_id, PAGE_SIZE, page * PAGE_SIZE))
        movie = cursor.fetchone()
        if not movie:
            abort (404)
        movie = remove_null_fields(movie)  # removing the null values using the function defined above

    with db_conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total FROM Movies")
        total = cursor.fetchone()
        last_page = math.ceil(total['total'] / page_size)

    db_conn.close() 

    return {'movies': movies, 
            'next_page': f'/movies?page={page+1}&page_size={page_size}',
              'last_page': f'/movies?page={last_page}&page_size={page_size}',
            }