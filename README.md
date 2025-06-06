# Black-Scholes Pricing Model

This repository provides an interactive Black-Scholes Pricing Model dashboard that helps in visualizing option prices under varying conditions. The dashboard is designed to be user-friendly and interactive, allowing users to explore how changes in spot price, volatility, and other parameters influence the value of options.

https://blackschole.streamlit.app/

## 🚀 Features:

1. **Options Pricing Visualization**:
   - Displays Call and Put option prices using interactive heatmaps.
   - Heatmaps update dynamically as you adjust parameters such as Spot Price, Volatility and Time to Maturity.
   - Includes profit/loss surfaces at expiry showing payoff minus the option premium.
   
2. **Interactive Dashboard**:
   - The dashboard allows real-time updates to the Black-Scholes model parameters.
   - Users can input different values for the Spot Price, Volatility, Strike Price, Time to Maturity, and Risk-Free Interest Rate to observe how these factors influence option prices.
   - Both Call and Put option prices are calculated and displayed for immediate comparison.
   
3. **Customizable Parameters**:
   - Set custom ranges for Spot Price and Volatility to generate a comprehensive view of option prices under different market conditions.

## 🔧 Dependencies

The application requires the following packages (see `requirements.txt` for exact versions). The
numpy and scipy versions have been bumped to ensure wheels are available for Python 3.12 and later:

- `streamlit`
- `numpy`
- `scipy`
- `plotly`

Install them with:

```bash
pip install -r requirements.txt
```

Then run the dashboard using:

```bash
streamlit run streamlit_app.py
```
If the `streamlit` command is not available on your system, you can also run the
app with:

```bash
python -m streamlit run streamlit_app.py
```

## 🧪 Testing

Unit tests are provided in the `tests/` directory. Run them with:

```bash
pytest
```
