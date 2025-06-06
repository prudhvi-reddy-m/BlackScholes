import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Assuming your BlackScholes.py is in the same directory
# It should handle the Black-Scholes formula and return call/put prices
from BlackScholes import BlackScholes

# --- Helper Function ---
def _step(val: float) -> float:
    """Return an appropriate step size based on the current value."""
    return max(0.01, round(val * 0.01, 2))

# --- Page Config ---
st.set_page_config(layout="wide", page_title="Option Analyzer")

# --- Title ---
st.title("Black-Scholes Option Analyzer")

# --- Tab Creation ---
tab1, tab2 = st.tabs(["Option Pricing & Expiry P&L", "Position P&L Tracker (Before Expiry)"])

# --- Tab 1: Option Pricing & Expiry P&L ---
with tab1:
    st.header("Current Market Snapshot & Expiry Outcomes")

    st.sidebar.header("Current Market Parameters")

    default_S = 100.0
    prev_S = st.session_state.get("spot_price_tab1", default_S)
    step_S = _step(prev_S)
    S = st.sidebar.number_input( # This S is the current Spot Price for BS calculation in Tab 1
        "Current Spot Price ($)",
        min_value=0.0,
        value=prev_S,
        step=step_S,
        key="spot_price_tab1",
        format="%.4f",
    )

    default_K = 100.0
    prev_K = st.session_state.get("strike_price_tab1", default_K)
    step_K = _step(prev_K)
    K = st.sidebar.number_input(
        "Strike Price ($)",
        min_value=0.0,
        value=prev_K,
        step=step_K,
        key="strike_price_tab1",
        format="%.4f",
    )

    sigma_pct = st.sidebar.number_input(
        "Current Volatility (%)",
        min_value=0.0,
        max_value=200.0,
        value=st.session_state.get("sigma_pct_tab1", 20.0),
        step=0.001,
        format="%.3f",
        key="sigma_pct_tab1",
    )
    sigma = sigma_pct / 100.0 # This sigma is the current volatility for Tab 1 calculations

    T_weeks = st.sidebar.slider(
        "Time to Maturity (weeks)",
        min_value=0, # Allow 0 for conceptual expiry view, though BS needs > 0
        max_value=104,
        value=st.session_state.get("T_weeks_tab1", 52),
        step=1,
        key="T_weeks_tab1",
    )
    T = T_weeks / 52.0 # Ensure float division

    r = st.sidebar.slider(
        "Risk-Free Rate (%)", min_value=0.0, max_value=0.2, value=st.session_state.get("r_tab1", 0.05), step=0.001, format="%.3f", key="r_tab1"
    )
    r /= 100.0 # Convert percentage to decimal

    # Calculate single price based on sidebar inputs (used for readout and P&L line graphs)
    # Use a small epsilon for T or sigma if they are zero, to avoid BS errors
    # If T=0, option value is just intrinsic value (payoff)
    if T <= 0:
        call_price_single = max(S - K, 0.0)
        put_price_single = max(K - S, 0.0)
        st.info("Time to Maturity is 0, showing intrinsic value.")
    elif sigma <= 0:
         # Handle sigma = 0, value is discounted deterministic payoff
        future_S = S * np.exp(r * T)
        call_price_single = max(future_S - K, 0.0) * np.exp(-r * T)
        put_price_single = max(K - future_S, 0.0) * np.exp(-r * T)
        st.info("Volatility is 0, showing discounted deterministic payoff.")
    else:
        bs_single = BlackScholes(T, K, S, sigma, r)
        call_price_single, put_price_single = bs_single.calculate_prices()


    st.subheader("Option Prices (Based on sidebar inputs)")
    st.write(f"Call Price: **${call_price_single:.4f}**")
    st.write(f"Put Price: **${put_price_single:.4f}**")
    st.markdown("---") # Separator

    st.subheader("Price and P&L Heatmaps")
    st.sidebar.header("Heatmap Ranges (Tab 1)")
    spot_range_slider_tab1 = st.sidebar.slider(
        "Current Spot Price Range ($)", # For y-axis of heatmaps
        min_value=0.0,
        max_value=max(2 * S, 200.0),
        value=(max(0.0, 0.5 * S), 1.5 * S),
        step=_step(S),
        format="%.4f",
        key="spot_range_tab1"
    )

    vol_range_pct_slider_tab1 = st.sidebar.slider(
        "Current Volatility Range (%)", # For x-axis of heatmaps
        min_value=0.0,
        max_value=200.0,
        value=(max(0.0, sigma_pct * 0.5), min(200.0, sigma_pct * 1.5)),
        step=0.1,
        format="%.1f",
        key="vol_range_tab1"
    )
    vol_range_heatmap_tab1 = (vol_range_pct_slider_tab1[0] / 100.0, vol_range_pct_slider_tab1[1] / 100.0)

    # Grids for heatmaps
    S_grid_tab1 = np.linspace(spot_range_slider_tab1[0], spot_range_slider_tab1[1], 50)
    # Handle case where vol_range_heatmap[0] == vol_range_heatmap[1]
    if vol_range_heatmap_tab1[0] == vol_range_heatmap_tab1[1]:
         vol_grid_tab1 = np.array([vol_range_heatmap_tab1[0]]) # Create a single point array
         vol_grid_pct_tab1 = vol_grid_tab1 * 100
    else:
         vol_grid_tab1 = np.linspace(vol_range_heatmap_tab1[0], vol_range_heatmap_tab1[1], 50)
         vol_grid_pct_tab1 = vol_grid_tab1 * 100


    # --- Data Calculation for Heatmaps (Tab 1) ---
    # Row 1: Option Price (vs. Current Spot & Vol)
    optionprice_call_heatmap_grid_tab1 = np.zeros((len(S_grid_tab1), len(vol_grid_tab1)))
    optionprice_put_heatmap_grid_tab1 = np.zeros_like(optionprice_call_heatmap_grid_tab1)

    # T and r are from sidebar (fixed for this plot)
    # The grids represent hypothetical current S and sigma values
    if T_weeks > 0: # Only calculate BS price heatmaps if T > 0
        for i, s_current_hypothetical in enumerate(S_grid_tab1):
            for j, v_current_hypothetical in enumerate(vol_grid_tab1):
                # Ensure volatility is positive for standard BS calculation
                if v_current_hypothetical > 1e-9: # Use a small epsilon
                     c, p = BlackScholes(T, K, s_current_hypothetical, v_current_hypothetical, r).calculate_prices()
                     optionprice_call_heatmap_grid_tab1[i, j] = c
                     optionprice_put_heatmap_grid_tab1[i, j] = p
                else:
                     # Handle zero volatility (linear payoff discounted)
                     future_s_hypothetical = s_current_hypothetical * np.exp(r * T)
                     optionprice_call_heatmap_grid_tab1[i, j] = max(future_s_hypothetical - K, 0) * np.exp(-r * T)
                     optionprice_put_heatmap_grid_tab1[i, j] = max(K - future_s_hypothetical, 0) * np.exp(-r * T)
    else:
         # If T is 0, the price is just the intrinsic value regardless of vol (for heatmap visualization consistency)
         for i, s_current_hypothetical in enumerate(S_grid_tab1):
              optionprice_call_heatmap_grid_tab1[i, :] = max(s_current_hypothetical - K, 0.0)
              optionprice_put_heatmap_grid_tab1[i, :] = max(K - s_current_hypothetical, 0.0)


    # Rows 2 and 3: P&L at Expiry vs. Expiry Spot and Initial Vol
    # Initial Cost is based on S (sidebar initial spot) and vol_grid_tab1 (as initial volatility range)
    # Payoff at Expiry is based on S_grid_tab1 (as expiry spot price range)
    # T and r are from sidebar

    initial_call_costs_for_pnl_heatmap_tab1 = np.zeros(len(vol_grid_tab1))
    initial_put_costs_for_pnl_heatmap_tab1 = np.zeros(len(vol_grid_tab1))

    # Calculate initial cost based on sidebar S and the range of initial volatilities (vol_grid_tab1)
    if T_weeks > 0 and S > 0:
        for j, v_initial in enumerate(vol_grid_tab1):
            if v_initial > 1e-9:
                 c, p = BlackScholes(T, K, S, v_initial, r).calculate_prices()
                 initial_call_costs_for_pnl_heatmap_tab1[j] = c
                 initial_put_costs_for_pnl_heatmap_tab1[j] = p
            else:
                 # Handle zero initial volatility cost
                 future_S = S * np.exp(r * T)
                 initial_call_costs_for_pnl_heatmap_tab1[j] = max(future_S - K, 0) * np.exp(-r * T)
                 initial_put_costs_for_pnl_heatmap_tab1[j] = max(K - future_S, 0) * np.exp(-r * T)
    elif T_weeks == 0 and S > 0:
         # If T=0, initial cost is intrinsic value regardless of vol
         initial_call_costs_for_pnl_heatmap_tab1[:] = max(S - K, 0.0)
         initial_put_costs_for_pnl_heatmap_tab1[:] = max(K - S, 0.0)
    else:
         # Cannot calculate initial cost if S=0 and T>0 or S=0 and T=0 etc.
         st.warning("Cannot calculate initial cost for P&L heatmaps if Initial Spot Price is 0.")


    # Payoff at expiry (depends on S_grid_tab1 as the spot price at expiry)
    call_payoff_at_expiry_tab1 = np.maximum(S_grid_tab1[:, None] - K, 0)
    put_payoff_at_expiry_tab1 = np.maximum(K - S_grid_tab1[:, None], 0)

    # P&L calculations for heatmaps (Tab 1)
    call_pnl_grid_long_tab1 = call_payoff_at_expiry_tab1 - initial_call_costs_for_pnl_heatmap_tab1[None, :]
    put_pnl_grid_long_tab1 = put_payoff_at_expiry_tab1 - initial_put_costs_for_pnl_heatmap_tab1[None, :]
    call_pnl_grid_short_tab1 = initial_call_costs_for_pnl_heatmap_tab1[None, :] - call_payoff_at_expiry_tab1
    put_pnl_grid_short_tab1 = initial_put_costs_for_pnl_heatmap_tab1[None, :] - put_payoff_at_expiry_tab1


    # --- Plotting Heatmaps (Tab 1) ---
    fig_heatmaps_tab1 = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            "Call Price (vs. Current Spot & Vol, T fixed)",
            "Put Price (vs. Current Spot & Vol, T fixed)",
            "Long Call P&L at Expiry (vs. Expiry Spot & Initial Vol)",
            "Long Put P&L at Expiry (vs. Expiry Spot & Initial Vol)",
            "Short Call P&L at Expiry (vs. Expiry Spot & Initial Vol)",
            "Short Put P&L at Expiry (vs. Expiry Spot & Initial Vol)"
        ),
        horizontal_spacing=0.1,
        vertical_spacing=0.2,
    )

    # Row 1: Option Prices (using the newly named grids for clarity)
    fig_heatmaps_tab1.add_trace(
        go.Heatmap(x=vol_grid_pct_tab1, y=S_grid_tab1, z=optionprice_call_heatmap_grid_tab1, colorscale="Viridis", colorbar=dict(title="Price ($)")),
        row=1, col=1
    )
    fig_heatmaps_tab1.add_trace(
        go.Heatmap(x=vol_grid_pct_tab1, y=S_grid_tab1, z=optionprice_put_heatmap_grid_tab1, colorscale="Viridis", colorbar=dict(title="Price ($)")),
        row=1, col=2
    )

    # Row 2: Long P&L at Expiry
    fig_heatmaps_tab1.add_trace(
        go.Heatmap(x=vol_grid_pct_tab1, y=S_grid_tab1, z=call_pnl_grid_long_tab1, colorscale="RdYlGn", zmid=0, colorbar=dict(title="P&L ($)")),
        row=2, col=1
    )
    fig_heatmaps_tab1.add_trace(
        go.Heatmap(x=vol_grid_pct_tab1, y=S_grid_tab1, z=put_pnl_grid_long_tab1, colorscale="RdYlGn", zmid=0, colorbar=dict(title="P&L ($)")),
        row=2, col=2
    )

    # Row 3: Short P&L at Expiry
    fig_heatmaps_tab1.add_trace(
        go.Heatmap(x=vol_grid_pct_tab1, y=S_grid_tab1, z=call_pnl_grid_short_tab1, colorscale="RdYlGn", zmid=0, colorbar=dict(title="P&L ($)")),
        row=3, col=1
    )
    fig_heatmaps_tab1.add_trace(
        go.Heatmap(x=vol_grid_pct_tab1, y=S_grid_tab1, z=put_pnl_grid_short_tab1, colorscale="RdYlGn", zmid=0, colorbar=dict(title="P&L ($)")),
        row=3, col=2
    )

    # Update axis titles for all subplots consistently
    for i in range(1, 4): # Rows
        for j in range(1, 3): # Cols
            fig_heatmaps_tab1.update_xaxes(title_text="Volatility (%)", row=i, col=j)
            if i == 1:
                fig_heatmaps_tab1.update_yaxes(title_text="Current Spot Price ($)", row=i, col=j)
            else: # For P&L plots
                fig_heatmaps_tab1.update_yaxes(title_text="Spot Price at Expiry ($)", row=i, col=j)


    fig_heatmaps_tab1.update_layout(
        height=1000,
        title_text="Option Price and P&L Heatmaps",
        title_x=0.5,
        margin=dict(t=100), # Add space for titles
        hovermode='closest' # Improve hover on heatmaps
    )

    st.plotly_chart(fig_heatmaps_tab1, use_container_width=True)

    st.markdown("---") # Separator
    st.subheader("Profit/Loss at Expiry (Line Graphs)")
    st.write("These graphs show P&L at expiry based on the current sidebar inputs (as initial parameters) and varying spot price at expiry.")

    # --- Data Calculation for P&L Line Graphs at Expiry (Tab 1) ---
    # These graphs use the single initial price calculated from sidebar inputs (S, sigma, T, K, r)
    # and show P&L purely as a function of the Spot Price at Expiry (S_grid_tab1)

    # Calculate P&L arrays for the line graphs
    # Long Call P&L = max(S_expiry - K, 0) - initial_call_premium
    # Short Call P&L = initial_call_premium - max(S_expiry - K, 0)
    # Long Put P&L = max(K - S_expiry, 0) - initial_put_premium
    # Short Put P&L = initial_put_premium - max(K - S_expiry, 0)

    call_pnl_line_long_tab1 = np.maximum(S_grid_tab1 - K, 0) - call_price_single
    call_pnl_line_short_tab1 = call_price_single - np.maximum(S_grid_tab1 - K, 0)
    put_pnl_line_long_tab1 = np.maximum(K - S_grid_tab1, 0) - put_price_single
    put_pnl_line_short_tab1 = put_price_single - np.maximum(K - S_grid_tab1, 0)


    # --- Plotting P&L Line Graphs at Expiry (Tab 1) ---

    # Call P&L Plot
    fig_call_pnl_line_tab1 = go.Figure()
    fig_call_pnl_line_tab1.add_trace(go.Scatter(x=S_grid_tab1, y=call_pnl_line_long_tab1, mode='lines', name='Long Call', line=dict(color='green', width=2)))
    fig_call_pnl_line_tab1.add_trace(go.Scatter(x=S_grid_tab1, y=call_pnl_line_short_tab1, mode='lines', name='Short Call', line=dict(color='red', width=2)))

    # Add breakeven point(s) for Long Call
    # Breakeven for Call is S_expiry = K + Premium
    call_breakeven_tab1 = K + call_price_single
    if S_grid_tab1.min() <= call_breakeven_tab1 <= S_grid_tab1.max():
         fig_call_pnl_line_tab1.add_vline(x=call_breakeven_tab1, line_dash="dash", line_color="grey", annotation_text=f"Call Breakeven: ${call_breakeven_tab1:.2f}", annotation_position="top right", annotation_font_size=10)

    # Add horizontal line at 0 P&L
    fig_call_pnl_line_tab1.add_shape(type="line", x0=S_grid_tab1.min(), y0=0, x1=S_grid_tab1.max(), y1=0, line=dict(color="gray", width=1, dash="dash"))


    fig_call_pnl_line_tab1.update_layout(
        title='Call Option P&L at Expiry',
        xaxis_title='Spot Price at Expiry ($)',
        yaxis_title='Profit / Loss ($)',
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        yaxis=dict(rangemode='tozero') # Start y-axis at 0
    )

    st.plotly_chart(fig_call_pnl_line_tab1, use_container_width=True)


    # Put P&L Plot
    fig_put_pnl_line_tab1 = go.Figure()
    fig_put_pnl_line_tab1.add_trace(go.Scatter(x=S_grid_tab1, y=put_pnl_line_long_tab1, mode='lines', name='Long Put', line=dict(color='green', width=2)))
    fig_put_pnl_line_tab1.add_trace(go.Scatter(x=S_grid_tab1, y=put_pnl_line_short_tab1, mode='lines', name='Short Put', line=dict(color='red', width=2)))

    # Add breakeven point(s) for Long Put
    # Breakeven for Put is S_expiry = K - Premium
    put_breakeven_tab1 = K - put_price_single
    if S_grid_tab1.min() <= put_breakeven_tab1 <= S_grid_tab1.max():
        fig_put_pnl_line_tab1.add_vline(x=put_breakeven_tab1, line_dash="dash", line_color="grey", annotation_text=f"Put Breakeven: ${put_breakeven_tab1:.2f}", annotation_position="top right", annotation_font_size=10)


    # Add horizontal line at 0 P&L
    fig_put_pnl_line_tab1.add_shape(type="line", x0=S_grid_tab1.min(), y0=0, x1=S_grid_tab1.max(), y1=0, line=dict(color="gray", width=1, dash="dash"))

    fig_put_pnl_line_tab1.update_layout(
        title='Put Option P&L at Expiry',
        xaxis_title='Spot Price at Expiry ($)',
        yaxis_title='Profit / Loss ($)',
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        yaxis=dict(rangemode='tozero')
    )

    st.plotly_chart(fig_put_pnl_line_tab1, use_container_width=True)


# --- Tab 2: Position P&L Tracker (Before Expiry) ---
with tab2:
    st.header("Track Option Position P&L Before Expiry")
    st.write("Enter your option purchase parameters and current market parameters to see the P&L.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("1. Purchase Parameters")
        # Pre-fill with values from Tab 1 sidebar as a starting point
        S_purchase = st.number_input(
            "Spot Price at Purchase ($S_{purchase}$)",
            min_value=0.0,
            value=st.session_state.get("spot_price_tab1", default_S),
            step=_step(st.session_state.get("spot_price_tab1", default_S)),
            format="%.4f",
            key="S_purchase"
        )
        K_purchase = st.number_input(
            "Strike Price ($K$)",
            min_value=0.0,
            value=st.session_state.get("strike_price_tab1", default_K),
             step=_step(st.session_state.get("strike_price_tab1", default_K)),
            format="%.4f",
            key="K_purchase"
        )
        sigma_pct_purchase = st.number_input(
            "Volatility at Purchase (%)",
            min_value=0.0,
            max_value=200.0,
            value=st.session_state.get("sigma_pct_tab1", 20.0),
            step=0.001,
            format="%.3f",
            key="sigma_pct_purchase"
        )
        sigma_purchase = sigma_pct_purchase / 100.0

        T_weeks_purchase = st.number_input(
            "Time to Expiry at Purchase (weeks)",
            min_value=1,
            max_value=104,
            value=st.session_state.get("T_weeks_tab1", 52),
            step=1,
            key="T_weeks_purchase"
        )
        T_purchase = T_weeks_purchase / 52.0

        r_purchase = st.number_input(
            "Risk-Free Rate at Purchase (%)",
            min_value=0.0,
            max_value=0.2,
            value=st.session_state.get("r_tab1", 0.05),
            step=0.001,
            format="%.3f",
            key="r_purchase"
        )
        r_purchase /= 100.0 # Convert percentage

    with col2:
        st.subheader("2. Current / Evaluation Parameters")
        S_current = st.number_input(
            "Current Spot Price ($S_{current}$)",
            min_value=0.0,
            value=S_purchase, # Default to purchase spot
            step=_step(S_purchase),
            format="%.4f",
            key="S_current"
        )
        sigma_pct_current = st.number_input(
            "Current Volatility (%)",
            min_value=0.0,
            max_value=200.0,
            value=sigma_pct_purchase, # Default to purchase vol
            step=0.001,
            format="%.3f",
            key="sigma_pct_current"
        )
        sigma_current = sigma_pct_current / 100.0

        time_elapsed_weeks = st.number_input(
             "Time Elapsed (weeks)",
             min_value=0,
             max_value=T_weeks_purchase, # Cannot elapsed more than total time
             value=0,
             step=1,
             key="time_elapsed_weeks"
        )
        T_remaining_weeks = T_weeks_purchase - time_elapsed_weeks
        T_remaining = T_remaining_weeks / 52.0


    st.markdown("---")

    # --- Calculate Initial Premium (based on Purchase Parameters) ---
    initial_call_premium = 0.0
    initial_put_premium = 0.0

    if T_purchase > 0 and S_purchase > 0:
        if sigma_purchase > 1e-9:
            bs_purchase = BlackScholes(T_purchase, K_purchase, S_purchase, sigma_purchase, r_purchase)
            initial_call_premium, initial_put_premium = bs_purchase.calculate_prices()
        else:
             # Handle zero initial volatility
             future_S_purchase = S_purchase * np.exp(r_purchase * T_purchase)
             initial_call_premium = max(future_S_purchase - K_purchase, 0.0) * np.exp(-r_purchase * T_purchase)
             initial_put_premium = max(K_purchase - future_S_purchase, 0.0) * np.exp(-r_purchase * T_purchase)

    st.subheader("Initial Premium (Based on Purchase Parameters)")
    st.write(f"Call Premium Paid/Received: **${initial_call_premium:.4f}**")
    st.write(f"Put Premium Paid/Received: **${initial_put_premium:.4f}**")

    st.markdown("---")
    st.subheader("P&L Before Expiry")
    st.write(f"Time Remaining: **{T_remaining_weeks:.0f} weeks** ({T_remaining:.2f} years)")

    # --- Position Selection ---
    selected_positions = st.multiselect(
        "Select Positions to Track:",
        ["Long Call", "Short Call", "Long Put", "Short Put"],
        default=["Long Call", "Short Call", "Long Put", "Short Put"] # Default to show all
    )

    # --- Numerical P&L Readout (Based on exact Current Parameters) ---
    st.subheader("P&L for Current Parameters")

    current_value_call = 0.0
    current_value_put = 0.0

    # Calculate current option value based on Current Parameters
    if T_remaining_weeks <= 0: # At or past expiry
         current_value_call = max(S_current - K_purchase, 0.0)
         current_value_put = max(K_purchase - S_current, 0.0)
         st.info("Time Remaining is 0 or less. Showing P&L at Expiry based on Current Spot Price.")
    elif sigma_current <= 1e-9: # Zero current volatility before expiry
         future_S_current = S_current * np.exp(r_purchase * T_remaining)
         current_value_call = max(future_S_current - K_purchase, 0.0) * np.exp(-r_purchase * T_remaining)
         current_value_put = max(K_purchase - future_S_current, 0.0) * np.exp(-r_purchase * T_remaining)
         st.info("Current Volatility is 0. Showing discounted deterministic payoff.")
    else:
         # Standard BS calculation for current value
         bs_current = BlackScholes(T_remaining, K_purchase, S_current, sigma_current, r_purchase)
         current_value_call, current_value_put = bs_current.calculate_prices()

    # Calculate P&L based on current values and initial premium
    current_pnl_long_call = current_value_call - initial_call_premium
    current_pnl_short_call = initial_call_premium - current_value_call
    current_pnl_long_put = current_value_put - initial_put_premium
    current_pnl_short_put = initial_put_premium - current_value_put

    pnl_readouts = {
        "Long Call": current_pnl_long_call,
        "Short Call": current_pnl_short_call,
        "Long Put": current_pnl_long_put,
        "Short Put": current_pnl_short_put,
    }

    for position in selected_positions:
        pnl_value = pnl_readouts[position]
        color = "green" if pnl_value >= 0 else "red"
        st.write(f"{position} P&L: <b style='color:{color}'>${pnl_value:.4f}</b>", unsafe_allow_html=True)


    st.markdown("---")
    st.subheader("P&L Heatmap (vs. Current Spot & Vol, Time Remaining Fixed)")
    st.write(f"Heatmap shows P&L for selected positions at **{T_remaining_weeks:.0f} weeks** to expiry, varying Current Spot and Current Volatility.")

    # --- Heatmap Ranges (Tab 2) ---
    st.sidebar.header("Heatmap Ranges (Tab 2)")
    spot_range_slider_tab2 = st.sidebar.slider(
        "Current Spot Price Range ($) for Heatmap", # For y-axis of heatmap
        min_value=0.0,
        max_value=max(2 * S_current, 200.0),
        value=(max(0.0, 0.5 * S_current), 1.5 * S_current),
        step=_step(S_current),
        format="%.4f",
        key="spot_range_tab2"
    )

    vol_range_pct_slider_tab2 = st.sidebar.slider(
        "Current Volatility Range (%) for Heatmap", # For x-axis of heatmap
        min_value=0.0,
        max_value=200.0,
        value=(max(0.0, sigma_pct_current * 0.5), min(200.0, sigma_pct_current * 1.5)),
        step=0.1,
        format="%.1f",
        key="vol_range_tab2"
    )
    vol_range_heatmap_tab2 = (vol_range_pct_slider_tab2[0] / 100.0, vol_range_pct_slider_tab2[1] / 100.0)

    # Grids for Tab 2 Heatmap
    S_current_grid_tab2 = np.linspace(spot_range_slider_tab2[0], spot_range_slider_tab2[1], 50)
    if vol_range_heatmap_tab2[0] == vol_range_heatmap_tab2[1]:
         vol_current_grid_tab2 = np.array([vol_range_heatmap_tab2[0]])
         vol_current_grid_pct_tab2 = vol_current_grid_tab2 * 100
    else:
         vol_current_grid_tab2 = np.linspace(vol_range_heatmap_tab2[0], vol_range_heatmap_tab2[1], 50)
         vol_current_grid_pct_tab2 = vol_current_grid_tab2 * 100


    # --- Data Calculation for P&L Heatmap (Tab 2) ---
    pnl_heatmap_grid_tab2 = {
        "Long Call": np.zeros((len(S_current_grid_tab2), len(vol_current_grid_tab2))),
        "Short Call": np.zeros((len(S_current_grid_tab2), len(vol_current_grid_tab2))),
        "Long Put": np.zeros((len(S_current_grid_tab2), len(vol_current_grid_tab2))),
        "Short Put": np.zeros((len(S_current_grid_tab2), len(vol_current_grid_tab2))),
    }

    # Use the fixed T_remaining and r_purchase from inputs for this heatmap
    # Vary S_current_grid_tab2 and vol_current_grid_tab2
    for i, s_eval in enumerate(S_current_grid_tab2):
        for j, v_eval in enumerate(vol_current_grid_tab2):
            # Calculate current value at this grid point (s_eval, v_eval) and T_remaining
            if T_remaining_weeks <= 0: # At or past expiry
                 value_call_eval = max(s_eval - K_purchase, 0.0)
                 value_put_eval = max(K_purchase - s_eval, 0.0)
            elif v_eval <= 1e-9: # Zero current volatility before expiry
                 future_s_eval = s_eval * np.exp(r_purchase * T_remaining)
                 value_call_eval = max(future_s_eval - K_purchase, 0.0) * np.exp(-r_purchase * T_remaining)
                 value_put_eval = max(K_purchase - future_s_eval, 0.0) * np.exp(-r_purchase * T_remaining)
            else:
                 # Standard BS calculation for evaluation point
                 bs_eval = BlackScholes(T_remaining, K_purchase, s_eval, v_eval, r_purchase)
                 value_call_eval, value_put_eval = bs_eval.calculate_prices()

            # Calculate P&L for this grid point
            pnl_heatmap_grid_tab2["Long Call"][i, j] = value_call_eval - initial_call_premium
            pnl_heatmap_grid_tab2["Short Call"][i, j] = initial_call_premium - value_call_eval
            pnl_heatmap_grid_tab2["Long Put"][i, j] = value_put_eval - initial_put_premium
            pnl_heatmap_grid_tab2["Short Put"][i, j] = initial_put_premium - value_put_eval

    # --- Plotting P&L Heatmap (Tab 2) ---
    if selected_positions:
        num_selected = len(selected_positions)
        # Arrange subplots dynamically (e.g., 2x2 if 4 selected, 1x2 if 2 selected, etc.)
        rows_tab2 = (num_selected + 1) // 2 if num_selected > 0 else 1
        cols_tab2 = 2 if num_selected > 1 else 1

        fig_heatmap_tab2 = make_subplots(
            rows=rows_tab2,
            cols=cols_tab2,
            subplot_titles=[f"{pos} P&L" for pos in selected_positions],
            horizontal_spacing=0.1,
            vertical_spacing=0.2,
        )

        for i, position in enumerate(selected_positions):
            row = (i // 2) + 1
            col = (i % 2) + 1
            fig_heatmap_tab2.add_trace(
                go.Heatmap(
                    x=vol_current_grid_pct_tab2,
                    y=S_current_grid_tab2,
                    z=pnl_heatmap_grid_tab2[position],
                    colorscale="RdYlGn",
                    zmid=0,
                    colorbar=dict(title="P&L ($)")
                ),
                row=row, col=col
            )
            fig_heatmap_tab2.update_xaxes(title_text="Current Volatility (%)", row=row, col=col)
            fig_heatmap_tab2.update_yaxes(title_text="Current Spot Price ($)", row=row, col=col)


        fig_heatmap_tab2.update_layout(
            height=400 * rows_tab2, # Adjust height based on number of rows
            title_text=f"P&L Heatmap at {T_remaining_weeks:.0f} Weeks Remaining",
            title_x=0.5,
             margin=dict(t=100),
             hovermode='closest'
        )
        st.plotly_chart(fig_heatmap_tab2, use_container_width=True)
    else:
        st.info("Select at least one position to display the heatmap.")