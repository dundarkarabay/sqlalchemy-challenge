import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
splitted_last_date = last_date[0].split("-")
year_of_last_date = int(splitted_last_date[0])
month_of_last_date = int(splitted_last_date[1])
day_of_last_date = int(splitted_last_date[2])
last_date = f"{year_of_last_date}-{month_of_last_date}-{day_of_last_date}"
formatted_last_date = dt.date(year_of_last_date,month_of_last_date,day_of_last_date)
formatted_begin_date = formatted_last_date - dt.timedelta(days=365)
year_of_begin_date = formatted_begin_date.strftime("%Y")
month_of_begin_date = formatted_begin_date.strftime("%m")
day_of_begin_date = formatted_begin_date.strftime("%d")
begin_date = f"{year_of_begin_date}-{month_of_begin_date}-{day_of_begin_date}"
session.close()

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/><br/><br/>"
        f"Important : Dates must be entered in YYYY-MM-DD<br/>" 
        f"format for last two API to work! "
    )


@app.route("/api/v1.0/precipitation")
def date_vs_prcp():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    d_vs_p = []
    for date, prcp in results:
        d_vs_p_dict = {date:prcp}   
        d_vs_p.append(d_vs_p_dict)
    return jsonify(d_vs_p)

@app.route("/api/v1.0/tobs")
def date_vs_tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
    filter(Measurement.date>=begin_date).order_by(Measurement.date).all()
    session.close()

    d_vs_t = []
    for date, tobs, station in results:
        d_vs_t_dict = {}
        d_vs_t_dict["date"] = date
        d_vs_t_dict["station"] = station
        d_vs_t_dict["tobs"] = tobs
        d_vs_t.append(d_vs_t_dict)
    return jsonify(d_vs_t)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.station).all()
    session.close()
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/<start>")
def calc_temps_open_end_date(start):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs).label("TMIN"),\
                        func.avg(Measurement.tobs).label("TAVG"), func.max(Measurement.tobs).label("TMAX"))\
                        .filter(Measurement.date >= start).filter(Measurement.date <= last_date).all()
    session.close()
    d_vs_temp = []
    for TMIN, TAVG, TMAX in results:
        temp_dict = {}
        temp_dict["Period"] = f"({start})-({last_date})"
        temp_dict["T_MIN"] = TMIN
        temp_dict["T_AVG"] = TAVG
        temp_dict["T_MAX"] = TMAX
        d_vs_temp.append(temp_dict)

    return jsonify(d_vs_temp)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps_close_end_date(start,end):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs).label("TMIN"),\
                        func.avg(Measurement.tobs).label("TAVG"), func.max(Measurement.tobs).label("TMAX"))\
                        .filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    d_vs_temp2 = []
    for TMIN, TAVG, TMAX in results:
        temp_dict2 = {}
        temp_dict2["Period"] = f"({start})-({end})"
        temp_dict2["T_MIN"] = TMIN
        temp_dict2["T_AVG"] = TAVG
        temp_dict2["T_MAX"] = TMAX
        d_vs_temp2.append(temp_dict2)

    return jsonify(d_vs_temp2)

if __name__ == '__main__':
    app.run(debug=True)
