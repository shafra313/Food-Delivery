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
    """Apply Pandas filters for location, item, and time window."""
    mask = (
        df["location"].isin(locations)
        & df["item"].isin(items)
        & (df["hour"] >= start_hour)
        & (df["hour"] <= end_hour)
    )
    return df[mask].copy()


def format_hour(hour: int) -> str:
    return HOUR_LABELS.get(hour, f"{hour}:00")


def render_charts(filtered: pd.DataFrame) -> None:
    """Display three Matplotlib charts for filtered order data."""
    if filtered.empty:
        st.warning("No orders found for the selected filters. Try different options.")
        return

    st.success(f"Showing **{len(filtered)}** orders | Revenue: **₹{filtered['revenue'].sum():,.0f}**")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    fig.suptitle("Food Delivery Insights", fontsize=14, fontweight="bold")

    # Chart 1: Orders by time (hour)
    hourly = filtered.groupby("hour").size().reindex(range(10, 24), fill_value=0)
    axes[0].bar(
        [format_hour(h) for h in hourly.index],
        hourly.values,
        color="#3498db",
        edgecolor="white",
    )
    axes[0].set_title("Orders by Time")
    axes[0].set_xlabel("Hour")
    axes[0].set_ylabel("Orders")
    axes[0].tick_params(axis="x", rotation=45)

    # Chart 2: Popular items
    item_counts = filtered.groupby("item")["quantity"].sum().sort_values(ascending=True)
    axes[1].barh(item_counts.index, item_counts.values, color="#2ecc71", edgecolor="white")
    axes[1].set_title("Popular Items")
    axes[1].set_xlabel("Quantity Sold")

    # Chart 3: Orders by location
    loc_counts = filtered.groupby("location").size().sort_values(ascending=False)
    colors = ["#9b59b6", "#e67e22", "#1abc9c", "#e74c3c", "#f39c12"]
    axes[2].pie(
        loc_counts.values,
        labels=loc_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors[: len(loc_counts)],
    )
    axes[2].set_title("Orders by Location")

    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Summary table
    st.subheader("Order Details")
    display_df = filtered[["order_date", "order_time", "location", "item", "quantity", "revenue"]].copy()
    display_df.columns = ["Date", "Time", "Location", "Item", "Qty", "Revenue (₹)"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="Food Delivery Dashboard", page_icon="🍽️", layout="wide")
    st.title("🍽️ Food Delivery Sales Dashboard")
    st.caption("Analyze order data by **time**, **location**, and **item**")

    df = load_data()

    with st.form("filter_form"):
        st.subheader("Select Filters")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📍 Location**")
            selected_locations = st.multiselect(
                "Choose locations",
                options=LOCATIONS,
                default=LOCATIONS,
                label_visibility="collapsed",
            )

        with col2:
            st.markdown("**🍛 Item**")
            selected_items = st.multiselect(
                "Choose items",
                options=ITEMS,
                default=ITEMS,
                label_visibility="collapsed",
            )

        with col3:
            st.markdown("**🕐 Time (10 AM – 11 PM)**")
            time_col_a, time_col_b = st.columns(2)
            with time_col_a:
                start_hour = st.selectbox(
                    "From",
                    options=list(range(10, 24)),
                    index=0,
                    format_func=format_hour,
                )
            with time_col_b:
                end_hour = st.selectbox(
                    "To",
                    options=list(range(10, 24)),
                    index=13,
                    format_func=format_hour,
                )

        submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)

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
        st.divider()
        render_charts(filtered)
    else:
        st.info("Select filters in the three columns above, then click **Submit** to view charts.")


if __name__ == "__main__":
    main()
