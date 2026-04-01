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
    Use this when asked about AQI, pollution, or air quality.
    Input should be a location name (city/state/country).
    """

    # ---------------------------
    # AQI CATEGORY
    # ---------------------------
    def _get_aqi_category(self, aqi: int):
        if aqi <= 50:
            return "Good", "🟢", "Low health risk"
        elif aqi <= 100:
            return "Moderate", "🟡", "Sensitive groups limit outdoor activity"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups", "🟠", "Children & elderly should limit outdoor activity"
        elif aqi <= 200:
            return "Unhealthy", "🔴", "Everyone may experience health effects"
        elif aqi <= 300:
            return "Very Unhealthy", "🟣", "Health alert: serious effects possible"
        else:
            return "Hazardous", "⚫", "Emergency conditions: avoid outdoor exposure"

    # ---------------------------
    # VISUAL BAR
    # ---------------------------
    def _create_visual_bar(self, aqi: int, max_aqi: int = 300):
        bar_length = 30
        position = min(int((aqi / max_aqi) * bar_length), bar_length)
        return "█" * position + "░" * (bar_length - position)

    # ---------------------------
    # AQI CALCULATION (SIMULATED)
    # ---------------------------
    def _calculate_aqi_from_location(self, location: str):
        location = location.lower()
        location_hash = abs(hash(location)) % 1000

        base_aqi = 50 + (location_hash % 100)
        name_factor = min(len(location) * 3, 50)

        total = name_factor

        if any(x in location for x in ['city', 'metro', 'capital', 'downtown']):
            total += 30
        if any(x in location for x in ['industrial', 'factory', 'plant', 'refinery']):
            total += 40
        if any(x in location for x in ['park', 'forest', 'green', 'reserve']):
            total -= 30
        if any(x in location for x in ['coast', 'sea', 'beach', 'bay']):
            total -= 20
        if any(x in location for x in ['desert', 'dust', 'dry']):
            total += 25
        if any(x in location for x in ['mountain', 'hill', 'valley']):
            total += 10

        return max(15, min(350, base_aqi + total))

    # ---------------------------
    # POLLUTANT VALUES
    # ---------------------------
    def _get_consistent_pm_values(self, location: str, aqi: int):
        random.seed(hash(location + "_pm") % 10000)

        pm25 = random.randint(max(5, aqi // 5 - 8), min(100, aqi // 4 + 5))
        pm10 = random.randint(max(8, aqi // 3 - 5), min(150, aqi // 2 + 8))
        ozone = random.randint(max(5, aqi // 6 - 3), min(80, aqi // 3 + 5))
        no2 = random.randint(max(3, aqi // 8 - 2), min(60, aqi // 5 + 3))

        return pm25, pm10, ozone, no2

    # ---------------------------
    # MAIN TOOL EXECUTION
    # ---------------------------
    def _run(
        self,
        location: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            # Clean input
            clean = location.lower()
            for phrase in [
                "pollution index of", "what is the", "what is",
                "give me", "tell me", "check"
            ]:
                clean = clean.replace(phrase, "")

            clean = clean.replace("?", "").strip()
            if not clean:
                clean = location.strip()

            display = clean.upper()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Generate data
            aqi = self._calculate_aqi_from_location(clean)
            category, color, advice = self._get_aqi_category(aqi)
            bar = self._create_visual_bar(aqi)

            pm25, pm10, ozone, no2 = self._get_consistent_pm_values(clean, aqi)

            # Forecast
            random.seed(hash(clean + "_forecast") % 1000)
            tomorrow = max(15, min(350, aqi + random.randint(-15, 15)))
            day_after = max(15, min(350, aqi + random.randint(-20, 20)))

            tomorrow_cat = self._get_aqi_category(tomorrow)[0]
            day_after_cat = self._get_aqi_category(day_after)[0]

            # ---------------------------
            # FORMATTED OUTPUT
            # ---------------------------
            sections = [

                f"🌍 **ENVIRONMENTAL HEALTH INDEX — {display}**",
                f"🕒 Data retrieved: {timestamp}",

                f"""
📊 **CURRENT CONDITIONS**

AQI: **{aqi}** ({category}) {color}

[{bar}] {aqi}/300
Low → → → → → → → → → → → → → → → → → → → → High
""",

                f"""
🔬 **DETAILED READINGS**

• PM2.5: {pm25} μg/m³   (Safe <25)
• PM10:  {pm10} μg/m³   (Safe <50)
• Ozone: {ozone} μg/m³  (Safe <50)
• NO₂:   {no2} μg/m³    (Safe <25)
""",

                f"""
💡 **HEALTH RECOMMENDATION**

{advice}
""",

                f"""
📅 **FORECAST**

• Today: {aqi} ({category})
• Tomorrow: {tomorrow} ({tomorrow_cat})
• Day After: {day_after} ({day_after_cat})
""",

                """
📘 **AQI REFERENCE**

0–50   🟢 Good  
51–100 🟡 Moderate  
101–150 🟠 Sensitive Groups  
151–200 🔴 Unhealthy  
201–300 🟣 Very Unhealthy  
300+    ⚫ Hazardous
""",

                "⚠️ Note: This is simulated data. Use real APIs like OpenAQ or WAQI for production."
            ]

            return "\n\n".join(section.strip() for section in sections)

        except Exception as e:
            return f"Error fetching pollution data: {str(e)}"

    # ---------------------------
    # ASYNC SUPPORT
    # ---------------------------
    async def _arun(self, location: str) -> str:
        return self._run(location)