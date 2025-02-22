import json
import requests
import pandas as pd
from datetime import datetime, timedelta

endpoint = "http://publicinfobanjir.water.gov.my/wp-content/themes/enlighten/data/latestreadingstrendabc.json"

def lambda_handler(event, context):

    ret = requests.get(endpoint, verify=False)
    data = ret.json()

    df = pd.DataFrame(data).rename(columns={
    'b': 'station_name',
    'c': 'long',
    'd': 'lat',
    'u': 'rainfall',
    'x': 'rainfall_indicator',
    'y': 'updated_on_rainfall'
    })


    df = df[
    (df['updated_on_rainfall'] != "") &  # Remove rows with empty 'updated_on_rainfall'
    (df['rainfall'] != "-")        # Remove rows where 'rainfall' is "-"
    ][['station_name', 'long', 'lat', 'rainfall', 'rainfall_indicator', 'updated_on_rainfall']]

    df['updated_on_rainfall'] = pd.to_datetime(df['updated_on_rainfall'], format="%d/%m/%Y %H:%M")
    df[['long', 'lat', 'rainfall']] = df[['long', 'lat', 'rainfall']].apply(pd.to_numeric)

    current_time = datetime.now()
    one_hour_ago = current_time - timedelta(minutes=30)
    df = df[df['updated_on_rainfall'] >= one_hour_ago]

    df = df.loc[df.groupby('station_name')['updated_on_rainfall'].idxmax()]

    data = json.loads(df.to_json(orient='split'))

    
    return {
        'statusCode': 200,
        'body': data,
        'headers': {
                'Content-Type': 'application/json'
            }
    }
