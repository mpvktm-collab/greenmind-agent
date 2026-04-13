# -*- coding: utf-8 -*-
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import random

class CarbonFootprintCalculator(BaseTool):
    name: str = "Carbon_Footprint_Calculator"
    description: str = "Provides carbon footprint estimates for cities and activities."
    return_direct: bool = True
    
    def _get_city_carbon_footprint(self, city):
        city_lower = city.lower()
        city_profiles = {
            "delhi": {"per_capita": 2.1, "main_sources": ["transportation", "industrial", "power plants"], "trend": "increasing", "rank": "moderate"},
            "mumbai": {"per_capita": 1.8, "main_sources": ["transportation", "commercial", "power plants"], "trend": "increasing", "rank": "moderate"},
            "chennai": {"per_capita": 2.0, "main_sources": ["transportation", "industry", "residential"], "trend": "increasing", "rank": "moderate"},
            "kolkata": {"per_capita": 1.9, "main_sources": ["transportation", "industry", "residential"], "trend": "increasing", "rank": "moderate"},
        }
        for city_name, profile in city_profiles.items():
            if city_name in city_lower:
                return profile.copy()
        return {"per_capita": 3.0, "main_sources": ["transportation", "industry", "residential"], "trend": "stable", "rank": "moderate"}
    
    def _run(self, activity: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        activity_lower = activity.lower()
        known_cities = ['delhi', 'mumbai', 'chennai', 'kolkata']
        
        for city in known_cities:
            if city in activity_lower:
                profile = self._get_city_carbon_footprint(city)
                if profile['per_capita'] <= 2.0:
                    color = "🟢"
                    impact = "Low Impact"
                elif profile['per_capita'] <= 5.0:
                    color = "🟡"
                    impact = "Moderate Impact"
                else:
                    color = "🔴"
                    impact = "High Impact"
                
                return f"""
========================================
CARBON FOOTPRINT: {city.upper()}
========================================

Per Capita: {profile['per_capita']} tons CO2/year {color} ({impact})
Rank: {profile['rank'].upper()}
Trend: {profile['trend']}
Main Sources: {', '.join(profile['main_sources'])}

========================================
Color Reference:
🟢 Low Impact (less than 2.0 tons)
🟡 Moderate Impact (2.0 - 5.0 tons)
🔴 High Impact (greater than 5.0 tons)
========================================
"""
        
        if "car" in activity_lower:
            return """
========================================
CARBON FOOTPRINT: Car Travel
========================================

Gasoline: 2.3 kg CO2 per 10 km 🟡
Electric: 1.2 kg CO2 per 10 km 🟢
Hybrid: 1.5 kg CO2 per 10 km 🟢

========================================
Color Reference:
🟢 Best choice    🟡 Moderate impact
========================================
"""
        
        return """
========================================
CARBON FOOTPRINT CALCULATOR
========================================

Ask about:
• "carbon footprint of Delhi"
• "carbon footprint of Mumbai"
• "car carbon footprint"

========================================
"""
    
    async def _arun(self, activity: str) -> str:
        return self._run(activity)


class SustainabilityTipsTool(BaseTool):
    name: str = "Sustainability_Tips"
    description: str = "Provides practical tips for sustainable living."
    return_direct: bool = True
    
    def _run(self, category: str = "general", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        category = category.lower().strip()
        
        tips_data = {
            "home": [
                "Switch to LED bulbs - 75% less energy 🟢",
                "Unplug electronics when not in use 🟢",
                "Use cold water for laundry 🟢",
                "Air dry clothes instead of dryer 🟢",
                "Fix leaky faucets 🟢",
                "Install low-flow showerheads 🟢"
            ],
            "transport": [
                "Walk or bike for short trips (under 2 miles) 🟢",
                "Use public transportation for commuting 🟢",
                "Carpool with colleagues or neighbors 🟢",
                "Consider an electric or hybrid vehicle 🟢",
                "Maintain proper tire pressure 🟡"
            ],
            "food": [
                "Eat locally-grown, seasonal food 🟢",
                "Reduce food waste by meal planning 🟢",
                "Choose plant-based meals 🟢",
                "Compost food scraps 🟢"
            ],
            "waste": [
                "Practice Reduce, Reuse, Recycle 🟢",
                "Avoid single-use plastics 🟢",
                "Use reusable bags and bottles 🟢",
                "Repair items instead of replacing 🟢"
            ],
            "general": [
                "Plant native trees in your community 🟢",
                "Support eco-friendly businesses 🟢",
                "Participate in local clean-up events 🟢",
                "Calculate your carbon footprint 🟡",
                "Reduce water usage - take shorter showers 🟢",
                "Use natural cleaning products 🟢"
            ]
        }
        
        # Check for specific categories in the query
        query_lower = category.lower()
        if 'home' in query_lower or 'house' in query_lower:
            category = 'home'
        elif 'transport' in query_lower or 'car' in query_lower or 'bike' in query_lower:
            category = 'transport'
        elif 'food' in query_lower or 'meal' in query_lower or 'diet' in query_lower:
            category = 'food'
        elif 'waste' in query_lower or 'recycle' in query_lower or 'plastic' in query_lower:
            category = 'waste'
        else:
            category = 'general'
        
        output = f"""
========================================
{category.upper()} SUSTAINABILITY TIPS
========================================

"""
        for i, tip in enumerate(tips_data[category], 1):
            output += f"{i}. {tip}\n"
        
        output += f"""
========================================
Color Reference: 🟢 Easy/High impact    🟡 Moderate effort
========================================
"""
        return output
    
    async def _arun(self, category: str = "general") -> str:
        return self._run(category)