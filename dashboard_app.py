"""
Interactive Food Delivery Dashboard
Three-column filters: Location | Item | Time (10 AM - 11 PM)
Submit button shows charts using Pandas filtering and Matplotlib.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

DATA_FILE = Path(__file__).parent / "food_delivery_orders.csv"

LOCATIONS = ["Theppakulam", "Ring Road", "Anna Nagar", "KK Nagar", "Pudur"]
ITEMS = ["Dosa", "Fried Rice", "Noodles", "Poori", "Shawarma", "Grill"]
HOUR_LABELS = {
    10: "10 AM", 11: "11 AM", 12: "12 PM", 13: "1 PM", 14: "2 PM",
    15: "3 PM", 16: "4 PM", 17: "5 PM", 18: "6 PM", 19: "7 PM",
    20: "8 PM", 21: "9 PM", 22: "10 PM", 23: "11 PM",
}


def apply_custom_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
        }

        .block-container {
            padding-top: 1.5rem;
            max-width: 1200px;
        }

        .hero-banner {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 50%, #ff9f43 100%);
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0 8px 24px rgba(255, 107, 53, 0.25);
        }

        .hero-title {
            color: #ffffff;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 8px 0;
            letter-spacing: -0.5px;
        }

        .hero-subtitle {
            color: rgba(255, 255, 255, 0.92);
            font-size: 1rem;
            margin: 0;
            font-weight: 400;
        }

        .filter-card {
            background: #ffffff;
            border: 1px solid #e8ecf1;
            border-radius: 14px;
            padding: 20px 18px 10px 18px;
            margin-bottom: 8px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
            min-height: 140px;
        }

        .filter-label {
            font-size: 0.95rem;
            font-weight: 600;
            color: #2d3436;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .filter-icon {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1rem;
        }

        .icon-location { background: #fff0eb; }
        .icon-item { background: #eafaf1; }
        .icon-time { background: #ebf5ff; }

        .hint-card {
            background: linear-gradient(135deg, #f8f9fc 0%, #eef2f7 100%);
            border: 1px dashed #c8d0dc;
            border-radius: 14px;
            padding: 22px 28px;
            text-align: center;
            margin-top: 20px;
        }

        .hint-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2d3436;
            margin: 0 0 6px 0;
        }

        .hint-text {
            color: #636e72;
            font-size: 0.95rem;
            margin: 0;
        }

        .hint-steps {
            display: flex;
            justify-content: center;
            gap: 24px;
            margin-top: 16px;
            flex-wrap: wrap;
        }

        .hint-step {
            background: white;
            border-radius: 10px;
            padding: 10px 18px;
            font-size: 0.85rem;
            color: #636e72;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .hint-step strong {
            color: #ff6b35;
        }

        .result-badge {
            background: linear-gradient(135deg, #00b894, #00cec9);
            color: white;
            border-radius: 12px;
            padding: 14px 22px;
            font-size: 1rem;
            font-weight: 500;
            margin-bottom: 20px;
            box-shadow: 0 4px 14px rgba(0, 184, 148, 0.3);
        }

        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, #ff6b35, #f7931e) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            font-size: 1rem !important;
            padding: 0.6rem 1.5rem !important;
            box-shadow: 0 4px 14px rgba(255, 107, 53, 0.35) !important;
            transition: transform 0.15s ease !important;
        }

        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(255, 107, 53, 0.45) !important;
        }

        .section-title {
            font-size: 1.15rem;
            font-weight: 600;
            color: #2d3436;
            margin: 0 0 16px 0;
            padding-left: 4px;
        }

        #MainMenu, footer, header { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)
    df["order_datetime"] = pd.to_datetime(
        df["order_date"] + " " + df["order_time"], format="%Y-%m-%d %H:%M"
    )
    df["hour"] = df["order_datetime"].dt.hour
    df["revenue"] = df["quantity"] * df["price"]
    return df


def filter_orders(
    df: pd.DataFrame,
    locations: list[str],
    items: list[str],
    start_hour: int,
    end_hour: int,
) -> pd.DataFrame:
    mask = (
        df["location"].isin(locations)
        & df["item"].isin(items)
        & (df["hour"] >= start_hour)
        & (df["hour"] <= end_hour)
    )
    return df[mask].copy()


def format_hour(hour: int) -> str:
    return HOUR_LABELS.get(hour, f"{hour}:00")


def render_welcome_hint() -> None:
    st.markdown(
        """
        <div class="hint-card">
            <p class="hint-title">👋 Ready to explore your sales data</p>
            <p class="hint-text">Pick your filters below and click <strong>Submit</strong> to generate charts.</p>
            <div class="hint-steps">
                <span class="hint-step"><strong>1.</strong> Choose locations</span>
                <span class="hint-step"><strong>2.</strong> Select food items</span>
                <span class="hint-step"><strong>3.</strong> Set time range</span>
                <span class="hint-step"><strong>4.</strong> Hit Submit</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_charts(filtered: pd.DataFrame) -> None:
    if filtered.empty:
        st.warning("No orders found for the selected filters. Try different options.")
        return

    total_orders = len(filtered)
    total_revenue = filtered["revenue"].sum()
    st.markdown(
        f'<div class="result-badge">📊 Showing <b>{total_orders}</b> orders &nbsp;|&nbsp; Revenue: <b>₹{total_revenue:,.0f}</b></div>',
        unsafe_allow_html=True,
    )

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    fig.patch.set_facecolor("#fafbfc")
    fig.suptitle("Food Delivery Insights", fontsize=15, fontweight="bold", color="#2d3436", y=1.02)

    hourly = filtered.groupby("hour").size().reindex(range(10, 24), fill_value=0)
    bar_colors = ["#ff6b35" if v == hourly.max() and v > 0 else "#74b9ff" for v in hourly.values]
    axes[0].bar([format_hour(h) for h in hourly.index], hourly.values, color=bar_colors, edgecolor="white", linewidth=0.8)
    axes[0].set_title("Orders by Time", fontweight="600", color="#2d3436")
    axes[0].set_xlabel("Hour", color="#636e72")
    axes[0].set_ylabel("Orders", color="#636e72")
    axes[0].tick_params(axis="x", rotation=45, labelsize=8)
    axes[0].set_facecolor("#fafbfc")

    item_counts = filtered.groupby("item")["quantity"].sum().sort_values(ascending=True)
    axes[1].barh(item_counts.index, item_counts.values, color="#00b894", edgecolor="white", linewidth=0.8)
    axes[1].set_title("Popular Items", fontweight="600", color="#2d3436")
    axes[1].set_xlabel("Quantity Sold", color="#636e72")
    axes[1].set_facecolor("#fafbfc")

    loc_counts = filtered.groupby("location").size().sort_values(ascending=False)
    pie_colors = ["#ff6b35", "#f7931e", "#00b894", "#74b9ff", "#a29bfe"]
    axes[2].pie(
        loc_counts.values,
        labels=loc_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=pie_colors[: len(loc_counts)],
        textprops={"fontsize": 8},
    )
    axes[2].set_title("Orders by Location", fontweight="600", color="#2d3436")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown('<p class="section-title">📋 Order Details</p>', unsafe_allow_html=True)
    display_df = filtered[["order_date", "order_time", "location", "item", "quantity", "revenue"]].copy()
    display_df.columns = ["Date", "Time", "Location", "Item", "Qty", "Revenue (₹)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Food Delivery Dashboard", page_icon="🍽️", layout="wide")
    apply_custom_styles()

    st.markdown(
        """
        <div class="hero-banner">
            <p class="hero-title">🍽️ Food Delivery Sales Dashboard</p>
            <p class="hero-subtitle">Analyze order patterns by time, location &amp; menu items</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = load_data()

    with st.form("filter_form"):
        st.markdown('<p class="section-title">🔍 Filter Orders</p>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                '<div class="filter-card"><div class="filter-label">'
                '<span class="filter-icon icon-location">📍</span> Location</div>',
                unsafe_allow_html=True,
            )
            selected_locations = st.multiselect(
                "Choose locations",
                options=LOCATIONS,
                default=LOCATIONS,
                label_visibility="collapsed",
                placeholder="Select locations...",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown(
                '<div class="filter-card"><div class="filter-label">'
                '<span class="filter-icon icon-item">🍛</span> Item</div>',
                unsafe_allow_html=True,
            )
            selected_items = st.multiselect(
                "Choose items",
                options=ITEMS,
                default=ITEMS,
                label_visibility="collapsed",
                placeholder="Select items...",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col3:
            st.markdown(
                '<div class="filter-card"><div class="filter-label">'
                '<span class="filter-icon icon-time">🕐</span> Time Window</div>',
                unsafe_allow_html=True,
            )
            time_col_a, time_col_b = st.columns(2)
            with time_col_a:
                start_hour = st.selectbox("From", options=list(range(10, 24)), index=0, format_func=format_hour)
            with time_col_b:
                end_hour = st.selectbox("To", options=list(range(10, 24)), index=13, format_func=format_hour)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("✨  Submit & Show Charts", use_container_width=True)

    if submitted:
        if start_hour > end_hour:
            st.error("Start time must be before or equal to end time.")
            return
        if not selected_locations:
            st.error("Please select at least one location.")
            return
        if not selected_items:
            st.error("Please select at least one item.")
            return

        filtered = filter_orders(df, selected_locations, selected_items, start_hour, end_hour)
        st.markdown("<br>", unsafe_allow_html=True)
        render_charts(filtered)
    else:
        render_welcome_hint()


if __name__ == "__main__":
    main()
