import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from supabase import create_client, Client
from matplotlib.ticker import MaxNLocator
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from statsmodels.tsa.arima.model import ARIMA


class InflationApp:
    def __init__(self):
        url = st.secrets["connections"]["supabase"]["SUPABASE_URL"]
        key = st.secrets["connections"]["supabase"]["SUPABASE_KEY"]
        self.db: Client = create_client(url, key)

    # Function to query the Supabase database
    # Only rerun when the query changes or after 10 minutes.
    def run_query(self, table_name, **kwargs):
        query = self.db.table(table_name).select('*')
        for key, value in kwargs.items():
            query = query.eq(key, value)
        return query.execute()

    # Function to get the list of countries
    def get_countries(self):
        result = self.run_query('inflation').data

        # Extract country names from the result
        countries = sorted(set(item['country'] for item in result))
        countries.sort()  # Sort countries alphabetically
        return countries

    def regression_model(self, df):
        df = df[['year', 'average_inflation']]
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

    def regression_model_poly(self, df):
        df = df[['year', 'average_inflation']]
        df = df.dropna()
        # Set variables
        X = df[['year']]
        y = df['average_inflation']

        # Add polynomial features
        poly = PolynomialFeatures(degree=3)
        X_poly = poly.fit_transform(X)

        # Train the model
        model = LinearRegression()
        model.fit(X_poly, y)

        # Make predictions for the next 10 years
        future_years = np.arange(df['year'].max() + 1, df['year'].max() + 11).reshape(-1, 1)
        future_years_poly = poly.transform(future_years)
        future_predictions = model.predict(future_years_poly)

        # Create a DataFrame for future predictions
        future_df = pd.DataFrame({
            'year': future_years.flatten(),
            'average_inflation': future_predictions
        })

        # Combine historical data with future predictions
        combined_df = pd.concat([df, future_df])

        return combined_df

    def plot_regression_poly(self, df, selected_country):
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

    def arima_model(self, df):
        df = df[['year', 'average_inflation']]
        df = df.dropna()
        # Ensure 'average_inflation' is numeric
        df['average_inflation'] = pd.to_numeric(df['average_inflation'], errors='coerce')
        df = df.dropna(subset=['average_inflation'])

        y = df['average_inflation'].values

        # Fit the ARIMA model
        model = ARIMA(y, order=(5, 1, 1))
        model_fit = model.fit()

        # Make predictions for the next 10 years
        future_steps = 10
        forecast = model_fit.forecast(steps=future_steps)

        # Create a DataFrame for future predictions
        future_years = np.arange(df['year'].max() + 1, df['year'].max() + 1 + future_steps)
        future_df = pd.DataFrame({
            'year': future_years,
            'average_inflation': forecast
        })

        # Combine historical data with future predictions
        combined_df = pd.concat([df, future_df])

        return combined_df

    def plot_arima(self, df, selected_country):
        # Plot using the ARIMA model dataframe
        combined_df = self.arima_model(df)

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

    def combined_forecast(self, df, selected_country):
        combined_df_poly = self.regression_model(df)
        combined_df_arima = self.arima_model(df)

        plt.figure(figsize=(10, 6))
        plt.plot(combined_df_poly['year'], combined_df_poly['average_inflation'], ls='--', color='#ff0000',
                 label='Polynomial Forecasted Inflation')
        plt.plot(combined_df_arima['year'], combined_df_arima['average_inflation'], ls='--', color='#00ff00',
                 label='ARIMA Forecasted Inflation')
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
        st.title(":earth_americas: World CPI Inflation")

        # Year picker
        selected_year = st.slider("Select a year", min_value=1956, max_value=2024, value=2024)

        # Display all users from the database
        result = self.run_query('inflation', year=selected_year).data

        # Convert the result into a DataFrame for easier handling
        df = pd.DataFrame(result)

        st.subheader(f"Inflation Data for {selected_year}")
        st.write(df[['year', 'country', 'average_inflation', 'annual_inflation']])

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

        counts2, bins2, patches2 = plt.hist(df_annual_inflation, bins=100, color='red', edgecolor='black', density=True,
                                            stacked=True)

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

        st.title(":japan: Countries Average CPI Inflation")

        # Description for countries
        st.write("Next you can select a country and see the inflation values for each recorded year. "
                 "The line plot shows how the inflation values developed over the years.")

        # Get list of countries for the selectbox
        countries = self.get_countries()
        selected_country = st.selectbox("Select a country", countries)

        if selected_country:
            # Display data for the selected country
            inflation_line = self.run_query('inflation', country=selected_country).data
            df_line = pd.DataFrame(inflation_line)
            df_line.sort_values(by='year', inplace=True)
            st.subheader(f"Inflation Data for {selected_country}")
            st.write(df_line[['year', 'country', 'average_inflation', 'annual_inflation']])

            # Create the line chart with both average and annual inflation
            st.line_chart(df_line.set_index('year')[['average_inflation', 'annual_inflation']],
                          color=['#00ffff', '#ff0000'], use_container_width=True)

            st.subheader(":chart_with_upwards_trend: Predictive models")
            st.write("Here you can see how one could implement models to predict future inflation values. "
                     "There are three different models, pros and cons are shown for each one.\n"
                     "These models should not be taken as financial advise (they are probably imprecise), "
                     "but should be have an educational purpose, "
                     "they could serve as ideas on how to analyze your own data.")

            # Run and plot regression model
            st.write("*Simple Linear Regression model*\n "
                     "\nPros:\n"
                     "* Simple linear regression is straightforward to implement and "
                     "understand, making it accessible for individuals without advanced statistical knowledge.\n"
                     "* The model provides a clear relationship between the year and inflation, "
                     "expressed as a linear equation. This makes it easy to explain and interpret "
                     "the impact of time on inflation.\n"
                     "* Requires minimal computational power and can be run on basic software tools.\n"
                     "\nCons:\n"
                     "* Linear Assumption - Inflation is influenced by numerous factors and might not follow "
                     "a linear trend over time. Assuming a simple linear relationship "
                     "can oversimplify the dynamics involved.\n"
                     "* Real-world data often exhibit non-linear patterns. "
                     "Simple linear regression fails to capture such complexities.\n"
                     "* Lack of Explanatory Variables - Inflation is affected by multiple variables such as "
                     "interest rates, monetary policy, supply and demand shocks, and geopolitical events. "
                     "Using only the year as a predictor ignores these critical factors, reducing the model’s "
                     "accuracy and reliability.\n"
                     "* Temporal Correlation vs. Causation - A linear regression model with year as the predictor "
                     "only shows correlation over time, not causation. It cannot explain why inflation changes, "
                     "merely that it has changed over time.\n"
                     "* The model may either overfit or underfit the data, leading to poor predictive performance.")
            self.regression_model(df_line)
            self.plot_regression(df_line, selected_country)

            st.write("*Polynomial Regression model*\n"
                     "\nPolynomial regression is an extension of linear regression where the relationship between "
                     "the independent variable 𝑋 and the dependent variable 𝑦 is modeled as an 𝑛-degree polynomial. "
                     "Instead of fitting a straight line to the data, polynomial regression fits a curve.\n"
                     "Since the model is quite simple, there are only two variables present, "
                     "there might no be much variation between this model and the Linear Regression model. "
                     "A degree of 3 was used, this is called a cubic model, allowing for more complex curves "
                     "with potential inflection points.\n"
                     "\nPros:\n"
                     "* This model can be more flexible, modelling non-linear relationships "
                     "by adding polynomial terms. It is also easy to understand and implement, "
                     "especially with existing linear regression tools.\n"
                     "* Better Fit - Potentially provides a better fit for data that is "
                     "not well-represented by a straight line.\n"
                     "\nCons:\n"
                     "* Overfitting - Higher-degree polynomials can overfit the data, capturing noise rather "
                     "than the underlying trend.\n"
                     "* Extrapolation Risk - Predictions outside the range of the data can be unreliable and extreme.")

            # Run and plot polynomial model
            self.regression_model_poly(df_line)
            self.plot_regression_poly(df_line, selected_country)

            st.write("*ARIMA (AutoRegressive Integrated Moving Average)*\n"
                     "\nARIMA is a time series forecasting method that combines three components: AutoRegressive (AR), "
                     "Integrated (I), and Moving Average (MA). "
                     "It is used for analyzing and forecasting time series data that may have autocorrelations, "
                     "trends, and seasonality.\n"
                     "* AR (AutoRegressive): The model uses the dependency between an observation and a number of "
                     "lagged observations (previous values).\n"
                     "* I (Integrated): The model uses differencing of observations "
                     "(subtracting an observation from an observation at the previous time step) "
                     "to make the time series stationary.\n"
                     "* MA (Moving Average): The model uses dependency between an observation and a residual error "
                     "from a moving average model applied to lagged observations.\n"
                     "\nIn the context of ARIMA models, the order is denoted as ARIMA(p, d, q), "
                     "where: 𝑝 is the number of lag observations included in the model "
                     "(the order of the autoregressive part). 𝑑 is the number of times the raw observations are "
                     "differenced to make the time series stationary (the order of differencing). "
                     "𝑞 is the size of the moving average window (the order of the moving average part).\n"
                     "\nThe model used was a ARIMA(5, 1, 1). This means the model uses the previous 5 lagged values"
                     " (years) of the series to predict the current value.\n"
                     "The series is differenced once to achieve stationarity, "
                     "meaning that the model looks at the difference between consecutive observations rather "
                     "than the observations themselves.\n"
                     "And the model includes one lagged forecast error in the model, due to some probable "
                     "autocorrelation and partial autocorrelation. Economic time series data like inflation often "
                     "exhibit autocorrelation due to economic cycles, monetary policies, and persistent shocks, "
                     "altough for most inflation data, we cannot call it stationary.\n"
                     "Ideally there would be a model evaluation for every country to better "
                     "determine if ARIMA is the best solution and determine p and q values.\n"
                     "\nThe model in short:\n"
                     "\nARIMA(5, 1, 1) Model\n"
                     "* AR(5): The model uses the previous 5 values of the time series (lagged observations) "
                     "to predict the current value, accounting for longer-term dependencies.\n"
                     "* I(1): Differencing once to remove trends and make the time series stationary.\n"
                     "* MA(1): The model uses the error term from the previous time step to predict the current value, "
                     "capturing short-term dependencies.\n"
                     "\nPros:\n"
                     "* Captures Temporal Dependencies - Effectively models time series data "
                     "with trends and seasonality.\n"
                     "* Flexibility - Can handle different types of time series data through differencing "
                     "and the combination of AR and MA components.\n"
                     "* Forecast Accuracy - Often provides accurate forecasts for time series data.\n"
                     "\nCons:\n"
                     "* Complexity - Requires understanding and tuning of multiple parameters (p, d, q), "
                     "which can be complex.\n"
                     "* Data Preprocessing - Needs data to be stationary, which requires preprocessing "
                     "such as differencing.\n"
                     "* More Computationally Intensive - Can be computationally intensive, especially with "
                     "large datasets or complex models.")

            # Run and plot ARIMA model
            self.arima_model(df_line)
            self.plot_arima(df_line, selected_country)

            st.write("Finally, in this plot you can see how the Polynomial and the ARIMA model compare.")
            # Plot combined forecast
            self.combined_forecast(df_line, selected_country)

    def sidebar(self):
        st.sidebar.title("Navigation")
        selection = st.sidebar.radio("Go to", ["Home", "Inflation Data", "References"])

        if selection == "Home":
            st.header("Home")
            st.write("Welcome to the Inflation Data App.")
            st.write("""
                    This application provides an overview and analysis of inflation data across different countries 
                    using the consumer price index (CPI).
                    
                    Data was scrapped from the [inflation.eu](https://www.inflation.eu/) website 
                    and stored in a MySQL database. 
                    You can check the code in the [GitHub repo](https://github.com/ds-kenwatanabe/world_inflation).
                    
                    **What is CPI?**
                    
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
                    - View world inflation data for a selected year.
                    - Select a country to see CPI inflation data.
                    - Forecast future inflation trends.

                    Use the sidebar to navigate between different sections of the app.
                    """)
            st.image("images/00044-1625230760.png")
        elif selection == "Inflation Data":
            self.display_inflation_data()
        elif selection == "References":
            st.header("References")
            st.markdown(":globe_with_meridians: [inflation.eu website](https://www.inflation.eu/en/)")
            st.markdown(":file_folder: [GitHub repo](https://github.com/ds-kenwatanabe/world_inflation)")
            st.markdown(":link: [About histograms](https://en.wikipedia.org/wiki/Histogram)")
            st.markdown(":link: [Probability Density Function (PDF)]"
                        "(https://en.wikipedia.org/wiki/Probability_density_function)")
            st.markdown(":link: [Polynomial Regression](https://en.wikipedia.org/wiki/Polynomial_regression)")
            st.markdown(":link: [ARIMA Models](https://www.ibm.com/topics/arima-model)")
            st.markdown(":link: [Guide to Time Series Forecasting Models](https://medium.com/"
                        "@wainaina.pierre/the-complete-guide-to-time-series-forecasting-models-ef9c8cd40037)")

    def ui(self):
        self.sidebar()


if __name__ == '__main__':
    app = InflationApp()
    app.ui()
