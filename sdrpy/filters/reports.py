import pandas as pd
from sdrpy.utils.util_functions import *
from sdrpy.filters.filter_functions import plot_notional_values_time
from tabulate import tabulate
import matplotlib.pyplot as plt


def traded_currency(xdf):
    df = xdf.copy()
    leg_1_curr = df["Notional currency-Leg 1"].dropna().unique()

    leg_2_curr = df["Notional currency-Leg 2"].dropna().unique()
    currency_list = list(set(leg_1_curr) | set(leg_2_curr))

    print(f"Currencies most active: {currency_list}")
    df['Notional amount-Leg 1'] = df['Notional amount-Leg 1'].astype(str).apply(convert_to_floats)
    df['Notional amount-Leg 2'] = df['Notional amount-Leg 2'].astype(str).apply(convert_to_floats)

    # Define a function to calculate total sum and number of contracts
    def calculate_totals(currency, leg_column, notional_column):
        filtered_df = df[df[leg_column] == currency]
        num_of_trades = len(filtered_df)
        total_sum = int(float((filtered_df[notional_column].sum() * 1000)))
        return num_of_trades, total_sum

    total_sums = {
        "Currency": currency_list,
        "Total_Sum in million": [],
        "No of Contracts": [],
        "USD Amount": [],
    }

    for curr in currency_list:
        num_of_trades_1, total_sum_1 = calculate_totals(
            curr, "Notional currency-Leg 1", "Notional amount-Leg 1")
        num_of_trades_2, total_sum_2 = calculate_totals(
            curr, "Notional currency-Leg 2", "Notional amount-Leg 2")

        # Calculate total sum, number of contracts, and USD amount
        total_sum = total_sum_1 + total_sum_2
        sum_of_trades = num_of_trades_1 + num_of_trades_2
        rate = conversion_rate(currency=curr)
        usd_amount = int(total_sum / rate)

        total_sums["Total_Sum in million"].append(total_sum)
        total_sums["No of Contracts"].append(sum_of_trades)
        total_sums["USD Amount"].append(usd_amount)

    result_df = pd.DataFrame(total_sums)
    result_df.set_index("Currency", inplace=True)

    # table = tabulate(result_df, headers="keys", tablefmt="pretty")
    # print(table)
    return result_df.sort_values(by=['No of Contracts'], ascending=False)

def findall_matching_trades(df, currency=None):
    if currency!=None:
        df = filter_currency(df, [currency])
    done_ids = []
    matched_ids = {}
    for id in df["_id"].astype(str):
        if id not in done_ids:
            matches = matching_trades(df, id)
            if len(matches)>1:
                done_ids.append(list(matches['_id'].astype(str).values))
                mc = matches[['Product name', 'Notional currency-Leg 1', 'Notional currency-Leg 2', 'maturity', 'Effective Date', 'Fixed rate-Leg 1',
 'Fixed rate-Leg 2',  'Event type', 'Event timestamp']].iloc[0]
                mc['num_matches'] = len(matches)
                matched_ids[str(id)] = mc
    return pd.DataFrame.from_dict(matched_ids, orient='index').sort_values(by=['num_matches'], ascending=False)

def findall_large_trades(df, num_trades=20, currency=None):
    #df[['USD_notional_leg1', 'USD_notional_leg2']] = df.apply(calculate_usd_notional, axis=1)
    return df.sort_values(by=['USD_notional_leg1', 'USD_notional_leg2'], ascending=False)[['USD_notional_leg1', 'USD_notional_leg2', 'Product name', 'Date', 'Notional currency-Leg 1', 'Notional currency-Leg 2', 'maturity', 'Effective Date', 'Fixed rate-Leg 1',
 'Fixed rate-Leg 2']].head(num_trades)

def plot_total_notional_by_maturity(df):
    mdf = df.groupby('maturity')[['USD_notional_leg1', 'USD_notional_leg2']].sum().sum(axis=1)
    bins = pd.cut(x=mdf.index, bins=list(range(int(max(mdf.index))+2)))
    mdf = pd.DataFrame(mdf, columns=['notional'])
    mdf['bins'] = bins

    # Group data by bins and sum counts
    binned_data = mdf.groupby("bins")["notional"].sum()
    binned_data.index = binned_data.index.astype('category')
    # Create the bar plot
    plt.figure(figsize=(12, 5))  # Set figure size
    plt.bar(binned_data.index.codes, binned_data.values, color='lightgreen', edgecolor='black')

    # Customize labels and title
    plt.xlabel('Maturity')
    plt.ylabel('Sum of notional (USD)')
    plt.title('Sum of notionals by maturity', fontsize=14)

    # Add grid and legend (optional)
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Make the plot pretty (optional)
    plt.xticks(rotation=15, ha='right')  # Rotate x-axis labels for better readability
    plt.tight_layout()  # Adjust spacing for better aesthetics

    # Show the plot
    plt.show()
    return mdf

"""
The main report function;
1. Currency-wise number of trades breakdown table
2. For top3 currencies: [findall_large_trades, plot_notionals_hourly, plot_notionals_maturity, findall_matching_trades]
"""
def daily_report(df, num_curr=3):
    tdc = traded_currency(df)

    # Account for missing USD notional
    try:
        df[['USD_notional_leg1', 'USD_notional_leg2']] = df.apply(calculate_usd_notional, axis=1)
    except:
        print("couldn't find any dataframe with these criteria")
    currency_trades_plot(tdc.head(10))
    for curr in list(tdc.index)[:num_curr]:
        print_header(f'Notionals of {curr} trades over timeframe')
        plot_notional_values_time(df, curr)
        print_header(f'Largest 10 trades {curr}')
        cdf = filter_currency(df, [curr])
        large = findall_large_trades(cdf)
        table = tabulate(large.head(10), headers="keys", tablefmt="pretty")
        print(table)

        print_header(f'Notional size vs maturity {curr}')
        plot_total_notional_by_maturity(cdf)
        try:
            matches = findall_matching_trades(cdf, None)
            table = tabulate(matches, headers="keys", tablefmt="pretty")
            print_header(f'Matching trades {curr}')
            print(table)
        except:
            pass
        print("")

def print_header(header_text):
    border_symbol = "*"
    margin_size = 60

    # Calculate total width, including borders and padding
    total_width = len(border_symbol) * 2 + len(header_text) + 6

    # Create the top and bottom borders with centered padding
    top_border = bottom_border = border_symbol * total_width

    # Create the left margin with spaces
    left_margin = " " * margin_size

    # Combine elements for centered printing
    print("")
    print(left_margin +top_border)
    # Combine elements with margin
    print(" " * (margin_size+4) + header_text)
    print(left_margin + bottom_border)
    print("")