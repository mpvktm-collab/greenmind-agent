# src/tools/extra_tools.py
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import random

class CarbonFootprintCalculator(BaseTool):
    """Tool for calculating carbon footprint"""
    
    name: str = "Carbon_Footprint_Calculator"
    description: str = """
    Provides estimates of carbon footprint for various activities and suggests reduction strategies.
    Use this when asked about carbon footprint of activities like driving, flying, electricity use, etc.
    Also provides city-level carbon footprint estimates with color-coded comparisons.
    Input should be an activity (car, flight, electricity, meat, plastic) or a city name.
    """
    
    def _get_footprint_color(self, value, low=2.0, high=5.0):
        """Return color indicator based on carbon footprint value"""
        if value <= low:
            return "🟢"  # Green - good
        elif value <= high:
            return "🟡"  # Yellow - moderate
        else:
            return "🔴"  # Red - high
    
    def _create_comparison_bar(self, value, max_value=10, bar_length=20):
        """Create a visual comparison bar"""
        position = int((value / max_value) * bar_length)
        if position > bar_length:
            position = bar_length
        
        bar = ""
        for i in range(bar_length):
            if i < position:
                bar += "█"
            else:
                bar += "░"
        
        return bar
    
    def _get_city_carbon_footprint(self, city):
        """Calculate approximate carbon footprint for a city with color coding"""
        city_lower = city.lower()
        
        # City-specific carbon profiles (simulated data)
        city_profiles = {
            "delhi": {
                "per_capita": 2.1,
                "main_sources": ["transportation", "industrial", "power plants"],
                "trend": "increasing",
                "rank": "moderate"
            },
            "mumbai": {
                "per_capita": 1.8,
                "main_sources": ["transportation", "commercial", "power plants"],
                "trend": "increasing",
                "rank": "moderate"
            },
            "new york": {
                "per_capita": 4.2,
                "main_sources": ["buildings", "transportation", "waste"],
                "trend": "stable",
                "rank": "high"
            },
            "london": {
                "per_capita": 3.8,
                "main_sources": ["buildings", "transportation", "aviation"],
                "trend": "decreasing",
                "rank": "moderate-high"
            },
            "tokyo": {
                "per_capita": 3.5,
                "main_sources": ["buildings", "transportation", "industry"],
                "trend": "stable",
                "rank": "moderate-high"
            },
            "beijing": {
                "per_capita": 5.1,
                "main_sources": ["industry", "power plants", "transportation"],
                "trend": "decreasing",
                "rank": "very high"
            },
            "shanghai": {
                "per_capita": 4.8,
                "main_sources": ["industry", "shipping", "power plants"],
                "trend": "increasing",
                "rank": "high"
            },
            "sydney": {
                "per_capita": 3.2,
                "main_sources": ["transportation", "buildings", "industry"],
                "trend": "stable",
                "rank": "moderate"
            },
            "melbourne": {
                "per_capita": 3.0,
                "main_sources": ["transportation", "buildings", "energy"],
                "trend": "stable",
                "rank": "moderate"
            },
            "paris": {
                "per_capita": 2.9,
                "main_sources": ["buildings", "transportation", "commercial"],
                "trend": "decreasing",
                "rank": "moderate"
            },
            "berlin": {
                "per_capita": 3.1,
                "main_sources": ["transportation", "buildings", "renewables"],
                "trend": "decreasing",
                "rank": "moderate"
            },
            "copenhagen": {
                "per_capita": 2.3,
                "main_sources": ["transportation", "buildings", "waste-to-energy"],
                "trend": "decreasing",
                "rank": "good"
            },
            "oslo": {
                "per_capita": 1.9,
                "main_sources": ["transportation", "buildings", "electric"],
                "trend": "decreasing",
                "rank": "good"
            },
            "singapore": {
                "per_capita": 3.3,
                "main_sources": ["industry", "shipping", "cooling"],
                "trend": "increasing",
                "rank": "moderate"
            },
            "hong kong": {
                "per_capita": 3.7,
                "main_sources": ["buildings", "transportation", "shipping"],
                "trend": "stable",
                "rank": "moderate-high"
            },
            "los angeles": {
                "per_capita": 3.9,
                "main_sources": ["transportation", "buildings", "industry"],
                "trend": "stable",
                "rank": "high"
            },
            "chicago": {
                "per_capita": 3.6,
                "main_sources": ["buildings", "transportation", "industry"],
                "trend": "stable",
                "rank": "moderate-high"
            },
            "toronto": {
                "per_capita": 3.4,
                "main_sources": ["buildings", "transportation", "industry"],
                "trend": "stable",
                "rank": "moderate"
            },
            "mexico city": {
                "per_capita": 2.8,
                "main_sources": ["transportation", "industry", "residential"],
                "trend": "increasing",
                "rank": "moderate"
            },
            "sao paulo": {
                "per_capita": 2.2,
                "main_sources": ["transportation", "industry", "deforestation"],
                "trend": "increasing",
                "rank": "moderate"
            },
            "jakarta": {
                "per_capita": 2.4,
                "main_sources": ["transportation", "industry", "waste"],
                "trend": "increasing",
                "rank": "moderate"
            },
            "bangkok": {
                "per_capita": 2.6,
                "main_sources": ["transportation", "commercial", "industry"],
                "trend": "increasing",
                "rank": "moderate"
            },
            "dubai": {
                "per_capita": 6.2,
                "main_sources": ["buildings", "transportation", "desalination"],
                "trend": "increasing",
                "rank": "very high"
            },
            "moscow": {
                "per_capita": 4.5,
                "main_sources": ["buildings", "transportation", "industry"],
                "trend": "stable",
                "rank": "high"
            }
        }
        
        # Check if city is in our profiles
        for city_name, profile in city_profiles.items():
            if city_name in city_lower:
                return profile
        
        # Default for unknown cities (based on name characteristics)
        name_length = len(city)
        if name_length < 5:
            per_capita = 2.5 + random.random() * 1.5
            rank = "moderate"
        elif name_length < 8:
            per_capita = 3.0 + random.random() * 2.0
            rank = "moderate-high"
        else:
            per_capita = 3.5 + random.random() * 2.5
            rank = "high"
        
        # Random trend
        trends = ["increasing", "stable", "decreasing"]
        trend = random.choice(trends)
        
        return {
            "per_capita": round(per_capita, 1),
            "main_sources": ["transportation", "industry", "residential"],
            "trend": trend,
            "rank": rank
        }
    
    def _run(self, activity: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Calculate carbon footprint for common activities or cities"""
        
        activity_lower = activity.lower()
        
        # Expanded city keywords for better detection
        city_keywords = [
            'delhi', 'mumbai', 'new york', 'london', 'tokyo', 'beijing', 'shanghai',
            'paris', 'berlin', 'sydney', 'melbourne', 'copenhagen', 'oslo', 'singapore',
            'hong kong', 'los angeles', 'chicago', 'toronto', 'mexico city', 'sao paulo',
            'jakarta', 'bangkok', 'dubai', 'moscow', 'city', 'town', 'capital'
        ]
        
        # Check if this is a city query (short query with city keywords)
        words = activity_lower.split()
        is_city_query = any(city in activity_lower for city in city_keywords) and len(words) < 6
        
        if is_city_query:
            # Extract city name (improved approach)
            city_name = activity_lower
            for word in words:
                # Check for multi-word cities
                if word in ['new', 'hong', 'los', 'sao', 'mexico']:
                    # Handle multi-word city names
                    if word == 'new' and 'york' in activity_lower:
                        city_name = 'new york'
                        break
                    elif word == 'hong' and 'kong' in activity_lower:
                        city_name = 'hong kong'
                        break
                    elif word == 'los' and 'angeles' in activity_lower:
                        city_name = 'los angeles'
                        break
                    elif word == 'sao' and 'paulo' in activity_lower:
                        city_name = 'sao paulo'
                        break
                    elif word == 'mexico' and 'city' in activity_lower:
                        city_name = 'mexico city'
                        break
                elif word in city_keywords:
                    city_name = word
                    break
            
            profile = self._get_city_carbon_footprint(city_name)
            color = self._get_footprint_color(profile['per_capita'])
            comparison_bar = self._create_comparison_bar(profile['per_capita'])
            
            # Determine trend arrow
            if profile['trend'] == 'increasing':
                trend_arrow = "↗️"
            elif profile['trend'] == 'decreasing':
                trend_arrow = "↘️"
            else:
                trend_arrow = "→"
            
            return f"""
CARBON FOOTPRINT for {city_name.upper()}

Estimated per capita carbon footprint: {profile['per_capita']} tons CO2 per year {color}

Comparison to global cities:
{comparison_bar} {profile['per_capita']}/10 tons
Low → → → → → → → → → → → → → → → → → → → → High

Rank: {profile['rank'].upper()}
Trend: {trend_arrow} {profile['trend']}

Main sources:
• {profile['main_sources'][0]}
• {profile['main_sources'][1]}
• {profile['main_sources'][2]}

Global benchmarks:
🟢 < 2.0 tons: Sustainable target
🟡 2.0 - 5.0 tons: Moderate
🔴 > 5.0 tons: High

REDUCTION STRATEGIES FOR CITIES:
1. Expand public transportation infrastructure
2. Increase renewable energy adoption
3. Implement building energy efficiency programs
4. Create low-emission zones
5. Invest in green spaces and urban forestry
6. Promote electric vehicle adoption
7. Improve waste management and recycling

Note: This is estimated data for demonstration purposes.
"""
        
        # Activity-based calculations with color coding
        if "car" in activity_lower or "drive" in activity_lower:
            return """
CARBON FOOTPRINT: Car Travel
• Gasoline car: 2.3 kg CO2 per 10 km 🟡
• Electric vehicle: 1.2 kg CO2 per 10 km 🟢
• Hybrid: 1.5 kg CO2 per 10 km 🟢

Comparison:
🟢 Electric/Hybrid: Best choice
🟡 Gasoline: Moderate impact
🔴 Diesel: Highest impact (not shown)

REDUCTION TIPS:
• Carpool with colleagues 🟢
• Use public transportation when possible 🟢
• Maintain proper tire pressure 🟡
• Consider an electric or hybrid vehicle 🟢
• Combine errands to reduce trips 🟡
"""
        elif "flight" in activity_lower or "fly" in activity_lower or "plane" in activity_lower:
            return """
CARBON FOOTPRINT: Air Travel
• Short flight (<1 hour): 90 kg CO2 per hour 🔴
• Long flight: 120 kg CO2 per hour 🔴
• Round trip NYC-London: ~1.5 tons CO2 🔴

Comparison:
🟢 Train: 6 kg CO2 per 100 km
🟡 Bus: 15 kg CO2 per 100 km
🔴 Plane: 25 kg CO2 per 100 km

REDUCTION TIPS:
• Take direct flights 🟢 (takeoff/landing use most fuel)
• Choose economy class 🟢 (more passengers per flight)
• Consider trains for short distances 🟢
• Offset your flights through certified programs 🟡
• Video conference instead of business travel 🟢
"""
        elif "electricity" in activity_lower or "energy" in activity_lower or "power" in activity_lower:
            return """
CARBON FOOTPRINT: Electricity Use
• Average home: 0.5 kg CO2 per kWh 🟡
• Monthly average: 300-400 kg CO2 🟡
• Annual average: 4-5 tons CO2 🟡

Comparison by energy source:
🟢 Solar/Wind: 0.02 kg CO2 per kWh
🟢 Nuclear: 0.01 kg CO2 per kWh
🟡 Natural Gas: 0.4 kg CO2 per kWh
🔴 Coal: 1.0 kg CO2 per kWh

REDUCTION TIPS:
• Switch to LED bulbs (75% less energy) 🟢
• Unplug electronics when not in use 🟢
• Use energy-efficient appliances 🟢
• Install a programmable thermostat 🟡
• Consider solar panels 🟢
• Choose green energy provider 🟢
"""
        elif "meat" in activity_lower or "food" in activity_lower or "diet" in activity_lower:
            return """
CARBON FOOTPRINT: Food Choices
• Meat-heavy diet: 3.5 kg CO2 per meal 🔴
• Vegetarian diet: 1.7 kg CO2 per meal 🟡
• Vegan diet: 1.2 kg CO2 per meal 🟢

Food comparison (per kg):
🔴 Beef: 27 kg CO2
🟡 Pork: 7 kg CO2
🟡 Chicken: 6 kg CO2
🟢 Vegetables: 2 kg CO2
🟢 Grains: 1.5 kg CO2

REDUCTION TIPS:
• Try meat-free Mondays 🟢
• Choose locally-grown food 🟢
• Reduce food waste 🟢
• Buy seasonal produce 🟡
• Compost food scraps 🟢
"""
        elif "plastic" in activity_lower:
            return """
CARBON FOOTPRINT: Plastic Use
• Plastic production: 6 kg CO2 per kg plastic 🔴
• Single-use bottle: 0.5 kg CO2 each 🟡
• Plastic bag: 0.1 kg CO2 each 🟢

Comparison:
🔴 Virgin plastic: 6 kg CO2 per kg
🟡 Recycled plastic: 3 kg CO2 per kg
🟢 Glass/Steel: 1.5 kg CO2 per kg (reusable)

REDUCTION TIPS:
• Use reusable water bottles 🟢
• Bring your own shopping bags 🟢
• Avoid products with excess packaging 🟡
• Choose glass or metal containers 🟢
• Recycle all plastic waste 🟢
"""
        else:
            return """
Please specify an activity or city:

🌍 CITIES (examples):
• "carbon footprint of Delhi"
• "emissions for New York"
• "carbon footprint London"
• "per capita carbon Tokyo"

🚗 ACTIVITIES (examples):
• "car carbon footprint"
• "flight emissions NYC to London"
• "home energy carbon footprint"
• "meat consumption carbon"
• "plastic footprint"

Color Guide:
🟢 Low impact / Best practice
🟡 Moderate impact
🔴 High impact / Needs improvement

Example: "carbon footprint of Delhi" or "flight emissions"
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
    
    def _get_category_color(self, category):
        """Get color for category header"""
        colors = {
            "home": "🏠",
            "transport": "🚗",
            "food": "🍎",
            "waste": "♻️",
            "general": "🌍"
        }
        return colors.get(category, "📌")
    
    def _run(self, category: str = "general", run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get sustainability tips by category with color coding"""
        
        tips = {
            "home": [
                ("Switch to LED bulbs - they use 75% less energy", "🟢"),
                ("Unplug electronics when not in use to avoid phantom energy", "🟢"),
                ("Use energy-efficient appliances (look for ENERGY STAR)", "🟢"),
                ("Install a programmable thermostat to optimize heating/cooling", "🟡"),
                ("Improve home insulation to reduce energy waste", "🟡"),
                ("Use cold water for laundry when possible", "🟢"),
                ("Air dry clothes instead of using a dryer", "🟢"),
                ("Fix leaky faucets promptly", "🟢"),
                ("Install low-flow showerheads", "🟢"),
                ("Use natural light during daytime", "🟢")
            ],
            "transport": [
                ("Walk or bike for short trips under 2 miles", "🟢"),
                ("Use public transportation for commuting", "🟢"),
                ("Carpool with colleagues or neighbors", "🟢"),
                ("Maintain proper tire pressure for better fuel efficiency", "🟡"),
                ("Consider an electric or hybrid vehicle", "🟢"),
                ("Combine errands into one trip", "🟡"),
                ("Avoid excessive idling", "🟢"),
                ("Use ride-sharing services wisely", "🟡"),
                ("Choose direct flights when flying", "🟡"),
                ("Offset unavoidable travel emissions", "🟡")
            ],
            "food": [
                ("Eat locally-grown, seasonal food", "🟢"),
                ("Reduce food waste by meal planning", "🟢"),
                ("Choose plant-based meals a few times a week", "🟢"),
                ("Compost food scraps", "🟢"),
                ("Grow your own vegetables or herbs", "🟢"),
                ("Buy in bulk to reduce packaging", "🟡"),
                ("Bring reusable containers for takeout", "🟢"),
                ("Support farmers markets", "🟢"),
                ("Choose sustainably caught seafood", "🟡"),
                ("Avoid single-use plastic water bottles", "🟢")
            ],
            "waste": [
                ("Practice the 3 R's: Reduce, Reuse, Recycle", "🟢"),
                ("Avoid single-use plastics", "🟢"),
                ("Use reusable bags, bottles, and containers", "🟢"),
                ("Repair items instead of replacing them", "🟢"),
                ("Buy products with minimal packaging", "🟢"),
                ("Start a composting system", "🟢"),
                ("Donate unwanted items instead of throwing away", "🟢"),
                ("Use both sides of paper", "🟢"),
                ("Choose products made from recycled materials", "🟡"),
                ("Properly dispose of hazardous waste", "🔴")
            ],
            "general": [
                ("Plant native trees and plants in your community", "🟢"),
                ("Support eco-friendly businesses and products", "🟢"),
                ("Educate others about environmental issues", "🟢"),
                ("Participate in local clean-up events", "🟢"),
                ("Choose sustainable and ethical products", "🟡"),
                ("Reduce water usage by taking shorter showers", "🟢"),
                ("Use natural cleaning products", "🟢"),
                ("Opt for digital documents instead of paper", "🟢"),
                ("Invest in renewable energy if possible", "🟢"),
                ("Calculate and track your carbon footprint", "🟡")
            ]
        }
        
        category = category.lower().strip()
        if category not in tips:
            category = "general"
        
        icon = self._get_category_color(category)
        response_lines = [
            f"{icon} {category.upper()} SUSTAINABILITY TIPS {icon}",
            ""
        ]
        
        for i, (tip, color) in enumerate(tips[category], 1):
            response_lines.append(f"{i}. {color} {tip}")
        
        response_lines.extend([
            "",
            "Color Guide:",
            "🟢 Easy / High impact",
            "🟡 Moderate effort / Medium impact",
            "🔴 Advanced / Special circumstances",
            "",
            "Every small action counts towards a greener planet! 🌍"
        ])
        
        return "\n".join(response_lines)
    
    async def _arun(self, category: str = "general") -> str:
        return self._run(category)