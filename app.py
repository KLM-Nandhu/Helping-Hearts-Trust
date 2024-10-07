import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Customer Manager", layout="wide")

# Custom CSS for background color and styling
st.markdown("""
    <style>
    .stApp {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to load data
def load_data(file_name):
    if os.path.exists(file_name):
        return pd.read_excel(file_name)
    return pd.DataFrame(columns=["Name", "Number", "Last Updated"])

# Function to save data
def save_data(df, file_name):
    df.to_excel(file_name, index=False)

# Load data
df = load_data("customers.xlsx")
df_repeating = load_data("repeating_customers.xlsx")

# Sidebar for adding new customers
with st.sidebar:
    st.title("📝 Add New Customer")
    new_name = st.text_input("Name")
    new_number = st.text_input("Number")
    if st.button("➕ Add Customer"):
        if new_name and new_number:
            if new_number in df["Number"].values:
                if st.sidebar.warning("This number already exists. Do you want to add it to the repeating sheet?"):
                    new_row = pd.DataFrame({
                        "Name": [new_name],
                        "Number": [new_number],
                        "Last Updated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                    })
                    df_repeating = pd.concat([df_repeating, new_row], ignore_index=True)
                    save_data(df_repeating, "repeating_customers.xlsx")
                    st.sidebar.success("Customer added to repeating sheet!")
            else:
                new_row = pd.DataFrame({
                    "Name": [new_name],
                    "Number": [new_number],
                    "Last Updated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df, "customers.xlsx")
                st.sidebar.success("Customer added successfully!")
        else:
            st.sidebar.error("Please enter both name and number.")

    # Edit and delete options
    st.subheader("✏️ Edit or 🗑️ Delete Customer")
    search_number = st.text_input("Search by contact number")
    if search_number:
        selected_customer = df[df["Number"] == search_number]
        if not selected_customer.empty:
            customer_index = selected_customer.index[0]
            edit_name = st.text_input("Edit Name", value=selected_customer["Name"].values[0])
            edit_number = st.text_input("Edit Number", value=selected_customer["Number"].values[0])
            if st.button("✅ Update Customer"):
                df.loc[customer_index, "Name"] = edit_name
                df.loc[customer_index, "Number"] = edit_number
                df.loc[customer_index, "Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_data(df, "customers.xlsx")
                st.success("Customer updated successfully!")
            if st.button("🗑️ Delete Customer"):
                df = df.drop(customer_index)
                save_data(df, "customers.xlsx")
                st.success("Customer deleted successfully!")
                st.experimental_rerun()
        else:
            st.warning("No customer found with this number.")

# Main content
st.title("👥 Customer Manager")

# View all customers
if st.button("👁️ View All Customers"):
    st.write(df[["Name", "Number"]].sort_values("Name"))

# Download option
if not df.empty:
    st.download_button(
        label="📥 Download Customer Data (XLSX)",
        data=df.to_excel(index=False, engine='openpyxl'),
        file_name="customer_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
