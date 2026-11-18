from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.schemas.comparison import ComparisonRequest, ComparisonResponse, SpecComparisonRow
from backend.app.schemas.product import ProductResponse
from backend.app.repositories.product_repository import ProductRepository

CATEGORY_SPEC_LABELS = {
    "Laptops": [
        ("price", "Price (INR)"),
        ("processor", "Processor"),
        ("ram_gb", "RAM (GB)"),
        ("storage_gb", "Storage (GB)"),
        ("gpu", "Graphics (GPU)"),
        ("display_size_inch", "Display Size (inches)"),
        ("battery_hours", "Battery Life (hours)"),
        ("weight_kg", "Weight (kg)"),
        ("os", "Operating System"),
    ],
    "Smartphones": [
        ("price", "Price (INR)"),
        ("processor", "Processor"),
        ("ram_gb", "RAM (GB)"),
        ("storage_gb", "Storage (GB)"),
        ("camera_mp", "Main Camera (MP)"),
        ("battery_mah", "Battery Capacity (mAh)"),
        ("display_size_inch", "Display Size (inches)"),
        ("refresh_rate_hz", "Refresh Rate (Hz)"),
        ("os", "Operating System"),
    ],
    "Headphones": [
        ("price", "Price (INR)"),
        ("type", "Headphone Type"),
        ("connectivity", "Connectivity"),
        ("active_noise_cancellation", "Active Noise Cancellation"),
        ("battery_hours", "Battery Life (hours)"),
        ("weight_g", "Weight (g)"),
    ],
    "Monitors": [
        ("price", "Price (INR)"),
        ("screen_size_inch", "Screen Size (inches)"),
        ("resolution", "Resolution"),
        ("refresh_rate_hz", "Refresh Rate (Hz)"),
        ("panel_type", "Panel Type"),
        ("response_time_ms", "Response Time (ms)"),
    ],
    "Keyboards": [
        ("price", "Price (INR)"),
        ("switch_type", "Switch Type"),
        ("layout", "Layout"),
        ("connectivity", "Connectivity"),
        ("rgb_backlight", "RGB Backlight"),
    ],
    "Mice": [
        ("price", "Price (INR)"),
        ("sensor_dpi", "Max DPI"),
        ("weight_g", "Weight (g)"),
        ("connectivity", "Connectivity"),
        ("programmable_buttons", "Programmable Buttons"),
    ],
    "Tablets": [
        ("price", "Price (INR)"),
        ("screen_size_inch", "Screen Size (inches)"),
        ("ram_gb", "RAM (GB)"),
        ("storage_gb", "Storage (GB)"),
        ("stylus_support", "Stylus Support"),
        ("cellular_5g", "Cellular 5G"),
    ],
    "Gaming Accessories": [
        ("price", "Price (INR)"),
        ("platform", "Supported Platforms"),
        ("connectivity", "Connectivity"),
        ("feature", "Core Feature"),
    ],
    "Storage Devices": [
        ("price", "Price (INR)"),
        ("type", "Storage Type"),
        ("capacity_gb", "Capacity (GB)"),
        ("read_speed_mbps", "Read Speed (MB/s)"),
        ("interface", "Interface"),
    ],
}

class ProductComparator:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ProductRepository(db)

    def compare_products(self, request: ComparisonRequest) -> ComparisonResponse:
        products = self.repo.get_by_ids(request.product_ids)
        if len(products) < 2:
            raise ValueError("At least 2 valid products are required for comparison.")

        primary_category = products[0].category
        prod_dicts = [self.repo.format_product_dict(p) for p in products]

        # Determine spec labels
        spec_keys = CATEGORY_SPEC_LABELS.get(primary_category, [("price", "Price (INR)")])

        specs_table: List[SpecComparisonRow] = []
        for key, label in spec_keys:
            row_values = {}
            for p in prod_dicts:
                if key == "price":
                    val_str = f"₹{p['price']:,.0f}"
                elif key in p.get("specifications", {}):
                    raw = p["specifications"][key]
                    val_str = f"{raw} {key.split('_')[-1].upper()}" if isinstance(raw, (int, float)) and key.endswith(("_gb", "_mah", "_hz", "_kg", "_g", "_hours")) else str(raw)
                else:
                    val_str = "Not available in catalogue"
                row_values[p["id"]] = val_str

            # Check if different
            distinct_vals = set(row_values.values())
            is_diff = len(distinct_vals) > 1

            # Determine winner if numeric
            winner_id = None
            winner_reason = None
            if key == "price":
                cheapest = min(prod_dicts, key=lambda x: x["price"])
                winner_id = cheapest["id"]
                winner_reason = f"Lowest price (₹{cheapest['price']:,.0f})"
            elif key in ["ram_gb", "battery_hours", "battery_mah", "refresh_rate_hz", "read_speed_mbps"]:
                try:
                    highest = max(prod_dicts, key=lambda x: float(x.get("specifications", {}).get(key, 0)))
                    winner_id = highest["id"]
                    winner_reason = f"Highest {label}"
                except (ValueError, TypeError):
                    pass
            elif key in ["weight_kg", "weight_g"]:
                try:
                    lightest = min(prod_dicts, key=lambda x: float(x.get("specifications", {}).get(key, 9999)))
                    winner_id = lightest["id"]
                    winner_reason = "Lightest / Most portable"
                except (ValueError, TypeError):
                    pass

            specs_table.append(SpecComparisonRow(
                spec_key=key,
                label=label,
                values=row_values,
                is_different=is_diff,
                winner_product_id=winner_id,
                winner_reason=winner_reason
            ))

        # Best For logic
        best_for = {}
        tradeoffs = []

        if primary_category == "Laptops":
            # Best for Programming: Max RAM, then CPU
            prog_winner = max(prod_dicts, key=lambda x: (x.get("specifications", {}).get("ram_gb", 0), x["rating"]))
            best_for["Best for Programming"] = f"{prog_winner['brand']} {prog_winner['name']}"

            # Best for Gaming: dedicated GPU
            gaming_candidates = [p for p in prod_dicts if p.get("specifications", {}).get("is_dedicated_gpu", False)]
            if gaming_candidates:
                gaming_winner = max(gaming_candidates, key=lambda x: x["price"])
                best_for["Best for Gaming"] = f"{gaming_winner['brand']} {gaming_winner['name']}"
            else:
                best_for["Best for Gaming"] = "None (All compared models use integrated graphics)"

            # Best for Battery
            bat_winner = max(prod_dicts, key=lambda x: x.get("specifications", {}).get("battery_hours", 0))
            best_for["Best for Battery Life"] = f"{bat_winner['brand']} {bat_winner['name']} ({bat_winner.get('specifications', {}).get('battery_hours')}h)"

        # Best Within Budget / Lowest Price
        cheapest_p = min(prod_dicts, key=lambda x: x["price"])
        best_for["Best Value / Budget"] = f"{cheapest_p['brand']} {cheapest_p['name']} (₹{cheapest_p['price']:,.0f})"

        # Tradeoffs
        if len(prod_dicts) >= 2:
            p1, p2 = prod_dicts[0], prod_dicts[1]
            diff_price = abs(p1["price"] - p2["price"])
            more_expensive = p1 if p1["price"] > p2["price"] else p2
            less_expensive = p2 if p1["price"] > p2["price"] else p1
            
            tradeoffs.append(
                f"{more_expensive['name']} costs ₹{diff_price:,.0f} more than {less_expensive['name']}."
            )
            
            p1_ram = p1.get("specifications", {}).get("ram_gb")
            p2_ram = p2.get("specifications", {}).get("ram_gb")
            if p1_ram and p2_ram and p1_ram != p2_ram:
                tradeoffs.append(
                    f"Memory difference: {p1['name']} has {p1_ram} GB RAM while {p2['name']} provides {p2_ram} GB RAM."
                )

        verdict = (
            f"Comparison completed between {len(prod_dicts)} products in {primary_category}. "
            f"If budget is your priority, {cheapest_p['name']} offers the lowest entry price at ₹{cheapest_p['price']:,.0f}. "
            f"For peak capability, consider the {prog_winner['name'] if primary_category == 'Laptops' else prod_dicts[0]['name']}."
        )

        return ComparisonResponse(
            products=[ProductResponse(**p) for p in prod_dicts],
            category=primary_category,
            specs_table=specs_table,
            best_for=best_for,
            tradeoffs=tradeoffs,
            summary_verdict=verdict
        )
