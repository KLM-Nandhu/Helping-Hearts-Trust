import streamlit as st
import pinecone
from pinecone import ServerlessSpec
import pandas as pd
import openai
from io import BytesIO

# Set up OpenAI and Pinecone (you should use environment variables for these)
openai.api_key = "your-openai-api-key"
pinecone.init(api_key="your-pinecone-api-key")

index_name = "contacts"
# Specify the serverless configuration
spec = ServerlessSpec(cloud="aws", region="us-east-1")
# Initialize the index with serverless spec
index = pinecone.Index(index_name, spec=spec)

def get_embedding(text):
    response = openai.Embedding.create(input=text, model="text-embedding-ada-002")
    return response['data'][0]['embedding']

def add_contact(name, number):
    embedding = get_embedding(f"{name} {number}")
    index.upsert(vectors=[(f"{name}_{number}", embedding, {"name": name, "number": number})])
    st.success("Contact added successfully!")

def view_contacts():
    query_response = index.query(vector=[0]*1536, top_k=1000, include_metadata=True)
    contacts = [match['metadata'] for match in query_response['matches']]
    df = pd.DataFrame(contacts)
    st.table(df)
    return df

def download_contacts(df):
    excel_file = BytesIO()
    df.to_excel(excel_file, index=False, engine="openpyxl")
    excel_file.seek(0)
    return excel_file

st.title("Contact Management System")

tab1, tab2 = st.tabs(["Add Contact", "View Contacts"])

with tab1:
    st.header("Add New Contact")
    name = st.text_input("Name")
    number = st.text_input("Number")
    if st.button("Add Contact"):
        add_contact(name, number)

with tab2:
    st.header("View Contacts")
    if st.button("Refresh Contacts"):
        df = view_contacts()
        if not df.empty:
            excel_file = download_contacts(df)
            st.download_button(
                label="Download contacts as Excel",
                data=excel_file,
                file_name="contacts.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("No contacts found.")
