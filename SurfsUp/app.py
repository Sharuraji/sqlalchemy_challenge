# Import the dependencies.
from flask import Flask,jsonify
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func 

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
# session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)                  

# session = Session(engine)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(f"List all the available routes:<br/>"
           f"/api/v1.0/precipitation<br/>"
           f"/api/v1.0/stations<br/>"
           f"/api/v1.0/tobs<br/>"
           f"/api/v1.0/<start><br/>"
           f"/api/v1.0/<start>/<end>")

#1. create precipitation url
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    twelve_month_date =dt.date(2017,8,23)-dt.timedelta(days=365)

    precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date>twelve_month_date).all()

    session.close()

    precipitation_list = []
    for date, prcp in precipitation:
        precipitation_dict = {}
        precipitation_dict['date'] = date
        precipitation_dict['prcp'] = prcp
        precipitation_list.append(precipitation_dict)
    
    return jsonify(precipitation_list)


#2. create station url
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    stations = session.query(Station.station).all()

    session.close()
    
    station_list = []
    for station in stations:
        print(station[0])
        station_dict = {}
        station_dict['station'] = station[0]

        station_list.append(station_dict)
    
    return jsonify(station_list)

#3. create tobs url

@app.route("/api/v1.0/tobs")
def tops():
    session = Session(engine)

    sel = [Measurement.station,func.count(Measurement.station)]
    active_stations = session.query(*sel).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    active_stations
    most_active_station = active_stations[0][0]

    latest = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    str=[]
    str=latest[0].split("-")
    print(str[0],str[1],str[2])

    latest_year = dt.date(int(str[0]),int(str[1]),int(str[2]))
    previous_year = latest_year.year-1 
    
    previous_year_start_date  =dt.date(previous_year,1,1)
    previous_year_end_date = dt.date(previous_year,12,31)

    temp_observation = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
    filter(Measurement.station == most_active_station).\
        filter(Measurement.date>=previous_year_start_date)\
               .filter(Measurement.date<=previous_year_end_date).all()
    session.close()

    temp_observation_list = []
    for list_data in temp_observation:
        temp_observation_dict = {}
        temp_observation_dict['date'] = list_data[0]
        temp_observation_dict['tobs'] = list_data[1]
        temp_observation_list.append(temp_observation_dict)

    return jsonify(temp_observation_list)

# create start url
@app.route("/api/v1.0/<start>")
def temp_stats_start(start):
    print(start)
    session = Session(engine)
    start_temp_stats = session.query(func.min(Measurement.tobs), \
                                     func.avg(Measurement.tobs),\
                                        func.max(Measurement.tobs)).\
                                            filter(Measurement.date>=start).all()
    session.close()

    start_temp_stats_dict = {"min_temperature": start_temp_stats[0][0],
                             "average_temperature": start_temp_stats[0][1],
                             "max_temperature": start_temp_stats[0][2]
                             }
    return jsonify(start_temp_stats_dict)

@app.route("/api/v1.0/<start>/<end>")
def temp_stat_startend(start,end):
    print(start,end)
    session = Session(engine)
    start_end_temp_stats = session.query(func.min(Measurement.tobs),\
                                         func.avg(Measurement.tobs),\
                                         func.max(Measurement.tobs)).\
                                            filter(Measurement.date>=start).\
                                            filter(Measurement.date<=end).all()
    session.close()

    start_end_temp_stats_dict = {"min_temperature": start_end_temp_stats[0][0],
                             "average_temperature": start_end_temp_stats[0][1],
                             "max_temperature": start_end_temp_stats[0][2]
                             }
    return jsonify(start_end_temp_stats_dict)                                         

   
if __name__ == '__main__':
    app.run(debug=True)
    