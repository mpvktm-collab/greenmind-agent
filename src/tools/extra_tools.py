# -*- coding: utf-8 -*-
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


class CarbonFootprintCalculator(BaseTool):
    name: str = "Carbon_Footprint_Calculator"
    description: str = "Provides carbon footprint estimates for cities and activities."
    return_direct: bool = True

    def _run(self, activity: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        activity_lower = activity.lower()

        city_data = {
            "delhi":    {"per_capita": 2.1, "sources": "transportation, industrial, power plants"},
            "mumbai":   {"per_capita": 1.8, "sources": "transportation, commercial, power plants"},
            "chennai":  {"per_capita": 2.0, "sources": "transportation, industry, residential"},
            "kolkata":  {"per_capita": 1.9, "sources": "transportation, industry, residential"},
            "london":   {"per_capita": 5.5, "sources": "transportation, heating, aviation"},
            "new york": {"per_capita": 6.3, "sources": "transportation, buildings, industry"},
            "tokyo":    {"per_capita": 4.7, "sources": "transportation, manufacturing, commercial"},
            "beijing":  {"per_capita": 7.2, "sources": "coal power, transportation, industry"},
            "paris":    {"per_capita": 4.2, "sources": "transportation, heating, aviation"},
        }

        for city, data in city_data.items():
            if city in activity_lower:
                if data["per_capita"] <= 2.0:
                    icon = "[GREEN]"
                elif data["per_capita"] <= 5.0:
                    icon = "[YELLOW]"
                else:
                    icon = "[RED]"
                return (
                    f"CARBON FOOTPRINT: {city.upper()}\n"
                    f"Per Capita: {data['per_capita']} tons CO2/year {icon}\n"
                    f"Main Sources: {data['sources']}\n"
                    f"---\n"
                    f"Impact Guide: [GREEN] Low (<2.0)  [YELLOW] Moderate (2-5)  [RED] High (>5)"
                )

        if "car" in activity_lower:
            return (
                "CARBON FOOTPRINT: Car Travel\n"
                "Gasoline: 2.3 kg CO2 per 10km [RED]\n"
                "Electric: 1.2 kg CO2 per 10km [GREEN]\n"
                "Hybrid: 1.5 kg CO2 per 10km [YELLOW]"
            )

        if "flight" in activity_lower or "aviation" in activity_lower or "plane" in activity_lower:
            return (
                "CARBON FOOTPRINT: Air Travel\n"
                "Short-haul flight (less than 3 hours): approximately 0.3 tons CO2 per trip [YELLOW]\n"
                "Long-haul flight (more than 8 hours): approximately 1.5 tons CO2 per trip [RED]\n"
                "Tip: Choose direct flights and offset your carbon footprint"
            )

        return "Ask about specific cities (Delhi, Mumbai, London, New York) or activities (car, flight)."

    async def _arun(self, activity: str) -> str:
        return self._run(activity)


class SustainabilityTipsTool(BaseTool):
    name: str = "Sustainability_Tips"
    description: str = "Provides practical tips for sustainable living."
    return_direct: bool = True

    TIPS = {
        "transport": [
            "Walk or cycle for trips under 3 km - zero emissions and great for your health.",
            "Use public transit (bus, metro, train) - a full bus emits much less CO2 per passenger than solo car trips.",
            "Carpool with colleagues or neighbours - halves per-person emissions instantly.",
            "Switch to an electric vehicle - lifetime emissions are 50-70 percent lower than petrol cars.",
            "Try e-scooters or e-bikes for urban last-mile commutes.",
            "Reduce short-haul flights - trains emit up to 90 percent less CO2 than planes on the same route.",
            "Keep your car well-maintained - correct tyre pressure alone improves fuel efficiency by up to 3 percent.",
            "Avoid idling - switching off the engine after 60 seconds saves fuel and cuts exhaust fumes.",
            "Work from home when possible - each remote day eliminates your commute emissions entirely.",
            "When flying, choose direct routes and offset your carbon via certified programmes.",
        ],
        "home": [
            "Switch to LED bulbs - uses 75 percent less energy than incandescent bulbs and lasts 25 times longer.",
            "Unplug chargers and electronics when idle - standby power accounts for about 10 percent of home electricity.",
            "Wash clothes in cold water - 90 percent of a washing machine's energy goes to heating water.",
            "Lower your thermostat by 1 degree Celsius - saves about 10 percent on heating bills.",
            "Install solar panels or switch to a green energy tariff.",
            "Shorten showers to under 5 minutes - saves up to 50 litres of water.",
            "Compost food scraps - diverts waste from landfill and enriches your garden soil.",
            "Seal draughts around windows and doors to reduce heat loss.",
            "Use a smart power strip to eliminate vampire power draw from multiple devices.",
        ],
        "food": [
            "Eat more plant-based meals - meat production emits 14.5 percent of global greenhouse gases.",
            "Buy local and seasonal produce to cut food-miles.",
            "Reduce food waste - plan meals, use leftovers, and freeze surplus.",
            "Avoid single-use plastics - bring reusable bags, bottles, and containers.",
            "Grow your own herbs and vegetables, even on a windowsill.",
        ],
        "general": [
            "Reduce, Reuse, Recycle - in that order of priority.",
            "Plant native trees - they support local biodiversity and sequester carbon.",
            "Support eco-friendly businesses and ethical supply chains.",
            "Choose products with minimal or recycled packaging.",
            "Fix leaking taps - a dripping tap wastes up to 20,000 litres per year.",
            "Go paperless - opt for e-statements, e-tickets, and digital documents.",
            "Buy second-hand clothes - the fashion industry is responsible for about 10 percent of global carbon emissions.",
        ],
    }

    def _detect_category(self, query: str) -> str:
        q = query.lower()
        transport_words = [
            'transport', 'transportation', 'travel', 'commute', 'car', 'bus', 'train',
            'metro', 'subway', 'bike', 'bicycle', 'cycling', 'walk', 'electric vehicle',
            'ev', 'flight', 'aviation', 'eco-friendly transport', 'green travel',
            'rideshare', 'carpool'
        ]
        home_words = ['home', 'house', 'energy', 'electricity', 'solar', 'heating', 'water', 'appliance']
        food_words = ['food', 'diet', 'vegan', 'meat', 'plant', 'eat', 'grocery', 'waste']

        if any(w in q for w in transport_words):
            return "transport"
        if any(w in q for w in home_words):
            return "home"
        if any(w in q for w in food_words):
            return "food"
        return "general"

    def _run(self, category: str = "general", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        bucket = self._detect_category(category)
        tips = self.TIPS[bucket]

        labels = {
            "transport": "Eco-Friendly Transportation",
            "home": "Sustainable Home",
            "food": "Sustainable Food and Diet",
            "general": "General Sustainability",
        }

        header = f"SUSTAINABILITY TIPS - {labels[bucket]}\n"
        header += "-" * 45 + "\n\n"
        body = "\n\n".join(f"- {tip}" for tip in tips)
        footer = "\n\n" + "-" * 45 + "\n"
        footer += "Ask me about home energy, food choices, or any city's carbon footprint."

        return header + body + footer

    async def _arun(self, category: str = "general") -> str:
        return self._run(category)