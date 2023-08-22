import requests
import pandas  as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

def getNumberPageProducts():   
    """
        Retrieves the number of pages of products from the API.
    """
    endpoint = "https://api.storerestapi.com/products?limit=10"   
    headers = {
        'Content-Type': 'application/json'
        }
    response = requests.request("GET", endpoint, headers=headers)
    numberOfPagesTransactions = response.json()['metadata']['totalPages']
    return numberOfPagesTransactions

def getData(pages):
    """
    Retrieves data from the API iterating by all pages and getting the products. 
    The retrieved data goes to a dataframe format.

    """
    data = []
    for i in range(1, pages + 1):
        endpoint = "https://api.storerestapi.com/products?limit=10&page=" + str(i)
        headers = {
            'Content-Type': 'application/json'
            }
        response = requests.request("GET", endpoint, headers=headers)
        data.append(response.json()['data'])
        products_flat = [item for sublist in data for item in sublist] # flattens the nested list
        df = pd.json_normalize(products_flat, max_level=1, sep='_')
        df.drop('descriotion', axis=1, inplace=True) # drop description column cause it always null or empty
        if df.columns.str.contains('image').any():  # drop column image
            df = df.drop('image', axis=1)
    return df

def insert_and_show(mydf):
    """
    Inserts DataFrame into the 'products' table. If the table already exists, it is replaced with the new data. 
    
    """
    try:
        mydf.to_sql('products', engine, if_exists='replace', index=False)
    except SQLAlchemyError as e:
            error = str(e.__dict__['orig'])
            print(error)
    #Check if df was inserted
    result = engine.connect().execute((text("""SELECT * FROM products LIMIT 5;""")))
    return pd.DataFrame(result.fetchall(), columns=result.keys())

engine= create_engine("postgresql://soldebenedet_coderhouse:yK63N2gW2u@data-engineer-cluster.cyhh5bfevlmn.us-east-1.redshift.amazonaws.com:5439/data-engineer-database")


pages = getNumberPageProducts()
#Check if there are duplicates
mydf = getData(pages).drop_duplicates()
#print(mydf.head())
#print(mydf.info)
#print(mydf.dtypes)

print(insert_and_show(mydf))

