# src/tools/extra_tools.py
from langchain.tools import BaseTool
from typing import Optional
from langchain.callbacks.manager import CallbackManagerForToolRun

class CarbonFootprintCalculator(BaseTool):
    """Tool for calculating carbon footprint"""
    
    name: str = "Carbon_Footprint_Calculator"
    description: str = """
    Provides estimates of carbon footprint for various activities and suggests reduction strategies.
    Use this when asked about carbon footprint of activities like driving, flying, electricity use, etc.
    Input should be an activity (car, flight, electricity, meat, plastic).
    """
    
    def _run(self, activity: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Calculate carbon footprint for common activities"""
        
        activity_lower = activity.lower()
        
        if "car" in activity_lower or "drive" in activity_lower:
            return """
CARBON FOOTPRINT: Car Travel
* Average: 2.3 kg CO2 per 10 km (gasoline car)
* Electric vehicle: 1.2 kg CO2 per 10 km
* Hybrid: 1.5 kg CO2 per 10 km

REDUCTION TIPS:
1. Carpool with colleagues
2. Use public transportation when possible
3. Maintain proper tire pressure
4. Consider an electric or hybrid vehicle
5. Combine errands to reduce trips
"""
        elif "flight" in activity_lower or "fly" in activity_lower or "plane" in activity_lower:
            return """
CARBON FOOTPRINT: Air Travel
* Short flight (<1 hour): 90 kg CO2 per hour
* Long flight: 120 kg CO2 per hour
* Round trip NYC-London: ~1.5 tons CO2

REDUCTION TIPS:
1. Take direct flights (takeoff/landing use most fuel)
2. Choose economy class (more passengers per flight)
3. Consider trains for short distances
4. Offset your flights through certified programs
5. Video conference instead of business travel
"""
        elif "electricity" in activity_lower or "energy" in activity_lower or "power" in activity_lower:
            return """
CARBON FOOTPRINT: Electricity Use
* Average home: 0.5 kg CO2 per kWh
* Monthly average: 300-400 kg CO2
* Annual average: 4-5 tons CO2

REDUCTION TIPS:
1. Switch to LED bulbs (75% less energy)
2. Unplug electronics when not in use
3. Use energy-efficient appliances
4. Install a programmable thermostat
5. Consider solar panels
6. Choose green energy provider
"""
        elif "meat" in activity_lower or "food" in activity_lower or "diet" in activity_lower:
            return """
CARBON FOOTPRINT: Food Choices
* Meat-heavy diet: 3.5 kg CO2 per meal
* Vegetarian diet: 1.7 kg CO2 per meal
* Vegan diet: 1.2 kg CO2 per meal
* Beef: 27 kg CO2 per kg
* Chicken: 6 kg CO2 per kg
* Vegetables: 2 kg CO2 per kg

REDUCTION TIPS:
1. Try meat-free Mondays
2. Choose locally-grown food
3. Reduce food waste
4. Buy seasonal produce
5. Compost food scraps
"""
        elif "plastic" in activity_lower:
            return """
CARBON FOOTPRINT: Plastic Use
* Plastic production: 6 kg CO2 per kg plastic
* Single-use bottle: 0.5 kg CO2 each
* Plastic bag: 0.1 kg CO2 each

REDUCTION TIPS:
1. Use reusable water bottles
2. Bring your own shopping bags
3. Avoid products with excess packaging
4. Choose glass or metal containers
5. Recycle all plastic waste
"""
        else:
            return """
Please specify an activity from these categories:
* Car travel
* Flight / air travel
* Electricity use
* Meat consumption / diet
* Plastic use

Example: "What's the carbon footprint of a flight?"
"""

    async def _arun(self, activity: str) -> str:
        return self._run(activity)


class SustainabilityTipsTool(BaseTool):
    """Tool for providing sustainability tips"""
    
    name: str = "Sustainability_Tips"
    description: str = """
    Provides practical, everyday tips for living more sustainably and reducing environmental impact.
    Use this when asked for eco-friendly tips, sustainable living advice, or green lifestyle suggestions.
    Input can be a category (home, transport, food, waste, general) or leave empty for general tips.
    """
    
    def _run(self, category: str = "general", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get sustainability tips by category"""
        
        tips = {
            "home": [
                "Switch to LED bulbs - they use 75% less energy",
                "Unplug electronics when not in use to avoid phantom energy",
                "Use energy-efficient appliances (look for ENERGY STAR)",
                "Install a programmable thermostat to optimize heating/cooling",
                "Improve home insulation to reduce energy waste",
                "Use cold water for laundry when possible",
                "Air dry clothes instead of using a dryer",
                "Fix leaky faucets promptly"
            ],
            "transport": [
                "Walk or bike for short trips under 2 miles",
                "Use public transportation for commuting",
                "Carpool with colleagues or neighbors",
                "Maintain proper tire pressure for better fuel efficiency",
                "Consider an electric or hybrid vehicle",
                "Combine errands into one trip",
                "Avoid excessive idling",
                "Use ride-sharing services wisely"
            ],
            "food": [
                "Eat locally-grown, seasonal food",
                "Reduce food waste by meal planning",
                "Choose plant-based meals a few times a week",
                "Compost food scraps",
                "Grow your own vegetables or herbs",
                "Buy in bulk to reduce packaging",
                "Bring reusable containers for takeout",
                "Support farmers markets"
            ],
            "waste": [
                "Practice the 3 R's: Reduce, Reuse, Recycle",
                "Avoid single-use plastics",
                "Use reusable bags, bottles, and containers",
                "Repair items instead of replacing them",
                "Buy products with minimal packaging",
                "Start a composting system",
                "Donate unwanted items instead of throwing away",
                "Use both sides of paper"
            ],
            "general": [
                "Plant native trees and plants in your community",
                "Support eco-friendly businesses and products",
                "Educate others about environmental issues",
                "Participate in local clean-up events",
                "Choose sustainable and ethical products",
                "Reduce water usage by taking shorter showers",
                "Use natural cleaning products",
                "Opt for digital documents instead of paper"
            ]
        }
        
        category = category.lower().strip()
        if category not in tips:
            category = "general"
        
        response = f"{category.upper()} SUSTAINABILITY TIPS:\n\n"
        for i, tip in enumerate(tips[category], 1):
            response += f"{i}. {tip}\n"
        
        return response
    
    async def _arun(self, category: str = "general") -> str:
        return self._run(category)