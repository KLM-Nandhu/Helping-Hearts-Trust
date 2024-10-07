import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Customer Manager", layout="wide")

# Function to load data
def load_data():
    if os.path.exists("customers.xlsx"):
        return pd.read_excel("customers.xlsx")
    return pd.DataFrame(columns=["Name", "Number", "Last Updated"])

# Function to save data
def save_data(df):
    df.to_excel("customers.xlsx", index=False)

# Load data
df = load_data()

# Sidebar for adding new customers
st.sidebar.title("📝 Add New Customer")
new_name = st.sidebar.text_input("Name")
new_number = st.sidebar.text_input("Number")
if st.sidebar.button("➕ Add Customer"):
    if new_name and new_number:
        new_row = pd.DataFrame({
            "Name": [new_name],
            "Number": [new_number],
            "Last Updated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.sidebar.success("Customer added successfully!")
    else:
        st.sidebar.error("Please enter both name and number.")

# Main content
st.title("👥 Customer Manager")

# View all customers
if st.button("👁️ View All Customers"):
    st.write(df.sort_values("Last Updated", ascending=False))

# Download option
if not df.empty:
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Customer Data",
        data=csv,
        file_name="customer_data.csv",
        mime="text/csv",
    )

# Edit and delete options
st.subheader("✏️ Edit or 🗑️ Delete Customer")
selected_customer = st.selectbox("Select a customer", df["Name"].tolist())

if selected_customer:
    customer_index = df[df["Name"] == selected_customer].index[0]
    col1, col2 = st.columns(2)

    with col1:
        edit_name = st.text_input("Edit Name", value=df.loc[customer_index, "Name"])
        edit_number = st.text_input("Edit Number", value=df.loc[customer_index, "Number"])
        if st.button("✅ Update Customer"):
            df.loc[customer_index, "Name"] = edit_name
            df.loc[customer_index, "Number"] = edit_number
            df.loc[customer_index, "Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_data(df)
            st.success("Customer updated successfully!")

    with col2:
        if st.button("🗑️ Delete Customer"):
            df = df.drop(customer_index)
            save_data(df)
            st.success("Customer deleted successfully!")
            st.experimental_rerun()
