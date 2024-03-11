import pandas as pd

from datetime import date
from sdrpy.utils.util_functions import *
from sdrpy.data.data_module import get_data

def get_trades (df=None, product="xccy", product_type="Basis", currency=None, currencies=None, maturity="m>3", date_range="-1d",dv01_min=None, usd_notional_min=None):
    
    if df is None:
        df=get_data(product,product_type,date_range=date_range)
    
    if currency != None :
        df = filter_by_currency(df, currency)

    if currencies != None :
        df = filter_by_currency(df, *currencies)
       
 
    if product!=None or product_type!=None:
        df = filter_product(df, product, product_type)

    if maturity!=None:
        df = filter_maturity(df, maturity)
    if date_range!=None:
        df = filter_date_range(df, date_range)
    if dv01_min!=None:
        df=df[df["dv01"]>=dv01_min]    
    try:
        df[['USD_notional_leg1', 'USD_notional_leg2']] = df.apply(calculate_usd_notional, axis=1)
    except:
        print("couldn't find any dataframe with these criteria")
    if usd_notional_min!=None:
        df = df[(df["USD_notional_leg1"] >= usd_notional_min) & (df["USD_notional_leg2"] >= usd_notional_min)]
    
    df['Notional amount-Leg 1'] = df['Notional amount-Leg 1'].astype(str).apply(convert_to_floats)
    df['Notional amount-Leg 2'] = df['Notional amount-Leg 2'].astype(str).apply(convert_to_floats)
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


def filter_date_range(df, date_range):
    duration = total_req_duration(date_range)
    df = df.loc[:, ~df.columns.duplicated()] ###remove previously duplecated columns
    today = date.today()
    df["Date"] = pd.to_datetime(df["Date"])
    today_timestamp = pd.Timestamp(today)
    df["Day_diff"]=today_timestamp - df["Date"]
    df=df[df["Day_diff"]<=pd.Timedelta(days=duration)]
    return df

def plot_notional_comparison(df,currencies):
    main_df=df
    if currencies != None :
      df = filter_by_currency(df, currencies)
    avg=main_df["USD_notional_leg1"].sum()/len(main_df["USD_notional_leg1"])
    notional_values = pd.Series()

    # Assuming you have a DataFrame 'df' containing your data
    for index, row in df.iterrows():
        currency = currencies  # Specify the currency you want to search for
        leg = find_leg(currency, row['Notional currency-Leg 1'], row['Notional currency-Leg 2'])
        if leg == 'Leg 1':
            notional_values[row['Event timestamp']] = row['USD_notional_leg1']
        elif leg == 'Leg 2':
            notional_values[row['Event timestamp']] = row['USD_notional_leg2']
    return notional_values, avg

def plot_notional_values_time(df, currencies):
  notional_values, avg = plot_notional_comparison(df, currencies)
  notional_values.index = pd.to_datetime(notional_values.index, format='ISO8601')
  # Assuming notional_values is a pandas Series with timestamps as index
  # and avg is the average value
  fig, ax = plt.subplots(figsize=(16, 6))

  # Create the bar plot
  ax.bar(notional_values.index, notional_values, color='blue', width=0.0006, alpha=0.7, label=f'{currencies} Notional') 
  #plt.bar(notional_values.index, notional_values, color='blue', alpha=0.7, label=f'EUR Notional')

  # Plot the average line with minimal label
  plt.axhline(y=avg, color='red', linestyle='--', label='Average Notional for all currencies')
  plt.yscale("log")  
  # Set x-axis labels with minimal formatting
  plt.xlabel('Time')
  plt.ylabel('Notional value (USD) Log-scale')
  plt.title(f'USD Notional value of trades over time for currency {currencies}')
  plt.legend()
  plt.tight_layout()  # Adjust layout for better spacing
  plt.show()
