from flask import Flask, request, Response
from imdbscrape.peopleandmovies import PeopleAndMovies

app = Flask(__name__)

imdbsearch = PeopleAndMovies("/search/title", 20, {
    "groups": "top_1000",
    "sort": "user_rating",
    "view": "simple",
})

@app.route('/', methods=['GET'])
def search():
    response = "Indexing..."
    name = request.args.get('name')
    if name:
        response = imdbsearch.search(name)
    return Response(str(response), mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
