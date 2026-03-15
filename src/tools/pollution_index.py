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
    
    def _get_aqi_category(self, aqi):
        """Get AQI category and color based on value"""
        if aqi <= 50:
            return "Good", "🟢", "Low health risk"
        elif aqi <= 100:
            return "Moderate", "🟡", "Sensitive groups limit outdoor activity"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups", "🟠", "Children, elderly limit outdoor activity"
        elif aqi <= 200:
            return "Unhealthy", "🔴", "Everyone may experience health effects"
        elif aqi <= 300:
            return "Very Unhealthy", "🟣", "Health alert - serious effects"
        else:
            return "Hazardous", "⚫", "Emergency conditions - avoid outdoors"
    
    def _create_visual_bar(self, aqi, max_aqi=300):
        """Create a visual bar showing where current AQI stands"""
        bar_length = 30
        position = int((aqi / max_aqi) * bar_length)
        if position > bar_length:
            position = bar_length
        
        bar = ""
        for i in range(bar_length):
            if i < position:
                bar += "█"
            else:
                bar += "░"
        
        return bar
    
    def _get_range_table(self):
        """Get AQI range reference table with color emojis - each on new line"""
        return ("\n" +
                "AQI RANGE REFERENCE:\n" +
                "  0 - 50:   🟢 Good\n" +
                " 51 - 100:  🟡 Moderate\n" +
                "101 - 150:  🟠 Unhealthy for Sensitive Groups\n" +
                "151 - 200:  🔴 Unhealthy\n" +
                "201 - 300:  🟣 Very Unhealthy\n" +
                "300+ :      ⚫ Hazardous\n")
    
    def _calculate_aqi_from_location(self, location):
        """Calculate AQI based on location characteristics without hardcoding"""
        # Use the location string to generate a deterministic but varied AQI
        location_lower = location.lower()
        
        # Base calculation using hash of location
        location_hash = abs(hash(location_lower)) % 1000
        
        # Factors that influence AQI (all derived from location name)
        
        # 1. Length of name (longer names tend to be larger cities - rough heuristic)
        name_length_factor = min(len(location_lower) * 3, 50)
        
        # 2. Presence of common metropolitan indicators
        metro_indicators = ['city', 'metro', 'capital', 'downtown', 'center']
        metro_factor = 30 if any(ind in location_lower for ind in metro_indicators) else 0
        
        # 3. Industrial/urban keywords
        urban_indicators = ['industrial', 'port', 'factory', 'plant', 'refinery']
        urban_factor = 40 if any(ind in location_lower for ind in urban_indicators) else 0
        
        # 4. Green/clean keywords (reduce AQI)
        green_indicators = ['park', 'garden', 'forest', 'national', 'reserve', 'clean', 'green']
        green_factor = -30 if any(ind in location_lower for ind in green_indicators) else 0
        
        # 5. Coastal keywords (better air quality)
        coastal_indicators = ['beach', 'coast', 'bay', 'ocean', 'sea', 'island', 'harbor']
        coastal_factor = -20 if any(ind in location_lower for ind in coastal_indicators) else 0
        
        # 6. Desert/dry areas (more dust)
        desert_indicators = ['desert', 'sand', 'dust', 'arid', 'dry']
        desert_factor = 25 if any(ind in location_lower for ind in desert_indicators) else 0
        
        # 7. Mountain areas (often cleaner but can trap pollution)
        mountain_indicators = ['mountain', 'hill', 'valley', 'highland']
        mountain_factor = 10 if any(ind in location_lower for ind in mountain_indicators) else 0
        
        # Calculate base AQI
        base_aqi = 50 + (location_hash % 100)
        
        # Apply all factors
        total_adjustment = (name_length_factor + metro_factor + urban_factor + 
                           desert_factor + mountain_factor +
                           green_factor + coastal_factor)
        
        # Calculate final AQI and ensure it's within 0-350 range
        aqi = base_aqi + total_adjustment
        aqi = max(15, min(350, aqi))
        
        return int(aqi)
    
    def _get_consistent_pm_values(self, location, aqi):
        """Generate consistent PM values based on location and AQI"""
        # Use location + "pm" as seed for reproducibility
        random.seed(hash(location + "_pm") % 10000)
        
        # PM values correlate with AQI
        pm25 = random.randint(max(5, aqi//5 - 8), min(100, aqi//4 + 5))
        pm10 = random.randint(max(8, aqi//3 - 5), min(150, aqi//2 + 8))
        ozone = random.randint(max(5, aqi//6 - 3), min(80, aqi//3 + 5))
        no2 = random.randint(max(3, aqi//8 - 2), min(60, aqi//5 + 3))
        
        return pm25, pm10, ozone, no2
    
    def _run(self, location: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get pollution data for a location"""
        try:
            # Clean the input - remove common phrases
            clean_location = location.lower()
            clean_location = clean_location.replace("pollution index of", "")
            clean_location = clean_location.replace("what is the", "")
            clean_location = clean_location.replace("what is", "")
            clean_location = clean_location.replace("give me the", "")
            clean_location = clean_location.replace("tell me the", "")
            clean_location = clean_location.replace("check", "")
            clean_location = clean_location.replace("?", "").strip()
            
            # If location is empty after cleaning, use original
            if not clean_location:
                clean_location = location.strip()
            
            # Store for display
            display_location = clean_location.upper()
            
            # Calculate AQI based on location characteristics
            aqi = self._calculate_aqi_from_location(clean_location)
            category, color, advice = self._get_aqi_category(aqi)
            visual_bar = self._create_visual_bar(aqi)
            
            # Get consistent PM values
            pm25, pm10, ozone, no2 = self._get_consistent_pm_values(clean_location, aqi)
            
            # Generate forecast with some variation
            random.seed(hash(clean_location + "_forecast") % 1000)
            tomorrow = aqi + random.randint(-15, 15)
            day_after = aqi + random.randint(-20, 20)
            
            # Ensure forecast values are within reasonable range
            tomorrow = max(15, min(350, tomorrow))
            day_after = max(15, min(350, day_after))
            
            # Get forecast categories
            tomorrow_cat = self._get_aqi_category(tomorrow)[0]
            day_after_cat = self._get_aqi_category(day_after)[0]
            
            # Build response with explicit line breaks - EACH LINE SEPARATE
            response_lines = [
                f"ENVIRONMENTAL HEALTH INDEX for {display_location}",
                f"Data retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "",
                "CURRENT CONDITIONS:",
                f"Air Quality Index (AQI): {aqi} - {category} {color}",
                "",
                "Visual Indicator:",
                f"[{visual_bar}] {aqi}/300",
                "Low → → → → → → → → → → → → → → → → → → → → High",
                "",
                "Detailed Readings:",
                f"• PM2.5: {pm25} μg/m³  [Safe: <25]",
                f"• PM10:  {pm10} μg/m³  [Safe: <50]",
                f"• Ozone: {ozone} μg/m³ [Safe: <50]",
                f"• NO2:   {no2} μg/m³   [Safe: <25]",
                "",
                "HEALTH RECOMMENDATIONS:",
                advice,
                "",
                "FORECAST (Next 3 days):",
                f"• Today: AQI {aqi} ({category})",
                f"• Tomorrow: AQI {tomorrow} ({tomorrow_cat})",
                f"• Day after: AQI {day_after} ({day_after_cat})",
                "",
                "AQI RANGE REFERENCE:",
                "  0 - 50:   🟢 Good",
                " 51 - 100:  🟡 Moderate",
                "101 - 150:  🟠 Unhealthy for Sensitive Groups",
                "151 - 200:  🔴 Unhealthy",
                "201 - 300:  🟣 Very Unhealthy",
                "300+ :      ⚫ Hazardous",
                "",
                "Note: This is simulated data based on location characteristics.",
                "For production, connect to real APIs like OpenAQ or WAQI."
            ]
            
            return "\n".join(response_lines)
            
        except Exception as e:
            return f"Error fetching pollution data: {str(e)}"
    
    async def _arun(self, location: str) -> str:
        return self._run(location)