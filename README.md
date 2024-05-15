# sdrpy

sdrpy is a Python library designed to facilitate the retrieval, analysis, and visualization of data from MongoDB containing live SDR (Swap Data Repository) data. Developed with a focus on robust filtering capabilities and versatile querying functions, sdrpy enables users to efficiently extract and manipulate trade data for in-depth analysis.

## Key Features

### Data Retrieval

The library provides a data module allowing users to retrieve live SDR data from MongoDB for analysis. Utilizing the `get_data` function, users can specify key parameters such as product type, date range, and other relevant filters to fetch tailored datasets.

### Robust Filtering

sdrpy offers strong filtering capabilities to retrieve specific trade data with precision. Through functions like `get_trades`, users can filter trades based on multiple criteria including product type, date range, currency, maturity, DV01, and USD notional, enabling focused analysis.

### Notional Comparison

Users can compare notional values of trades using the `plot_notional_comparison` function, which supports two types of comparisons: by a specific currency or by a list of currencies. This feature facilitates the visualization of notional values over time and across different currencies.

### Trade Analysis

The library includes functions such as `findall_matching_trades` and `findall_large_trades` for detailed trade analysis. `findall_matching_trades` filters trades matching specific criteria, while `findall_large_trades` identifies trades with the largest notional amounts, aiding in the identification of significant market movements.

### Summary Statistics

Users can generate summary statistics for all trades by currency using the `traded_currency` function. This method provides insights into the most actively traded currencies, including the number of contracts and their total sum in USD.

### Maturity Analysis

sdrpy enables users to analyze the sum of notional for each maturity on a daily basis. The `plot_total_notional_by_maturity` function calculates total notional values by maturity and visualizes the results through histograms, facilitating trend analysis.

**Installation:**

- Clone this repository:
  ```bash
  git clone https://github.com/your-username/sdrpy.git
  ```
- Install using setuptools:
  ```bash
  cd sdrpy
  python setup.py install
  ```


# Examples  
**Example 1:** lets download some trade data, I assume to get crosscurrency FixedFloat data for last week or last seven days

get_data(product="xccy", product_type="Basis", date_range="-13d"):

This function establishes a connection with MongoDB and retrieves the trading data based on the specified parameters from a MongoDB collection. It then closes the MongoDB connection after all actions are complete.

    Parameters:

    product (str): The type of product. The default is "xccy".
    product_type (str): The type of the product type. The default is "Basis".
    date_range (str): The date range for the data to be collected. Default is "-13d"

    Returns:

    DataFrame: a pandas dataframe with the trading data for the specified product, product type and date range.  


```python
df = get_data(key=key, product="irswap", product_type="FixedFloat",date_range="-1w") # or can use "-7d" in the date_range argument
```


**Example 2** :lets filter out some trades that traded for last 4 days, have USD leg, maturity is 3 to 5 years, minimum DV01 is 0.01 and minimum USD notional is 1 million

get_trades(df=None, product="xccy", product_type="Basis", currency=None, currencies=None, maturity="m>3", date_range="-1d", dv01_min=None, usd_notional_min=None)

    Retrieves trades based on specified filtering criteria.
    Parameters:
        df: (optional) DataFrame containing trade data.
        product: Product type to filter for (e.g., "xccy", "OIS").
        product_type: Product type within product (e.g., "Basis", "FixedFloat").
        currency: (optional) Specific currency to filter for.
        currencies: (optional) List of currencies to filter for.
        maturity: Maturity filter (e.g., "m>3", "s<1y").
        date_range: Date range for trades (e.g., "-1d", "-1w").
        dv01_min: (optional) Minimum DV01 threshold.
        usd_notional_min: (optional) Minimum USD notional threshold.
    Returns: DataFrame containing filtered trades.


```python
from sdrpy.filters.filter_functions import get_trades
US_df = get_trades(df, product="xccy",product_type="FixedFloat", date_range="-4d", currency="USD", maturity="3<m<5", dv01_min=0.01, usd_notional_min=1000000)
```

**EXAMPLE 3 and 4:** : can we compare the cad OIS notional vs the average?
The plot_notional_comparison function plots a comparison of notional values to the average notional value.

It supports two types of notional comparison:

1.   By a specific currency where it shows a timeline of notional values for trades involving that currency
2.   By a list of currencies where it compares the total notional value for each specified currency.
    


```
    Inputs:
    - df (DataFrame): The original DataFrame containing trades data.
    - currencies (list of str, optional): The list of currencies to be plotted. Default is None.
    - currency (str, optional): The specific currency to be used for the comparison. Default is None.
    
    Outputs:
    - This function does not have a return value. It directly produces a plot.
    - Supported data types:
        DataFrame column values should be numeric for 'USD_notional_leg1', 'USD_notional_leg2',
        string types for 'Notional currency-Leg 1', 'Notional currency-Leg 2',
        and datetime for 'Event timestamp'.
```

      
          
      Notes:
      - currencies and currency are both optional parameters. But at least one should be provided for the function to display a meaningful plot.
      - When both are given, this function will produce two separate plots, one for each parameter.

```python
from sdrpy.plotting.plot import plot_notional_comparison
plot_notional_comparison(US_df, currency = "USD")
```
![Alt text](https://github.com/anchorblock/sdrpy/blob/main/notional_comp1.png)


```python
from sdrpy.plotting.plot import plot_notional_comparison
plot_notional_comparison(df1,currencies=("USD","PEN","CAD","TRY"))
```
![Alt text](https://github.com/anchorblock/sdrpy/blob/main/notional_comp2.png)



<!-- **Main Functions:**

**`get_trades(df=None, product="xccy", product_type="Basis", currency=None, currencies=None, maturity="m>3", date_range="-1d", dv01_min=None, usd_notional_min=None)`**

- Retrieves trades based on specified filtering criteria.
- **Parameters:**
  - `df`: (optional) DataFrame containing trade data.
  - `product`: Product type to filter for (e.g., "xccy", "OIS").
  - `product_type`: Product type within product (e.g., "Basis", "FixedFloat").
  - `currency`: (optional) Specific currency to filter for.
  - `currencies`: (optional) List of currencies to filter for.
  - `maturity`: Maturity filter (e.g., "m>3", "s<1y").
  - `date_range`: Date range for trades (e.g., "-1d", "-1w").
  - `dv01_min`: (optional) Minimum DV01 threshold.
  - `usd_notional_min`: (optional) Minimum USD notional threshold.
- **Returns:** DataFrame containing filtered trades.

**`daily_report(df, num_curr=3)`**

- Generates a currency-wise daily report based on provided trade data.
- **Parameters:**
  - `df`: DataFrame containing trade data.
  - `num_curr`: (optional) Number of currencies to include in report.
- **Outputs:** Plots and tables containing trade data statistics and insights.


**Usage:**
```python
import sdrpy
sdrpy.get_trades()
```
```python
import sdrpy
sdrpy.daily_report()
``` -->