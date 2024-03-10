import re
import os
import pandas as pd
from datetime import date
import numpy as np
import math
import matplotlib.pyplot as plt

import locale
from sdrpy.utils.usd_conversion import currency_rate_updater
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

today = date.today()

def convert_to_floats(x):
    try:
        if x[-1]=="+":
            return locale.atoi(x[:-1])
        elif x=="nan":
            return np.nan
        else:       
            return locale.atoi(x)
    except:
        return np.nan

def filter_by_currency(df, *currencies):
    """
    Filter DataFrame rows based on currencies.

    Args:
    - df: DataFrame to filter
    - *currencies: Variable-length arguments representing currencies to filter for

    Returns:
    - Filtered DataFrame
    """
    currencies_list = list(currencies)
    filter_condition = df["Notional currency-Leg 1"].isin(currencies_list) | df["Notional currency-Leg 2"].isin(currencies_list)
    filtered_df = df[filter_condition]
    return filtered_df

import re

# To utils
def get_maturity_column(df):
    df["Effective Date"] = pd.to_datetime(df["Effective Date"])
    df["Expiration Date"] = pd.to_datetime(df["Expiration Date"])
    df["maturity"] = (df["Expiration Date"] - df["Effective Date"]).dt.days / 365

    return df

# To utils
def extract_bounds(maturity_cond):
  """
  Extracts lower and upper bounds with their operators from a maturity condition string.

  Args:
      maturity_cond: A string representing the maturity condition (e.g., "3<m<30").

  Returns:
      A list of tuples containing (lower_bound, operator) and (upper_bound, operator).
  """
  
  pattern1 = r"(?:^|\s+)(\d+)\s*([<>]=?)\s*m\s*([<>]=?)\s*(\d+)(?:$|\s+)" # match continuous range
  pattern2 = r"m\s*([<>]=?)\s*(\d+)" # single bound
  pattern3 = r"m\s*([<>]=?)\s*(\d+)\s*,\s*m\s*([<>]=?)\s*(\d+)" # match mutually-exclusive range

  match1 = re.search(pattern1, maturity_cond)
  match2 = re.search(pattern2, maturity_cond)
  match3 = re.search(pattern3, maturity_cond)
  
  if match3:
    lower_op, lower_bound, upper_op, upper_bound = map(str, match3.groups())
    return [3, (int(lower_bound), lower_op), (int(upper_bound), upper_op)] # "m>5, m<3" returns [(5, '>'), (3, '<')]
  elif match1:
    lower_bound, lower_op, upper_op, upper_bound = map(str, match1.groups())
    return [2, (int(lower_bound), lower_op), (int(upper_bound), upper_op)] # "3<m<5" returns [(3, '<'), (5, '<')]
  elif match2:
    return [1, (match2.groups()[1], match2.groups()[0])]  # "m>3" returns ('>', '3')

# TO utils
def custom_merge(left, right, on, how='inner'):
  """
  Merges DataFrames with custom suffix removal.

  Args:
      left: The left DataFrame.
      right: The right DataFrame.
      on: The column(s) to use for merging.
      how: The merge method (default: 'inner').

  Returns:
      The merged DataFrame without suffixes.
  """
  merged_df = left.merge(right.copy(), on=on, how=how, suffixes=('', '_r'))
  merged_df.columns = [col.rstrip('_r') for col in merged_df.columns]
  return merged_df


def total_req_duration(date_range):
    duration= date_range[-1]
    if duration=="d":
        mult=1
    elif duration=="w":
        mult=7
    elif duration=="m":
        mult=30
    elif duration=="y":
        mult=365
    else:
        mult=1
    match = re.match(r'-([0-9]+)', date_range)
    num = int(match.group(1))
    total_duration =num*mult
    return total_duration


def conversion_rate(currency: str):
    if currency == "CLF":
        return 0.026
    if currency == "MXV":
        return 2.1
    if currency =="COU":
        return 2735334504056501
    if currency == "USD":
        return 1

    else:
        if os.path.exists(f"sdrpy/data/currency_conversion_for_{today}.csv"):
            conversion_df = pd.read_csv(f"sdrpy/data/currency_conversion_for_{today}.csv", index_col=0)
        else:
            currency_rate_updater()
            conversion_df = pd.read_csv(f"sdrpy/data/currency_conversion_for_{today}.csv", index_col=0)
        try:
            rate = conversion_df.loc[currency]["conversion_rates"]
        except:
            rate=np.nan
            print(f"we couldn't convert {currency} to USD, Please inform this to the developer")
        return rate
    
def calculate_usd_notional(row):
    if row['Notional currency-Leg 1'] != row['Notional currency-Leg 1']:
        usd_notional_leg1 = 0
    else:
        rate1 = conversion_rate(row['Notional currency-Leg 1'])
        usd_notional_leg1 = (row['Notional amount-Leg 1 mm']*1000000) / rate1

    if row['Notional currency-Leg 2'] != row['Notional currency-Leg 2']:
        usd_notional_leg2 = 0
    else:
        rate2 = conversion_rate(row['Notional currency-Leg 2'])
        usd_notional_leg2 = (row['Notional amount-Leg 2 mm']*1000000) / rate2
    return pd.Series({'USD_notional_leg1': usd_notional_leg1, 'USD_notional_leg2': usd_notional_leg2})


def find_leg(currency, leg1_currency, leg2_currency):
    if currency == leg1_currency:
        return 'Leg 1'
    elif currency == leg2_currency:
        return 'Leg 2'
    else:
        return None  # Currency not found in either leg

def matching_trades(df, trade_id):
    trade = df.loc[df['_id'].astype(str)==trade_id]
    maturity_df = df.loc[df['Expiration Date']==trade['Expiration Date'].values[0]]
    coupon_df = maturity_df.loc[(df['Fixed rate-Leg 1']==trade['Fixed rate-Leg 1'].values[0]) | (df['Fixed rate-Leg 2']==trade['Fixed rate-Leg 2'].values[0])]
    return coupon_df

def filter_currency(df, currency):
    return df[(df["Notional currency-Leg 1"] == currency[0]) | (df["Notional currency-Leg 2"] == currency[0])]

def currency_trades_plot(df):
    # Define colors for each currency
    colors = ['skyblue', 'lightcoral', 'lightgreen', 'gold', 'orange', 'purple', 'pink', 'red', 'teal', 'brown']

    # Create the figure and subplots
    fig, ax1 = plt.subplots(figsize=(14, 5))
    ax2 = ax1.twinx()

    # Plot No of Contracts on the left axis (ax1)
    ax1.bar(df.index, df['No of Contracts'], color=colors, label='No of Contracts')
    ax1.set_xlabel('Currency')
    ax1.set_ylabel('No of Contracts traded')
    ax1.tick_params(axis='y')  # Only display ticks on the left y-axis

    # Plot USD Notional on the right axis (ax2)
    ax2.plot(df.index, df['USD Amount'] / 1e10, label='USD Notional (in bllions)')  # Normalize for better readability
    ax2.set_ylabel('USD Notional (billions)')
    ax2.tick_params(axis='y')  # Only display ticks on the right y-axis

    # Customize the plot
    plt.title('No of Contracts traded vs. USD Notional (billions) by Currency')
    plt.xticks(df.index, df.index, rotation=4)
    plt.show()