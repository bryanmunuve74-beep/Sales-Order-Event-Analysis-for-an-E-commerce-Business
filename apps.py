import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sales Funnel Executive Dashboard", layout="wide")

st.title("📊 Sales Funnel Executive Dashboard")
st.markdown("Interactive revenue and funnel performance overview")

# Load data
df = pd.read_csv("data/full2.csv")

st.subheader("Preview of Data")
st.dataframe(df.head())

# Funnel Analysis
st.subheader("Funnel Size by Stage")

funnel_counts = (
    df.groupby("event_type")["customer_id"]
    .nunique()
    .sort_index()
)

st.write(funnel_counts)

fig, ax = plt.subplots()
funnel_counts.plot(kind="bar", ax=ax)
ax.set_title("Sales Funnel – Customers per Stage")
ax.set_xlabel("Stage")
ax.set_ylabel("Unique Customers")
st.pyplot(fig)

# Conversion Rates
st.subheader("Conversion Rates Between Stages")
conversion_rates = funnel_counts / funnel_counts.shift(1)
st.write(conversion_rates)

# Revenue Leakage
st.subheader("Revenue Leakage Analysis")

df["expected_price"] = df["List Price"]
df["revenue_loss"] = df["expected_price"] - df["Final Price"]

leakage_by_rep = (
    df.groupby("sales_rep")["revenue_loss"]
    .sum()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots()
leakage_by_rep.plot(kind="bar", ax=ax)
ax.set_title("Revenue Leakage by Sales Rep")
ax.set_xlabel("Sales Rep")
ax.set_ylabel("Revenue Lost")
st.pyplot(fig)

# Lost deals
lost_deals = df[df["deal_status"] == "Lost"]
lost_revenue = lost_deals["Final Price"].sum()
st.metric("Lost Revenue", f"{lost_revenue:.2f}")
