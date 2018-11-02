
'''this script retrieves weather and tide data for each day for each beach, everyday as a scheduled task
and populates the SQLite database so that a user can enter their session time and get the right weather data
for their surf session '''

import requests
import sqlite3
from datetime import datetime
from buoyant import Buoy
import pdb



def create_connection(db_file):

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Errpr as e:
        print(e)


    return None


def create_weatherentry(conn,key,zipcode,weatherentry):

    '''create an entry in the weather table'''

    sql = ''' INSERT INTO weather(windspeed,winddirection,tide,swell,swelldirection,swellperiod,key,dtwind,dtbuoy)
    VALUES (?,?,?,?,?,?,?,?,?)'''

    cur = conn.cursor()


    cur.execute(sql,get_weatherentry(key,zipcode))



def get_weatherentry(key,zipcode):
        #get wind data for zipcode of beach
        r = requests.get('https://api.openweathermap.org/data/2.5/weather?zip='+str(zipcode)+',us&appid=27ea716e83aba632912e091d46b17ac2',verify=False)
        jsonObj = r.json() #parse as json
        wind_speed = float(jsonObj['wind']['speed'])
        wind_direction = float(jsonObj['wind']['deg'])
        dt = float(jsonObj['dt'])

        #9414290 - SF

        #9413450 - Monterrey

        santacruzbeaches =['santacruz']
        #get buoy data for all beaches
        if key in santacruzbeaches:
            santacruz = Buoy(46042)
            waves_out = santacruz.waves
            #grab UTC time without UTC extra digits for timezone
            dt_buoy = waves_out['sea_surface_wave_significant_height'].datetime.strftime("%Y-%m-%d %H:%M")

            tide = requests.get('https://tidesandcurrents.noaa.gov/api/datagetter?date=recent&station=9413450&product=water_level&datum=mllw&units=metric&time_zone=lst&application=web_services&format=json')
            tidejson = tide.json()
            last_tide = tidejson['data'].pop()
            last_tide_obs = last_tide['v']


        else:
            sf = Buoy(46237)
            waves_out = sf.waves
            dt_buoy = waves_out['sea_surface_wave_significant_height'].datetime.strftime("%Y-%m-%d %H:%M")

            #get tide data for SF

            tide = requests.get('https://tidesandcurrents.noaa.gov/api/datagetter?date=recent&station=9414290&product=water_level&datum=mllw&units=metric&time_zone=lst&application=web_services&format=json')
            tidejson = tide.json()
            last_tide = tidejson['data'].pop()
            last_tide_obs = last_tide['v']


        swell_period = waves_out['sea_surface_swell_wave_period']
        swell_height = waves_out['sea_surface_swell_wave_significant_height']


        if waves_out['sea_surface_swell_wave_to_direction'].real > 180:
            swell_direction = waves_out['sea_surface_swell_wave_to_direction'].real-180
        else:
            swell_direction = waves_out['sea_surface_swell_wave_to_direction'].real+180


        return wind_speed, wind_direction,last_tide_obs,swell_height,swell_direction,swell_period,key,dt,dt_buoy


def main():

    database = 'session.db'
    conn = create_connection(database)

    with conn:


        tide=0


        beaches = {'santacruz':95060,'pacifica':94044,'oceanbeach':94122}
        for key,zipcode in beaches.items():
            create_weatherentry(conn,key,zipcode,get_weatherentry(key,zipcode))


if __name__ =='__main__':
    main()
