# src/tools/pollution_index.py
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from datetime import datetime
import random


class PollutionIndexTool(BaseTool):
    """Tool for getting pollution and environmental health index"""

    name: str = "Pollution_Health_Index"
    description: str = (
        "Retrieves current pollution levels and environmental health indices "
        "for any location. Input should be a location name."
    )

    # ---------------------------
    # AQI CATEGORY
    # ---------------------------
    def _get_aqi_category(self, aqi):
        if aqi <= 50:
            return "Good", "🟢", "Low health risk"
        elif aqi <= 100:
            return "Moderate", "🟡", "Sensitive groups limit outdoor activity"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups", "🟠", "Children & elderly should limit outdoor activity"
        elif aqi <= 200:
            return "Unhealthy", "🔴", "Everyone may experience health effects"
        elif aqi <= 300:
            return "Very Unhealthy", "🟣", "Health alert - serious effects"
        else:
            return "Hazardous", "⚫", "Emergency conditions - avoid outdoors"

    # ---------------------------
    # VISUAL BAR
    # ---------------------------
    def _create_visual_bar(self, aqi, max_aqi=300):
        bar_length = 30
        position = int((aqi / max_aqi) * bar_length)
        position = min(position, bar_length)

        bar = ""
        for i in range(bar_length):
            if i < position:
                bar += "█"
            else:
                bar += "░"

        return bar

    # ---------------------------
    # AQI CALCULATION
    # ---------------------------
    def _calculate_aqi_from_location(self, location):
        location = location.lower()
        location_hash = abs(hash(location)) % 1000

        name_factor = min(len(location) * 3, 50)

        metro = 30 if any(x in location for x in ['city', 'metro', 'capital', 'downtown']) else 0
        industrial = 40 if any(x in location for x in ['industrial', 'factory', 'plant', 'refinery']) else 0
        green = -30 if any(x in location for x in ['park', 'forest', 'green', 'reserve']) else 0
        coastal = -20 if any(x in location for x in ['coast', 'sea', 'beach', 'bay']) else 0
        desert = 25 if any(x in location for x in ['desert', 'dust', 'dry']) else 0
        mountain = 10 if any(x in location for x in ['mountain', 'hill', 'valley']) else 0

        base_aqi = 50 + (location_hash % 100)

        total = base_aqi + name_factor + metro + industrial + green + coastal + desert + mountain

        return max(15, min(350, total))

    # ---------------------------
    # POLLUTANT VALUES
    # ---------------------------
    def _get_consistent_pm_values(self, location, aqi):
        random.seed(hash(location + "_pm") % 10000)

        pm25 = random.randint(max(5, aqi // 5 - 8), min(100, aqi // 4 + 5))
        pm10 = random.randint(max(8, aqi // 3 - 5), min(150, aqi // 2 + 8))
        ozone = random.randint(max(5, aqi // 6 - 3), min(80, aqi // 3 + 5))
        no2 = random.randint(max(3, aqi // 8 - 2), min(60, aqi // 5 + 3))

        return pm25, pm10, ozone, no2

    # ---------------------------
    # MAIN EXECUTION
    # ---------------------------
    def _run(self, location: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Clean input
            clean = location.lower()
            for phrase in [
                "pollution index of", "what is the", "what is",
                "give me the", "tell me the", "check"
            ]:
                clean = clean.replace(phrase, "")

            clean = clean.replace("?", "").strip()

            if not clean:
                clean = location.strip()

            display = clean.upper()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Generate values
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
            # FORCE LINE-BY-LINE OUTPUT
            # ---------------------------
            lines = [
                f"🌍 ENVIRONMENTAL HEALTH INDEX — {display}",
                f"🕒 Data retrieved: {timestamp}",
                "",
                "📊 CURRENT CONDITIONS",
                f"AQI: {aqi} ({category}) {color}",
                "",
                f"[{bar}] {aqi}/300",
                "Low → → → → → → → → → → → → → → → → → → → → High",
                "",
                "🔬 DETAILED READINGS",
                f"• PM2.5: {pm25} μg/m³ (Safe <25)",
                f"• PM10:  {pm10} μg/m³ (Safe <50)",
                f"• Ozone: {ozone} μg/m³ (Safe <50)",
                f"• NO₂:   {no2} μg/m³ (Safe <25)",
                "",
                "💡 HEALTH RECOMMENDATION",
                advice,
                "",
                "📅 FORECAST",
                f"• Today: {aqi} ({category})",
                f"• Tomorrow: {tomorrow} ({tomorrow_cat})",
                f"• Day After: {day_after} ({day_after_cat})",
                "",
                "📘 AQI REFERENCE",
                "0–50   🟢 Good",
                "51–100 🟡 Moderate",
                "101–150 🟠 Sensitive Groups",
                "151–200 🔴 Unhealthy",
                "201–300 🟣 Very Unhealthy",
                "300+    ⚫ Hazardous",
                "",
                "⚠️ Note: This is simulated data."
            ]

            # CRITICAL: join with explicit newline
            return "\n".join(lines)

        except Exception as e:
            return f"Error fetching pollution data: {str(e)}"

    # ---------------------------
    # ASYNC SUPPORT
    # ---------------------------
    async def _arun(self, location: str) -> str:
        return self._run(location)