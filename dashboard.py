import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_monthly_orders_df(df):
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    monthly_orders_df = df.resample(rule='4M', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price_less_freight": "sum"
    })
    monthly_orders_df.index = monthly_orders_df.index.strftime('%Y-%m')

    monthly_orders_df = monthly_orders_df.reset_index()
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "price_less_freight": "revenue"
    }, inplace=True)

    return monthly_orders_df

def create_bystate_df(df):
    bystate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    return bystate_df

def create_product_category_sales_df(df):
    product_category_sales_df = df.groupby('product_category_name_english')['order_id'].count().sort_values(ascending=False)
    return product_category_sales_df

def create_review_count_df(df):
    review_counts_df = df['review_score'].value_counts().sort_values(ascending=False)
    return review_counts_df

def create_rfm_df(df):
    rfm_df = df.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (df['order_purchase_timestamp'].max() - x.max()).days,  # Recency
        'order_id': 'count',  # Frequency
        'price_less_freight': 'sum'  # Monetary Value
    }).reset_index()

    rfm_df['customer_id'] = rfm_df['customer_id'].str[:5]

    rfm_df.rename(columns={
        'order_purchase_timestamp': 'Recency',
        'order_id': 'Frequency',
        'price_less_freight': 'Monetary'
    }, inplace=True)

    return rfm_df

all_df = pd.read_csv("all_data.csv")
order_review_df = pd.read_csv("order_reviews_clean.csv")

monthly_orders_df = create_monthly_orders_df(all_df)
bystate_df = create_bystate_df(all_df)
product_category_sales_df = create_product_category_sales_df(all_df)
rfm_df = create_rfm_df(all_df)
review_count_df = create_review_count_df(order_review_df)

st.header('Proyek Analisis Data: E-Commerce Public Dataset')
#membuat visulisasi total orders
st.subheader('Total Orders')

col1, col2 = st.columns(2)
 
with col1:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)
 
with col2:
    total_revenue = format_currency(monthly_orders_df.revenue.sum(), "AUD", locale='es_CO') 
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(10, 5))
plt.plot(monthly_orders_df["order_purchase_timestamp"], monthly_orders_df["order_count"], marker='o', linewidth=2, color="#72BCD4")
plt.title("Number of Orders per 4 Month", loc="center", fontsize=20)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
st.pyplot(fig)

fig, ax = plt.subplots(figsize=(10, 5))
plt.plot(monthly_orders_df["order_purchase_timestamp"], monthly_orders_df["revenue"], marker='o', linewidth=2, color="#72BCD4")
plt.title("Total Revenue per 4 Month", loc="center", fontsize=20)
plt.xticks(fontsize=10)
plt.yticks(fontsize=10)
st.pyplot(fig)

#membuat visualisasi persebaran customer 'bystate'
st.subheader('Customer Demograpic')
fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="customer_count",
    y="customer_state",
    data=bystate_df.sort_values(by="customer_count", ascending=False).head(5),
    palette=colors
)
plt.title("Number of Customer by States", loc="center", fontsize=15)
plt.ylabel(None)
plt.xlabel(None)
plt.tick_params(axis='y', labelsize=12)
st.pyplot(fig)

#membuat visualisasi best seller dan worst seller
st.subheader("Best & Worst Categories Product")
fig, axes = plt.subplots(1, 2, figsize=(35, 15))

# Plot for the most sold product categories
sns.barplot(ax=axes[0], x=product_category_sales_df.head(5).values, y=product_category_sales_df.head(5).index, palette=colors)
axes[0].set_title("Top 5 Most Sold Product Categories", fontsize=50, loc="center")
axes[0].set_xlabel("Number of Sales", fontsize=30)
axes[0].set_ylabel(None)
axes[0].tick_params(axis='y', labelsize=35)
axes[0].tick_params(axis='x', labelsize=30)

# Plot for the least sold product categories
sns.barplot(ax=axes[1], x=product_category_sales_df.tail(5).values, y=product_category_sales_df.tail(5).index, palette=colors)
axes[1].set_title("Top 5 Least Sold Product Categories", fontsize=50, loc="center")
axes[1].set_ylabel(None)
axes[1].set_xlabel("Number of Sales", fontsize=30)
axes[1].invert_xaxis()
axes[1].yaxis.set_label_position("right")
axes[1].yaxis.tick_right()
axes[1].tick_params(axis='y', labelsize=35)
axes[1].tick_params(axis='x', labelsize=30)


plt.tight_layout()
st.pyplot(fig)

#Membuat visualisasi persebaran ratings
st.subheader("Rating Counts")
colors = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3" ,"#72BCD4"]

fig, ax = plt.subplots(figsize=(8, 4))
sns.barplot(x=review_count_df.index, y=review_count_df.values, palette=colors)
plt.xlabel("Rating")
plt.ylabel(None)
plt.title("Number of Reviews per Rating")
st.pyplot(fig)

#Membuat visualisasi rfm_df
st.subheader("Best Customer Based on RFM Parameters")

col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(rfm_df.Recency.mean(), 1)
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(rfm_df.Frequency.mean(), 2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_frequency = format_currency(rfm_df.Monetary.mean(), "AUD", locale='es_CO') 
    st.metric("Average Monetary", value=avg_frequency)

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(40, 15))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

sns.barplot(y="Recency", x="customer_id", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("customer_id", fontsize=30)
ax[0].set_title("By Recency (days)", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', labelsize=35)

sns.barplot(y="Frequency", x="customer_id", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("customer_id", fontsize=30)
ax[1].set_title("By Frequency", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', labelsize=35)

sns.barplot(y="Monetary", x="customer_id", data=rfm_df.sort_values(by="Monetary", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("customer_id", fontsize=30)
ax[2].set_title("By Monetary", loc="center", fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', labelsize=35)

plt.suptitle("Best Customer Based on RFM Parameters (customer_id)", fontsize=20)
st.pyplot(fig)