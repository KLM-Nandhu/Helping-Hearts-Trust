import streamlit as st
import pandas as pd
import os
from datetime import datetime
from io import BytesIO

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

# Function to convert DataFrame to Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

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
    search_option = st.radio("Search by:", ("Name", "Number"))
    search_term = st.text_input(f"Enter {search_option}")
    
    if search_term:
        if search_option == "Name":
            selected_customers = df[df["Name"].str.contains(search_term, case=False, na=False)]
        else:  # Number
            selected_customers = df[df["Number"].str.contains(search_term, na=False)]
        
        if not selected_customers.empty:
            st.write("Matching customers:")
            st.write(selected_customers[["Name", "Number"]])
            
            selected_index = st.selectbox("Select a customer to edit/delete:", 
                                          options=selected_customers.index,
                                          format_func=lambda x: f"{selected_customers.loc[x, 'Name']} - {selected_customers.loc[x, 'Number']}")
            
            edit_name = st.text_input("Edit Name", value=selected_customers.loc[selected_index, "Name"])
            edit_number = st.text_input("Edit Number", value=selected_customers.loc[selected_index, "Number"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Update Customer"):
                    df.loc[selected_index, "Name"] = edit_name
                    df.loc[selected_index, "Number"] = edit_number
                    df.loc[selected_index, "Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_data(df, "customers.xlsx")
                    st.success("Customer updated successfully!")
            with col2:
                if st.button("🗑️ Delete Customer"):
                    df = df.drop(selected_index)
                    save_data(df, "customers.xlsx")
                    st.success("Customer deleted successfully!")
                    st.experimental_rerun()
        else:
            st.warning(f"No customer found with this {search_option.lower()}.")

# Main content
st.title("👥 Customer Manager")

# View all customers
if st.button("👁️ View All Customers"):
    st.write(df[["Name", "Number"]].sort_values("Name"))

# Download options
col1, col2 = st.columns(2)

with col1:
    if not df.empty:
        excel_file = to_excel(df)
        st.download_button(
            label="📥 Download Customer Data (XLSX)",
            data=excel_file,
            file_name="customer_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

with col2:
    if not df_repeating.empty:
        excel_file_repeating = to_excel(df_repeating)
        st.download_button(
            label="📥 Download Repeating Customers (XLSX)",
            data=excel_file_repeating,
            file_name="repeating_customers.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    else:
        st.write("No repeating customers data available.")
