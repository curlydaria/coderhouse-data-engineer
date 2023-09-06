from datetime import timedelta,datetime
import requests
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import os
import logging 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib


# DW variables
DW_HOST = os.getenv('DW_HOST')
DW_USER = os.getenv('DW_USER')
DW_PASSWORD = os.getenv('DW_PASSWORD')
DW_PORT = os.getenv('DW_PORT')
DW_DATABASE = os.getenv('DW_DATABASE')

engine = create_engine(f'postgresql://{DW_USER}:{DW_PASSWORD}@{DW_HOST}:{DW_PORT}/{DW_DATABASE}')

# Function to create table 'products' in readshift
def create_table():
    try:
          engine.connect()
          logging.info("Connected to Redshift successfully!")
    except Exception as e:
          logging.error(e)
    sql_file = 'dags/create_table.sql'
    with open(sql_file, 'r') as f:
        sql = f.read()
        try:
            engine.execute(sql)
            logging.info("Table created successfully!")
        except Exception as e:
            logging.error(e)
# Function to extract data from api
def get_products_data(**context):
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
    df_raw=pd.json_normalize(products_flat, max_level=1, sep='_')
    logging.info("Cantidad de productos: %d", df_raw.shape[0])
    csv_raw_filename = f"{context['ds']}_raw_data.csv"
    df_raw.to_csv(csv_raw_filename, index=False)
    return csv_raw_filename
    

# Function to transform and merged data
def process_data(**context):       
    csv_raw_filename = context['ti'].xcom_pull(task_ids='extraer_data')
    #logging.info(f"csv_raw_filename: {csv_raw_filename}")
    df=pd.read_csv(csv_raw_filename)
    df.drop('description', axis=1, inplace=True) # drop description column cause it always null or empty
    if df.columns.str.contains('image').any():  # drop column image
            df = df.drop('image', axis=1)
    df.drop_duplicates(inplace=True) # to drop duplicates if any
    df_stock = pd.read_csv('products_data/products_in_stock.csv', usecols=['_id','inStock'])
    df_sales = pd.read_csv('products_data/products_sales_data.csv', usecols=['_id','sold'], sep=';')    
    merged = pd.merge(df, df_stock,on=['_id']).merge(df_sales,on=['_id'])
    csv_processed_filename = f"{context['ds']}_transformed_data.csv"
    merged.to_csv(csv_processed_filename, index=False)
    return csv_processed_filename

# Function to check oversaled products and send alert
def check_and_alert(**context):
    csv_processed_filename = context['ti'].xcom_pull(task_ids='transformar_data')
    df=pd.read_csv(csv_processed_filename)
    df_over_saled = df[df['sold'] > df['inStock']] #check if oversales
    if df_over_saled.shape[0] > 0:
        table = df_over_saled[['_id','title','sold','inStock']].to_html(border=0,index=False)
        #send email alert
        try:
            subject = "Alerta: Falta de stock"
            sender = os.getenv('SMTP_USER')
            receipient = os.getenv('SMTP_TO')
            password = os.getenv('SMTP_PASSWORD')
            message = MIMEMultipart() 
            message['Subject'] = subject
            message['From'] = sender
            message['To'] = receipient
            html = """
            <html>
                <head>Se han detectado productos con stock insuficiente y que se han sobrevendido</head>
                <body>{0}</body>
            </html>
            """.format(table)
            part = MIMEText(html, 'html')
            message.attach(part)
            with smtplib.SMTP_SSL(os.getenv('SMTP_HOST'), os.getenv('SMTP_PORT')) as server:
                server.login(sender, password)
                server.sendmail(sender, receipient, message.as_string())
            logging.info("Email sent successfully!")
        except Exception as exception:
            logging.error(exception)
            logging.error("Error sending email")



# Function to insert data
def insert_data(**context):
    csv_filename = context['ti'].xcom_pull(task_ids='transformar_data')
    df=pd.read_csv(csv_filename)
    try: 
        df.to_sql('products', engine, if_exists='replace', index=False)
        logging.info("Data inserted successfully!")
    except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            logging.error(error)

# Function to send email
def send_email():
    try:
        subject = "Email desde Airflow"
        sender = os.getenv('SMTP_USER')
        receipient = os.getenv('SMTP_TO')
        password = os.getenv('SMTP_PASSWORD')
        message = MIMEText("El proceso ETL_products se ha ejecutado correctamente el dia " + datetime.now().strftime("%d/%m/%Y") + ".")
        message['Subject'] = subject
        message['From'] = sender
        message['To'] = receipient
        with smtplib.SMTP_SSL(os.getenv('SMTP_HOST'), os.getenv('SMTP_PORT')) as server:
            server.login(sender, password)
            server.sendmail(sender, receipient, message.as_string())
        logging.info("Email sent successfully!")
    except Exception as exception:
        logging.error(exception)
        logging.error("Error sending email")





