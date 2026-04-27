# -*- coding: utf-8 -*-
# src/tools/extra_tools.py
#
# FIX NOTES (2026-04-27-v3):
#   - Replaced "===" ASCII borders with markdown bold/bullets.
#     Streamlit treats a line of "=" under text as an <h2> underline,
#     which caused the giant-font rendering bug.
#   - Replaced "\n\n========\nSECTION\n========\n" section separators
#     with markdown "---" horizontal rules (renders as a thin <hr>).
#   - All section titles now use **bold** instead of ALL-CAPS headings.
 
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
 
 
class CarbonFootprintCalculator(BaseTool):
    name: str = "Carbon_Footprint_Calculator"
    description: str = "Provides carbon footprint estimates for cities and activities."
    return_direct: bool = True
 
    def _get_city_carbon_footprint(self, city: str) -> dict:
        city_lower = city.lower()
        city_profiles = {
            "delhi": {
                "per_capita": 2.1,
                "main_sources": ["transportation", "industrial", "power plants"],
                "trend": "📈 Increasing",
                "rank": "Moderate",
            },
            "mumbai": {
                "per_capita": 1.8,
                "main_sources": ["transportation", "commercial", "power plants"],
                "trend": "📈 Increasing",
                "rank": "Moderate",
            },
            "chennai": {
                "per_capita": 2.0,
                "main_sources": ["transportation", "industry", "residential"],
                "trend": "📈 Increasing",
                "rank": "Moderate",
            },
            "kolkata": {
                "per_capita": 1.9,
                "main_sources": ["transportation", "industry", "residential"],
                "trend": "📈 Increasing",
                "rank": "Moderate",
            },
            "london": {
                "per_capita": 5.5,
                "main_sources": ["transportation", "heating", "aviation"],
                "trend": "📉 Decreasing",
                "rank": "High",
            },
            "new york": {
                "per_capita": 6.3,
                "main_sources": ["transportation", "buildings", "industry"],
                "trend": "📉 Decreasing",
                "rank": "High",
            },
            "beijing": {
                "per_capita": 8.1,
                "main_sources": ["coal power", "industry", "transportation"],
                "trend": "📉 Decreasing",
                "rank": "Very High",
            },
            "tokyo": {
                "per_capita": 4.4,
                "main_sources": ["transportation", "industry", "residential"],
                "trend": "📉 Decreasing",
                "rank": "Moderate",
            },
            "sydney": {
                "per_capita": 7.9,
                "main_sources": ["electricity", "transportation", "buildings"],
                "trend": "📉 Decreasing",
                "rank": "High",
            },
        }
        for city_name, profile in city_profiles.items():
            if city_name in city_lower:
                return profile.copy()
        # Generic fallback for unknown cities
        return {
            "per_capita": 3.0,
            "main_sources": ["transportation", "industry", "residential"],
            "trend": "➡️ Stable",
            "rank": "Moderate",
        }
 
    def _impact_label(self, per_capita: float) -> tuple[str, str]:
        if per_capita <= 2.0:
            return "🟢", "Low Impact"
        elif per_capita <= 5.0:
            return "🟡", "Moderate Impact"
        else:
            return "🔴", "High Impact"
 
    def _run(
        self,
        activity: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        activity_lower = activity.lower()
        known_cities = [
            "delhi", "mumbai", "chennai", "kolkata",
            "london", "new york", "beijing", "tokyo", "sydney",
        ]
 
        # ── City carbon footprint ─────────────────────────────────────
        for city in known_cities:
            if city in activity_lower:
                profile = self._get_city_carbon_footprint(city)
                icon, impact = self._impact_label(profile["per_capita"])
                sources = ", ".join(profile["main_sources"])
 
                return (
                    f"🌱 **Carbon Footprint — {city.title()}**\n\n"
                    f"| Metric | Value |\n"
                    f"|--------|-------|\n"
                    f"| Per Capita CO₂ | **{profile['per_capita']} tons/year** {icon} |\n"
                    f"| Impact Level | {impact} |\n"
                    f"| Rank | {profile['rank']} |\n"
                    f"| Trend | {profile['trend']} |\n\n"
                    f"**Main Sources:** {sources}\n\n"
                    "---\n"
                    "**Impact Reference**\n"
                    "- 🟢 Low Impact — below 2.0 tons CO₂/year\n"
                    "- 🟡 Moderate Impact — 2.0 to 5.0 tons CO₂/year\n"
                    "- 🔴 High Impact — above 5.0 tons CO₂/year\n"
                )
 
        # ── Activity: car travel ──────────────────────────────────────
        if "car" in activity_lower or "drive" in activity_lower or "vehicle" in activity_lower:
            return (
                "🚗 **Carbon Footprint — Car Travel**\n\n"
                "| Vehicle Type | CO₂ per 10 km | Impact |\n"
                "|--------------|---------------|--------|\n"
                "| Gasoline/Petrol | 2.3 kg CO₂ | 🔴 High |\n"
                "| Hybrid | 1.5 kg CO₂ | 🟡 Moderate |\n"
                "| Electric (grid avg.) | 1.2 kg CO₂ | 🟢 Low |\n\n"
                "**Tip:** Switching from a petrol car to an EV can cut your "
                "travel emissions by nearly 50% depending on your local grid.\n"
            )
 
        # ── Activity: flight ──────────────────────────────────────────
        if "flight" in activity_lower or "fly" in activity_lower or "plane" in activity_lower:
            return (
                "✈️ **Carbon Footprint — Air Travel**\n\n"
                "| Flight Type | CO₂ per passenger |\n"
                "|-------------|-------------------|\n"
                "| Short haul (< 1,500 km) | ~0.26 tons CO₂ |\n"
                "| Medium haul (1,500–4,000 km) | ~0.60 tons CO₂ |\n"
                "| Long haul (> 4,000 km) | ~1.50 tons CO₂ |\n\n"
                "**Tip:** One long-haul return flight can account for over "
                "half of an average person's annual carbon budget.\n"
            )
 
        # ── Generic help text ─────────────────────────────────────────
        return (
            "🌱 **Carbon Footprint Calculator**\n\n"
            "I can estimate the carbon footprint for:\n\n"
            "- **Cities:** e.g. *carbon footprint of Delhi*, *London CO₂ emissions*\n"
            "- **Transport:** e.g. *car carbon footprint*, *flight emissions*\n\n"
            "Please include a city name or activity in your query.\n"
        )
 
    async def _arun(self, activity: str) -> str:
        return self._run(activity)
 
 
# ─────────────────────────────────────────────────────────────────────────────
 
 
class SustainabilityTipsTool(BaseTool):
    name: str = "Sustainability_Tips"
    description: str = "Provides practical tips for sustainable living."
    return_direct: bool = True
 
    # Tips database — each category is a list of (tip_text, impact) tuples.
    # impact: "high" | "medium"
    TIPS: dict = {
        "home": [
            ("Switch to LED bulbs — uses 75% less energy than incandescent", "high"),
            ("Unplug electronics and chargers when not in use (phantom load)", "high"),
            ("Wash clothes in cold water — saves ~90% of the energy used for heating", "high"),
            ("Air-dry clothes instead of using a tumble dryer", "high"),
            ("Fix leaky faucets — a dripping tap wastes up to 20 litres/day", "high"),
            ("Install low-flow showerheads to cut water use by 40%", "high"),
            ("Set your thermostat 1°C lower in winter — saves ~8% on heating bills", "medium"),
            ("Use a smart power strip to eliminate standby power drain", "medium"),
        ],
        "transport": [
            ("Walk or cycle for trips under 3 km — zero emissions, better health", "high"),
            ("Use public transport for your daily commute", "high"),
            ("Carpool with colleagues or neighbours", "high"),
            ("Consider an electric or hybrid vehicle for your next purchase", "high"),
            ("Maintain correct tyre pressure — improves fuel efficiency by ~3%", "medium"),
            ("Combine errands into one trip to reduce total mileage", "medium"),
            ("Work from home when possible to eliminate commute emissions", "medium"),
        ],
        "food": [
            ("Choose locally-grown, seasonal produce — cuts transport emissions", "high"),
            ("Reduce food waste by meal planning and batch cooking", "high"),
            ("Eat more plant-based meals — meat production is a major GHG source", "high"),
            ("Compost food scraps to divert waste from landfill", "high"),
            ("Bring reusable bags and containers when shopping", "medium"),
            ("Buy in bulk to reduce packaging waste", "medium"),
        ],
        "waste": [
            ("Follow the hierarchy: Reduce → Reuse → Recycle → Recover", "high"),
            ("Avoid single-use plastics — choose reusable alternatives", "high"),
            ("Repair and maintain items instead of replacing them", "high"),
            ("Donate or sell unwanted goods rather than discarding", "high"),
            ("Separate recyclables correctly — contamination ruins whole batches", "medium"),
            ("Choose products with minimal or recyclable packaging", "medium"),
        ],
        "water": [
            ("Take shorter showers — cutting by 2 minutes saves ~18 litres", "high"),
            ("Turn off the tap while brushing teeth — saves 6 litres/minute", "high"),
            ("Collect rainwater for watering plants and gardens", "high"),
            ("Run dishwashers and washing machines only when full", "medium"),
            ("Use a broom instead of a hosepipe to clean driveways", "medium"),
        ],
        "energy": [
            ("Switch to a renewable energy tariff from your electricity supplier", "high"),
            ("Install rooftop solar panels if possible", "high"),
            ("Improve home insulation to reduce heating and cooling needs", "high"),
            ("Use a programmable or smart thermostat", "medium"),
            ("Replace old appliances with energy-rated (A+++) models", "medium"),
        ],
        "general": [
            ("Calculate your personal carbon footprint and set reduction targets", "high"),
            ("Plant native trees — they support local biodiversity too", "high"),
            ("Support and vote for environmentally responsible policies", "high"),
            ("Participate in local clean-up and rewilding events", "high"),
            ("Use natural, biodegradable cleaning products", "medium"),
            ("Choose eco-certified products (FSC, Fair Trade, EU Ecolabel)", "medium"),
        ],
    }
 
    CATEGORY_MAP: dict = {
        "home": ["home", "house", "flat", "apartment", "indoors", "indoor", "kitchen", "lighting", "bulb"],
        "transport": ["transport", "car", "drive", "commute", "travel", "bike", "cycle", "bus", "train", "flight", "fly"],
        "food": ["food", "meal", "diet", "eat", "grocery", "shop", "vegan", "vegetarian", "meat"],
        "waste": ["waste", "recycle", "recycling", "trash", "rubbish", "litter", "plastic", "packaging"],
        "water": ["water", "shower", "tap", "irrigation", "drought"],
        "energy": ["energy", "electricity", "solar", "power", "heating", "cooling", "appliance"],
    }
 
    def _detect_category(self, query: str) -> str:
        q = query.lower()
        for category, keywords in self.CATEGORY_MAP.items():
            if any(kw in q for kw in keywords):
                return category
        return "general"
 
    def _run(
        self,
        category: str = "general",
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        detected = self._detect_category(category)
        tips = self.TIPS.get(detected, self.TIPS["general"])
 
        # Separate by impact level
        high = [(i + 1, t) for i, (t, lvl) in enumerate(tips) if lvl == "high"]
        medium = [(i + 1, t) for i, (t, lvl) in enumerate(tips) if lvl == "medium"]
 
        lines = [f"♻️ **Sustainability Tips — {detected.title()}**\n"]
 
        if high:
            lines.append("**🟢 High Impact Actions**\n")
            for _, tip in high:
                lines.append(f"- {tip}")
            lines.append("")
 
        if medium:
            lines.append("**🟡 Medium Impact Actions**\n")
            for _, tip in medium:
                lines.append(f"- {tip}")
            lines.append("")
 
        lines.append("---")
        lines.append(
            "*🌍 Every action counts. Small daily changes compound into "
            "meaningful environmental impact over time.*"
        )
 
        return "\n".join(lines)
 
    async def _arun(self, category: str = "general") -> str:
        return self._run(category)