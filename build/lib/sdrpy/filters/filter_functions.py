import pandas as pd


def get_trades(data,product:str, product_type="FixedFloat"):
    if product=="xccy":
        real_product="InterestRate:CrossCurrency:"
    product_name = str(real_product+product_type)
    df=data[data["Product name"]==product_name]
    return df