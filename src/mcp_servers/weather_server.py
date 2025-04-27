# https://github.com/Zippland/weather-mcp
if __name__ == "__main__":
    import os
    import sys
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_script_dir)
    sys.path.append(project_dir)

# weather_mcp_server.py
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import requests
from datetime import datetime, timedelta, timezone
import os
from configs import get_logger
logger = get_logger("__WEATHER_MCP_SERVER__")


# Create MCP server instance
mcp = FastMCP(
    name="WeatherForecastServer",
    description="Provides global weather forecasts and current weather conditions",
    version="1.0.0"
)

# Define data models
class WindInfo(BaseModel):
    speed: str = Field(..., description="Wind speed in meters per second")
    direction: str = Field(..., description="Wind direction in degrees")

class WeatherEntry(BaseModel):
    time: str = Field(..., description="Time of the weather data")
    temperature: str = Field(..., description="Temperature in Celsius")
    feels_like: str = Field(..., description="Feels like temperature in Celsius")
    temp_min: str = Field(..., description="Minimum temperature in Celsius")
    temp_max: str = Field(..., description="Maximum temperature in Celsius")
    weather_condition: str = Field(..., description="Weather condition description")
    humidity: str = Field(..., description="Humidity percentage")
    wind: WindInfo = Field(..., description="Wind speed and direction information")
    rain: str = Field(..., description="Rainfall amount")
    clouds: str = Field(..., description="Cloud coverage percentage")

class WeatherForecast(BaseModel):
    today: List[WeatherEntry] = Field(..., description="Today's weather forecast, including current weather")
    tomorrow: List[WeatherEntry] = Field(..., description="Tomorrow's weather forecast")

# Helper function to get API key
def get_api_key(provided_key: Optional[str] = None) -> str:
    """
    Get API key, prioritizing provided key, then trying to read from environment variables
    
    Parameters:
        provided_key: User-provided API key (optional)
    
    Returns:
        API key string
    """
    if provided_key:
        return provided_key
    
    env_key = os.environ.get("OPENWEATHER_API_KEY")
    if env_key:
        return env_key
    
    raise ValueError("No API key provided and no OPENWEATHER_API_KEY found in environment variables")

# Core weather forecast function
def get_weather_forecast(present_location, time_zone_offset, api_key=None):
    # Get API key
    try:
        api_key = get_api_key(api_key)
    except ValueError as e:
        return {'error': str(e)}
    
    # Get geographic coordinates
    geocode_url = f"https://api.openweathermap.org/data/2.5/weather?q={present_location}&appid={api_key}&units=metric"
    
    try:
        # Request current weather data to get geographic coordinates
        response = requests.get(geocode_url)
        response.raise_for_status()
        data = response.json()
        
        lat = data['coord']['lat']
        lon = data['coord']['lon']
        
        # Get 5-day 3-hour forecast
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        
        response = requests.get(forecast_url)
        response.raise_for_status()
        forecast_data = response.json()
        
        # Set timezone
        tz = timezone(timedelta(hours=time_zone_offset))
        
        today = datetime.now(tz).date()
        tomorrow = today + timedelta(days=1)
        
        today_and_current_forecast = []
        tomorrow_forecast = []
        
        # Current weather
        current_weather = {
            'time': datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'),
            'temperature': f"{data['main']['temp']} °C",
            'feels_like': f"{data['main']['feels_like']} °C",
            'temp_min': f"{data['main']['temp_min']} °C",
            'temp_max': f"{data['main']['temp_max']} °C",
            'weather_condition': data['weather'][0]['description'],
            'humidity': f"{data['main']['humidity']}%",
            'wind': {
                'speed': f"{data['wind']['speed']} m/s",
                'direction': f"{data['wind']['deg']} degrees"
            },
            'rain': f"{data.get('rain', {}).get('1h', 0)} mm/h" if 'rain' in data else 'No rain',
            'clouds': f"{data['clouds']['all']}%"
        }
        
        today_and_current_forecast.append(current_weather)
        
        for entry in forecast_data['list']:
            dt = datetime.fromtimestamp(entry['dt'], tz)
            if dt.date() == today:
                today_and_current_forecast.append({
                    'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': f"{entry['main']['temp']} °C",
                    'feels_like': f"{entry['main']['feels_like']} °C",
                    'temp_min': f"{entry['main']['temp_min']} °C",
                    'temp_max': f"{entry['main']['temp_max']} °C",
                    'weather_condition': entry['weather'][0]['description'],
                    'humidity': f"{entry['main']['humidity']}%",
                    'wind': {
                        'speed': f"{entry['wind']['speed']} m/s",
                        'direction': f"{entry['wind']['deg']} degrees"
                    },
                    'rain': f"{entry.get('rain', {}).get('3h', 0)} mm/3h" if 'rain' in entry else 'No rain',
                    'clouds': f"{entry['clouds']['all']}%"
                })
            elif dt.date() == tomorrow:
                tomorrow_forecast.append({
                    'time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'temperature': f"{entry['main']['temp']} °C",
                    'feels_like': f"{entry['main']['feels_like']} °C",
                    'temp_min': f"{entry['main']['temp_min']} °C",
                    'temp_max': f"{entry['main']['temp_max']} °C",
                    'weather_condition': entry['weather'][0]['description'],
                    'humidity': f"{entry['main']['humidity']}%",
                    'wind': {
                        'speed': f"{entry['wind']['speed']} m/s",
                        'direction': f"{entry['wind']['deg']} degrees"
                    },
                    'rain': f"{entry.get('rain', {}).get('3h', 0)} mm/3h" if 'rain' in entry else 'No rain',
                    'clouds': f"{entry['clouds']['all']}%"
                })
        
        # Return current weather and forecast for today and tomorrow
        return {
            'today': today_and_current_forecast,
            'tomorrow': tomorrow_forecast
        }
    except requests.RequestException as e:
        return {'error': f"Request error: {str(e)}"}
    except ValueError as e:
        return {'error': f"JSON parsing error: {str(e)}"}
    except KeyError as e:
        return {'error': f"Data structure error: Missing key {str(e)}"}
    except Exception as e:
        return {'error': f"Unexpected error: {str(e)}"}

# Define MCP tools
@mcp.tool()
def get_weather(location: str, api_key: Optional[str] = None, timezone_offset: float = 0) -> Dict[str, Any]:
    """
    Get current weather and forecast for a specified location
    
    Parameters:
        location: Location name, e.g., "Beijing", "New York", "Tokyo"
        api_key: OpenWeatherMap API key (optional, will read from environment variable if not provided)
        timezone_offset: Timezone offset in hours, e.g., 8 for Beijing, -4 for New York. Default is 0 (UTC time)
    
    Returns:
        Dictionary containing today's and tomorrow's weather forecast
    """
    # Call weather forecast function
    return get_weather_forecast(location, timezone_offset, api_key)

@mcp.tool()
def get_current_weather(location: str, api_key: Optional[str] = None, timezone_offset: float = 0) -> Dict[str, Any]:
    """
    Get current weather for a specified location
    
    Parameters:
        location: Location name, e.g., "Beijing", "New York", "Tokyo"
        api_key: OpenWeatherMap API key (optional, will read from environment variable if not provided)
        timezone_offset: Timezone offset in hours, e.g., 8 for Beijing, -4 for New York. Default is 0 (UTC time)
    
    Returns:
        Current weather information
    """
    # Get full weather information
    full_weather = get_weather(location, api_key, timezone_offset)
    
    # Check if an error occurred
    if 'error' in full_weather:
        return full_weather
    
    # Only return current weather (first entry of today)
    if full_weather['today'] and len(full_weather['today']) > 0:
        return full_weather['today'][0]
    else:
        return {"error": "Unable to get current weather information"}

# Start server
if __name__ == "__main__":
    # Check if environment variable is set and print log information
    if os.environ.get("OPENWEATHER_API_KEY"):
        logger.info("API key found in environment variables")
        logger.info("API tools are ready, can be called without api_key parameter")
    else:
        logger.info("No API key found in environment variables")
        logger.info("API key parameter required when calling tools")
    
    logger.info("Weather Forecast MCP Server running...")
    mcp.run(transport='stdio') 