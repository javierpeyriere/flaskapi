select primaryTitle, rating
from movies
inner join bechdel
on movies.movieId = bechdel.movieId
where primaryTitle like '%WALL·E%';

-- which actor has played in the most different genres
select people.primaryName, count(distinct moviesgenres.genre) as countname
from people
	inner join moviespeople
		on people.personId = moviespeople.personId
	inner join movies
		on moviespeople.movieId = movies.movieId
	inner join moviesgenres
		on movies.movieId = moviesgenres.movieId
group by people.primaryName
order by countname DESC;

select people.primaryName, moviesgenres.genre
from people
	inner join moviespeople
		on people.personId = moviespeople.personId
	inner join movies
		on moviespeople.movieId = movies.movieId
	inner join moviesgenres
		on movies.movieId = moviesgenres.movieId
where people.primaryName like '%Tim Bevan%';

-- correction
SELECT primaryName, count(distinct MoviesGenres.genre) as mx FROM People
LEFT JOIN MoviesPeople
	ON People.personId = MoviesPeople.personId
LEFT JOIN Movies
	ON MoviesPeople.movieId = Movies.movieId
LEFT JOIN MoviesGenres
	ON Movies.movieId = MoviesGenres.movieId
GROUP BY People.primaryName
ORDER BY MX DESC;

select p.personId, m.primaryTitle, m.startYear, m.runtimeMinutes
	from bechdel.movies as m
	inner join moviespeople as mp
		on m.movieId = mp.movieId
	inner join bechdel.people as p
		on p.personId = mp.personId
	where p.personId = 5;