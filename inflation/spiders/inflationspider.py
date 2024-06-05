import scrapy
import re
import random
from inflation.items import InflationItem


class InflationSpider(scrapy.Spider):
    name = "inflationspider"
    allowed_domains = ["www.inflation.eu"]
    start_urls = ["https://www.inflation.eu/en/inflation-rates/cpi-inflation-2024.aspx"]

    # Initialize a set to store visited URLs
    visited_urls = set()

    def parse(self, response):
        # List of users
        user_agent_list = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 '
            'Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_4_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) '
            'Version/14.0.3 Mobile/15E148 Safari/604.1',
            'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 '
            'Safari/537.36 Edg/87.0.664.75',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 '
            'Safari/537.36 Edge/18.18363',
        ]

        # Add the current URL to the visited URLs set
        self.visited_urls.add(response.url)

        # Classes with inflation data
        tabledata1 = response.css('tr.tabledata1')
        tabledata2 = response.css('tr.tabledata2')

        # Combine both tabledata1 and tabledata2 to loop through
        all_rows = tabledata1 + tabledata2

        for row in all_rows:
            country_year = row.css('a::text').get()
            td_values = row.css('td[align="right"]::text').getall()

            if len(td_values) == 2:
                # Remove other characters and leave inflation value
                annual_inflation = td_values[0].replace('\xa0%', '').strip()
                average_inflation = td_values[1].replace('\xa0%', '').strip()

                # Extract country and year using regex
                match = re.match(r'CPI inflation (.+?) (\d{4})', country_year)
                if match:
                    # If the string matches the regex pattern, extract
                    country = match.group(1)
                    year = match.group(2)

                    # Initialize InflationItems
                    inflation_item = InflationItem()
                    inflation_item['country'] = country
                    inflation_item['year'] = year
                    inflation_item['annual_inflation'] = annual_inflation
                    inflation_item['average_inflation'] = average_inflation

                    yield inflation_item

        # Extract all links from the pagination table
        pagination_links = response.css('table.notelinkstable a.notelinks::attr(href)').getall()

        for next_page in pagination_links:
            next_page_url = response.urljoin(next_page)

            # Check if the next page has been visited
            if next_page_url not in self.visited_urls:
                # Add the next page URL to the visited set
                self.visited_urls.add(next_page_url)
                yield response.follow(next_page_url, callback=self.parse,
                                      headers={"User-Agent": user_agent_list[random.randint(
                                          0, len(user_agent_list) - 1)]})
