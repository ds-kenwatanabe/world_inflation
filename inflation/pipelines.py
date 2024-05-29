# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import mysql.connector


class InflationPipeline:
    def process_item(self, item, spider):
        # Initialize adapter
        adapter = ItemAdapter(item)
        # Substitute unavailable values ('-') and convert to float
        inflation_keys = ['annual_inflation', 'average_inflation']
        for key in inflation_keys:
            value = adapter.get(key)
            if value == '-':
                adapter[key] = None
            else:
                try:
                    adapter[key] = float(value)
                except ValueError:
                    print(f"{value} Could not be converted to float.")

        # Change year to integer
        years = ['year']
        for year in years:
            y = adapter.get(year)
            adapter[year] = int(y)

        return item


class SaveToMySQLPipeline:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='password',  # Add your password
                database='inflation'
            )
            self.cur = self.conn.cursor()
            self.cur.execute(
                '''
                CREATE TABLE IF NOT EXISTS inflation(
                id INTEGER NOT NULL AUTO_INCREMENT,
                country VARCHAR(255),
                year INTEGER,
                average_inflation DECIMAL(10, 2),
                annual_inflation DECIMAL(10, 2),
                PRIMARY KEY (id)
                )
                '''
            )
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.conn.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        try:
            self.cur.execute(
                '''
                INSERT INTO inflation (
                    country,
                    year,
                    average_inflation,
                    annual_inflation
                ) VALUES (%s, %s, %s, %s)
                ''', (
                    adapter.get('country'),
                    adapter.get('year'),
                    adapter.get('average_inflation'),
                    adapter.get('annual_inflation')
                )
            )
            self.conn.commit()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
