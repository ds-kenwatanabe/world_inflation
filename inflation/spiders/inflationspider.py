import scrapy


class InflationSpider(scrapy.Spider):
    name = "inflationspider"
    allowed_domains = ["www.inflation.eu"]
    start_urls = ["https://www.inflation.eu/en/inflation-rates/cpi-inflation-2024.aspx"]

    # Initialize a set to store visited URLs
    visited_urls = set()

    def parse(self, response):
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

                yield {
                    'current_inflation_and_country': country_year,
                    'annual_inflation': annual_inflation,
                    'average_inflation': average_inflation
                }

        # Extract all links from the pagination table
        pagination_links = response.css('table.notelinkstable a.notelinks::attr(href)').getall()

        for next_page in pagination_links:
            next_page_url = response.urljoin(next_page)

            # Check if the next page has been visited
            if next_page_url not in self.visited_urls:
                # Add the next page URL to the visited set
                self.visited_urls.add(next_page_url)
                yield response.follow(next_page_url, callback=self.parse)
