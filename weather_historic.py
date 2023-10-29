#!/usr/bin/python
# Imports
import logging
import logging.config
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import pandas as pd
from geopy.geocoders import Nominatim
from meteostat import Point, Daily

logging.config.fileConfig('weatherHistoricLogger.conf')
logger = logging.getLogger('weatherLogger')


# Class
class WeatherHistoric:
    def __init__(self):
        """default constructor"""
        self.__useragent = 'weather_historic'
        self.__geolocator = Nominatim(user_agent=self.__useragent)

    def get_coordinates_from_city(self, city_name: str) -> tuple[float, float]:
        """
    The get_coordinates_from_city function takes in a city name and returns the latitude and longitude of that city.

    :param self: Represent the instance of the class
    :param city_name: str: Pass the name of the city to fetch coordinates for
    :return: A tuple of floats
    :doc-author: Berk Mehmet Gurlek
    """
        try:
            logger.info(msg=f'Fetching location data for city: {city_name}')
            location = self.__geolocator.geocode(city_name)
            return location.point[0], location.point[1]

        except Exception as e:
            logger.error(msg=f'Could not fetch location data for city: {city_name} \t with exception:{e}')

    def get_historic_weather_data(self, city_name: str, start_date: datetime,
                                  end_date: datetime) -> pd.DataFrame:
        """
    The get_historic_weather_data function takes in a city name, start date and end date as input.
    It then uses the get_coordinates_from_city function to fetch the latitude and longitude of that city.
    The latitude and longitude are used to create a Point object which is passed into the Daily class from
    the weather-api package along with start date and end date. The Daily class fetches historic data for that location
    between those dates using DarkSky API (which is what weather-api uses). This data is returned as a pandas DataFrame.

    :param self: Represent the instance of the class
    :param city_name:str: Pass in the name of the city to get weather data for
    :param start_date: datetime: Specify the start date of the historic weather data
    :param end_date: datetime: Specify the end date of the weather data to be fetched
    :return: A pandas dataframe
    :doc-author: Berk Mehmet Gurlek
    """
        try:
            latitude, longitude = self.get_coordinates_from_city(city_name)
            location = Point(latitude, longitude)
            weather_data = Daily(location, start_date, end_date)
            weather_data = weather_data.fetch()
            return weather_data
        except Exception as e:
            logger.error(msg=f'''Could not fetch historic data for city:{city_name} between:{start_date}-{end_date}
            with exception:{e}''')


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-c", "--city_name", help="City Name")
    parser.add_argument("-s", "--start_date", type=str, help="Start date of weather data interval "
                                                             "format: YYYY/MM/DD")
    parser.add_argument("-e", "--end_date", type=str, help="End date of weather data interval "
                                                           "format: YYYY/MM/DD")
    parser.add_argument("-o", "--output_directory", type=str, help="Output directory", default='')

    args = vars(parser.parse_args())

    city_name = args["city_name"]
    start_str = args["start_date"]
    end_str = args["end_date"]
    output_dir = args["output_directory"]

    try:
        start_date = datetime.strptime(start_str, '%Y/%m/%d')
        end_date = datetime.strptime(end_str, '%Y/%m/%d')
        w = WeatherHistoric()
        data = w.get_historic_weather_data(city_name, start_date, end_date)
        data.to_csv(f'{output_dir}{city_name}_weather.csv')
    except Exception as e:
        logger.error(e)



