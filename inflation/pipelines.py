# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import firebase_admin
from firebase_admin import credentials, firestore


class InflationPipeline:
    def process_item(self, item, spider):
        # Initialize adapter
        adapter = ItemAdapter(item)

        # Convert year to int
        year = adapter.get('year')
        if year is not None:
            try:
                adapter['year'] = int(year)
            except ValueError:
                print(f"{year} could not be converted to int.")
                adapter['year'] = None

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
                        # Remove the first dot if the number is in the thousands format
                        # Values over 1000 are set to 1.000.00, when casting to float it causes a value error
                        if value.count('.') > 1:
                            value = value.replace('.', '', 1)
                        adapter[key] = float(value.replace(',', '.'))  # Replace comma with dot for float conversion
                    except ValueError:
                        print(f"{value} could not be converted to float.")
                        adapter[key] = None

        return item


class SaveToFirebasePipeline:
    def __init__(self):
        self.db = None
        self.initialize_firebase()

    def initialize_firebase(self):
        # Use a service account
        cred = credentials.Certificate("/home/chris/PycharmProjects/world_inflation/inflation/"
                                       "inflation-9a2aa-firebase-adminsdk-1ne09-7a5cd5cd36.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        country = adapter.get('country')
        year = adapter.get('year')
        average_inflation = adapter.get('average_inflation')
        annual_inflation = adapter.get('annual_inflation')

        doc_ref = self.db.collection('inflation').document(f"{country}_{year}")
        doc = doc_ref.get()

        if doc.exists:
            print(f"Item already exists: {country} {year}")
        else:
            try:
                doc_ref.set({
                    'country': country,
                    'year': year,
                    'average_inflation': average_inflation,
                    'annual_inflation': annual_inflation
                })
                print(f"Item saved: {country} {year}")
            except Exception as e:
                print(f"Error inserting item: {e}")

        return item

    def close_spider(self, spider):
        # No explicit closing required for Firebase connections
        pass
