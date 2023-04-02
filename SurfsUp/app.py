# import all dependances
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#################################################
# create connection to database
#################################################

# create engine to hawaii.sqlite
#using absolute rout, because relative gives me an error
engine = create_engine("sqlite:////Users/violettajanuskevica/Desktop/sqlalchemy_challenge/Resources/hawaii.sqlite")
#relative path
#engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# create Flask Routes 

# homepage route
@app.route("/")
def welcome():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    #find latest date available
    latest_date = session.query(Measurement.date).order_by(Measurement.date).first()

    # Close session
    session.close()

    #print to homepage
    return (
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<br/>"
        f"note: for start and end dates use format: yyyy-mm-dd<br/>"
        f"available date range {latest_date[0]} - {recent_date[0]}"
    )

# new rout defining
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #get query for date prcp, for the last 12 months order by date
    year_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= '2016-08-23').\
            order_by(Measurement.date).all()
    
    # Close session
    session.close()

    # Convert the query results from your precipitation analysis date as the key and prcp as the value.
    year_data_values = []
    for date, prcp in year_data:
        precipitation_dict = {}
        precipitation_dict["precipitation"] = prcp
        precipitation_dict["date"] = date
        year_data_values.append(precipitation_dict)

    #print out
    return jsonify(year_data_values)

# new rout defining
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #query to get station list
    station_data = session.query(Station.station, Station.id, Station.name ).all()

    # Close session
    session.close()

    # Convert the query results from your station analysis as JSON list.
    station_values = []
    for station, id, name in station_data:
        station_dict = {}
        station_dict["station"] = station
        station_dict["id"] = id
        station_dict["name"] = name
        station_values.append(station_dict)

    #print values
    return jsonify(station_values)

# new rout defining
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    #print(recent_date)
    #returns 2017-08-23

    # Calculate the date one year from the last date in data set.
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #print(year_ago)
    #returns 2016-08-23

    # Design a query to find the most active stations (i.e. what stations have the most rows?)
    # List the stations and the counts in descending order.
    active_stat = session.query(Measurement.station, func.count(Measurement.station)).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).all()
    #print(active_stat[0])
    #returns ('USC00519281', 2772)

    #Query the dates and temperature observations of the most-active station for the previous year of data.
    active_station = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
        filter(Measurement.station == active_stat[0][0]).\
            filter((Measurement.date >= year_ago)).all()
    
    # Close session
    session.close()

    # Convert the query results as JSON list.
    active_station_values = []
    for station, date, tobs in active_station:
        active_station_dict = {}
        active_station_dict["station"] = station
        active_station_dict["date"] = date
        active_station_dict["tobs"] = tobs
        active_station_dict
        active_station_values.append(active_station_dict)

    #print result
    return jsonify(active_station_values)

# new rout defining
@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #query Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start.
    sel = [func.avg(Measurement.tobs),
           func.min(Measurement.tobs),
           func.max(Measurement.tobs)
       ]
    tstart = session.query(*sel).\
        filter(Measurement.date >= start).all()
    
    # Close session
    session.close()

    # Convert the query results as JSON list.
    start_values = []
    for tavg, tmin, tmax in tstart:
        tstation_dict = {}
        tstation_dict["average"] = tavg
        tstation_dict["minimum"] = tmin
        tstation_dict["maximum"] = tmax
        start_values.append(tstation_dict)

    #print results
    return jsonify(start_values)

# new rout defining
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
    sel = [func.avg(Measurement.tobs),
           func.min(Measurement.tobs),
           func.max(Measurement.tobs)
       ]
    tend = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    
    # Close session
    session.close()

    # Convert the query results as JSON list.
    end_values = []
    for tavg, tmin, tmax in tend:
        endtstation_dict = {}
        endtstation_dict["average"] = tavg
        endtstation_dict["minimum"] = tmin
        endtstation_dict["maximum"] = tmax
        end_values.append(endtstation_dict)

    #print results
    return jsonify(end_values)

if __name__ == "__main__":
    app.run(debug=True)