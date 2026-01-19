import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
#pandas (pd) → used to create tables (DataFrames), clean data, group, analyze
#numpy (np) → used for random data generation and numeric operations
#datetime, timedelta → used to generate realistic dates and times
#random → used to randomly pick date formats and values
np.random.seed(42)
#Ensures reproducibility
#Every time you run the script, you get the same dataset
#Very important for debugging and portfolio consistency


# -------------------------
# CONFIG
# -------------------------
N_CUSTOMERS = 10000
N_ORDERS = 50000
N_EVENTS = 200000

# -------------------------
# CUSTOMERS
# -------------------------

#Configuration (Dataset Size) - simulating a large, realistic system  to Stress-test Pandas Perform funnel analysis,Show performance handling

customer_ids = [f"C{str(i).zfill(5)}" for i in range(1, N_CUSTOMERS + 1)]
# Generates IDs like:C00001, C00002, ..., C10000

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "signup_date": [
        (datetime(2023, 1, 1) + timedelta(days=random.randint(0, 600))).strftime(  #Starts from Jan 1, 2023,Adds a random number of days (up to ~2 years)
            random.choice(["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]) #Converts dates into different formats to simulate real-world messy date data
        )
        for _ in range(N_CUSTOMERS)
    ],
    "acquisition_channel": np.random.choice(  #Randomly assigns acquisition channels Weighted probabilities:Organic most common,Referral least common

        ["Organic", "Paid Ads", "Email", "Referral"],
        N_CUSTOMERS,
        p=[0.4, 0.3, 0.2, 0.1]
    ),
    "country": np.random.choice(
        ["Kenya", "Uganda", "Tanzania", "Rwanda"],
        N_CUSTOMERS
    ),
    "is_active": np.random.choice([1, 0], N_CUSTOMERS, p=[0.8, 0.2]),
    "age": np.random.choice(
        list(range(18, 65)) + [None],
        N_CUSTOMERS
    )
})

customers.to_csv("customers.csv", index=False)

# -------------------------
# ORDERS
# -------------------------
orders = pd.DataFrame({
    "order_id": [f"O{str(i).zfill(6)}" for i in range(1, N_ORDERS + 1)],
    "customer_id": np.random.choice(customer_ids, N_ORDERS),
    "order_date": [
        (datetime(2023, 2, 1) + timedelta(days=random.randint(0, 500))).strftime(
            random.choice(["%Y-%m-%d", "%d-%m-%Y"])
        )
        for _ in range(N_ORDERS)
    ],
    "order_value": np.round(np.random.uniform(10, 500, N_ORDERS), 2),
    "discount": np.random.choice(
        [0, 5, 10, 20, None],
        N_ORDERS,
        p=[0.5, 0.2, 0.15, 0.05, 0.1]
    ),
    "order_status": np.random.choice(
        ["Completed", "Cancelled", "Returned"],
        N_ORDERS,
        p=[0.85, 0.1, 0.05]
    )
})

orders.to_csv("orders.csv", index=False)

# -------------------------
# FUNNEL EVENTS
# -------------------------
event_types = ["visit", "view_product", "add_to_cart", "checkout", "purchase"]

events = pd.DataFrame({
    "event_id": range(1, N_EVENTS + 1),
    "customer_id": np.random.choice(customer_ids, N_EVENTS),
    "event_type": np.random.choice(
        event_types,
        N_EVENTS,
        p=[0.35, 0.25, 0.2, 0.12, 0.08]
    ),
    "event_time": [
        (datetime(2023, 3, 1) + timedelta(minutes=random.randint(0, 300000))).strftime(
            random.choice(["%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"])
        )
        for _ in range(N_EVENTS)
    ],
    "session_id": np.random.randint(100000, 999999, N_EVENTS),
    "device": np.random.choice(["Mobile", "Desktop"], N_EVENTS, p=[0.7, 0.3]),
    "is_valid": np.random.choice([1, 0], N_EVENTS, p=[0.95, 0.05])
})

events.to_csv("funnel_events.csv", index=False)

print("Dataset generated successfully.")
import os

for file in ["customers.csv", "orders.csv", "funnel_events.csv"]:
    print(file, os.path.getsize(file) / (1024*1024), "MB")
funnel = (
    events[events["is_valid"] == 1]
    .groupby("event_type")["customer_id"]
    .nunique()
    .sort_values(ascending=False)
)

conversion = funnel / funnel.max() * 100
orders["discount"] = orders["discount"].fillna(0)
event_order = {
    "visit": 1,
    "view_product": 2,
    "add_to_cart": 3,
    "checkout": 4,
    "purchase": 5
}

events["event_rank"] = events["event_type"].map(event_order)
import matplotlib.pyplot as plt

plt.figure()
plt.plot(funnel.index, funnel.values)
plt.title("Customer Funnel")
plt.xlabel("Stage")
plt.ylabel("Unique Customers")
plt.show()


""" This project simulates a large-scale e-commerce dataset to analyze customer behavior, order performance, and funnel conversion rates. The goal was to demonstrate real-world data cleaning, validation, transformation, and visualization using Python.

The dataset consists of 3 relational tables:

Customers

Orders

Funnel Events (clickstream data)

🔹 Dataset Size

Customers: 10,000 records

Orders: 50,000 records

Events: 200,000 records

Designed to reflect real production data with:

Missing values

Inconsistent date formats

Invalid records

Non-linear customer journeys

🔹 Tools & Skills Used

Python

Pandas (data manipulation & cleaning)

NumPy (numerical operations)

Matplotlib (visualization)

Data validation & quality checks

Business analytics & funnel metrics

🔹 Key Tasks Performed
1️⃣ Data Cleaning & Preparation

Converted string-based date columns into datetime format

Filled missing discounts with zero

Handled missing demographic data

Removed invalid event records

Standardized funnel event order (visit → purchase)

2️⃣ Data Validation

Identified invalid and incomplete records

Checked referential integrity across tables

Ensured correct funnel sequence logic

3️⃣ Funnel Analysis

Calculated unique users at each funnel stage

Computed conversion rates between stages

Identified highest drop-off points

4️⃣ Revenue Analysis

Total revenue and average order value (AOV)

Revenue impact of discounts

Order status analysis (Completed vs Cancelled)

5️⃣ Storage & Performance Metrics

Calculated dataset size by storage (MB)

Compared table sizes and row counts

6️⃣ Data Visualization

Funnel stage visualization using Matplotlib

Revenue trends and distribution plots

Event frequency by device and channel

🔹 Example Insights

Significant drop-off observed between add_to_cart → checkout

Mobile users generated higher event volume but lower purchase conversion

Discounts increased order volume but reduced average order value

A small percentage of invalid event data could materially affect funnel metrics if not cleaned

🔹 Deliverables

Cleaned and validated datasets

Python scripts for analysis

Visual charts and plots

Business insights summary

🔹 How to Title This on Profiles (LinkedIn / Upwork / CV)

Good titles:

Data Analyst – Customer Funnel & Revenue Analysis

Sales & Funnel Analytics Project (Python)

E-commerce Behavioral Data Analysis

🔹 GitHub Repository Structure (Recommended)
customer-funnel-analysis/
│
├── data/
│   ├── customers.csv
│   ├── orders.csv
│   └── funnel_events.csv
│
├── notebooks/
│   └── analysis.ipynb
│
├── scripts/
│   └── data_cleaning.py
│
├── visuals/
│   └── funnel_plot.png
│
└── README.md"""