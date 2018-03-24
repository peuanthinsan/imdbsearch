from urllib.parse import parse_qs

from imdbscrape.peopleandmovies import PeopleAndMovies

imdbsearch = PeopleAndMovies("/search/title", 20, {
	"groups": "top_1000",
	"sort": "user_rating",
	"view": "simple",
})

def application(env, start_response):
	response = "Indexing..."
	start_response('200 OK', [('Content-Type','application/json')])

	query_string = parse_qs(env['QUERY_STRING'])
	if 'name' in query_string and len(query_string['name']):
		response = imdbsearch.search(query_string['name'][0])

	return str(response).encode()
