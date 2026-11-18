import re
from typing import Dict, Any, List, Optional
from backend.app.schemas.assistant import ExtractedConstraints

CATEGORY_KEYWORDS = {
    "Laptops": ["laptop", "laptops", "notebook", "ultrabook", "macbook", "thinkpad", "workstation"],
    "Smartphones": ["smartphone", "smartphones", "phone", "phones", "mobile", "android", "iphone", "cellular"],
    "Headphones": ["headphone", "headphones", "earphone", "earphones", "earbuds", "airpods", "headset", "audio"],
    "Smartwatches": ["smartwatch", "smartwatches", "watch", "wearable", "fitness band", "tracker"],
    "Monitors": ["monitor", "monitors", "display", "screen"],
    "Keyboards": ["keyboard", "keyboards", "mechanical keyboard", "keeb"],
    "Mice": ["mouse", "mice", "trackpad"],
    "Tablets": ["tablet", "tablets", "ipad", "tab"],
    "Gaming Accessories": ["controller", "gamepad", "capture card", "gaming headset", "gaming accessory"],
    "Storage Devices": ["ssd", "nvme", "hard drive", "storage", "portable ssd", "flash drive", "thumb drive"],
}

KNOWN_BRANDS = [
    "Apple", "Lenovo", "Dell", "HP", "ASUS", "Acer", "Samsung", "OnePlus",
    "Google", "Xiaomi", "Nothing", "Sony", "Bose", "Sennheiser", "JBL",
    "Audio-Technica", "Garmin", "Amazfit", "Fitbit", "LG", "BenQ",
    "Keychron", "Logitech", "Corsair", "Razer", "Ducky", "SteelSeries",
    "Glorious", "Crucial", "Western Digital", "Kingston", "Elgato", "HyperX"
]

class QueryParser:
    @staticmethod
    def parse(query: str) -> ExtractedConstraints:
        """Extract category, brand, budget, ram, and intended usage from natural query."""
        q_lower = query.lower()
        extracted = ExtractedConstraints()
        
        # 1. Category extraction
        for cat, keywords in CATEGORY_KEYWORDS.items():
            for kw in keywords:
                if re.search(r"\b" + re.escape(kw) + r"\b", q_lower):
                    extracted.category = cat
                    break
            if extracted.category:
                break
                
        # 2. Brand extraction
        for brand in KNOWN_BRANDS:
            if re.search(r"\b" + re.escape(brand.lower()) + r"\b", q_lower):
                extracted.brand = brand
                break

        # 3. Budget extraction (e.g., "under 70,000", "below 70k", "my budget is ₹70000", "budget of 50k")
        budget_match = re.search(r"(?:under|below|less than|within|budget\s*(?:is|of|:)?|max(?:imum)?)\s*(?:rs\.?|inr|₹)?\s*([\d,]+)\s*(k|thousand|lakh|lac)?", q_lower)
        if budget_match:
            val_str = budget_match.group(1).replace(",", "")
            multiplier = 1.0
            unit = budget_match.group(2)
            if unit in ["k", "thousand"]:
                multiplier = 1000.0
            elif unit in ["lakh", "lac"]:
                multiplier = 100000.0
            try:
                extracted.budget_max = float(val_str) * multiplier
            except ValueError:
                pass

        # Check for range: e.g. "between 30000 and 60000"
        range_match = re.search(r"between\s*(?:rs\.?|inr|₹)?\s*([\d,]+)\s*(?:and|to)\s*(?:rs\.?|inr|₹)?\s*([\d,]+)", q_lower)
        if range_match:
            try:
                extracted.budget_min = float(range_match.group(1).replace(",", ""))
                extracted.budget_max = float(range_match.group(2).replace(",", ""))
            except ValueError:
                pass

        # 4. RAM extraction: e.g., "16 gb ram", "16gb", "32 gb"
        ram_match = re.search(r"\b(\d{1,2})\s*(?:gb|g)\s*(?:ram)?\b", q_lower)
        if ram_match:
            try:
                extracted.ram_gb = float(ram_match.group(1))
            except ValueError:
                pass

        # 5. Intended usage extraction
        usage_terms = []
        for term in ["coding", "programming", "python", "machine learning", "ml", "data science", "gaming", "college", "student", "video editing", "office", "travel", "fitness"]:
            if term in q_lower:
                usage_terms.append(term)
        if usage_terms:
            extracted.intended_usage = ", ".join(usage_terms)

        # 6. Raw keywords (exclude stopwords)
        stopwords = {"i", "want", "a", "an", "the", "for", "with", "and", "or", "in", "under", "below", "to", "prefer", "good", "best", "recommend", "find", "show"}
        tokens = [w.strip() for w in re.findall(r"\b[a-zA-Z0-9_\-\.]{2,}\b", q_lower)]
        extracted.raw_keywords = [t for t in tokens if t not in stopwords]

        return extracted
