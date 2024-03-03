import pandas as pd
from sdrpy.utils.util_functions import *

def get_trades (df, product="xccy", product_type="Basis", currencies="CAD", maturity="m>3", date_range="-1d"):
    if currencies is not None :
        if len(currencies) > 1:
            df = filter_by_currency(df, *currencies)
        else:     
            df = filter_currency(df, currencies)
    print('currency filter returns;', len(df))
    if product!=None or product_type!=None:
        df = filter_product(df, product, product_type)
    print('product filter returns;', len(df))
    if maturity!=None:
        df = filter_maturity(df, maturity)
    #if date_range!=None:
        #df = filter_date_range(df, date_range)
    return df

def filter_product(df, product, product_type):
    product_name_map = pd.read_csv('./sdrpy/data/product_name_map.csv', index_col=0)
    try:
        real_product_name = product_name_map.loc[product].real_name
    except:
        print('ERROR: Could not match product name! Please check data/product_name_map.csv for correct name mapping')
    product_name = str(real_product_name + product_type)
    print(product_name)
    xdf = df[df["Product name"] == product_name]
    return xdf

def filter_currency(df, currency):
    return df[(df["Notional currency-Leg 1"] == currency[0]) | (df["Notional currency-Leg 2"] == currency[0])]
    #return df.loc[(df["Notional currency-Leg 1"]==currency) | (df["Notional currency-Leg 2"]==currency)]

def filter_maturity(df, maturity_conditions):
  """
  Filters a dataframe based on the values in the "maturity" column.

  Args:
    df : dataframe to filter
    maturity_conditions: string that can take several forms
      "m>3" : simple one-sided bound
      "3<m<6" : continuous range bound with smaller bound first [NOT 6>m>3]
      "m<3, m>8" : Multiple mutually exclusive bounds

  Returns:
      A new pandas dataframe containing the filtered rows.
  """
  df5 = get_maturity_column(df)
  bounds = extract_bounds(maturity_conditions)

  if bounds[0]==1:
      # Type 1 means single bound [(3, >)], so just use regular eval
      for bound, operator in bounds[1:]:
          print(operator, bound)
          df5 = df5.loc[eval(f"df5['maturity'] {operator} {bound}")].copy()
      overlap_df = df5
  elif bounds[0]==2:
      # Type 2 is continuous range [(3, '<'), (5, '<')], so merge separately
      low_bound, low_operator = bounds[1]
      low_df5 = df5.loc[eval(f"{low_bound} {low_operator} df5['maturity']")].copy()

      hi_bound, hi_operator = bounds[2]
      hi_df5 = df5.loc[eval(f"df5['maturity'] {hi_operator} {hi_bound}")].copy()
      
      overlap_df = custom_merge(low_df5, hi_df5, on='_id', how='inner')
  elif bounds[0]==3:
      # Type 3 is broken range [(3, '<'), (5, '>')], so concat separately
      low_bound, low_operator = bounds[1]
      low_df5 = df5.loc[eval(f"df5['maturity'] {low_operator} {low_bound}")].copy()

      hi_bound, hi_operator = bounds[2]
      hi_df5 = df5.loc[eval(f"df5['maturity'] {hi_operator} {hi_bound}")].copy()

      overlap_df = pd.concat([low_df5, hi_df5], ignore_index=True).drop_duplicates()
  return overlap_df
