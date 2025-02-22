import json
import requests
import pandas as pd
from datetime import datetime, timedelta

endpoint = "http://publicinfobanjir.water.gov.my/wp-content/themes/enlighten/data/latestreadingstrendabc.json"

#github action

def lambda_handler(event, context):

    ret = requests.get(endpoint, verify=False)
    data = ret.json()

    df = pd.DataFrame(data).rename(columns={
    'b': 'station_name',
    'c': 'long',
    'd': 'lat',
    'm': 'water_level',
    'n': 'water_level_indicator',
    'q': 'updated_on_water',
    's': 'water_level_trend',
    })


    df = df[
    (df['updated_on_water'] != "") &  # Remove rows with empty 'updated_on_water'
    (df['water_level'] != "-")        # Remove rows where 'water_level' is "-"
    ][['station_name', 'long', 'lat', 'water_level', 'water_level_indicator', 'updated_on_water', 'water_level_trend']]

    df['updated_on_water'] = pd.to_datetime(df['updated_on_water'], format="%d/%m/%Y %H:%M")
    df[['long', 'lat', 'water_level']] = df[['long', 'lat', 'water_level']].apply(pd.to_numeric)

    current_time = datetime.now()
    one_hour_ago = current_time - timedelta(minutes=30)
    df = df[df['updated_on_water'] >= one_hour_ago]

    df = df.loc[df.groupby('station_name')['updated_on_water'].idxmax()]


    data = json.loads(df.to_json(orient='split'))

    
    return {
        'statusCode': 200,
        'body': data,
        'headers': {
                'Content-Type': 'application/json'
            }
    }
