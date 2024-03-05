import re
import pandas as pd

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


def total_req_duration(df, date_range):
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
    if currency == "USD":
        return 1
    else:
        conversion_df = pd.read_csv("./currency_conversion.csv", index_col=0)
        rate = conversion_df.loc[currency]["conversion_rates"]
        return rate
    
def calculate_usd_notional(row):
    rate1 = conversion_rate(row['Notional currency-Leg 1'])
    rate2 = conversion_rate(row['Notional currency-Leg 2'])
    usd_notional_leg1 = (row['Notional amount-Leg 1 mm']*1000000) / rate1
    usd_notional_leg2 = (row['Notional amount-Leg 2 mm']*1000000) / rate2
    return pd.Series({'USD_notional_leg1': usd_notional_leg1, 'USD_notional_leg2': usd_notional_leg2})

def find_leg(currency, leg1_currency, leg2_currency):
    if currency == leg1_currency:
        return 'Leg 1'
    elif currency == leg2_currency:
        return 'Leg 2'
    else:
        return None  # Currency not found in either leg