import streamlit as st
import mysql.connector
import pandas as pd

# Connect to the database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456789",
    database="Redbus"
)
mycursor = mydb.cursor()

# Retrieve data
mycursor.execute("SELECT * FROM combined_data")
data = mycursor.fetchall()
columns = [desc[0] for desc in mycursor.description]
table = pd.DataFrame(data, columns=columns)

# Change column types
table['Seat_Availability'] = pd.to_numeric(table['Seat_Availability'].str.extract(r'(\d+)')[0], errors='coerce', downcast='integer')
table['Star_Rating'] = table['Star_Rating'].astype(float).round(0).astype('Int64')
table['Price'] = table['Price'].astype(float).round(0).astype('Int64')

# User interface
st.title(" RedBus Availability Checker")
st.write("Discover the best bus routes and their availability!")

# Dropdown for route selection
statelist = ["Choose your Route_Link"] + table["Route_Link"].unique().tolist()
selected_state = st.selectbox("Select Your Route_Link", statelist)

if selected_state != "Choose your Route_Link":
    # Get routes for the selected Route_Link
    routes = table[table["Route_Link"] == selected_state]["Route_Name"].unique().tolist()
    route_selected = st.selectbox("Select Your Route", ["Choose your route"] + routes)

    if route_selected != "Choose your route":
        st.sidebar.subheader(" Filter Options")

        # Star Rating filter
        rating = st.sidebar.radio("Star Rating", options=[5, 4, 3, 2, 1], horizontal=True)

        # Maximum Price filter
        max_price = st.sidebar.slider(" Max Ticket Price (INR)", 100, 10000, step=100, value=5000)

        # Required Seats filter
        seats = st.sidebar.number_input(" Seats Required", min_value=1, max_value=57, value=1)

        # Apply filters
        filtered_buses = table[
            (table["Route_Name"] == route_selected) &
            (table["Star_Rating"] >= rating) &
            (table["Price"] <= max_price) &
            (table["Seat_Availability"] >= seats)
        ]

        # Display available buses
        if not filtered_buses.empty:
            bus_names = filtered_buses["Bus_Name"].unique().tolist()
            bus_selected = st.radio("Available Buses", bus_names)

            if bus_selected:
                if st.button(f"Show {bus_selected} Bus Details"):
                    bus_details = filtered_buses[filtered_buses["Bus_Name"] == bus_selected][
                        ["Bus_Type", "Departing_Time", "Duration", "Star_Rating", "Price", "Reaching_Time", "Seat_Availability"]
                    ]
                    st.subheader("Bus Details:")
                    st.table(bus_details)
        else:
            st.warning(" No buses found with the selected criteria. Please tweak your filters.")
