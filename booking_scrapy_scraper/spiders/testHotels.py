import scrapy

class testHotels(scrapy.Spider):
    name = "testHotels"
    allowed_domains = ["booking.com"]
    start_urls = [
        'https://www.booking.com/searchresults.cs.html?ss=Praha&ssne=Praha&ssne_untouched=Praha&label=gog235jc-1DCAEoggI46AdIM1gDaDqIAQGYAQW4AQfIAQzYAQPoAQGIAgGoAgO4ArOak6oGwAIB0gIkY2M5MGNmZTYtNzM0Mi00OGY1LTlkZTgtYjA1ZTRiM2JkZGEx2AIE4AIB&sid=a326d50f4f5fac494b51155a82a4508a&aid=397594&lang=cs&sb=1&src_elem=sb&src=searchresults&dest_id=-553173&dest_type=city&checkin=2023-12-06&checkout=2023-12-07&group_adults=2&no_rooms=1&group_children=0'
    ]

    def parse(self, response):
        # Corrected selector to get the first hotel link
        first_hotel_link = response.css(
            'div[data-testid="property-card"] a[data-testid="title-link"]::attr(href)').extract_first()

        if first_hotel_link:
            yield scrapy.Request(url=first_hotel_link, callback=self.parse_hotel_page)
        else:
            self.logger.warning("Could not find the first hotel link.")

    # def parse_hotel_page(self, response):
        # Extract the HTML content of the entire page
        rooms = response.css("table.hprt-table tbody tr")

        for room in rooms:
            roomtype = room.css("td.hprt-table-cell-roomtype span:first-child::text").get()
            occupancy = room.css("td.hprt-table-cell-occupancy span.bui-u-sr-only::text").get()
            price = room.css("td.hprt-table-cell-price span:first-child::text").get()
            breakfast = room.css("td.hprt-table-cell-conditions div.bui-list__description::text").get()

            # Check if all required data is present before yielding the item
            if all([roomtype, occupancy, price, breakfast]):
                yield {
                    "Room type": roomtype.strip(),
                    "Occupancy": occupancy.strip(),
                    "Price": price.strip(),
                    "Breakfast": breakfast.strip()
                }
            else:
                self.logger.warning(f"Skipping incomplete data for a room. Roomtype: {roomtype}, Occupancy: {occupancy}, Price: {price}, Breakfast: {breakfast}")
