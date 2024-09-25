from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('{}/databases/bookings.json'.format("."), "r") as jsf:
   bookings = json.load(jsf)["bookings"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_json():
   return make_response(jsonify(bookings), 200)

@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_foor_user(userid):
   for user in bookings:
      if user['userid'] == userid:
         return make_response(user, 200)
   return make_response("User not found", 400)

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   req = request.get_json()
   plannedMovies = requests.get("http://127.0.0.1:3202/showmovies/" + req['date']).json()['movies']
   for pMovie in plannedMovies:
      if pMovie == req['movie']:
         for booking in bookings:
            if booking['userid'] == userid:
               for date in booking['dates']:
                  if date['date'] == req['date']:
                     for movie in date['movies']:
                        if movie == req['movie']:
                           return make_response("Movie already booked on this day", 409)
                     date['movies'].append(req['movie'])
                     write(bookings)
                     return make_response(jsonify(booking), 200)
               booking['dates'].append({  "date": req['date'],
                                          "movies": [req['movie']]
                                       })
               write(bookings)
               return make_response(jsonify(booking), 200)
   return make_response("Movie not planned on this date", 409)

def write(bookings):
    with open('{}/databases/bookings.json'.format("."), 'w') as f:
        json.dump({"bookings" : bookings}, f)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
