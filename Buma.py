import streamlit as st
from shareplum import Site, Office365
from shareplum.site import Version

USERNAME = "biosafety@blisshealthcare.co.ke"
PASSWORD = "Buma#2025"
SHAREPOINT_URL = "https://blissgvske.sharepoint.com"
SHAREPOINT_SITE = "https://blissgvske.sharepoint.com/sites/BlissHealthcareReports/"

# Authenticate with SharePoint
authcookie = Office365(SHAREPOINT_URL, username=USERNAME, password=PASSWORD).GetCookies()
site = Site(SHAREPOINT_SITE, version=Version.v365, authcookie=authcookie)

# Define your data
my_data = [{'Title': 'First Row!'}, {'Title': 'Another One!'}]

# Create a new list object
new_list = site.List('Maintenance Report')

# Streamlit UI
st.title("Add Rows to SharePoint List")

# Collect data from user input
data = [{
    'Title': st.text_input("Enter Title"),
    'Admin Approval': st.text_input("Enter Value for Admin Approval")
}]

# Button to trigger the add action
if st.button("Add Row"):
    if all(data):
        # Add list items to the SharePoint list
        new_list.UpdateListItems(data=data, kind='New')
        st.success("Row added successfully!")
    else:
        st.error("Please fill in all fields")
