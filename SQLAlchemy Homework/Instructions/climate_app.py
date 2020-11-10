import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)

app = Flask(__name__)


latestDate = (session.query(measurement.date)
                .order_by(measurement.date.desc())
                .first())
latestDate = list(np.ravel(latestDate))[0]

latestDate = dt.datetime.strptime(latestDate, '%Y-%m-%d')
latestYear = int(dt.datetime.strftime(latestDate, '%Y'))
latestMonth = int(dt.datetime.strftime(latestDate, '%m'))
latestDay = int(dt.datetime.strftime(latestDate, '%d'))

yearBefore = dt.date(latestYear, latestMonth, latestDay) - dt.timedelta(days=365)
yearBefore = dt.datetime.strftime(yearBefore, '%Y-%m-%d')

@app.route("/")
def home():
    return (f"Welcome to Surf's Up!: Hawai'i Climate API<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/stations ~~~~~ a list of all weather observation stations<br/>"
            f"/api/v1.0/precipitaton ~~ the latest year of preceipitation data<br/>"
            f"/api/v1.0/temperature ~~ the latest year of temperature data<br/>"
            f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
   
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(measurement.date, measurement.prcp, measurement.station)
                      .filter(measurement.date > yearBefore)
                      .order_by(measurement.date)
                      .all())
    
    precipData = []
    for result in results:
        precipDict = {result.date: result.prcp, "station": result.station}
        precipData.append(precipDict)

    return jsonify(precipData)

@app.route("/api/v1.0/temperature")
def temperature():

    results = (session.query(measurement.date, measurement.tobs, measurement.station)
                      .filter(measurement.date > yearBefore)
                      .order_by(measurement.date)
                      .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "station": result.station}
        tempData.append(tempDict)

    return jsonify(tempData)

@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [measurement.date, 
    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", measurement.date) >= startDate)
                       .group_by(measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [measurement.date, 
    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", measurement.date) <= endDate)
                       .group_by(measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)
    