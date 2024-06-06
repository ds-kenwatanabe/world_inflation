import streamlit as st
import mysql.connector
import pandas as pd


class InflationApp:
    # Function to establish a connection to the MySQL database using secrets
    def get_connection(self):
        conn = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            user=st.secrets["mysql"]["username"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        return conn

    # Function to query the database
    def run_query(self, query):
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchall()
        conn.close()
        return result

    # Function to get the list of countries
    def get_countries(self):
        query = "SELECT DISTINCT country FROM inflation;"
        result = self.run_query(query)
        return [row['country'] for row in result]

    def ui(self, query):
        # Streamlit UI
        st.title("Country Average Inflation Since 1956")

        # Display all users from the database
        inflation = self.run_query(query)

        # Convert the result into a DataFrame for easier handling
        df = pd.DataFrame(inflation)

        st.subheader("Venezuela and Argentina excluded")
        st.write(df)

        # Get list of countries for the selectbox
        countries = self.get_countries()
        selected_country = st.selectbox("Select a country", countries)

        if selected_country:
            # Update the query to filter by the selected country
            line_query = (f"SELECT year, average_inflation "
                          f"FROM inflation "
                          f"WHERE country = '{selected_country}' "
                          f"ORDER BY year;")

            # Display data for the selected country
            inflation_line = self.run_query(line_query)
            df_line = pd.DataFrame(inflation_line)

            st.subheader(f"Inflation Data for {selected_country}")
            st.write(df_line)
            # Line chart
            st.line_chart(df_line, x="year", y="average_inflation", color="#FF0000")


if __name__ == '__main__':
    app = InflationApp()
    app.get_connection()
    sql_query = ("SELECT country, year, average_inflation, annual_inflation "
                 "FROM inflation "
                 "ORDER BY average_inflation DESC;")
    app.run_query(sql_query)
    app.ui(sql_query)
