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
        
        # City data
        city_data = {
            "delhi": {"per_capita": 2.1, "sources": "transportation, industrial, power plants"},
            "mumbai": {"per_capita": 1.8, "sources": "transportation, commercial, power plants"},
            "chennai": {"per_capita": 2.0, "sources": "transportation, industry, residential"},
            "kolkata": {"per_capita": 1.9, "sources": "transportation, industry, residential"},
            "london": {"per_capita": 5.5, "sources": "transportation, heating, aviation"},
            "new york": {"per_capita": 6.3, "sources": "transportation, buildings, industry"},
        }
        
        for city, data in city_data.items():
            if city in activity_lower:
                icon = "🟢" if data["per_capita"] <= 2.0 else "🟡" if data["per_capita"] <= 5.0 else "🔴"
                return f"""
CARBON FOOTPRINT: {city.upper()}
Per Capita: {data['per_capita']} tons CO2/year {icon}
Main Sources: {data['sources']}
---
Impact Guide: 🟢 Low (<2.0)  🟡 Moderate (2-5)  🔴 High (>5)
"""
        
        if "car" in activity_lower:
            return """
CARBON FOOTPRINT: Car Travel
Gasoline: 2.3 kg CO2/10km 🔴
Electric: 1.2 kg CO2/10km 🟢
Hybrid: 1.5 kg CO2/10km 🟡
"""
        
        return "Ask about specific cities like Delhi, Mumbai, or car travel."

    async def _arun(self, activity: str) -> str:
        return self._run(activity)


class SustainabilityTipsTool(BaseTool):
    name: str = "Sustainability_Tips"
    description: str = "Provides practical tips for sustainable living."
    return_direct: bool = True

    def _run(self, category: str = "general", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        tips = {
            "home": [
                "Switch to LED bulbs - uses 75% less energy 🟢",
                "Unplug electronics when not in use 🟢",
                "Use cold water for laundry 🟢",
            ],
            "transport": [
                "Walk or bike for short trips 🟢",
                "Use public transportation 🟢",
                "Carpool with colleagues 🟢",
            ],
            "general": [
                "Reduce, Reuse, Recycle 🟢",
                "Plant native trees 🟢",
                "Support eco-friendly businesses 🟢",
            ]
        }
        
        category_lower = category.lower()
        if 'home' in category_lower:
            selected = tips["home"]
        elif 'transport' in category_lower or 'car' in category_lower:
            selected = tips["transport"]
        else:
            selected = tips["general"]
        
        return "SUSTAINABILITY TIPS\n\n" + "\n".join(f"• {t}" for t in selected)

    async def _arun(self, category: str = "general") -> str:
        return self._run(category)