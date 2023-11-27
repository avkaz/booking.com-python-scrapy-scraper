# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from datetime import datetime
import re

class BookingScrapyScraperPipeline:

    def __init__(self):
        self.previous_roomtype = None

    def process_item(self, item, spider):
        if item is not None:
            adapter = ItemAdapter(item)

            # hotelname and roomtype cleaning
            hotel = adapter.get('hotelname')

            if hotel is not None:
                cleaned_hotel = hotel.strip()
                adapter['hotelname'] = cleaned_hotel

            # Roomtype -> save roomtype from first cell and input it to next cells until new roomtype appears
            current_roomtype = adapter.get('roomtype')

            if current_roomtype:
                cleaned_roomtype = current_roomtype.strip()
                self.previous_roomtype = cleaned_roomtype

            item['roomtype'] = self.previous_roomtype

            # stars -> int()
            starsString = adapter.get('stars')
            adapter['stars'] = int(starsString)

            # Rating -> float()
            ratingString = adapter.get('rating')

            if ratingString:
                if isinstance(ratingString, str):
                    # If it's a string, replace ',' with '.' and convert to float
                    try:
                        adapter['rating'] = float(ratingString.replace(',', '.'))
                    except ValueError:
                        print(f"Unable to convert {ratingString} to float.")
                elif isinstance(ratingString, float):
                    # If it's already a float, leave it as is
                    adapter['rating'] = ratingString
                else:
                    print(f"Unsupported data type for rating: {type(ratingString)}")

            # Reviews -> extract numbers and merge
            reviewsString = adapter.get('reviews')

            if reviewsString and isinstance(reviewsString, str):
                numbers = re.findall(r'\d+', reviewsString)
                adapter['reviews'] = int(''.join(numbers)) if numbers else None
            elif reviewsString and isinstance(reviewsString, int):
                adapter['reviews'] = reviewsString

            # Occupancy -> extract number of occupancy
            occupancyString = adapter.get('occupancy')
            occupancy_match = re.search(r'\d+', occupancyString)
            adapter['occupancy'] = int(occupancy_match.group()) if occupancy_match else None

            #Price -> devide on number and currency
            priceString = adapter.get('price')

            if priceString and isinstance(priceString, str):
                numbers = re.findall(r'\d+', priceString)
                currency = ''.join(re.findall(r'[^\d.,]+', priceString)).strip()

                adapter['price'] = int(''.join(numbers)) if numbers else None
                adapter['currency'] = currency if currency else None
            else:
                adapter['price'] = None
                adapter['currency'] = None

            # URL to check-in and check-out
            url = item.get('url')

            # Define regex patterns for extracting checkin and checkout dates
            checkin_pattern = re.compile(r'[?&;]checkin=([^&;]+)')
            checkout_pattern = re.compile(r'[?&;]checkout=([^&;]+)')

                # Search for the patterns in the URL
            checkin_match = checkin_pattern.search(url)
            checkout_match = checkout_pattern.search(url)

            # If the patterns are found, extract checkin and checkout dates
            checkin_date_str = checkin_match.group(1) if checkin_match else None
            checkout_date_str = checkout_match.group(1) if checkout_match else None


            # If the pattern is found, extract checkin and checkout dates
            adapter['checkin_date'] = datetime.strptime(checkin_date_str, "%Y-%m-%d").date() if checkin_date_str else None
            adapter['checkout_date'] = datetime.strptime(checkout_date_str, "%Y-%m-%d").date() if checkout_date_str else None


            return item