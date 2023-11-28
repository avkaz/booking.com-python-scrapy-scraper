import scrapy
from datetime import datetime, timedelta
from booking_scrapy_scraper.items import BookingScrapyScraperItem


class BookingSpider(scrapy.Spider):
    name = "bookingSpider"

    # Custom settings for the spider
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['hotelname', 'stars', 'rating', 'reviews', 'roomtype', 'checkin_date', 'checkout_date',
                               'occupancy', 'price', 'breakfast', 'currency', 'url'],
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'CONCURRENT_REQUESTS_PER_IP': 1,
    }

    # The domain(s) that this spider is allowed to crawl
    allowed_domains = ["booking.com"]

    # The starting URL(s) for the spider
    start_urls = [
        'https://www.booking.com/searchresults.cs.html?label=gog235jc-1FCAEoggI46AdIM1gDaDqIAQGYAQW4AQfIAQzYAQHoAQH4AQ2IAgGoAgO4ArOak6oGwAIB0gIkY2M5MGNmZTYtNzM0Mi00OGY1LTlkZTgtYjA1ZTRiM2JkZGEx2AIG4AIB&sid=c0b14234663a36fc66ae8b417d55092c&aid=397594&ss=Praha%2C+%C4%8Cesk%C3%A1+republika&ssne=%C4%8Cesk%C3%A1+republika&ssne_untouched=%C4%8Cesk%C3%A1+republika&lang=cs&src=searchresults&dest_id=-553173&dest_type=city&checkin=2023-12-10&checkout=2023-12-11&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D201%3Broomfacility%3D38%3Bhotelfacility%3D2%3Breview_score%3D80%3Bhotelfacility%3D107&offset=0'
    ]

    # Generate initial requests
    def start_requests(self):
        # setting the range of searching
        start_date = datetime(2023, 12, 10).date()
        end_date = start_date + timedelta(days=2)
        starting_offset = 0

        for current_date in range((end_date - start_date).days):
            checkin_date = (start_date + timedelta(days=current_date)).strftime("%Y-%m-%d")
            checkout_date = (start_date + timedelta(days=current_date + 1)).strftime("%Y-%m-%d")

            # Make initial request to get necessary attribute
            initial_url = f'https://www.booking.com/searchresults.cs.html?label=gog235jc-1FCAEoggI46AdIM1gDaDqIAQGYAQW4AQfIAQzYAQHoAQH4AQ2IAgGoAgO4ArOak6oGwAIB0gIkY2M5MGNmZTYtNzM0Mi00OGY1LTlkZTgtYjA1ZTRiM2JkZGEx2AIG4AIB&sid=c0b14234663a36fc66ae8b417d55092c&aid=397594&ss=Praha%2C+%C4%8Cesk%C3%A1+republika&ssne=%C4%8Cesk%C3%A1+republika&ssne_untouched=%C4%8Cesk%C3%A1+republika&lang=cs&src=searchresults&dest_id=-553173&dest_type=city&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D201%3Broomfacility%3D38%3Bhotelfacility%3D2%3Breview_score%3D80%3Bhotelfacility%3D107&offset={starting_offset}'
            yield scrapy.Request(url=initial_url, callback=self.parse_initial_response,
                                 meta={'checkin_date': checkin_date, 'checkout_date': checkout_date})

    # Parse the initial response to extract needed attributes
    def parse_initial_response(self, response):
        # Extract the needed attribute from the response
        # Replace 'your_attribute_selector' with the actual selector for the attribute you need
        pages_number_text = response.css(
            'div[data-testid="pagination"] ol li:last-child button::attr(aria-label)').get()
        max_offset = (int(pages_number_text)) * 25

        # Calculate the offset range based on the extracted attribute
        offset_range = range(0, max_offset, 25)

        # Continue with generating requests using the calculated offset range
        for offset in offset_range:
            checkin_date = response.meta['checkin_date']
            checkout_date = response.meta['checkout_date']
            url = f'https://www.booking.com/searchresults.cs.html?label=gog235jc-1FCAEoggI46AdIM1gDaDqIAQGYAQW4AQfIAQzYAQHoAQH4AQ2IAgGoAgO4ArOak6oGwAIB0gIkY2M5MGNmZTYtNzM0Mi00OGY1LTlkZTgtYjA1ZTRiM2JkZGEx2AIG4AIB&sid=c0b14234663a36fc66ae8b417d55092c&aid=397594&ss=Praha%2C+%C4%8Cesk%C3%A1+republika&ssne=%C4%8Cesk%C3%A1+republika&ssne_untouched=%C4%8Cesk%C3%A1+republika&lang=cs&src=searchresults&dest_id=-553173&dest_type=city&checkin={checkin_date}&checkout={checkout_date}&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D201%3Broomfacility%3D38%3Bhotelfacility%3D2%3Breview_score%3D80%3Bhotelfacility%3D107&offset={offset}'

            yield scrapy.Request(url=url, callback=self.parse,
                                 meta={'checkin_date': checkin_date, 'checkout_date': checkout_date})

    # Parse the response to extract hotel links
    def parse(self, response):
        # Corrected selector to get the first hotel link
        hotel_links = response.css(
            'div[data-testid="property-card"] a[data-testid="title-link"]::attr(href)')

        for hotel_link in hotel_links:
            if hotel_link:
                yield scrapy.Request(url=hotel_link.get(), callback=self.parse_hotel_page)
            else:
                self.logger.warning("Could not find hotel link.")

    # Parse the hotel page to extract detailed information
    def parse_hotel_page(self, response):
        # Extract the HTML content of the entire page
        hotel_item = BookingScrapyScraperItem()
        hotel_item['hotelname'] = response.css(
            "div[data-capla-component-boundary='b-property-web-property-page/PropertyHeaderName'] h2.pp-header__title::text").get()
        hotel_item['stars'] = len(
            response.css("div[data-testid='quality-rating'] span[data-testid='rating-stars'] span"))
        hotel_item['rating'] = response.css(
            "div[data-testid='review-score-right-component'] div:first-child::text").get()
        hotel_item['reviews'] = response.css(
            "div[data-testid='review-score-right-component'] div:nth-child(2) div:nth-child(2)::text").get()

        rooms = response.css("table.hprt-table tbody tr")

        for room in rooms:
            hotel_item['url'] = response.url
            hotel_item['roomtype'] = room.css("td.hprt-table-cell-roomtype span:first-child::text").get()
            hotel_item['occupancy'] = room.css("td.hprt-table-cell-occupancy span.bui-u-sr-only::text").get()
            hotel_item['price'] = room.css("td.hprt-table-cell-price span:first-child::text").get()
            conditions = room.css("td.hprt-table-cell-conditions div.hprt-block ul li")
            hotel_item['breakfast'] = 0

            for condition in conditions:
                # Check if the condition contains a coffee icon with fill color '#008009'
                coffee_icon = condition.css("span svg[class*='food_coffee']")

                if coffee_icon and coffee_icon.attrib['fill'] == '#008009':
                    hotel_item['breakfast'] = 1
                    break  # No need to continue checking if breakfast is already found

            yield hotel_item
