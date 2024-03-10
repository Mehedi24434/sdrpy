import pandas as pd
import os
from datetime import date
today=date.today()


def currency_rate_updater():
    df = pd.read_json(
        "https://v6.exchangerate-api.com/v6/972a1e54b791700cf2d671b5/latest/USD"
    )
    df.to_csv(f"sdrpy/data/currency_conversion_for_{today}.csv")
