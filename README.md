## World Inflation 🌎

❗ Status:

![Static Badge](https://img.shields.io/badge/App-Test-yellow)
![Static Badge](https://img.shields.io/badge/README-Development-red)

### Introduction
This is a project that has the objective to scrape inflation data from different countries and show the data in a streamlit [app](https://worldinflation.streamlit.app/).
In the app you can see the average and annual CPI inflation for each country and through out the years.

### Tools used 🧰
<div id="tools" align="left">
  <span>Scrapy for Crawling/Scraping</span>
  <img src="https://scrapingant.com/blog/img/blog/scrapy-logo.png" title="Windows" alt="Windows" width="100" height="40"/>&nbsp;
  <br>
  <br>
  <span>Firebase as Database</span>
  <img src="https://github.com/devicons/devicon/blob/master/icons/firebase/firebase-plain-wordmark.svg" title="Firebase" alt="Firebase" width="50" height="50"/>&nbsp;
  <br>
  <br>
  <span>Streamlit for the app</span>
  <img src="https://github.com/devicons/devicon/blob/master/icons/streamlit/streamlit-plain-wordmark.svg" title="Streamlit" alt="Streamlit" width="50" height="50"/>&nbsp;
</div>


### Extract, Transform, Load
The data was scraped from the [inflation.eu](https://www.inflation.eu/en/) website using [Scrapy](https://scrapy.org/) which also loads the collected data in a [Firebase Database](https://firebase.google.com/). 
The [streamlit](https://streamlit.io/) app queries the data and displays it.

A diagram of the ETL process can be seen below:

![ETL Process](images/inflation_etl.svg)


#### Firestore Database
It is a scalable NoSQL cloud database, built on Google Cloud infrastructure, to store and sync data. This type of database can be complex, as the documents can have documents nested in them and are not as rigid as SQL databases.
In this case, the database structure is quite simple, if you wish to implement this code, you can change the pipelines to a SQL database like MongoDB or PostgreSQL and run the database locally.

The pipelines set the country name and year as the unique IDs for each document, 
for example Belgium_1999 is one unique ID and Belgium_2000 is another. Each document has four fields: 'annual_inflation', 'average_inflation', 'country', and 'year'.
