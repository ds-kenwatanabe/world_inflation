# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


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
