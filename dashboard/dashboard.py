import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def create_best_sellers_df(all_data):
    best_sellers = all_data.groupby("product_category_name_english")["product_id"].count().reset_index()
    best_sellers = best_sellers.rename(columns={
        "product_category_name_english": "product",
        "product_id": "total_product"
    })
    best_sellers = best_sellers.sort_values(by="total_product", ascending=False)

    return best_sellers

def customers_by_city_df(all_data):
    most_customer_by_city = all_data.groupby(by="customer_city").customer_id.nunique().reset_index()
    most_customer_by_city.rename(columns={
        "customer_id": "total_customer"
    }, inplace=True)
    most_customer_by_city = most_customer_by_city.sort_values(by="total_customer", ascending=False)

    return most_customer_by_city

def create_recency_df(all_data):
    all_data['order_approved_at'] = pd.to_datetime(all_data['order_approved_at'], errors='coerce')
    current_date = pd.Timestamp('2018-12-31')  # Hitung dari akhir tahun 2018 ke belakang
    recency_df = all_data.groupby('customer_id').agg({
        'order_approved_at': 'max'
    }).reset_index()
    recency_df['recency'] = (current_date - recency_df['order_approved_at']).dt.days

    # Hapus kolom 'order_approved_at' karena tidak diperlukan
    recency_df.drop(columns='order_approved_at', inplace=True)
    recency_df.sort_values(by="recency", ascending=False, inplace=True)

    return recency_df

def create_frequency_df(all_data):
    end_date = all_data['order_approved_at'].max() 
    start_date = end_date - pd.DateOffset(months=1) 
    recent_orders = all_data[(all_data['order_approved_at'] >= start_date) & 
                              (all_data['order_approved_at'] <= end_date)]

    frequency_df = recent_orders.groupby('customer_id').agg({
        'order_approved_at': 'count'
    }).reset_index()

    frequency_df.rename(columns={'order_approved_at': 'frequency'}, inplace=True)

    return frequency_df

def create_monetary_df(all_data):
    monetary_df = all_data.groupby('customer_id').agg({
        'payment_value': 'sum'
    }).reset_index()

    monetary_df.rename(columns={'payment_value': 'monetary'}, inplace=True)

    return monetary_df

try:
    all_df = pd.read_csv("./all_data.csv")
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

best_sellers = create_best_sellers_df(all_df)
most_customer_by_city = customers_by_city_df(all_df)
recency_df = create_recency_df(all_df)
frequency_df = create_frequency_df(all_df)
monetary_df = create_monetary_df(all_df)

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    st.title("Dominic Naufal")

st.title('Dashboard')
st.header('Best Seller & Worst Products')

col1, col2 = st.columns(2)
 
with col1:
    st.metric("Best Category Product", value="Bed Bath Table")

with col2:
    st.metric("Worst Category Product", value="Security and Service")

# ============== CATEGORY PRODUCT GRAPH ===============================

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))

colors = ["#72BCD4"] * 5 + ["#D3D3D3"] * 5  # Color for best sellers and worse products

sns.barplot(x="total_product", y="product", data=best_sellers.head(5), palette=colors[:5], ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=18)
ax[0].tick_params(axis='y', labelsize=15)

sns.barplot(x="total_product", y="product", data=best_sellers.sort_values(by="total_product", ascending=True).head(5), palette=colors[5:], ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

plt.suptitle("Produk Paling Banyak dan Paling Sedikit Terjual", fontsize=20)

st.pyplot(fig)

st.caption("With this graph, we can encounter that bed bath table is the most valuable category product and it has great potential in market")

# ============== CUSTOMER GRAPH ===============================
st.header('Top 10 cities with the most customers')
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))

sns.barplot(x="total_customer", y="customer_city", data=most_customer_by_city.head(10), palette="viridis")

plt.title("Top 10 cities", fontsize=16)
plt.xlabel("Total Customer", fontsize=12)
plt.ylabel("Customer City", fontsize=12)

plt.tight_layout()
st.pyplot(fig)

st.caption("Sao Paulo city would be the great place to penetrate a new market and have big chances for any category")

# ============== RECENCY ===============================
st.header('Customer Recency Analysis')
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))

sns.histplot(data=recency_df, x='recency', bins=30, kde=True)

plt.title('Customer Recency Distribution', fontsize=16)
plt.xlabel('Jumlah Hari Sejak Pembelian Terakhir', fontsize=14)
plt.ylabel('Jumlah Pelanggan', fontsize=14)
st.pyplot(fig)

st.caption("Most of customers have not made a purchase more than 100 days after the last transaction. This can be due by changes that occur in e-commerce")

# ============== FREQUENCY ===============================
st.header('Customer Frequency Analysis')
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))

sns.barplot(data=frequency_df.sort_values(by='frequency', ascending=False).head(20), 
            x='customer_id', y='frequency', palette='viridis')

plt.title('Top 20 customers by frequency on last month', fontsize=16)
plt.xlabel('Customer ID', fontsize=14)
plt.ylabel('Jumlah Transaksi (Frequency)', fontsize=14)

plt.xticks(rotation=90)  # Memutar label sumbu X agar tidak tumpang tindih
plt.grid(axis='y')
st.pyplot(fig)

st.caption("However, there are some customers who still do transactions at least 15 in last month")

# ============== MONETARY ===============================
st.header('Customer MONETARY Analysis')
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(12, 6))

sns.barplot(data=monetary_df.sort_values(by='monetary', ascending=False).head(20), 
            x='customer_id', y='monetary', palette='magma')

plt.title('Top 20 Customers by Monetary', fontsize=16)
plt.xlabel('Customer ID', fontsize=14)
plt.ylabel('Total Pembelian (Monetary)', fontsize=14)

plt.xticks(rotation=90)
plt.grid(axis='y')
st.pyplot(fig)

st.caption("The highest transaction was more than 1.000.000 in some transactions")
print(sns.__version__)