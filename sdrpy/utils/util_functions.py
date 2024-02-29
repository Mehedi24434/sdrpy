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