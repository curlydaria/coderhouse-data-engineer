from datetime import timedelta,datetime
from pathlib import Path
import json
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import os
from airflow.models import Connection

# DB connection
connection = Connection.get_connection_from_secrets("redshift-coderhouse")
data_base = connection.schema
url = connection.host
user = connection.login
port = "5439"
password = connection.password # This is a getter that returns the unencrypted password.

engine = create_engine(f'postgresql://{user}:{password}@{url}:{port}/{data_base}')

# function to extract data from api
def get_data():
    endpoint = "https://api.storerestapi.com/products?limit=10"
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", endpoint, headers=headers)
    number_of_pages = response.json()['metadata']['totalPages']

    data = []
    for i in range(1, number_of_pages + 1):
        page_endpoint = f"https://api.storerestapi.com/products?limit=10&page={i}"
        page_response = requests.request("GET", page_endpoint, headers=headers)
        data.append(page_response.json()['data'])
        products_flat = [item for sublist in data for item in sublist] # flattens the nested list
        with open(os.path.join("raw_data","data.json"), "w") as json_file:
            json.dump(products_flat, json_file)


# Function to transform data
def process_data():       
    with open(os.path.join("raw_data","data.json"), "r") as json_file:
        loaded_data=json.load(json_file)
    df=pd.json_normalize(loaded_data, max_level=1, sep='_')
    df.drop('description', axis=1, inplace=True) # drop description column cause it always null or empty
    if df.columns.str.contains('image').any():  # drop column image
            df = df.drop('image', axis=1)
    df.drop_duplicates(inplace=True) # to drop duplicates if any
    df.to_csv(os.path.join("processed_data","data.csv"), index=False)

# Finction to check if table exists
def redshift_conn():
     #engine = create_engine(f'postgresql://{user}:{password}@{url}:{port}/{data_base}')
     try:
          engine.connect()
          print("Connected to Redshift successfully!")
     except Exception as e:
          print(e)
          

# Function to insert data
def insert_data():
    #engine = create_engine(f'postgresql://{user}:{password}@{url}:{port}/{data_base}')
    df=pd.read_csv(os.path.join("processed_data","data.csv"))
    try: 
        df.to_sql('products_new', engine, if_exists='replace', index=False)
    except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            print(error)

