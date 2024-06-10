import streamlit as st
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
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

        # Determine min and max inflation values
        min_inflation = df['average_inflation'].min()
        max_inflation = df['average_inflation'].max()

        # Calculate the bin width
        bin_width = (max_inflation - min_inflation) / 100

        # Histogram for distribution
        st.subheader(f"Normalized Average Inflation Distribution for {selected_year}")
        fig, ax = plt.subplots()
        counts, bins, patches = plt.hist(df['average_inflation'], bins=100, color='cyan', edgecolor='black',
                                         density=True, stacked=True)

        # Set ax colors and labels
        ax.set_xlabel('Inflation Percentage', color='white')
        ax.set_ylabel('Probability Density', color='white')
        ax.xaxis.label.set_color('white')
        ax.yaxis.label.set_color('white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

        # Set x-axis ticks
        ax.xaxis.set_major_locator(MaxNLocator(nbins=15))

        # Set the background color to be transparent
        plt.gca().set_facecolor('none')
        plt.gcf().patch.set_facecolor('none')
        st.pyplot(fig)

        # Description
        st.write("*Normalization of Histogram*: When a histogram is normalized, "
                 "the area under the histogram sums to 1. "
                 "This means each bar's height represents the relative frequency "
                 "or density rather than the raw count of observations.\n"
                 "\n*Y-axis Interpretation*: The y-axis in a normalized histogram shows the density, "
                 "which is the frequency per unit interval of the x-axis. "
                 "This means if you sum the areas of all bars, you will get 1, representing the entire dataset.\n"
                 "\n*Bar Height*: If a bar reaches 0.35 on the y-axis, this means that the density of that interval "
                 "is 0.35, not that there is a 35% chance of the values in that interval occurring. "
                 "The probability of a value falling within a specific interval is found by multiplying "
                 "the height (density) by the width of the interval, which you can try below.")

        # Bin selection slider
        st.subheader("Select a bin to see the probability")
        selected_bin = st.slider("Select bin for the average inflation", 0, 99, 0)

        # Calculate the probability for the selected bin
        selected_density = counts[selected_bin]
        selected_bin_start = bins[selected_bin]
        selected_bin_end = bins[selected_bin + 1]
        selected_bin_probability = selected_density * bin_width

        st.write(f"Selected bin: {selected_bin}")
        st.write(f"Bin range: {selected_bin_start:.2f} to {selected_bin_end:.2f}")
        st.write(f"Probability: {selected_bin_probability:.4f} or {100 * selected_bin_probability:.2f}%")

        # Determine min and max inflation values
        min_annual_inflation = df['annual_inflation'].min()
        max_annual_inflation = df['annual_inflation'].max()

        # Calculate the bin width
        bin_width_annual = (max_annual_inflation - min_annual_inflation) / 100

        st.subheader(f"Normalized Annual Inflation Distribution for {selected_year} (dec vs. dec)")
        fig2, ax2 = plt.subplots()
        # Drop None values, current year not available
        df_annual_inflation = df['annual_inflation'].dropna()

        counts2, bins2, patches2 = plt.hist(df_annual_inflation, bins=100, color='red', edgecolor='black', density=True, stacked=True)

        # Set ax colors and labels
        ax2.set_xlabel('Inflation Percentage', color='white')
        ax2.set_ylabel('Probability Density', color='white')
        ax2.xaxis.label.set_color('white')
        ax2.yaxis.label.set_color('white')
        ax2.tick_params(axis='x', colors='white')
        ax2.tick_params(axis='y', colors='white')

        # Set x-axis ticks
        ax2.xaxis.set_major_locator(MaxNLocator(nbins=15))

        # Set the background color to be transparent
        plt.gca().set_facecolor('none')
        plt.gcf().patch.set_facecolor('none')
        st.pyplot(fig2)

        # Bin selection slider
        st.subheader("Select a bin to see the probability")
        selected_bin2 = st.slider("Select bin for the annual inflation", 0, 99, 0)

        # Calculate the probability for the selected bin
        selected_density2 = counts2[selected_bin2]
        selected_bin_start2 = bins2[selected_bin2]
        selected_bin_end2 = bins2[selected_bin2 + 1]
        selected_bin_probability2 = selected_density2 * bin_width_annual

        st.write(f"Selected bin: {selected_bin2}")
        st.write(f"Bin range: {selected_bin_start2:.2f} to {selected_bin_end2:.2f}")
        st.write(f"Probability: {selected_bin_probability2:.4f} or {100 * selected_bin_probability2:.2f}%")

        # Description for countries
        st.write(":earth_americas: Next you can select a country and see the inflation values for each recorded year."
                 "The line plot shows how the inflation values developed over the years.")

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
            st.markdown(":link: [About histograms](https://en.wikipedia.org/wiki/Histogram)")
            st.markdown(":link: [Probability Density Function (PDF)](https://en.wikipedia.org/wiki/Histogram)")

    def ui(self):
        self.sidebar()


if __name__ == '__main__':
    app = InflationApp()
    app.get_connection()
    app.ui()
