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
        background-color: #fcffff;
    }
    .main .block-container {
        background-color: #96f2f2;
        padding: 3rem;
        border-radius: 10px;
    }
    [data-testid="stSidebar"] {
        background-color: #96f2f2;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    [data-testid="stSidebar"] .stButton>button {
        background-color: #3498db;
        color: white;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #333333;
        color: white;
        text-align: center;
        padding: 10px 0;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# Function to load data
def load_data(file_name):
    if os.path.exists(file_name):
        df = pd.read_excel(file_name)
        df['Number'] = df['Number'].astype(str).str.replace(',', '')  # Remove commas from numbers
        return df.sort_values('Name')  # Sort alphabetically by name
    return pd.DataFrame(columns=["Name", "Number", "Last Updated"])

# Function to save data
def save_data(df, file_name):
    df = df.sort_values('Name')  # Sort alphabetically by name before saving
    df.to_excel(file_name, index=False, engine='openpyxl')

# Function to convert DataFrame to Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    return processed_data

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = load_data("customers.xlsx")
if 'df_repeating' not in st.session_state:
    st.session_state.df_repeating = load_data("repeating_customers.xlsx")

# Sidebar for adding new customers
with st.sidebar:
    st.title("📝 Add New Customer")
    new_name = st.text_input("Name")
    new_number = st.text_input("Number")
    if st.button("➕ Add Customer", key="add_customer"):
        if new_name and new_number:
            new_number = new_number.replace(',', '')  # Remove any commas from the input
            if new_number in st.session_state.df["Number"].values:
                if st.sidebar.warning("This number already exists. Do you want to add it to the repeating sheet?"):
                    new_row = pd.DataFrame({
                        "Name": [new_name],
                        "Number": [new_number],
                        "Last Updated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                    })
                    st.session_state.df_repeating = pd.concat([st.session_state.df_repeating, new_row], ignore_index=True)
                    save_data(st.session_state.df_repeating, "repeating_customers.xlsx")
                    st.success("Customer added to repeating sheet!")
            else:
                new_row = pd.DataFrame({
                    "Name": [new_name],
                    "Number": [new_number],
                    "Last Updated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
                })
                st.session_state.df = pd.concat([st.session_state.df, new_row], ignore_index=True)
                save_data(st.session_state.df, "customers.xlsx")
                st.success("Customer added successfully!")
        else:
            st.error("Please enter both name and number.")

    # Search, edit and delete options
    st.subheader("🔍 Search, ✏️ Edit or 🗑️ Delete Customer")
    search_option = st.radio("Search by:", ("Name", "Number"))
    search_term = st.text_input(f"Enter {search_option}")
    
    if search_term:
        # Search in both regular and repeating customers
        if search_option == "Name":
            selected_regular = st.session_state.df[st.session_state.df["Name"].str.contains(search_term, case=False, na=False)]
            selected_repeating = st.session_state.df_repeating[st.session_state.df_repeating["Name"].str.contains(search_term, case=False, na=False)]
        else:  # Number
            selected_regular = st.session_state.df[st.session_state.df["Number"].str.contains(search_term, na=False)]
            selected_repeating = st.session_state.df_repeating[st.session_state.df_repeating["Number"].str.contains(search_term, na=False)]
        
        if not selected_regular.empty or not selected_repeating.empty:
            st.write("Matching customers:")
            if not selected_regular.empty:
                st.write("Regular Customers:")
                st.write(selected_regular[["Name", "Number"]])
            if not selected_repeating.empty:
                st.write("Repeating Customers:")
                st.write(selected_repeating[["Name", "Number"]])
            
            # Combine results for selection
            all_results = pd.concat([selected_regular, selected_repeating]).reset_index(drop=True)
            selected_index = st.selectbox("Select a customer to edit/delete:", 
                                          options=range(len(all_results)),
                                          format_func=lambda x: f"{all_results.iloc[x]['Name']} - {all_results.iloc[x]['Number']}")
            
            selected_customer = all_results.iloc[selected_index]
            edit_name = st.text_input("Edit Name", value=selected_customer["Name"])
            edit_number = st.text_input("Edit Number", value=selected_customer["Number"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Update Customer", key="update_customer"):
                    # Determine which DataFrame to update
                    if selected_index < len(selected_regular):
                        df_to_update = st.session_state.df
                        file_to_update = "customers.xlsx"
                    else:
                        df_to_update = st.session_state.df_repeating
                        file_to_update = "repeating_customers.xlsx"
                    
                    # Update the customer
                    customer_index = df_to_update[
                        (df_to_update["Name"] == selected_customer["Name"]) & 
                        (df_to_update["Number"] == selected_customer["Number"])
                    ].index[0]
                    df_to_update.loc[customer_index, "Name"] = edit_name
                    df_to_update.loc[customer_index, "Number"] = edit_number.replace(',', '')
                    df_to_update.loc[customer_index, "Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_data(df_to_update, file_to_update)
                    st.success("Customer updated successfully!")
            with col2:
                if st.button("🗑️ Delete Customer", key="delete_customer"):
                    # Determine which DataFrame to update
                    if selected_index < len(selected_regular):
                        df_to_update = st.session_state.df
                        file_to_update = "customers.xlsx"
                    else:
                        df_to_update = st.session_state.df_repeating
                        file_to_update = "repeating_customers.xlsx"
                    
                    # Delete the customer
                    customer_index = df_to_update[
                        (df_to_update["Name"] == selected_customer["Name"]) & 
                        (df_to_update["Number"] == selected_customer["Number"])
                    ].index[0]
                    df_to_update = df_to_update.drop(customer_index).reset_index(drop=True)
                    save_data(df_to_update, file_to_update)
                    st.success("Customer deleted successfully!")
                    
                    # Update the session state
                    if file_to_update == "customers.xlsx":
                        st.session_state.df = df_to_update
                    else:
                        st.session_state.df_repeating = df_to_update
        else:
            st.warning(f"No customer found with this {search_option.lower()}.")

# Main content
st.title("👥 Customer Manager")

# View customers
col1, col2 = st.columns(2)

with col1:
    show_regular = st.checkbox("👁️ Show Regular Customers", value=True)
    if show_regular:
        st.subheader("Regular Customers")
        st.write(st.session_state.df[["Name", "Number"]].reset_index(drop=True).rename_axis('Index').reset_index())

with col2:
    show_repeating = st.checkbox("👁️ Show Repeating Customers", value=True)
    if show_repeating:
        st.subheader("Repeating Customers")
        st.write(st.session_state.df_repeating[["Name", "Number"]].reset_index(drop=True).rename_axis('Index').reset_index())

# Download options
col1, col2 = st.columns(2)

with col1:
    if not st.session_state.df.empty:
        excel_file = to_excel(st.session_state.df)
        st.download_button(
            label="📥 Download Regular Customer Data (XLSX)",
            data=excel_file,
            file_name="customer_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

with col2:
    if not st.session_state.df_repeating.empty:
        excel_file_repeating = to_excel(st.session_state.df_repeating)
        st.download_button(
            label="📥 Download Repeating Customer Data (XLSX)",
            data=excel_file_repeating,
            file_name="repeating_customers.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
# Footer
st.markdown(
    """
    <div class="footer">
        © 2024 JOSHUA. All rights reserved.
    </div>
    """,
    unsafe_allow_html=True
)
