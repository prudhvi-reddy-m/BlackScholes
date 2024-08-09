# Black-Scholes Pricing Model

This repository provides an interactive Black-Scholes Pricing Model dashboard that helps in visualizing option prices under varying conditions. The dashboard is designed to be user-friendly and interactive, allowing users to explore how changes in spot price, volatility, and other parameters influence the value of options.

https://blackschole.streamlit.app/

## 🚀 Features:

1. **Options Pricing Visualization**: 
   - Displays both Call and Put option prices using an interactive heatmap.
   - The heatmap dynamically updates as you adjust parameters like Spot Price, Volatility, and Time to Maturity.
   
2. **Interactive Dashboard**:
   - The dashboard allows real-time updates to the Black-Scholes model parameters.
   - Users can input different values for the Spot Price, Volatility, Strike Price, Time to Maturity, and Risk-Free Interest Rate to observe how these factors influence option prices.
   - Both Call and Put option prices are calculated and displayed for immediate comparison.
   
3. **Customizable Parameters**:
   - Set custom ranges for Spot Price and Volatility to generate a comprehensive view of option prices under different market conditions.

## 🔧 Dependencies:

- `yfinance`: To fetch current asset prices.
- `numpy`: For numerical operations.
- `matplotlib`: For heatmap visualization.


