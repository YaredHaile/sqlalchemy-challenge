from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base

# Set up the database connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a Flask app
app = Flask(__name__)

# Define the home route
@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt/&lt;end&gt"
    )

# Define the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year from the last date in the dataset
    last_date = session.query(func.max(Measurement.date)).scalar()
    first_date = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
   
    # Query the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= first_date).all()

    # Convert the query results to a dictionary
    precipitation_dict = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)

# Define the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # Query the list of stations
    stations = session.query(Station.station).all()
    station_list = [station[0] for station in stations]

    return jsonify(station_list)

# Define the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    # Calculate the date one year from the last date in the dataset
    last_date = session.query(func.max(Measurement.date)).scalar()
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    first_date = last_date - dt.timedelta(days=365)

    # Query the temperature observations for the most active station
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= first_date).\
        filter(Measurement.station == most_active_station_id).all()

    # Convert the query results to a list of dictionaries
    temperature_list = [{"date": date, "tobs": tobs} for date, tobs in temperature_data]

    return jsonify(temperature_list)

# Define the /api/v1.0/<start> and /api/v1.0/<start>/<end> routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    # Define a function to calculate temperature statistics
    def calculate_temperature_stats(start_date, end_date=None):
        # Query temperature statistics based on the date range
        if end_date:
            results = session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs)
            ).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
        else:
            results = session.query(
                func.min(Measurement.tobs),
                func.avg(Measurement.tobs),
                func.max(Measurement.tobs)
            ).filter(Measurement.date >= start_date).all()

        # Convert the query results to a list of dictionaries
        stats_list = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]

        return stats_list

    # Convert the start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    if end:
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    else:
        end_date = None

    # Calculate temperature statistics
    temperature_stats = calculate_temperature_stats(start_date, end_date)

    return jsonify(temperature_stats)

if __name__ == "__main__":
    # Create a session
    session = Session(engine)

    # Run the app
    app.run(debug=True)
