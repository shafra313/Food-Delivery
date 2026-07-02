"""
Food Delivery Sales & Customer Insights
Analyze order data, identify peak times, popular dishes, and build a dashboard.
Tools: Pandas, Filtering, Matplotlib
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

DATA_FILE = Path(__file__).parent / "food_delivery_orders.csv"
OUTPUT_DIR = Path(__file__).parent / "output"


def load_and_prepare_data(filepath: Path) -> pd.DataFrame:
    """Load CSV and enrich with datetime and revenue columns."""
    df = pd.read_csv(filepath)
    df["order_datetime"] = pd.to_datetime(
        df["order_date"] + " " + df["order_time"], format="%Y-%m-%d %H:%M"
    )
    df["hour"] = df["order_datetime"].dt.hour
    df["day_of_week"] = df["order_datetime"].dt.day_name()
    df["revenue"] = df["quantity"] * df["price"]
    return df


def filter_orders(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Demonstrate Pandas filtering for targeted business segments."""
    return {
        "downtown_orders": df[df["location"] == "Downtown"],
        "lunch_rush": df[(df["hour"] >= 12) & (df["hour"] < 14)],
        "dinner_peak": df[(df["hour"] >= 18) & (df["hour"] < 21)],
        "high_value": df[df["revenue"] >= 30],
        "repeat_customers": df[df["customer_id"].duplicated(keep=False)],
    }


def peak_order_times(df: pd.DataFrame) -> pd.Series:
    """Count orders per hour to find peak ordering windows."""
    return df.groupby("hour").size().sort_values(ascending=False)


def popular_dishes(df: pd.DataFrame) -> pd.DataFrame:
    """Rank dishes by total quantity sold and revenue."""
    return (
        df.groupby("item")
        .agg(orders=("order_id", "count"), quantity_sold=("quantity", "sum"), revenue=("revenue", "sum"))
        .sort_values("quantity_sold", ascending=False)
    )


def location_insights(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize orders and revenue by delivery location."""
    return (
        df.groupby("location")
        .agg(orders=("order_id", "count"), revenue=("revenue", "sum"))
        .sort_values("revenue", ascending=False)
    )


def print_insights(df: pd.DataFrame, peak_hours: pd.Series, dishes: pd.DataFrame, locations: pd.DataFrame) -> None:
    """Print key business insights to the console."""
    filters = filter_orders(df)

    print("=" * 60)
    print("FOOD DELIVERY SALES & CUSTOMER INSIGHTS")
    print("=" * 60)

    print(f"\nTotal Orders: {len(df)}")
    print(f"Total Revenue: ${df['revenue'].sum():,.2f}")
    print(f"Unique Customers: {df['customer_id'].nunique()}")
    print(f"Date Range: {df['order_date'].min()} to {df['order_date'].max()}")

    print("\n--- Peak Order Times (by hour) ---")
    for hour, count in peak_hours.head(3).items():
        period = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        print(f"  {display_hour}:00 {period} -> {count} orders")

    print("\n--- Most Popular Dishes ---")
    for item, row in dishes.head(5).iterrows():
        print(f"  {item}: {int(row['quantity_sold'])} units | ${row['revenue']:,.2f} revenue")

    print("\n--- Orders by Location ---")
    for loc, row in locations.iterrows():
        print(f"  {loc}: {int(row['orders'])} orders | ${row['revenue']:,.2f} revenue")

    print("\n--- Filtered Segments (Pandas Filtering) ---")
    print(f"  Downtown orders: {len(filters['downtown_orders'])}")
    print(f"  Lunch rush (12-2 PM): {len(filters['lunch_rush'])}")
    print(f"  Dinner peak (6-9 PM): {len(filters['dinner_peak'])}")
    print(f"  High-value orders (>= $30): {len(filters['high_value'])}")
    print(f"  Repeat customer orders: {len(filters['repeat_customers'])}")
    print("=" * 60)


def create_dashboard(
    df: pd.DataFrame,
    peak_hours: pd.Series,
    dishes: pd.DataFrame,
    locations: pd.DataFrame,
    output_path: Path,
) -> None:
    """Build a multi-panel Matplotlib dashboard for business insights."""
    plt.style.use("seaborn-v0_8-whitegrid")
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle(
        "Food Delivery Sales & Customer Insights Dashboard",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    # 1. Peak order times (hourly bar chart)
    ax1 = fig.add_subplot(2, 2, 1)
    hourly = df.groupby("hour").size()
    colors = ["#e74c3c" if h in peak_hours.head(3).index else "#3498db" for h in hourly.index]
    ax1.bar(hourly.index, hourly.values, color=colors, edgecolor="white")
    ax1.set_xlabel("Hour of Day")
    ax1.set_ylabel("Number of Orders")
    ax1.set_title("Orders by Hour (Peak Times Highlighted)")
    ax1.set_xticks(range(0, 24, 2))

    # 2. Most popular dishes (horizontal bar)
    ax2 = fig.add_subplot(2, 2, 2)
    top_dishes = dishes.head(5)
    ax2.barh(top_dishes.index, top_dishes["quantity_sold"], color="#2ecc71", edgecolor="white")
    ax2.set_xlabel("Quantity Sold")
    ax2.set_title("Top 5 Most Popular Dishes")
    ax2.invert_yaxis()

    # 3. Revenue by location (pie chart)
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.pie(
        locations["revenue"],
        labels=locations.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=["#9b59b6", "#f39c12", "#1abc9c"],
    )
    ax3.set_title("Revenue Share by Location")

    # 4. Daily order trend (line chart)
    ax4 = fig.add_subplot(2, 2, 4)
    daily = df.groupby("order_date").agg(orders=("order_id", "count"), revenue=("revenue", "sum"))
    ax4.plot(daily.index, daily["orders"], marker="o", color="#e67e22", linewidth=2, label="Orders")
    ax4.set_xlabel("Date")
    ax4.set_ylabel("Orders")
    ax4.set_title("Daily Order Trend")
    ax4.tick_params(axis="x", rotation=45)

    ax4_twin = ax4.twinx()
    ax4_twin.plot(daily.index, daily["revenue"], marker="s", color="#2980b9", linewidth=2, linestyle="--", label="Revenue")
    ax4_twin.set_ylabel("Revenue ($)")
    ax4.legend(loc="upper left")
    ax4_twin.legend(loc="upper right")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nDashboard saved to: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = load_and_prepare_data(DATA_FILE)
    peak_hours = peak_order_times(df)
    dishes = popular_dishes(df)
    locations = location_insights(df)

    print_insights(df, peak_hours, dishes, locations)
    create_dashboard(df, peak_hours, dishes, locations, OUTPUT_DIR / "dashboard.png")


if __name__ == "__main__":
    main()
