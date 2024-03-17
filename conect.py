
import streamlit as st
from st_login_form import login_form
from st_supabase_connection import SupabaseConnection
from supabase import create_client, Client
import pandas as pd
from datetime import datetime, timedelta
from IPython.display import display
import calendar
import numpy as np
import plotly.express as px
from IPython.display import HTML
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
import streamlit_option_menu as option_menu
import plotly.graph_objects as go
# Set the page configuration



st.set_page_config(page_title="My Streamlit App", layout="wide")

def home():
    st.session_state.is_authenticated = False 
    
    col1, col2 = st.columns([2,1])
    with col1:
        menu = ["Login", "Sign up", "Log Out"]
        choice = st.sidebar.selectbox("", menu)

        form_container = st.empty()
        with form_container :
            # Initialize connection.
            # Uses st.cache_resource to only run once.
            @st.cache_resource
            def init_connection():
                url = st.secrets["SUPABASE_URL"]
                key = st.secrets["SUPABASE_KEY"]
                return create_client(url, key)

            supabase = init_connection()
            
            response = supabase.from_('facilities').select('*').execute()
            location_df = pd.DataFrame(response.data)

            # Perform query.
            # Uses st.cache_data to only rerun when the query changes or after 10 min.
            @st.cache_resource(ttl=600)
            def create_usertable():
                try:
                    # Assuming `supabase` is your Supabase client
                    query = """
                    CREATE TABLE IF NOT EXISTS users (
                        staffnumber INTEGER NOT NULL,
                        password TEXT NOT NULL,
                        location TEXT NOT NULL,
                        region TEXT NOT NULL
                    );
                    """
                    supabase.query(query)
                    return True

                except Exception as e:
                    print(f"Error creating usertable: {e}")
                    return False
        
                            
            def add_userdata(staffnumber, password, location, region,supabase):
                try:
                    # Insert a new record into the 'users' table
                    supabase.table('users').insert({
                        'staffnumber': staffnumber,
                        'password': password,
                        'location': location,
                        'region': region
                    }).execute()
                    return True
                except Exception as e:
                    print(f"Error adding userdata: {e}")
                    return False
            
            def get_facilities(staffnumber):
                # Perform a Supabase query to fetch data from the 'users' table
                response = supabase.from_('users').select('*').eq('staffnumber', staffnumber).execute()
                login_df = response.data
                return login_df
           
            def login_user(staffnumber, password):
                try:
                    # Query the 'usertable' using Supabase client
                    query = f"SELECT * FROM users WHERE staffnumber = {staffnumber} AND password = '{password}'"
                    result = supabase.query(query).execute()

                    # Fetch location and region based on staffnumber
                    facilities_df = get_facilities(staffnumber)

                    if facilities_df:
                        location = facilities_df[0]['location']
                        region = facilities_df[0]['region']

                        # Return the result, location, and region
                        return result, location, region
                    else:
                        return None, None, None
                except Exception as e:
                    print(f"Error logging in user: {e}")
                    return None, None, None
                
            def view_all_users():
                try:
                    # Query the 'usertable' using Supabase client
                    query = "SELECT * FROM users"
                    result = supabase.query(query).execute()

                    # Return the result
                    return result
                except Exception as e:
                    print(f"Error fetching all users: {e}")
                    return None
                
                
            response = supabase.from_('facilities').select('*').execute()
            location_df = pd.DataFrame(response.data)
            location_names = location_df["Location"]
            
            
            
             # log in app
             
            if choice == "Log Out":
                st.subheader("Log Out")

            elif choice == "Login":
                with st.form("Login Form"):
                    st.write("Login Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
                    load = st.form_submit_button("Login")
                    st.session_state.logged_in = False

                    if load or st.session_state.logged_in:
                        st.session_state.logged_in = True
                        result, location, region = login_user(staffnumber, password)
                        if result:
                            st.success("Logged In successfully")
                            st.write(f"Location: {location}, Region: {region}")
                            st.session_state.is_authenticated = True
                            st.session_state["logged_in"] = True
                            form_container.empty()
                        else:
                            st.warning("Invalid credentials. Please try again.")

            elif choice == "Sign up":
                with st.form("Sign-up Form"):
                    st.write("Sign-up Form")
                    staffnumber = st.text_input("Staffnumber")
                    password = st.text_input("Password", type='password')
                    location = st.selectbox("Select Location", location_names)
                    selected_location = location_df[location_df['Location'] == location]
                    # Filter location_df based on selected_location
                    filtered_df = location_df[location_df['Location'] == selected_location]
                    # Get unique regions for the selected location
                    unique_regions = filtered_df['Region'].unique()
                    region = st.text_input("Region", value=unique_regions[0] if unique_regions else "")
                    if st.form_submit_button("Sign up"):
                        if add_userdata(staffnumber, password, location, region,supabase):
                            st.success("You have created a new account")
                            st.session_state["logged_in"] = True
                            st.session_state.is_authenticated = True
                            form_container.empty()
                        else:
                            st.warning("Failed to create a new account. Please try again.")

with st.sidebar:
    #st.image("Dashboard/logo.png", caption="Bliss Healthcare")
    selected_page = option_menu.option_menu(
        menu_title='DASHBOARDS',
        options=['Medical centre Dashboard', 'Region Dashboard', 'Departments Dashboard', "Maintenance Dashboard", 'Summary Dashboard', 'Account'],
        icons=['house-fill', 'receipt', 'receipt', 'receipt', 'receipt', 'person-circle'],
        menu_icon='house-fill',
        default_index=0,
        styles={
            "container": {"padding": "15", "background-color": {"grey": "black", "font-size": "10px"}},
            "nav-link": {"color": "Blck", "font-size": "13px", "text-align": "left"},
            "nav-link-selected": {"background-color": "Black"}
        }
    )

if st.session_state.get('selected_page'):
    selected_page = st.session_state['selected_page']
if selected_page == "Medical centre Dashboard":
    home()
else:
    pass
