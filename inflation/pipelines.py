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
        # Substitute unavailable values ('-' and 'nan') and convert to float
        inflation_keys = ['annual_inflation', 'average_inflation']
        for key in inflation_keys:
            value = adapter.get(key)
            if value is not None:
                value = value.strip()  # Remove any leading/trailing whitespace
                if value.lower() == 'nan' or value == '-':
                    adapter[key] = None
                else:
                    try:
                        adapter[key] = float(value)
                    except ValueError:
                        print(f"{value} could not be converted to float.")
                        adapter[key] = None

        # Change year to integer
        year_value = adapter.get('year')
        try:
            adapter['year'] = int(year_value)
        except (TypeError, ValueError):
            print(f"{year_value} could not be converted to integer.")
            adapter['year'] = None

        return item


class SaveToMySQLPipeline:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.open_connection()

    def open_connection(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='mysql',  # Add your password
                database='inflation'
            )
            self.cur = self.conn.cursor()
            self.create_table()
        except mysql.connector.Error as err:
            print(f"Error with MySQL connector: {err}")

    def create_table(self):
        try:
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
            print(f"Error creating table: {err}")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if self.conn is None or self.cur is None:
            self.open_connection()

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
            print(f"Error inserting item: {err}")

        return item

    def close_spider(self, spider):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
