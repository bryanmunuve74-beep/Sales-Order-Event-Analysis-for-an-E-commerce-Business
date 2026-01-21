import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/full2.csv")
pd.set_option('display.max_columns', None)

# Data cleaning
df['Order Date'] = pd.to_datetime(df['Order Date'], errors='coerce')
df['Discount'] = df['Discount'].fillna(0)
stage_order = ['Checkout', 'Purchase', 'Add_to_cart']
df['event_type'] = pd.Categorical(df['event_type'], categories=stage_order, ordered=True)
df = df[(df['Final Price'] > 0) & (df['Discount'] < 1)]

# Funnel size and conversion analysis
funnel_counts = df.groupby('event_type')['customer_id'].nunique().sort_index()
conversion_rates = funnel_counts / funnel_counts.shift(1)

# Revenue leakage analysis
df['expected_price'] = df['List Price']
df['revenue_loss'] = df['expected_price'] - df['Final Price']
leakage_by_rep = df.groupby('sales_rep')['revenue_loss'].sum().sort_values(ascending=False)

# Deal delay analysis
df['Expected Delivery Date'] = pd.to_datetime(df['Expected Delivery Date'], errors='coerce')
df = df.sort_values(['customer_id', 'Order Date'])
df['delay_days'] = (df['Expected Delivery Date'] - df['Order Date']).dt.days
avg_delay = df.groupby('event_type')['delay_days'].mean()

# Discount optimization
threshold = np.percentile(df['Discount'], 90)
df['high_discount_flag'] = np.where(df['Discount'] > threshold, 1, 0)
high_discount_impact = df[df['high_discount_flag'] == 1]['revenue_loss'].sum()

# Revenue recovery simulation
df['optimized_price'] = df['expected_price'] * 1.05
df['recovered_revenue'] = (df['optimized_price'] - df['Final Price']).clip(lower=0)
recovered_total = df['recovered_revenue'].sum()
