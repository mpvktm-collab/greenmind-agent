# src/tools/pollution_index.py
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from datetime import datetime
import random

class PollutionIndexTool(BaseTool):
    """Tool for getting pollution and environmental health index"""
    
    name: str = "Pollution_Health_Index"
    description: str = """
    Retrieves current pollution levels and environmental health indices for any location.
    Use this when asked about air quality, pollution levels, AQI, or environmental health of a city, state, or country.
    Input should be a location name (city, state, or country).
    """
    
    def _run(self, location: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get pollution data for a location"""
        try:
            # Simulate AQI based on location name (for demo purposes)
            random.seed(hash(location) % 100)
            
            aqi = random.randint(35, 180)
            
            if aqi <= 50:
                category = "Good"
                recommendation = "Ideal for outdoor activities"
            elif aqi <= 100:
                category = "Moderate"
                recommendation = "Sensitive groups should limit prolonged outdoor exertion"
            elif aqi <= 150:
                category = "Unhealthy for Sensitive Groups"
                recommendation = "Children, elderly, and people with respiratory issues should limit outdoor activities"
            elif aqi <= 200:
                category = "Unhealthy"
                recommendation = "Everyone should limit outdoor activities"
            else:
                category = "Very Unhealthy"
                recommendation = "Avoid outdoor activities"
            
            response = f"""
ENVIRONMENTAL HEALTH INDEX for {location.upper()}
Data retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CURRENT CONDITIONS:
* Air Quality Index (AQI): {aqi} - {category}
* PM2.5: {random.randint(5, 50)} μg/m³
* PM10: {random.randint(10, 80)} μg/m³
* Ozone: {random.randint(20, 70)} μg/m³
* Nitrogen Dioxide: {random.randint(10, 60)} μg/m³

HEALTH RECOMMENDATIONS:
{recommendation}

FORECAST (Next 3 days):
* Today: AQI {aqi} ({category})
* Tomorrow: AQI {aqi + random.randint(-10, 10)} (Moderate)
* Day after: AQI {aqi + random.randint(-15, 15)} (Moderate)

Note: This is simulated data for demonstration. For production, connect to real APIs like OpenAQ, WAQI, or OpenWeatherMap.
"""
            return response
            
        except Exception as e:
            return f"Error fetching pollution data: {str(e)}"
    
    async def _arun(self, location: str) -> str:
        return self._run(location)