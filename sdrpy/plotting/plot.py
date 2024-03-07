from sdrpy.filters.filter_functions import *
import matplotlib.pyplot as plt

def plot_notional_comparison(df, currencies=None, currency=None):
    main_df = df
    if currency is not None:
        df = filter_by_currency(df, currency)
        avg = main_df["USD_notional_leg1"].sum() / len(main_df["USD_notional_leg1"])
        notional_values = []
        event_time = []

        # Assuming you have a DataFrame 'df' containing your data
        for index, row in df.iterrows():
        
            leg = find_leg(currency, row['Notional currency-Leg 1'], row['Notional currency-Leg 2'])
            if leg == 'Leg 1':
                notional_values.append(row['USD_notional_leg1'])
                event_time.append(row["Event timestamp"])
            elif leg == 'Leg 2':
                notional_values.append(row['USD_notional_leg2'])
                event_time.append(row["Event timestamp"])
        new_df = pd.DataFrame(notional_values, index=event_time)
        new_df.sort_index(ascending=False)

        # Plotting
        plt.figure(figsize=(18, 6))  
        plt.bar(new_df.index, new_df[0], color='blue', label=f'{currency} Notional')
        plt.axhline(y=avg, color='red', linestyle='--', label='Average Notional')
        plt.xlabel('Event Timestamp')
        plt.ylabel('Notional')
        plt.title('Comparison of Notional Values to Average')
        plt.xticks(rotation=90)  
        plt.legend()
        plt.show()
    
    if currencies is not None:
        df = filter_by_currency(df, *currencies)
        
        dict_data = {}
        grouped_df1 = df.groupby("Notional currency-Leg 1")["USD_notional_leg1"].sum()
        grouped_df1 = grouped_df1.reset_index()
        grouped_df2 = df.groupby("Notional currency-Leg 2")["USD_notional_leg2"].sum()
        grouped_df2 = grouped_df2.reset_index()
        # Process df1
        for index, row in grouped_df1.iterrows():
            if row[0] in dict_data:
                dict_data[row[0]] += row[1]
            else:
                dict_data[row[0]] = row[1]

        # Process df2
        for index, row in grouped_df2.iterrows():
            if row[0] in dict_data:
                dict_data[row[0]] += row[1]
            else:
                dict_data[row[0]] = row[1]
        avg = main_df["USD_notional_leg1"].sum() / len(dict_data)
        curr_list=list(currencies)
        filtered_dict = {key: value for key, value in dict_data.items() if key in curr_list}
        # Plotting
        plt.figure(figsize=(18, 6))  
        plt.bar(filtered_dict.keys(), filtered_dict.values(), color='blue', label=f'{currencies} Notional')
        plt.axhline(y=avg, color='red', linestyle='--', label='Average Notional')
        plt.xlabel('Currencies')
        plt.ylabel('Notional')
        plt.title('Comparison of Notional Values to Average')
        plt.xticks(rotation=90)  
        plt.legend()
        plt.show()