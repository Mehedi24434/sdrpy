import pandas as pd
import os


df = pd.read_json(
    "https://v6.exchangerate-api.com/v6/972a1e54b791700cf2d671b5/latest/USD"
)
df.to_csv("currency_conversion.csv")
