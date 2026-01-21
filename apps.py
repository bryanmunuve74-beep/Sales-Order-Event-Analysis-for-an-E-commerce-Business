import git
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv(r"D:\sql-course-materials\New folder\full2.csv")
print(df)


# 3. Sales Funnel Analysis
### Funnel Size by Stage 
funnel_counts = ( 
df.groupby('event_type')['customer_id'] 
.nunique() 
.sort_index() 
)
print(funnel_counts) 
### Conversion Rates Between Stages 
conversion_rates = funnel_counts / funnel_counts.shift(1) 
print("Conversion Rates:",conversion_rates)
### Funnel Visualization 
plt.figure() 
funnel_counts.plot(kind='bar') 
plt.title('Sales Funnel – Customers per Stage') 
plt.xlabel('Stage') 
plt.ylabel('Unique Customers') 
plt.tight_layout() 
plt.show() 
# 4. Revenue Leakage Analysis 
### A. Discount Leakage 
# Expected price without discount 
df['expected_price'] = df['List Price']
df['revenue_loss'] = df['expected_price'] - df['Final Price']

# Revenue lost due to discounting 
df['revenue_loss'] = df['expected_price'] - df['Final Price'] 
# Leakage by sales rep 
leakage_by_rep = ( 
df.groupby('sales_rep')['revenue_loss'] 
.sum() 
.sort_values(ascending=False) 
) 
leakage_by_rep 
plt.figure() 
leakage_by_rep.plot(kind='bar') 
plt.title('Revenue Leakage by Sales Rep') 
plt.xlabel('Sales Rep') 
plt.ylabel('Revenue Lost') 
plt.tight_layout() 
plt.show() 
### B. Lost Revenue from Dropped Deals 
lost_deals = df[df['deal_status'] == 'Lost'] 
lost_revenue = lost_deals['Final Price'].sum() 
print("LOST Revenue;",lost_revenue)
## 5. Deal Delay Analysis  
# Calculate delay between stages 
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Expected Delivery Date'] = pd.to_datetime(df['Expected Delivery Date'], errors='coerce')
df = df.sort_values(['customer_id', 'Order Date'])  
df['delay_days'] = (df['Expected Delivery Date'] - df['Order Date']).dt.days 
avg_delay = df.groupby('event_type')['delay_days'].mean() 
print("AVG delay:", avg_delay)
plt.figure()
avg_delay.plot(kind='bar')

plt.title('Average Delay Between Funnel Stages')
plt.xlabel('Funnel Stage')
plt.ylabel('Average Delay (Days)')

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

## 6. NumPy-Based Optimization Scenarios 
### A. Identify Extreme Discounts 
threshold = np.percentile(df['Discount'], 90) 
df['high_discount_flag'] = np.where(df['Discount'] > threshold, 1, 0) 
print("Threshold:", threshold) 
high_discount_impact = df[df['high_discount_flag'] == 1]['revenue_loss'].sum() 
print("High Discount Impact:", high_discount_impact)
# Summarize revenue loss by discount flag
discount_summary = (
    df.groupby('high_discount_flag')['revenue_loss']
      .sum()
)

# Rename index for readability
discount_summary.index = ['Normal Discounts', 'High Discounts']
print("discount_summary:", discount_summary)

plt.figure()
discount_summary.plot(kind='bar')

plt.title('Revenue Loss from High vs Normal Discounts')
plt.xlabel('Discount Category')
plt.ylabel('Revenue Loss')

plt.xticks(rotation=0)
plt.tight_layout()
plt.show()


### B. Revenue Recovery Simulation 
# Simulate optimized pricing (5% improvement) 
df['optimized_price'] = df['expected_price'] * 1.05

df['recovered_revenue'] = ( 
df['optimized_price'] - df['Final Price'] 
).clip(lower=0) 
recovered_total = df['recovered_revenue'].sum() 
print("recovered Total;",recovered_total)

price_summary = pd.DataFrame({
    'Metric': ['Final Revenue', 'Optimized Revenue', 'Recovered Revenue'],
    'Amount': [
        df['Final Price'].sum(),
        df['optimized_price'].sum(),
        df['recovered_revenue'].sum()
    ]
})
print("price_summary:", price_summary)

#Revenue Comparison
plt.figure()
plt.bar(price_summary['Metric'], price_summary['Amount'])

plt.title('Revenue Recovery from Pricing Optimization')
plt.xlabel('Revenue Type')
plt.ylabel('Amount')

plt.tight_layout()
plt.show()
#Recovered Revenue Distribution
plt.figure()
plt.hist(df['recovered_revenue'], bins=20)

plt.title('Distribution of Recovered Revenue per Deal')
plt.xlabel('Recovered Revenue')
plt.ylabel('Number of Deals')

plt.tight_layout()
plt.show()


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
# DATA (from your analysis)
# -----------------------------
funnel_counts = pd.Series(
    [2, 6, 12],
    index=["Add to Cart", "Checkout", "Purchase"]
)

conversion_rates = pd.Series(
    [np.nan, 3.0, 2.0],
    index=["Add to Cart", "Checkout", "Purchase"]
)

avg_delay = pd.Series(
    [36.0, 30.17, 24.08],
    index=["Add to Cart", "Checkout", "Purchase"]
)

discount_summary = pd.Series(
    [425, 155],
    index=["Normal Discounts", "High Discounts"]
)

price_summary = pd.DataFrame({
    "Metric": ["Final Revenue", "Optimized Revenue", "Recovered Revenue"],
    "Amount": [4755.00, 5601.75, 846.75]
})

lost_revenue = 1140
recovered_revenue = 846.75

# -----------------------------
# KPI SECTION
# -----------------------------
st.subheader("🔑 Key Business KPIs")

col1, col2, col3 = st.columns(3)

col1.metric("Lost Revenue", f"{lost_revenue}")
col2.metric("Recovered Revenue", f"{recovered_revenue}")
col3.metric(
    "Recovery Rate",
    f"{(recovered_revenue / lost_revenue) * 100:.1f}%"
)

st.divider()

# -----------------------------
# INTERACTIVE CONTROLS
# -----------------------------
st.subheader("🎛 Scenario Controls")

recovery_slider = st.slider(
    "Adjust Revenue Recovery (%)",
    min_value=0,
    max_value=100,
    value=74
)

simulated_recovery = lost_revenue * (recovery_slider / 100)
simulated_total_revenue = price_summary.loc[
    price_summary["Metric"] == "Final Revenue", "Amount"
].values[0] + simulated_recovery

st.info(
    f"💡 Simulated Recovered Revenue: {simulated_recovery:.2f} | "
    f"Projected Total Revenue: {simulated_total_revenue:.2f}"
)

st.divider()

# -----------------------------
# CHARTS
# -----------------------------
colA, colB = st.columns(2)

# Funnel Volume
with colA:
    st.subheader("Funnel Volume by Stage")
    fig, ax = plt.subplots()
    funnel_counts.plot(kind="bar", ax=ax)
    ax.set_ylabel("Customers")
    st.pyplot(fig)

# Conversion Rates
with colB:
    st.subheader("Conversion Rates")
    fig, ax = plt.subplots()
    conversion_rates.plot(kind="bar", ax=ax)
    ax.set_ylabel("Rate")
    st.pyplot(fig)

colC, colD = st.columns(2)

# Average Delay
with colC:
    st.subheader("Average Delay (Days)")
    fig, ax = plt.subplots()
    avg_delay.plot(kind="bar", ax=ax)
    ax.set_ylabel("Days")
    st.pyplot(fig)

# Discount Impact
with colD:
    st.subheader("Revenue Loss by Discount Type")
    fig, ax = plt.subplots()
    discount_summary.plot(kind="bar", ax=ax)
    ax.set_ylabel("Revenue Loss")
    st.pyplot(fig)

# Revenue Performance
st.subheader("💰 Revenue Performance")
fig, ax = plt.subplots()
ax.bar(price_summary["Metric"], price_summary["Amount"])
ax.set_ylabel("Amount")
st.pyplot(fig)

# -----------------------------
# EXECUTIVE INSIGHTS
# -----------------------------
st.subheader("🧠 Executive Insights")

st.markdown("""
- Funnel shows **data inconsistency** (more purchases than add-to-carts)
- **Early-stage delays** are highest and reduce conversion
- **High discounts** contribute disproportionately to revenue leakage
- **Up to 74% of lost revenue** is realistically recoverable
""")

st.success("✅ Recommendation: Improve event tracking, reduce high discounts, and accelerate early-stage follow-ups.")