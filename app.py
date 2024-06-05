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

    def ui(self, query):
        # Streamlit UI
        st.title("TOP 100 Biggest Average Inflations Since 1956")

        # Display all users from the database
        inflation = self.run_query(query)

        # Convert the result into a DataFrame for easier handling
        df = pd.DataFrame(inflation)

        st.subheader("Venezuela and Argentina excluded")
        st.write(df)

        # Line chart
        st.line_chart(df, x="year", y="average_inflation")


if __name__ == '__main__':
    app = InflationApp()
    app.get_connection()
    sql_query = ("SELECT country, year, average_inflation, annual_inflation "
                 "FROM inflation "
                 "ORDER BY average_inflation DESC;")
    app.run_query(sql_query)
    app.ui(sql_query)
