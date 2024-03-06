from pymongo import MongoClient
import pandas as pd
from sdrpy.utils.util_functions import *
from datetime import date


def get_data(product="xccy", product_type="Basis", date_range="-13d"):

    if product!=None or product_type!=None:
        product_name = product_naming(product, product_type)

    if date_range!=None:
        duration = total_req_duration(date_range)
        today = date.today()
        
        

    # Connect to MongoDB
    client = MongoClient('mongodb://root:Anchorblock443215@13.233.125.116:27019,3.110.156.25:27018/?retryWrites=true&replicaSet=myReplicaSet&readPreference=secondary')  

    # Access the desired database and collection
    db = client['dtcc-cftc-data']  # Replace 'your_database_name' with the name of your database
    collection = db['rates']  # Replace 'your_collection_name' with the name of your collection

    # Define the date range
    start_date = str(today-pd.Timedelta(days=duration))
    end_date = str(today)

    # Query the collection to retrieve data for the date range and product name
    query = {"Date": {"$gte": start_date, "$lte": end_date}, "Product name": product_name}
    cursor = collection.find(query)

    # Convert the cursor to a list of dictionaries
    data = list(cursor)

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data)

    # Close the MongoDB connection
    client.close()
    return df

def product_naming(product, product_type):
    product_name_map = pd.read_csv('./sdrpy/data/product_name_map.csv', index_col=0)
    try:
        real_product_name = product_name_map.loc[product].real_name
    except:
        print('ERROR: Could not match product name! Please check data/product_name_map.csv for correct name mapping')
    product_name = str(real_product_name + product_type)
    return(product_name)
   