import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="SOCKET REPORT ITEM WISE", layout="wide")
st.title("🔧 SOCKET REPORT ITEM WISE")

@st.cache_data
def load_data():
    with open('dashboard_data.json', 'r') as f:
        data = json.load(f)
    return {float(k): v for k, v in data.items()}

data = load_data()
sizes = sorted(data.keys())

selected_size = st.sidebar.selectbox("📏 Select Size (inch)", sizes, format_func=lambda x: f"{x} inch")
size_info = data[selected_size]
structure = size_info['structure']
total_qty = size_info['total_qty']
total_amount = size_info['total_amount']
unique_orders = size_info['unique_orders']
has_product_type = size_info['has_product_type']

avg_qty_per_order = total_qty / unique_orders if unique_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("📦 Total QTY", f"{total_qty:,.0f}")
col2.metric("💰 Total AMOUNT", f"₹{total_amount:,.2f}")
col3.metric("🧾 Number of Orders", f"{unique_orders}")
col4.metric("📊 Avg QTY / Order", f"{avg_qty_per_order:.1f}")

st.markdown("---")
st.subheader(f"📂 Detailed Breakdown for {selected_size} inch")

def show_orders(orders, title):
    df = pd.DataFrame(orders)
    qty = df['qty'].sum()
    amt = df['amount'].sum()
    st.write(f"**{title} – Subtotal:** QTY = {qty}, AMOUNT = ₹{amt:,.2f}")
    st.dataframe(df, use_container_width=True, hide_index=True)

# ----- Exclusive expansion using radio buttons -----
if has_product_type:
    # List product types
    product_types = sorted(structure.keys())
    selected_type = st.radio("Select Product Type", product_types, horizontal=False)

    # Show details for the selected product type only
    prod_dict = structure[selected_type]
    pt_qty = sum(order['qty'] for w in prod_dict.values() for m in w.values() for order in m)
    pt_amt = sum(order['amount'] for w in prod_dict.values() for m in w.values() for order in m)
    st.write(f"**Product type subtotal:** QTY = {pt_qty}, AMOUNT = ₹{pt_amt:,.2f}")

    for wattage, mat_dict in sorted(prod_dict.items(), key=lambda x: float(x[0])):
        with st.expander(f"⚡ Wattage: {wattage} W"):
            w_qty = sum(order['qty'] for m in mat_dict.values() for order in m)
            w_amt = sum(order['amount'] for m in mat_dict.values() for order in m)
            st.write(f"**Wattage subtotal:** QTY = {w_qty}, AMOUNT = ₹{w_amt:,.2f}")
            for material, orders in mat_dict.items():
                with st.expander(f"🧪 Material: {material}"):
                    show_orders(orders, f"Material: {material}")
else:
    # For sizes without product types, use wattage as radio buttons
    wattages = sorted(structure.keys(), key=float)
    selected_wattage = st.radio("Select Wattage", wattages, format_func=lambda x: f"{x} W", horizontal=False)

    mat_dict = structure[selected_wattage]
    w_qty = sum(order['qty'] for m in mat_dict.values() for order in m)
    w_amt = sum(order['amount'] for m in mat_dict.values() for order in m)
    st.write(f"**Wattage subtotal:** QTY = {w_qty}, AMOUNT = ₹{w_amt:,.2f}")
    for material, orders in mat_dict.items():
        with st.expander(f"🧪 Material: {material}"):
            show_orders(orders, f"Material: {material}")
