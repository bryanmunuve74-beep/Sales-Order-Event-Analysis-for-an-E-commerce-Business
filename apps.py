import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Sales Funnel Executive Dashboard",
    layout="wide"
)

st.title("📊 Sales Funnel Executive Dashboard")
st.markdown("Interactive revenue and funnel performance overview")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    return pd.read_csv("data/full2.csv")

df = load_data()

st.subheader("✅ Dataset Preview")
st.dataframe(df.head())

# -----------------------------
# CHECK REQUIRED COLUMNS
# -----------------------------
required_cols = [
    "customer_id", "event_type", "List Price", "Final Price",
    "sales_rep", "deal_status", "Discount", "Order Date", "Expected Delivery Date"
]

missing_cols = [c for c in required_cols if c not in df.columns]

if missing_cols:
    st.error(f"❌ Missing columns in your dataset: {missing_cols}")
    st.stop()

# -----------------------------
# 3. SALES FUNNEL ANALYSIS
# -----------------------------
st.subheader("3️⃣ Sales Funnel Analysis")

funnel_counts = (
    df.groupby("event_type")["customer_id"]
    .nunique()
    .sort_values(ascending=False)
)

st.write("### Funnel Size by Stage")
st.write(funnel_counts)

fig, ax = plt.subplots()
funnel_counts.plot(kind="bar", ax=ax)
ax.set_title("Sales Funnel – Customers per Stage")
ax.set_xlabel("Stage")
ax.set_ylabel("Unique Customers")
st.pyplot(fig)

# Conversion Rates
st.write("### Conversion Rates Between Stages")

conversion_rates = funnel_counts / funnel_counts.shift(1)
st.write(conversion_rates)

# -----------------------------
# 4. REVENUE LEAKAGE ANALYSIS
# -----------------------------
st.subheader("4️⃣ Revenue Leakage Analysis")

df["expected_price"] = df["List Price"]
df["revenue_loss"] = df["expected_price"] - df["Final Price"]

# Leakage by sales rep
leakage_by_rep = (
    df.groupby("sales_rep")["revenue_loss"]
    .sum()
    .sort_values(ascending=False)
)

st.write("### Revenue Leakage by Sales Rep")
st.write(leakage_by_rep)

fig, ax = plt.subplots()
leakage_by_rep.plot(kind="bar", ax=ax)
ax.set_title("Revenue Leakage by Sales Rep")
ax.set_xlabel("Sales Rep")
ax.set_ylabel("Revenue Lost")
st.pyplot(fig)

# Lost Revenue from Dropped Deals
st.write("### Lost Revenue from Dropped Deals")

lost_deals = df[df["deal_status"] == "Lost"]
lost_revenue = lost_deals["Final Price"].sum()

st.metric("💸 Lost Revenue", f"{lost_revenue:,.2f}")

# -----------------------------
# 5. DEAL DELAY ANALYSIS
# -----------------------------
st.subheader("5️⃣ Deal Delay Analysis")

df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
df["Expected Delivery Date"] = pd.to_datetime(df["Expected Delivery Date"], errors="coerce")

df["delay_days"] = (df["Expected Delivery Date"] - df["Order Date"]).dt.days

avg_delay = df.groupby("event_type")["delay_days"].mean().sort_values(ascending=False)

st.write("### Average Delay by Funnel Stage (Days)")
st.write(avg_delay)

fig, ax = plt.subplots()
avg_delay.plot(kind="bar", ax=ax)
ax.set_title("Average Delay Between Funnel Stages")
ax.set_xlabel("Funnel Stage")
ax.set_ylabel("Average Delay (Days)")
plt.xticks(rotation=45)
st.pyplot(fig)

# -----------------------------
# 6. OPTIMIZATION SCENARIOS
# -----------------------------
st.subheader("6️⃣ Optimization Scenarios (NumPy-Based)")

# Identify Extreme Discounts
threshold = np.percentile(df["Discount"].dropna(), 90)

df["high_discount_flag"] = np.where(df["Discount"] > threshold, 1, 0)

high_discount_impact = df[df["high_discount_flag"] == 1]["revenue_loss"].sum()

st.write(f"✅ 90th Percentile Discount Threshold: **{threshold:.2f}**")
st.write(f"🔥 High Discount Revenue Impact: **{high_discount_impact:,.2f}**")

discount_summary = df.groupby("high_discount_flag")["revenue_loss"].sum()
discount_summary.index = ["Normal Discounts", "High Discounts"]

fig, ax = plt.subplots()
discount_summary.plot(kind="bar", ax=ax)
ax.set_title("Revenue Loss from High vs Normal Discounts")
ax.set_xlabel("Discount Category")
ax.set_ylabel("Revenue Loss")
plt.xticks(rotation=0)
st.pyplot(fig)

# Revenue Recovery Simulation
st.write("### Revenue Recovery Simulation")

df["optimized_price"] = df["expected_price"] * 1.05
df["recovered_revenue"] = (df["optimized_price"] - df["Final Price"]).clip(lower=0)

recovered_total = df["recovered_revenue"].sum()
st.metric("✅ Total Recovered Revenue (Simulated)", f"{recovered_total:,.2f}")

price_summary = pd.DataFrame({
    "Metric": ["Final Revenue", "Optimized Revenue", "Recovered Revenue"],
    "Amount": [
        df["Final Price"].sum(),
        df["optimized_price"].sum(),
        recovered_total
    ]
})

fig, ax = plt.subplots()
ax.bar(price_summary["Metric"], price_summary["Amount"])
ax.set_title("Revenue Recovery from Pricing Optimization")
ax.set_xlabel("Revenue Type")
ax.set_ylabel("Amount")
st.pyplot(fig)

# -----------------------------
# KPI + CONTROLS SECTION
# -----------------------------
st.subheader("🔑 KPI Scenario Controls")

recovery_slider = st.slider(
    "Adjust Revenue Recovery (%)",
    min_value=0,
    max_value=100,
    value=50
)

simulated_recovery = lost_revenue * (recovery_slider / 100)
simulated_total_revenue = df["Final Price"].sum() + simulated_recovery

st.info(
    f"💡 Simulated Recovered Revenue: **{simulated_recovery:,.2f}** | "
    f"Projected Total Revenue: **{simulated_total_revenue:,.2f}**"
)

# -----------------------------
# EXECUTIVE INSIGHTS
# -----------------------------
st.subheader("🧠 Executive Insights")

st.markdown("""
- Funnel shows where **customers drop off**
- **Discounting reduces profits**, especially extreme discounts
- **Lost deals** create direct revenue loss
- Reducing delays can improve conversion rates
""")

st.success("✅ Recommendation: Improve early-stage follow-ups, reduce heavy discounting, and optimize conversion stages.")
