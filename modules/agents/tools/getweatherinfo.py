import requests
from datetime import datetime, timezone
from geopy.geocoders import Nominatim

# Set up the geocoder
geolocator = Nominatim(user_agent="BorAI")

def get_latitude_longitude(location):
    # Query the geocoder with the location
    location = geolocator.geocode(location)
    
    # Extract the latitude and longitude from the location
    latitude = location.latitude
    longitude = location.longitude
    
    return latitude, longitude

def get_weather_info(location="Budapest", start_date=None, end_date=None):
    """
    Get weather information for a given location and time.
    
    Parameters:
    location (str): The location to get weather information for. Defaults to "Budapest".
    start_date (str): The start date to get weather information for in ISO format. Defaults to current date in UTC.
    end_date (str): The end date to get weather information for in ISO format. Defaults to current date in UTC.
    
    Returns:
    dict: A dictionary containing weather information for the given location and time.
    """
    if start_date is None:
        start_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        
    latitude, longitude = get_latitude_longitude(location) # get latitude and longitude using geopy
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,relativehumidity_2m,precipitation_probability,precipitation,snow_depth,cloudcover,visibility,windspeed_10m,winddirection_10m&start_date={start_date}&end_date={end_date}"
    response = requests.get(url)
    return response.json()
