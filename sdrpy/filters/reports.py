import pandas as pd
from sdrpy.utils.util_functions import *


def traded_currency(xdf):
    df = xdf.copy()
    leg_1_curr = df["Notional currency-Leg 1"].dropna().unique()

    leg_2_curr = df["Notional currency-Leg 2"].dropna().unique()
    currency_list = list(set(leg_1_curr) | set(leg_2_curr))

    print(f"Currencies used over the past 24 Hours: {currency_list}")
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
    return result_df.sort_values(by=['USD Amount'], ascending=False)

def findall_matching_trades(df):
    done_ids = []
    matched_ids = {}
    for id in df["_id"]:
        if id not in done_ids:
            matches = matching_trades(df, id)
            if len(matches)>1:
                done_ids.append(list(matches['_id'].values))
                matched_ids[id] = matches[['Product name', 'Notional currency-Leg 1', 'Notional currency-Leg 2', 'maturity', 'Effective Date', 'Fixed rate-Leg 1',
 'Fixed rate-Leg 2']].iloc[0]
    return matched_ids

def findall_large_trades(df, num_trades=20):
    df[['USD_notional_leg1', 'USD_notional_leg2']] = df.apply(calculate_usd_notional, axis=1)
    return df.sort_values(by=['USD_notional_leg1', 'USD_notional_leg2'], ascending=False)[['Product name', 'Date', 'Notional currency-Leg 1', 'Notional currency-Leg 2', 'maturity', 'Effective Date', 'Fixed rate-Leg 1',
 'Fixed rate-Leg 2']].head(num_trades)
