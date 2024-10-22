from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

with open('{}/databases/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

def isUserExisting(userid):
   """Test if the id userid exist"""
   for user in users:
      if user['id'] == userid:
         return True
   return False

def write(users):
   """Write users in the database"""
   with open('{}/databases/users.json'.format("."), 'w') as f:
      json.dump({"users" : users}, f)

@app.route("/", methods=['GET'])
def home():
   """Get the welcoming HTLM message of the service"""
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users", methods=['GET'])
def get_all_users() -> str:
    """Return all the users in the database"""
    return make_response(jsonify(users), 200)

@app.route("/users", methods = ['POST'])
def create_user() -> str:
   """Create en user using the content of the http request"""
   user = request.get_json()
   if isUserExisting(user['id']) : return make_response("This user is already existing", 409)
   users.append(user)
   write(users)
   return make_response(user, 200)

@app.route("/users/<userid>", methods=['GET'])
def get_user_byid(userid : str) -> str:
   """Searches all the users in the database with a specific id."""
   for user in users:
         if str(user['id']) == str(userid):
            return make_response(jsonify(user), 200) 
   return make_response("No user with this id.", 400)

@app.route("/users/<userid>", methods=['PUT'])
def update_user(userid : str) -> str:
   """Update the data of the user userid using the body of the HTTP request. We can change the id of the user, in this case userid is the old id, and the id in the body is the new id"""
   if not isUserExisting(userid) : return make_response("Unexisting user", 400)
   req = request.get_json()
   if req['id'] != userid and isUserExisting(req['id']): return make_response("Id already used by another user", 409)
   for user in users:
      if user['id'] == userid:
         user['id'] = req['id']
         user['name'] = req['name']
         user['last_active'] = req['last_active']
   write(users)
   return make_response(user, 200)


@app.route("/users/<userid>", methods=['DELETE'])
def delete_user(userid : str) -> str:
   """Delete the user with id userid"""
   global users
   newUsers = []
   deletedUsers = []
   for user in users:
         if user['id'] != userid:
            newUsers.append(user)
         else :
            deletedUsers.append(user)
   users = newUsers
   write(newUsers)
   return make_response(jsonify(deletedUsers), 200)

@app.route("/users/name", methods=['GET'])
def get_users_byname() -> str:
   """Searches all the users in the database with a specific name."""
   username = request.get_data(as_text=True)
   usersWithName = [user for user in users if user['name'].lower() == username.lower()]
   return make_response(jsonify(usersWithName), 200)

@app.route("/users/<userid>/bookings", methods = ['GET'])
def get_booking_user(userid : str) -> str:
   """Searches all the bookings of an user in the database"""
   if not isUserExisting(userid) : return make_response("Unexisting user", 400)
   reqBook = requests.get("http://127.0.0.1:3201/bookings/" + userid)
   return make_response(reqBook.content, reqBook.status_code)

@app.route("/users/<userid>/bookings/details", methods = ['GET'])
def get_detailed_booking_user(userid : str) -> str:
   """Searches all the bookings of an user in the database, and show all the details for each movie"""
   if not isUserExisting(userid) : return make_response("Unexisting user", 400)
   reqBook = requests.get("http://127.0.0.1:3201/bookings/" + userid)
   books = reqBook.json()
   for date in books['dates']:
      detailedMovies = []
      for movie in date['movies']:
         reqMovie = requests.get("http://127.0.0.1:3200/movies/" + movie)
         if reqMovie.status_code != 200 : return make_response("An issue occured when retrieving a movie data : " + reqMovie.content, 400)
         detailedMovies.append(reqMovie.json())
      date['movies'] = detailedMovies
   return make_response(books, 200)

@app.route("/users/<userid>/book", methods = ['POST', 'DELETE'])
def create_or_delete_booking_for_user(userid : str) -> str:
   """Create or delete a booking for the user userid. We use the incomming method as method to call the booking service"""
   req = request.get_json()
   if not isUserExisting(userid) : return make_response("Unexisting user", 409)
   reqBook = requests.request(request.method ,"http://127.0.0.1:3201/bookings/" + userid, json = req)
   if reqBook.status_code != 200 : return make_response(reqBook.content, 409)
   return make_response(reqBook.content, 200)

@app.route("/users/<userid>/bookMovie", methods = ['POST', 'DELETE'])
def create_or_delete_booking_for_user_with_title(userid : str) -> str:
   """Create or delete a booking for the user userid using the title of the movie. We use the incomming method as method to call the booking service"""
   req = request.get_json()
   reqMovie = requests.get("http://127.0.0.1:3200/movies/title", data=req["movieTitle"])
   if reqMovie.status_code != 200 : return make_response(reqMovie.content, 409)
   reqMovieJson = reqMovie.json()
   if len(reqMovieJson) == 0: return make_response("Movie not found", 409)
   jsonReqBook = {"movie" : reqMovieJson[0]["id"], "date" : req["date"]}
   reqBook = requests.request(request.method,"http://127.0.0.1:3203/users/" + userid + "/book", json= jsonReqBook)
   if reqBook.status_code != 200 : return make_response(reqBook.content, 409)
   return make_response(reqBook.content, 200)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)