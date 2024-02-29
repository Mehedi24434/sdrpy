import pandas as pd
from sdrpy.utils.util_functions import filter_by_currency

def get_trades(data, product:str, currencies=None, product_type="FixedFloat", **kwargs):
    if product == "xccy":
        real_product = "InterestRate:CrossCurrency:"
    product_name = str(real_product + product_type)
    df = data[data["Product name"] == product_name]
    
    # Check if currencies is None or contains only one currency
    if currencies is not None :
        if len(currencies) > 1:
        
            df = filter_by_currency(df, *currencies)
            
        else:     
      
            df = filter_by_currency(df, currencies)
            
       
    
    return df