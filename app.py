import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


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

    def regression_model(self, df):
        # Drop None values
        df = df.dropna()
        # set variables
        X = df[['year']]
        y = df['average_inflation']

        # Train the model
        model = LinearRegression()
        model.fit(X, y)

        # Make predictions for the next 10 years
        future_years = np.arange(df['year'].max() + 1, df['year'].max() + 11).reshape(-1, 1)
        future_predictions = model.predict(future_years)

        # Create a DataFrame for future predictions
        future_df = pd.DataFrame({
            'year': future_years.flatten(),
            'average_inflation': future_predictions
        })

        # Combine historical data with future predictions
        combined_df = pd.concat([df, future_df])

        return combined_df

    def plot_regression(self, df, selected_country):
        # Plot using the regression model dataframe
        combined_df = self.regression_model(df)

        plt.figure(figsize=(10, 6))
        plt.plot(combined_df['year'], combined_df['average_inflation'], ls='--', color='#ff0000',
                 label='Forecasted Inflation')
        plt.plot(df['year'], df['average_inflation'], color='#00ffff', label='Historical Inflation')
        plt.xlabel('Year', color='white')
        plt.ylabel('Average Inflation', color='white')
        plt.title(f'Inflation Forecast for {selected_country}', color='white')
        plt.legend()
        plt.grid(True, color='#c0c0c0', linewidth=0.1)

        # Customize axis labels and ticks
        ax = plt.gca()
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        # Set the background color to be transparent
        plt.gca().set_facecolor('none')
        plt.gcf().patch.set_facecolor('none')
        # Plot the image
        st.pyplot(plt)

    def display_inflation_data(self):
        # Streamlit UI
        st.title("Countries CPI Inflation")

        # Year picker
        selected_year = st.slider("Select a year", min_value=1956, max_value=2024, value=2024)

        # Update the query to filter by the selected year
        sql_query = (f"SELECT country, year, average_inflation, annual_inflation "
                     f"FROM inflation "
                     f"WHERE year = {selected_year} "
                     f"ORDER BY average_inflation DESC;")

        # Display all users from the database
        inflation = self.run_query(sql_query)

        # Convert the result into a DataFrame for easier handling
        df = pd.DataFrame(inflation)

        # Ensure numeric columns are correctly typed
        df['average_inflation'] = pd.to_numeric(df['average_inflation'], errors='coerce')
        df['annual_inflation'] = pd.to_numeric(df['annual_inflation'], errors='coerce')

        st.subheader(f"Inflation Data for {selected_year}")
        st.write(df)

        # Summary statistics
        st.subheader(f"Summary Statistics for {selected_year}")
        st.write(df[["average_inflation", "annual_inflation"]].describe())

        # Histogram for distribution
        st.subheader(f"Average Inflation Distribution for {selected_year} (bins of 100)")
        fig, ax = plt.subplots()
        plt.hist(df['average_inflation'], bins=100, color='cyan')

        # Set ax colors
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        # Set the background color to be transparent
        plt.gca().set_facecolor('none')
        plt.gcf().patch.set_facecolor('none')
        st.pyplot(fig)

        st.subheader(f"Annual Inflation Distribution for {selected_year} (dec vs. dec, bins of 100)")
        fig2, ax2 = plt.subplots()
        # Drop None values, current year not available
        df_annual_inflation = df['annual_inflation'].dropna()

        plt.hist(df_annual_inflation, bins=100, color='red')

        # Set ax colors
        ax2.xaxis.label.set_color('white')
        ax2.yaxis.label.set_color('white')
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')

        # Set the background color to be transparent
        plt.gca().set_facecolor('none')
        plt.gcf().patch.set_facecolor('none')
        st.pyplot(fig2)

        # Get list of countries for the selectbox
        countries = self.get_countries()
        selected_country = st.selectbox("Select a country", countries)

        if selected_country:
            # Update the query to filter by the selected country
            line_query = (f"SELECT year, average_inflation, annual_inflation "
                          f"FROM inflation "
                          f"WHERE country = '{selected_country}' "
                          f"ORDER BY year;")

            # Display data for the selected country
            inflation_line = self.run_query(line_query)
            df_line = pd.DataFrame(inflation_line)

            # Ensure numeric columns are correctly typed
            df_line['year'] = pd.to_numeric(df_line['year'], errors='coerce')
            df_line['average_inflation'] = pd.to_numeric(df_line['average_inflation'], errors='coerce')
            df_line['annual_inflation'] = pd.to_numeric(df_line['annual_inflation'], errors='coerce')

            st.subheader(f"Inflation Data for {selected_country}")
            st.write(df_line)

            # Create the line chart with both average and annual inflation
            st.line_chart(df_line.set_index('year')[['average_inflation', 'annual_inflation']],
                          color=['#00ffff', '#ff0000'], use_container_width=True)

            # Run regression query
            reg_query = (f"SELECT year, average_inflation "
                         f"FROM inflation "
                         f"WHERE country = '{selected_country}' "
                         f"ORDER BY year;")
            reg_run_query = self.run_query(reg_query)
            df_reg = pd.DataFrame(reg_run_query)
            # Run and plot regression model
            self.regression_model(df_reg)
            self.plot_regression(df_reg, selected_country)

    def sidebar(self):
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", ["Home", "Inflation Data", "References"])

        if selection == "Home":
            st.header("Home")
            st.write("Welcome to the Inflation Data App.")
            st.write("""
                    This application provides an overview and analysis of inflation data across different countries 
                    using the consumer price index (CPI).

                    A consumer price index (CPI) measures the average change in prices over time for a basket of 
                    consumer goods and services commonly purchased by households. 

                    By monitoring changes in this index, we can track price fluctuations and inflation. 
                    The CPI is determined using a representative basket of goods and services, 
                    which is periodically updated to reflect shifts in consumer spending habits. 
                    Prices for the items in this basket are gathered monthly from a sample of retail and 
                    service establishments and are adjusted for any changes in quality or features. 

                    While the CPI is not a perfect measure of inflation or cost of living, 
                    it remains a valuable tool for tracking these economic indicators and comparing 
                    inflation rates across different countries.

                    **Features:**
                    - View inflation data for a selected year.
                    - Select a country to see CPI inflation data.
                    - Forecast future inflation trends using linear regression.

                    Use the sidebar to navigate between different sections of the app.
                    """)
            st.image("/home/chris/Pictures/inflation/00044-1625230760.png")
        elif selection == "Inflation Data":
            self.display_inflation_data()
        elif selection == "References":
            st.header("References")
            st.markdown(":globe_with_meridians: [inflation.eu website](https://www.inflation.eu/en/)")

    def ui(self):
        self.sidebar()


if __name__ == '__main__':
    app = InflationApp()
    app.get_connection()
    app.ui()
