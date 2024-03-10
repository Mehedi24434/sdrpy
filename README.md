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

**Main Functions:**

`get_trades(df=None, product="xccy", product_type="Basis", currency=None, currencies=None, maturity="m>3", date_range="-1d", dv01_min=None, usd_notional_min=None)`

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
```