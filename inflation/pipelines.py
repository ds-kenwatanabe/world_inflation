import os
from dotenv import load_dotenv
from supabase import create_client
from itemadapter import ItemAdapter


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


class SaveToSupabasePipeline:
    def __init__(self):
        self.client = None
        self.load_environment_variables()
        self.initialize_supabase()

    def load_environment_variables(self):
        # Load environment variables from .env file
        load_dotenv()

    def initialize_supabase(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        if not url or not key:
            raise ValueError("Supabase URL and Key must be set in environment variables")
        self.client = create_client(url, key)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        country = adapter.get('country')
        year = adapter.get('year')
        average_inflation = adapter.get('average_inflation')
        annual_inflation = adapter.get('annual_inflation')

        try:
            # Check if the item already exists in the database
            response = self.client.table('inflation').select('*').eq('country', country).eq('year', year).execute()

            if response.data:
                print(f"Item already exists: {country} {year}")
            else:
                # Insert the item into the database
                self.client.table('inflation').insert({
                    'country': country,
                    'year': year,
                    'average_inflation': average_inflation,
                    'annual_inflation': annual_inflation
                }).execute()
                print(f"Item saved: {country} {year}")

        except Exception as e:
            print(f"Error processing item: {e}")

        return item
