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
   """Get the welcoming HTLM message of the service"""
   return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"

@app.route("/bookings", methods=['GET'])
def get_json():
   """Get all the bookings"""
   return make_response(jsonify(bookings), 200)

@app.route("/bookings/<userid>", methods=['GET'])
def get_bookings_for_user(userid):
   """Get the bookings of the user userid"""
   for user in bookings:
      if user['userid'] == userid:
         return make_response(user, 200)
   return make_response("No bookings for this user", 200)

def getObjFromListAttr(list, attr, val):
   """Get the object in the list list having it's attribute attr equal to val. Return None otherwise"""
   for l in list:
      if l[attr] == val:
         return l
   return None

@app.route("/bookings/<userid>", methods=['POST'])
def add_booking_byuser(userid):
   """Add a booking for the user userid using the body of the HTTP request"""
   req = request.get_json()
   #Get the planned movies on the date of the potential booking
   plannedMovies = requests.get("http://127.0.0.1:3202/showmovies/" + req['date']).json()['movies']
   if not req['movie'] in plannedMovies:
      return make_response("Movie not planned on this date", 409)
   booking = getObjFromListAttr(bookings, 'userid', userid)
   date = getObjFromListAttr(booking['dates'], 'date', req['date']) if booking else None #If booking = None, we need to create the userid in this database
   if date and req['movie'] in date['movies']:
      return make_response("Movie already booked on this day", 409)
   if not booking:
      booking = {"userid": userid, "dates": []}
      bookings.append(booking)
   if not date:
      date = {  "date": req['date'], "movies": []}
      booking['dates'].append(date)
   date['movies'].append(req['movie'])
   write(bookings)
   return make_response(jsonify(booking), 200)

def removeObjFromListAttr(list, val, attrVal = None):
   """Remove the object from the list list equal to val or having his attribute attrVal equal to val. Side effect on the list. Return the list"""
   indexsToRemove = []
   i = 0
   for elem in list:
      if attrVal:
         if elem[attrVal] == val:
            indexsToRemove.append(i)
      else:
         if elem == val:
            indexsToRemove.append(i)
      i += 1
   for iIndex in range(len(indexsToRemove) - 1, -1, -1): #Start from the last index to avoid changing the index of the other objects to remove
      del list[indexsToRemove[iIndex]]
   return list

@app.route("/bookings/<userid>", methods=['DELETE'])
def delete_booking_ofuser(userid):
   """Delete the booking of the user userid using the body of the HTTP request"""
   req = request.get_json()
   booking = getObjFromListAttr(bookings, 'userid', userid)
   date = getObjFromListAttr(booking['dates'], 'date', req['date']) if booking else None
   if not (date and req['movie'] in date['movies']):
      return make_response("Movie not booked on this day", 409)
   if not removeObjFromListAttr(date['movies'], req['movie']):
      if not removeObjFromListAttr(booking['dates'], req['date'], 'date'):
         removeObjFromListAttr(bookings, userid, 'userid')
   write(bookings)
   return make_response(jsonify(getObjFromListAttr(bookings, 'userid', userid)), 200)

def write(bookings):
   """Write booking in the database"""
   with open('{}/databases/bookings.json'.format("."), 'w') as f:
      json.dump({"bookings" : bookings}, f)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
