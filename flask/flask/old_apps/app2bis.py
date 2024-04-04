# Let's write your code here!

from flask import Flask, request
import pymysql
import os

app = Flask(__name__)

@app.route("/movies/<int:movie_id>")
def movie(movie_id):
    db_conn = pymysql.connect(host="localhost", user="root", password = "Alsimar10", database="bechdel",
                              cursorclass=pymysql.cursors.DictCursor)
    with db_conn.cursor() as cursor:
        cursor.execute("""SELECT * FROM Movies M 
                       JOIN Bechdel B
                       on B.movieID = M.movieID
                       WHERE M.movieId=%s""", (movie_id, ))
        movie = cursor.fetchone()
    with db_conn.cursor() as cursor: # for genre
        cursor.execute("SELECT * FROM MoviesGenres WHERE movieId=%s", (movie_id, ))
        genres = cursor.fetchall()
        movie['genres'] = [g['genre'] for g in genres]
    with db_conn.cursor() as cursor:  # for people
        cursor.execute("""SELECT * 
                       FROM people
                       inner join moviespeople as MP
                            on people.personId = MP.personId
                       inner join movies as M
                            on M.movieId = MP.movieId
                       where M.movieId=%s""", (movie_id, ))

        peopls = cursor.fetchall()
        movie['peopls'] = [p['primaryName'] for p in peopls]
    
# correction
#        with db_conn.cursor() as cursor:
#    cursor.execute("""
#        SELECT * FROM MoviesPeople MP
#        JOIN People P on P.personId = MP.personId
#        WHERE MP.movieId=%s
#    """, (movie_id, ))
#    people = cursor.fetchall()
#    movie['people'] = people

    db_conn.close() 
    return movie

