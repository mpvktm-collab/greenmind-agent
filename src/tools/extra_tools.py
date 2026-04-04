# src/tools/extra_tools.py
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import random
import re

class CarbonFootprintCalculator(BaseTool):
    """Tool for calculating carbon footprint"""
    
    name: str = "Carbon_Footprint_Calculator"
    description: str = """
    Provides estimates of carbon footprint for cities and activities.
    """
    
    return_direct: bool = True
    
    def _get_city_carbon_footprint(self, city):
        """Calculate approximate carbon footprint for a city"""
        city_lower = city.lower()
        
        # City carbon profiles
        city_profiles = {
            "delhi": {"per_capita": 2.1, "main_sources": ["transportation", "industrial", "power plants"], "trend": "increasing", "rank": "moderate"},
            "mumbai": {"per_capita": 1.8, "main_sources": ["transportation", "commercial", "power plants"], "trend": "increasing", "rank": "moderate"},
            "new york": {"per_capita": 4.2, "main_sources": ["buildings", "transportation", "waste"], "trend": "stable", "rank": "high"},
            "london": {"per_capita": 3.8, "main_sources": ["buildings", "transportation", "aviation"], "trend": "decreasing", "rank": "moderate-high"},
            "tokyo": {"per_capita": 3.5, "main_sources": ["buildings", "transportation", "industry"], "trend": "stable", "rank": "moderate-high"},
            "beijing": {"per_capita": 5.1, "main_sources": ["industry", "power plants", "transportation"], "trend": "decreasing", "rank": "very high"},
            "paris": {"per_capita": 2.9, "main_sources": ["buildings", "transportation", "commercial"], "trend": "decreasing", "rank": "moderate"},
            "berlin": {"per_capita": 3.1, "main_sources": ["transportation", "buildings", "renewables"], "trend": "decreasing", "rank": "moderate"},
            "singapore": {"per_capita": 3.3, "main_sources": ["industry", "shipping", "cooling"], "trend": "increasing", "rank": "moderate"},
            "los angeles": {"per_capita": 3.9, "main_sources": ["transportation", "buildings", "industry"], "trend": "stable", "rank": "high"},
            "chicago": {"per_capita": 3.6, "main_sources": ["buildings", "transportation", "industry"], "trend": "stable", "rank": "moderate-high"},
            "toronto": {"per_capita": 3.4, "main_sources": ["buildings", "transportation", "industry"], "trend": "stable", "rank": "moderate"},
            "mexico city": {"per_capita": 2.8, "main_sources": ["transportation", "industry", "residential"], "trend": "increasing", "rank": "moderate"},
            "dubai": {"per_capita": 6.2, "main_sources": ["buildings", "transportation", "desalination"], "trend": "increasing", "rank": "very high"},
            "moscow": {"per_capita": 4.5, "main_sources": ["buildings", "transportation", "industry"], "trend": "stable", "rank": "high"},
            "chennai": {"per_capita": 2.0, "main_sources": ["transportation", "industry", "residential"], "trend": "increasing", "rank": "moderate"},
            "kolkata": {"per_capita": 1.9, "main_sources": ["transportation", "industry", "residential"], "trend": "increasing", "rank": "moderate"},
            "bangalore": {"per_capita": 2.2, "main_sources": ["transportation", "IT sector", "residential"], "trend": "increasing", "rank": "moderate"},
            "hyderabad": {"per_capita": 2.0, "main_sources": ["transportation", "industry", "residential"], "trend": "increasing", "rank": "moderate"},
            "ahmedabad": {"per_capita": 2.3, "main_sources": ["transportation", "industry", "residential"], "trend": "increasing", "rank": "moderate"},
            "pune": {"per_capita": 2.1, "main_sources": ["transportation", "industry", "residential"], "trend": "increasing", "rank": "moderate"}
        }
        
        for city_name, profile in city_profiles.items():
            if city_name in city_lower:
                return profile.copy()
        
        return {"per_capita": 3.0, "main_sources": ["transportation", "industry", "residential"], "trend": "stable", "rank": "moderate"}
    
    def _run(self, activity: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Calculate carbon footprint for cities or activities"""
        
        activity_lower = activity.lower()
        
        # List of known cities
        known_cities = [
            'delhi', 'mumbai', 'new york', 'london', 'tokyo', 'beijing', 'shanghai',
            'paris', 'berlin', 'sydney', 'melbourne', 'singapore', 'los angeles',
            'chicago', 'toronto', 'mexico city', 'dubai', 'moscow', 'chennai',
            'kolkata', 'bangalore', 'hyderabad', 'ahmedabad', 'pune'
        ]
        
        # Check if query contains a city name
        is_city_query = False
        city_found = None
        
        for city in known_cities:
            if city in activity_lower:
                is_city_query = True
                city_found = city
                break
        
        # Also check for "carbon footprint of X" pattern
        if 'carbon footprint of' in activity_lower:
            is_city_query = True
            match = re.search(r'carbon footprint of\s+([a-zA-Z\s]+?)(?:\?|$)', activity_lower)
            if match:
                city_found = match.group(1).strip()
        
        # Handle city query
        if is_city_query and city_found:
            profile = self._get_city_carbon_footprint(city_found)
            
            if profile['per_capita'] <= 2.0:
                color = "🟢"
                level = "Low Impact"
            elif profile['per_capita'] <= 5.0:
                color = "🟡"
                level = "Moderate Impact"
            else:
                color = "🔴"
                level = "High Impact"
            
            bar_length = 20
            position = int((profile['per_capita'] / 10) * bar_length)
            bar = "█" * position + "░" * (bar_length - position)
            
            if profile['trend'] == 'increasing':
                trend_arrow = "↗️"
            elif profile['trend'] == 'decreasing':
                trend_arrow = "↘️"
            else:
                trend_arrow = "→"
            
            return f"""
========================================
CARBON FOOTPRINT: {city_found.upper()}
========================================

Per Capita Carbon Footprint: {profile['per_capita']} tons CO2/year {color}
Impact Level: {level}

Visual Indicator:
[{bar}] {profile['per_capita']}/10 tons
Low → → → → → → → → → → → → → → → → → → → → High

Rank: {profile['rank'].upper()}
Trend: {trend_arrow} {profile['trend']}

Main Emission Sources:
• {profile['main_sources'][0]}
• {profile['main_sources'][1]}
• {profile['main_sources'][2]}

Global Benchmarks:
🟢 Less than 2.0 tons: Sustainable Target
🟡 2.0 - 5.0 tons: Moderate
🔴 Greater than 5.0 tons: High

Recommended Reduction Strategies:
1. Expand public transportation
2. Increase renewable energy adoption
3. Implement building efficiency programs
4. Create low-emission zones
5. Promote electric vehicles

========================================
"""
        
        # Handle car query
        if "car" in activity_lower or "drive" in activity_lower:
            return """
========================================
CARBON FOOTPRINT: Car Travel
========================================

Per 10 km emissions:
• Gasoline car: 2.3 kg CO2 🟡
• Electric vehicle: 1.2 kg CO2 🟢
• Hybrid: 1.5 kg CO2 🟢

Comparison:
🟢 Electric/Hybrid: Best choice
🟡 Gasoline: Moderate impact
🔴 Diesel: Highest impact

Reduction Tips:
• Carpool with colleagues 🟢
• Use public transportation 🟢
• Maintain proper tire pressure 🟡
• Consider electric/hybrid vehicle 🟢
• Combine errands to reduce trips 🟡

========================================
"""
        
        # Handle flight query
        if "flight" in activity_lower or "fly" in activity_lower or "plane" in activity_lower:
            return """
========================================
CARBON FOOTPRINT: Air Travel
========================================

Emissions:
• Short flight (under 1 hour): 90 kg CO2/hour 🔴
• Long flight: 120 kg CO2/hour 🔴
• Round trip NYC-London: ~1.5 tons CO2 🔴

Comparison per 100 km:
🟢 Train: 6 kg CO2
🟡 Bus: 15 kg CO2
🔴 Plane: 25 kg CO2

Reduction Tips:
• Take direct flights 🟢
• Choose economy class 🟢
• Use trains for short distances 🟢
• Offset emissions through certified programs 🟡
• Use video conferencing instead 🟢

========================================
"""
        
        # Handle electricity query
        if "electricity" in activity_lower or "energy" in activity_lower:
            return """
========================================
CARBON FOOTPRINT: Electricity Use
========================================

Average home: 0.5 kg CO2 per kWh 🟡
Monthly average: 300-400 kg CO2 🟡
Annual average: 4-5 tons CO2 🟡

By Energy Source (per kWh):
🟢 Solar/Wind: 0.02 kg CO2
🟢 Nuclear: 0.01 kg CO2
🟡 Natural Gas: 0.4 kg CO2
🔴 Coal: 1.0 kg CO2

Reduction Tips:
• Switch to LED bulbs 🟢
• Unplug unused electronics 🟢
• Use energy-efficient appliances 🟢
• Install programmable thermostat 🟡
• Consider solar panels 🟢

========================================
"""
        
        # Handle food/meat query
        if "meat" in activity_lower or "food" in activity_lower or "diet" in activity_lower:
            return """
========================================
CARBON FOOTPRINT: Food Choices
========================================

Per Meal:
• Meat-heavy diet: 3.5 kg CO2 🔴
• Vegetarian diet: 1.7 kg CO2 🟡
• Vegan diet: 1.2 kg CO2 🟢

Per kg of Food:
🔴 Beef: 27 kg CO2
🟡 Pork: 7 kg CO2
🟡 Chicken: 6 kg CO2
🟢 Vegetables: 2 kg CO2
🟢 Grains: 1.5 kg CO2

Reduction Tips:
• Try meat-free Mondays 🟢
• Choose locally-grown food 🟢
• Reduce food waste 🟢
• Buy seasonal produce 🟡
• Compost food scraps 🟢

========================================
"""
        
        # Default response
        return """
========================================
CARBON FOOTPRINT CALCULATOR
========================================

Please ask about:

CITIES (examples):
• "What is the carbon footprint of Delhi?"
• "Carbon footprint of New York City"
• "Emissions for London"

ACTIVITIES (examples):
• "Car carbon footprint"
• "Flight emissions"
• "Home energy carbon footprint"
• "Meat consumption carbon"

Color Guide:
🟢 Low impact
🟡 Moderate impact
🔴 High impact

========================================
"""

    async def _arun(self, activity: str) -> str:
        return self._run(activity)


class SustainabilityTipsTool(BaseTool):
    """Tool for providing sustainability tips"""
    
    name: str = "Sustainability_Tips"
    description: str = "Provides practical tips for sustainable living."
    return_direct: bool = True
    
    def _run(self, category: str = "general", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get sustainability tips by category"""
        
        category = category.lower().strip()
        
        tips_data = {
            "home": [
                "Switch to LED bulbs - they use 75% less energy 🟢",
                "Unplug electronics when not in use 🟢",
                "Use cold water for laundry 🟢",
                "Air dry clothes instead of using a dryer 🟢",
                "Fix leaky faucets promptly 🟢",
                "Install low-flow showerheads 🟢"
            ],
            "transport": [
                "Walk or bike for short trips under 2 miles 🟢",
                "Use public transportation for commuting 🟢",
                "Carpool with colleagues or neighbors 🟢",
                "Maintain proper tire pressure 🟡",
                "Consider an electric or hybrid vehicle 🟢",
                "Avoid excessive idling 🟢"
            ],
            "food": [
                "Eat locally-grown, seasonal food 🟢",
                "Reduce food waste by meal planning 🟢",
                "Choose plant-based meals a few times a week 🟢",
                "Compost food scraps 🟢",
                "Bring reusable containers for takeout 🟢",
                "Avoid single-use plastic water bottles 🟢"
            ],
            "waste": [
                "Practice the 3 R's: Reduce, Reuse, Recycle 🟢",
                "Avoid single-use plastics 🟢",
                "Use reusable bags, bottles, and containers 🟢",
                "Repair items instead of replacing them 🟢",
                "Start a composting system 🟢",
                "Donate unwanted items instead of throwing away 🟢"
            ],
            "general": [
                "Plant native trees and plants in your community 🟢",
                "Support eco-friendly businesses 🟢",
                "Participate in local clean-up events 🟢",
                "Reduce water usage by taking shorter showers 🟢",
                "Use natural cleaning products 🟢",
                "Calculate and track your carbon footprint 🟡"
            ]
        }
        
        if category not in tips_data:
            category = "general"
        
        output = f"""
========================================
{category.upper()} SUSTAINABILITY TIPS
========================================

"""
        for i, tip in enumerate(tips_data[category], 1):
            output += f"{i}. {tip}\n"
        
        output += """

Color Guide:
🟢 Easy / High impact
🟡 Moderate effort / Medium impact

========================================
"""
        return output
    
    async def _arun(self, category: str = "general") -> str:
        return self._run(category)