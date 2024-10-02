from flask import Flask, render_template, request, jsonify, make_response
import json
import sys
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'

with open('{}/databases/movies.json'.format("."), 'r') as jsf:
   movies = json.load(jsf)["movies"]

# root message
@app.route('/', methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

@app.route("/help", methods=['GET'])
def get_help():
    """Gives the entrypoints available."""
    with open('{}/UE-archi-distribuees-Movie-1.0.0-resolved.yaml'.format("."), 'r') as documentation:
        entrypoints = documentation.read()
    return make_response(entrypoints, 200)

@app.route("/json", methods=['GET'])
def get_json():
    return make_response(jsonify(movies), 200)

@app.route("/template", methods=['GET'])
def template():
    return make_response(render_template("index.html", body_text="This is my HTML template for Movie service"),200)

@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid) -> any:
    """Searches all the movies in the database with a specific id."""
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie), 200)
            return res
    return make_response(jsonify({"error" : "Movie ID not found"}), 400)

@app.route("/movies/<movieid>", methods=['POST'])
def add_movie(movieid : str) -> None:
    req = request.get_json()
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            return make_response(jsonify({"error":"movie ID already exists"}),409)
    movies.append(req)
    write(movies)
    res = make_response(jsonify({"message":"movie added"}),200)
    return res

@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid :str) -> any:
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            write(movies)
            return make_response(jsonify(movie), 200)
    res = make_response(jsonify({"error" : "movie ID not found"}), 400)
    return res

@app.route("/movies/title", methods=['GET'])
def get_movie_bytitle() -> str:
    """Searches all the movies in the database with a specific title."""
    title = request.get_data(as_text=True)
    for movie in movies:
        if movie["title"].lower() == title.lower():
            return make_response(jsonify(movie), 200)
    return make_response(jsonify({"error" : "movie title not found"}), 400)


@app.route("/movies/rating", methods=['GET'])
def get_movie_byrating() -> str:
    """Searches all the movies in the database with a specific rating."""
    movieRating = float(request.get_data(as_text=True))
    print(type(movieRating))
    print(movieRating)
    moviesRate = [movie for movie in movies if movie['rating'] == movieRating]
    if len(moviesRate) > 0:
        return make_response(jsonify(moviesRate), 200)
    return make_response(jsonify({"error" : "No movie with this rating."}), 400)

@app.route("/movies/director", methods=['GET'])
def get_movie_bydirector() -> str:
    """Searches all the movies in the database with a specific director."""
    director = request.get_data(as_text=True)
    movieDirector = [movie for movie in movies if movie['director'].lower() == director.lower()]
    if len(movieDirector) > 0:
        return make_response(jsonify(movieDirector), 200)
    return make_response(jsonify({"error" : "No movie with this director."}), 400)

def write(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        json.dump({"movies" : movies}, f)

@app.route("/movies/<movieid>/<rate>", methods=['PUT'])
def update_movie_rating(movieid : str, rate : float) -> any:
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movie["rating"] = rate
            res = make_response(jsonify(movie), 200)
            write(movies)
            return res
    res = make_response(jsonify({"error" : "movie ID not found"}), 201)
    return res


if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)