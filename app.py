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

    def ui(self):
        # Streamlit UI
        st.title("Countries Inflation")

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


if __name__ == '__main__':
    app = InflationApp()
    app.get_connection()
    app.ui()
