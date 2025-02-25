import streamlit as st
import mysql.connector
import pandas as pd

# Function to establish database connection
def get_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456789",  
            database="Redbus"  
        )
        return connection
    except mysql.connector.Error as err:
        st.error(f"Database connection error: {err}")
        return None

# Function to fetch route names starting with a specific letter
def fetch_route_names(connection, starting_letter):
    query = """
        SELECT DISTINCT Route_Name 
        FROM combined_data 
        WHERE Route_Name LIKE %s
        ORDER BY Route_Name
    """
    cursor = connection.cursor()
    cursor.execute(query, (starting_letter + '%',))
    route_names = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return route_names

# Function to fetch bus data for the selected route
def fetch_data(connection, selected_route, price_sort_order):
    order = 'ASC' if price_sort_order == 'Low to High' else 'DESC'
    query = f"""
        SELECT * 
        FROM combined_data
        WHERE Route_Name = %s 
        ORDER BY Price {order}
    """
    cursor = connection.cursor(dictionary=True)
    cursor.execute(query, (selected_route,))
    data = pd.DataFrame(cursor.fetchall())
    cursor.close()
    return data

# Main Streamlit App
def main():
    st.title("Easy and Secure Online Bus Tickets Booking")

    # Establish database connection
    connection = get_connection()
    if not connection:
        return

    # Input for starting letter of Route Name
    starting_letter = st.text_input("Enter the starting letter of the route name")

    if starting_letter:
        route_names = fetch_route_names(connection, starting_letter.upper())
        if not route_names:
            st.warning(f"No routes found starting with '{starting_letter}'.")
            return

        selected_route = st.selectbox("Select a Route", route_names)

        if selected_route:
            # Sort preference for price
            price_sort_order = st.radio("Sort by Price", ['Low to High', 'High to Low'])

            # Fetch data for the selected route
            data = fetch_data(connection, selected_route, price_sort_order)
            if data.empty:
                st.warning(f"No data available for route '{selected_route}'.")
            else:
                st.write(f" Bus details for route: {selected_route}")
                st.dataframe(data)

                # Filtering options
                star_ratings = data['Star_Rating'].unique()
                selected_ratings = st.multiselect("Filter by Star Rating", star_ratings)

                bus_types = data['Bus_Type'].unique()
                selected_bus_types = st.multiselect("Filter by Bus Type", bus_types)

                if selected_ratings or selected_bus_types:
                    filtered_data = data[
                        (data['Star_Rating'].isin(selected_ratings)) & 
                        (data['Bus_Type'].isin(selected_bus_types))
                    ]
                    if filtered_data.empty:
                        st.warning("No buses match the selected filters.")
                    else:
                        st.write(" Filtered Bus Details")
                        st.dataframe(filtered_data)

if __name__ == "__main__":
    main()
