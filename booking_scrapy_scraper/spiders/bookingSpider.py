import scrapy
from booking_scrapy_scraper.items import BookingScrapyScraperItem

class bookingSpider(scrapy.Spider):
    name = "bookingSpider"
    custom_settings = {
        'FEED_EXPORT_FIELDS': ['hotelname', 'stars', 'rating', 'reviews', 'roomtype', 'checkin_date', 'checkout_date', 'occupancy', 'price', 'breakfast','currency', 'url']
    }
    allowed_domains = ["booking.com"]
    start_urls = [
        'https://www.booking.com/searchresults.cs.html?ss=Praha&ssne=Praha&ssne_untouched=Praha&label=gog235jc-1DCAEoggI46AdIM1gDaDqIAQGYAQW4AQfIAQzYAQPoAQGIAgGoAgO4ArOak6oGwAIB0gIkY2M5MGNmZTYtNzM0Mi00OGY1LTlkZTgtYjA1ZTRiM2JkZGEx2AIE4AIB&sid=a326d50f4f5fac494b51155a82a4508a&aid=397594&lang=cs&sb=1&src_elem=sb&src=searchresults&dest_id=-553173&dest_type=city&checkin=2023-12-10&checkout=2023-12-11&group_adults=2&no_rooms=1&group_children=0'
    ]

    def parse(self, response):
        # Corrected selector to get the first hotel link
        first_hotel_link = response.css(
            'div[data-testid="property-card"] a[data-testid="title-link"]::attr(href)').extract_first()

        if first_hotel_link:
            yield scrapy.Request(url=first_hotel_link, callback=self.parse_hotel_page)
        else:
            self.logger.warning("Could not find the first hotel link.")

    # def parse(self, response):
    #     # Corrected selector to get the first hotel link
    #     hotel_links = response.css(
    #         'div[data-testid="property-card"] a[data-testid="title-link"]::attr(href)')
    #
    #
    #     for hotel_link in hotel_links:
    #         if hotel_link:
    #             yield scrapy.Request(url=hotel_link.get(), callback=self.parse_hotel_page)
    #         else:
    #             self.logger.warning("Could not find the first hotel link.")
    #

    def parse_hotel_page(self, response):
        # Extract the HTML content of the entire page
        hotel_item = BookingScrapyScraperItem()
        hotel_item['hotelname'] = response.css("div[data-capla-component-boundary='b-property-web-property-page/PropertyHeaderName'] h2.pp-header__title::text").get()
        hotel_item['stars'] = len(response.css("div[data-testid='quality-rating'] span[data-testid='rating-stars'] span"))
        hotel_item['rating'] = response.css("div[data-testid='review-score-right-component'] div:first-child::text").get()
        hotel_item['reviews'] = response.css(
            "div[data-testid='review-score-right-component'] div:nth-child(2) div:nth-child(2)::text").get()

        rooms = response.css("table.hprt-table tbody tr")

        for room in rooms:
            hotel_item['url']= response.url
            hotel_item['roomtype'] = room.css("td.hprt-table-cell-roomtype span:first-child::text").get()
            hotel_item['occupancy'] = room.css("td.hprt-table-cell-occupancy span.bui-u-sr-only::text").get()
            hotel_item['price'] = room.css("td.hprt-table-cell-price span:first-child::text").get()
            conditions= room.css("td.hprt-table-cell-conditions div.hprt-block ul li")
            hotel_item['breakfast'] = 0

            for condition in conditions:
                # Check if the condition contains a coffee icon with fill color '#008009'
                coffee_icon = condition.css("span svg[class*='food_coffee']")

                if coffee_icon and coffee_icon.attrib['fill'] == '#008009':
                    hotel_item['breakfast'] = 1
                    break  # No need to continue checking if breakfast is already found

            yield hotel_item

# https://www.booking.com/hotel/cz/orea-place-sensa-hlavni-mesto-praha.cs.html?aid=397594&label=gog235jc-1FCAEoggI46AdIM1gDaDqIAQGYAQW4AQfIAQzYAQHoAQH4AQ2IAgGoAgO4ArOak6oGwAIB0gIkY2M5MGNmZTYtNzM0Mi00OGY1LTlkZTgtYjA1ZTRiM2JkZGEx2AIG4AIB&sid=c0b14234663a36fc66ae8b417d55092c&all_sr_blocks=725909301_310556482_2_0_0;checkin=2023-12-10;checkout=2023-12-11;dest_id=-553173;dest_type=city;dist=0;group_adults=2;group_children=0;hapos=2;highlighted_blocks=725909301_310556482_2_0_0;hpos=2;matching_block_id=725909301_310556482_2_0_0;nflt=ht_id%3D201%3Broomfacility%3D38%3Bhotelfacility%3D2%3Breview_score%3D80;no_rooms=1;req_adults=2;req_children=0;room1=A%2CA;sb_price_type=total;sr_order=popularity;sr_pri_blocks=725909301_310556482_2_0_0__15750;srepoch=1701090007;srpvid=2d7671896c9e007b;type=total;ucfs=1&#hotelTmpl