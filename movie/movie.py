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

@app.route("/template", methods=['GET'])
def template():
    return make_response(render_template("index.html", body_text="This is my HTML template for Movie service"),200)

@app.route("/json", methods=['GET'])
def get_json():
    res = make_response(jsonify(movies), 200)
    return res

@app.route("/movies/<movieid>", methods=['GET'])
def get_movie_byid(movieid) -> any:
    """Searches all the movies in the database with a specific id."""
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            res = make_response(jsonify(movie), 200)
            return res
    return make_response(jsonify({"error" : "Movie ID not found"}), 400)

@app.route("/moviesbytitle", methods=['GET'])
def get_movie_bytitle() -> str:
    """Searches all the movies in the database with a specific title."""
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie["title"]) == str(req["title"]):
                json = movie
    if not json:
        res = make_response(jsonify({"error" : "movie title not found"}), 400)
    else:
        res = make_response(jsonify(json), 200)
    return res

@app.route("/moviesbyrating", methods=['GET'])
def get_movie_byrating() -> str:
    """Searches all the movies in the database with a specific rating."""
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie['rating']) == str(req['rating']):
                json = movie
    if not json:
        res = make_response(jsonify({"error" : "No movie with this rating."}), 400)
    else:
        res = make_response(jsonify(json), 200)
    return res

@app.route("/moviesbydirector", methods=['GET'])
def get_movie_bydirector() -> str:
    """Searches all the movies in the database with a specific director."""
    json = ""
    if request.args:
        req = request.args
        for movie in movies:
            if str(movie['rating']) == str(req['rating']):
                json = movie
    if not json:
        res = make_response(jsonify({"error" : "No movie with this director."}))
    else:
        res = make_response(jsonify(json), 200)    
    return res

def write(movies):
    with open('{}/databases/movies.json'.format("."), 'w') as f:
        json.dump({"movies" : movies}, f)

@app.route("/addmovie/<movieid>", methods=['POST'])
def add_movie(movieid : str) -> None:
    req = request.get_json()
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            return make_response(jsonify({"error":"movie ID already exists"}),409)
    movies.append(req)
    write(movies)
    res = make_response(jsonify({"message":"movie added"}),200)
    return res

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

@app.route("/movies/<movieid>", methods=['DELETE'])
def del_movie(movieid :str) -> any:
    for movie in movies:
        if str(movie["id"]) == str(movieid):
            movies.remove(movie)
            write(movies)
            return make_response(jsonify(movie), 200)
    res = make_response(jsonify({"error" : "movie ID not found"}), 400)
    return res

if __name__ == "__main__":
    #p = sys.argv[1]
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)