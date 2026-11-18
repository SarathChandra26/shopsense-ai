import json
import random
import csv
from pathlib import Path
from typing import List, Dict, Any
from backend.app.core.config import settings
from backend.app.core.logging import logger

random.seed(42)

def generate_laptops(count: int = 150) -> List[Dict[str, Any]]:
    brands = [
        ("Lenovo", ["ThinkPad E14", "ThinkPad T14", "IdeaPad Gaming 3", "Legion Pro 5", "Yoga Slim 7", "LOQ 15"]),
        ("Dell", ["XPS 13", "XPS 15", "Inspiron 15", "G15 Gaming", "Latitude 5430", "Alienware m16"]),
        ("ASUS", ["ZenBook 14", "ROG Zephyrus G14", "TUF Gaming A15", "Vivobook Pro 15", "ROG Strix G16"]),
        ("HP", ["Pavilion 15", "Envy x360", "Victus 16", "Spectre x360", "Omen 16", "ProBook 440"]),
        ("Apple", ["MacBook Air M2", "MacBook Air M3", "MacBook Pro 14 M3", "MacBook Pro 16 M3 Pro"]),
        ("Acer", ["Aspire 5", "Swift Go 14", "Nitro V 15", "Predator Helios Neo 16"]),
    ]
    
    processors = [
        ("Intel Core i5-13420H", "Intel"),
        ("Intel Core i7-13700H", "Intel"),
        ("Intel Core i9-13900HX", "Intel"),
        ("AMD Ryzen 5 7535HS", "AMD"),
        ("AMD Ryzen 7 7840HS", "AMD"),
        ("AMD Ryzen 9 7940HS", "AMD"),
        ("Apple M2 8-Core", "Apple"),
        ("Apple M3 8-Core", "Apple"),
        ("Apple M3 Pro 12-Core", "Apple"),
    ]
    
    rams = [8, 16, 16, 16, 32, 32]
    storages = [512, 512, 1024, 1024, 2048]
    gpus = [
        ("Intel Iris Xe Graphics", False),
        ("AMD Radeon 780M", False),
        ("Apple Integrated 10-core GPU", False),
        ("NVIDIA GeForce RTX 3050 4GB", True),
        ("NVIDIA GeForce RTX 4050 6GB", True),
        ("NVIDIA GeForce RTX 4060 8GB", True),
        ("NVIDIA GeForce RTX 4070 8GB", True),
        ("NVIDIA GeForce RTX 4080 12GB", True),
    ]

    displays = [13.3, 14.0, 15.6, 16.0]
    
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        
        if brand == "Apple":
            proc, _ = random.choice([p for p in processors if "Apple" in p[0]])
            gpu_name, is_dedicated = ("Apple Integrated GPU", False)
            os_name = "macOS Sonoma"
            base_price = random.randint(85000, 195000)
            ram = random.choice([8, 16, 36])
            storage = random.choice([256, 512, 1024])
            battery = round(random.uniform(14.0, 18.0), 1)
            weight = round(random.uniform(1.24, 1.62), 2)
        else:
            proc, _ = random.choice([p for p in processors if "Apple" not in p[0]])
            gpu_name, is_dedicated = random.choice(gpus)
            os_name = "Windows 11 Home"
            ram = random.choice(rams)
            storage = random.choice(storages)
            battery = round(random.uniform(6.0, 10.5), 1)
            weight = round(random.uniform(1.35, 2.45), 2)
            
            # Base price logic
            base_price = 42000
            if "i7" in proc or "Ryzen 7" in proc: base_price += 22000
            elif "i9" in proc or "Ryzen 9" in proc: base_price += 48000
            if ram == 16: base_price += 8000
            elif ram == 32: base_price += 18000
            if storage == 1024: base_price += 6000
            elif storage == 2048: base_price += 14000
            if "RTX 4050" in gpu_name: base_price += 20000
            elif "RTX 4060" in gpu_name: base_price += 34000
            elif "RTX 4070" in gpu_name: base_price += 55000
            elif "RTX 4080" in gpu_name: base_price += 95000
            base_price += random.randint(-3000, 4000)

        disp = random.choice(displays)
        prod_id = f"PROD-LAP-{i:03d}"
        full_name = f"{brand} {model} ({proc}, {ram} GB RAM, {storage} GB SSD, {gpu_name})"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        # Determine main use case in description
        use_cases = []
        if is_dedicated:
            use_cases.append("gaming, machine learning tasks, 3D modeling")
        if ram >= 16:
            use_cases.append("software engineering, Python development, heavy multitasking, Docker workflows")
        if battery >= 12 or weight <= 1.5:
            use_cases.append("college work, lightweight travel, all-day battery productivity")
        if not use_cases:
            use_cases.append("everyday office work, web browsing, student productivity")
        
        desc = (
            f"Powerful {brand} laptop built with {proc}, {ram} GB RAM and {storage} GB NVMe storage. "
            f"Equipped with a crisp {disp}-inch display and {gpu_name}. "
            f"Well-suited for {', '.join(use_cases)}. Offers up to {battery} hours of battery life."
        )

        specs = {
            "processor": proc,
            "ram_gb": ram,
            "storage_gb": storage,
            "gpu": gpu_name,
            "is_dedicated_gpu": is_dedicated,
            "display_size_inch": disp,
            "battery_hours": battery,
            "weight_kg": weight,
            "os": os_name
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Laptops",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(3.9, 4.8), 1),
            "review_count": random.randint(45, 1420),
            "availability_status": "In Stock" if random.random() > 0.08 else "Limited Stock",
            "image_url": f"https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_smartphones(count: int = 150) -> List[Dict[str, Any]]:
    brands = [
        ("Apple", ["iPhone 15", "iPhone 15 Pro", "iPhone 15 Plus", "iPhone 14", "iPhone 13"]),
        ("Samsung", ["Galaxy S24 Ultra", "Galaxy S24", "Galaxy S23 FE", "Galaxy A55 5G", "Galaxy Z Flip 5"]),
        ("OnePlus", ["OnePlus 12", "OnePlus 12R", "OnePlus Nord 4", "OnePlus Open"]),
        ("Google", ["Pixel 8 Pro", "Pixel 8", "Pixel 7a", "Pixel 8a"]),
        ("Xiaomi", ["Xiaomi 14", "Redmi Note 13 Pro+", "Xiaomi 13T"]),
        ("Nothing", ["Nothing Phone (2)", "Nothing Phone (2a)"]),
    ]
    
    processors = ["Snapdragon 8 Gen 3", "Snapdragon 8 Gen 2", "Snapdragon 7+ Gen 3", "A17 Pro", "A16 Bionic", "Tensor G3", "Dimensity 9300"]
    rams = [6, 8, 8, 12, 12, 16]
    storages = [128, 256, 256, 512, 1024]
    
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        ram = random.choice(rams)
        storage = random.choice(storages)
        
        if brand == "Apple":
            proc = random.choice(["A17 Pro", "A16 Bionic", "A15 Bionic"])
            os_name = "iOS 17"
            base_price = random.randint(58000, 145000)
            camera = random.choice([48, 48, 12])
            battery = random.randint(3279, 4422)
            disp = random.choice([6.1, 6.7])
        else:
            proc = random.choice(processors)
            os_name = "Android 14"
            camera = random.choice([50, 64, 108, 200])
            battery = random.randint(4500, 5500)
            disp = round(random.uniform(6.4, 6.8), 2)
            base_price = random.randint(21000, 95000)
            if "Ultra" in model or "Pro" in model:
                base_price += 25000
                
        prod_id = f"PROD-PHN-{i:03d}"
        full_name = f"{brand} {model} ({ram} GB RAM, {storage} GB Storage, {camera}MP Camera)"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        desc = (
            f"Flagship mobile device from {brand} equipped with {proc} processor, {ram} GB RAM, "
            f"and {storage} GB fast storage. Highlights a {disp}-inch high-refresh 120Hz display, "
            f"{camera}MP ultra-clear camera system, and long-lasting {battery} mAh battery with fast charging."
        )

        specs = {
            "processor": proc,
            "ram_gb": ram,
            "storage_gb": storage,
            "camera_mp": camera,
            "battery_mah": battery,
            "display_size_inch": disp,
            "refresh_rate_hz": 120,
            "os": os_name
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Smartphones",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.0, 4.8), 1),
            "review_count": random.randint(120, 3100),
            "availability_status": "In Stock" if random.random() > 0.05 else "Limited Stock",
            "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_headphones(count: int = 120) -> List[Dict[str, Any]]:
    brands = [
        ("Sony", ["WH-1000XM5", "WH-1000XM4", "WF-1000XM5", "WH-CH720N", "LinkBuds S"]),
        ("Bose", ["QuietComfort Ultra", "QuietComfort 45", "QuietComfort Earbuds II"]),
        ("Sennheiser", ["Momentum 4 Wireless", "HD 450BT", "Momentum True Wireless 3"]),
        ("Apple", ["AirPods Pro (2nd Gen)", "AirPods Max", "AirPods (3rd Gen)"]),
        ("JBL", ["Live 660NC", "Tune 760NC", "Live Pro 2"]),
        ("Audio-Technica", ["ATH-M50xBT2", "ATH-SR30BT"]),
    ]
    
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        is_over_ear = "WH" in model or "Max" in model or "45" in model or "450" in model or "760" in model or "M50" in model
        headphone_type = "Over-Ear" if is_over_ear else "In-Ear"
        has_anc = "AirPods (3rd" not in model and "SR30BT" not in model
        battery = random.randint(24, 60) if is_over_ear else random.randint(6, 12)
        weight = random.randint(220, 385) if is_over_ear else random.randint(45, 60)
        
        base_price = random.randint(4500, 34000)
        if "XM5" in model or "Ultra" in model or "Max" in model:
            base_price = random.randint(26000, 48000)
            
        prod_id = f"PROD-AUD-{i:03d}"
        full_name = f"{brand} {model} ({headphone_type}, ANC, {battery}h Battery)"
        orig_price = round(base_price * random.uniform(1.12, 1.25), -2)
        
        desc = (
            f"Premium {headphone_type.lower()} audio headphones from {brand}. Features "
            f"{'industry-leading Active Noise Cancellation (ANC)' if has_anc else 'crisp acoustic tuning'}, "
            f"crystal-clear microphone array for online meetings and voice calls, and up to {battery} hours of playback."
        )

        specs = {
            "type": headphone_type,
            "connectivity": "Bluetooth Wireless / 3.5mm Wired",
            "battery_hours": battery,
            "active_noise_cancellation": has_anc,
            "microphone": True,
            "weight_g": weight
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Headphones",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.1, 4.9), 1),
            "review_count": random.randint(80, 2400),
            "availability_status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_smartwatches(count: int = 100) -> List[Dict[str, Any]]:
    brands = [
        ("Apple", ["Watch Series 9", "Watch Ultra 2", "Watch SE (2nd Gen)"]),
        ("Samsung", ["Galaxy Watch 6 Classic", "Galaxy Watch 6", "Galaxy Watch 5 Pro"]),
        ("Garmin", ["Forerunner 265", "Venu 3", "Fenix 7 Pro", "Instinct 2"]),
        ("Amazfit", ["GTR 4", "Active Edge", "Cheetah Pro"]),
        ("OnePlus", ["Watch 2", "Watch 2R"]),
    ]
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        battery_days = round(random.uniform(1.5, 3.0), 1) if brand in ["Apple", "Samsung"] else random.randint(7, 18)
        water_res = 10 if "Ultra" in model or "Fenix" in model else 5
        base_price = random.randint(8999, 44999)
        if "Ultra" in model or "Fenix" in model:
            base_price = random.randint(62000, 89000)
            
        prod_id = f"PROD-WAT-{i:03d}"
        full_name = f"{brand} {model} (AMOLED, GPS, Heart Rate, {battery_days} Days Battery)"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        desc = (
            f"Feature-packed fitness and health smartwatch from {brand}. Includes precision multi-band GPS, "
            f"continuous heart rate tracking, SpO2 sensor, sleep analytics, AMOLED display, and {water_res}ATM water resistance."
        )

        specs = {
            "display_type": "AMOLED Always-On",
            "battery_days": battery_days,
            "water_resistance_atm": water_res,
            "gps": True,
            "heart_rate_monitor": True,
            "os": "watchOS" if brand == "Apple" else ("Wear OS" if brand in ["Samsung", "OnePlus"] else "Proprietary OS")
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Smartwatches",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.0, 4.8), 1),
            "review_count": random.randint(90, 1800),
            "availability_status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_monitors(count: int = 100) -> List[Dict[str, Any]]:
    brands = [
        ("LG", ["UltraGear 27GP850", "UltraFine 32UN880", "UltraGear OLED 27GR95QE"]),
        ("Dell", ["UltraSharp U2723QE", "Alienware AW3423DWF", "S2721DGF"]),
        ("ASUS", ["TUF Gaming VG27AQ", "ROG Swift PG27AQDM", "ProArt PA278CV"]),
        ("Samsung", ["Odyssey G7 32\"", "Odyssey Neo G9", "ViewFinity S8 4K"]),
        ("BenQ", ["Mobiuz EX2710Q", "PD2705U 4K", "GW2785TC"]),
    ]
    resolutions = [("1080p Full HD", 1920), ("1440p QHD", 2560), ("4K UHD", 3840)]
    refresh_rates = [60, 144, 165, 240]
    sizes = [24.0, 27.0, 27.0, 32.0, 34.0]
    
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        res_label, _ = random.choice(resolutions)
        hz = random.choice(refresh_rates)
        size = random.choice(sizes)
        panel = "OLED" if "OLED" in model or "AW34" in model else "IPS"
        
        base_price = 14500
        if "4K" in res_label: base_price += 18000
        if hz >= 165: base_price += 9000
        if panel == "OLED": base_price += 45000
        base_price += random.randint(-2000, 3500)
        
        prod_id = f"PROD-MON-{i:03d}"
        full_name = f"{brand} {model} ({size}\", {res_label}, {hz}Hz, {panel})"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        desc = (
            f"High clarity {size}-inch {panel} monitor from {brand} with {res_label} resolution "
            f"and fluid {hz}Hz refresh rate. Excellent color accuracy for creative software development, "
            f"office productivity, and competitive fast-response gaming."
        )

        specs = {
            "screen_size_inch": size,
            "resolution": res_label,
            "refresh_rate_hz": hz,
            "panel_type": panel,
            "response_time_ms": 0.03 if panel == "OLED" else 1.0
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Monitors",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.1, 4.8), 1),
            "review_count": random.randint(60, 1200),
            "availability_status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_keyboards(count: int = 100) -> List[Dict[str, Any]]:
    brands = [
        ("Keychron", ["K2 V2", "V1 Custom", "Q1 Pro", "K8 Pro"]),
        ("Logitech", ["MX Keys S", "G Pro X TKL", "G915 Lightspeed", "POP Keys"]),
        ("Corsair", ["K70 RGB PRO", "K65 RGB MINI", "K100 AIR"]),
        ("Razer", ["BlackWidow V4", "Huntsman Mini", "DeathStalker V2 Pro"]),
        ("Ducky", ["One 3 TKL", "One 2 Mini", "Mecha Mini"]),
    ]
    switches = ["Mechanical Red (Linear)", "Mechanical Brown (Tactile)", "Mechanical Blue (Clicky)", "Low Profile Scissor"]
    layouts = ["75% Compact", "Tenkeyless (TKL)", "Full Size 100%", "60% Mini"]
    
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        switch = random.choice(switches)
        layout = random.choice(layouts)
        is_wireless = random.choice([True, False])
        base_price = random.randint(4500, 18500)
        
        prod_id = f"PROD-KEY-{i:03d}"
        full_name = f"{brand} {model} ({layout}, {switch}, {'Wireless' if is_wireless else 'Wired'})"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        desc = (
            f"Ergonomic computer keyboard from {brand} featuring {switch} switches and a {layout} format. "
            f"Designed for smooth software coding, rapid typing tactile feedback, and gaming ergonomics. "
            f"Supports {'Bluetooth + 2.4GHz wireless' if is_wireless else 'detachable braided USB-C wired'} connectivity."
        )

        specs = {
            "switch_type": switch,
            "layout": layout,
            "connectivity": "Wireless Bluetooth/2.4G" if is_wireless else "USB-C Wired",
            "rgb_backlight": True
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Keyboards",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.1, 4.8), 1),
            "review_count": random.randint(70, 950),
            "availability_status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_mice(count: int = 100) -> List[Dict[str, Any]]:
    brands = [
        ("Logitech", ["MX Master 3S", "G Pro X Superlight 2", "G502 X PLUS", "G305 Lightspeed", "Lift Vertical Ergonomic"]),
        ("Razer", ["DeathAdder V3 Pro", "Viper V2 Pro", "Basilisk V3 Pro", "Cobra Pro"]),
        ("Glorious", ["Model O 2 Wireless", "Model D Wireless"]),
        ("SteelSeries", ["Aerox 3 Wireless", "Prime Wireless"]),
    ]
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        is_wireless = True if "Wireless" in model or "Light" in model or "Pro" in model or "3S" in model else False
        dpi = random.choice([8000, 16000, 26000, 30000])
        weight = random.randint(58, 140)
        base_price = random.randint(2200, 14500)
        
        prod_id = f"PROD-MOU-{i:03d}"
        full_name = f"{brand} {model} ({dpi} DPI, {weight}g, {'Wireless' if is_wireless else 'Wired'})"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        desc = (
            f"High-precision optical mouse from {brand}. Equipped with a {dpi} DPI optical sensor, "
            f"lightweight {weight}g ergonomic body, and {'flawless low-latency wireless' if is_wireless else 'drag-free paracord wired'} performance. "
            f"Tailored for productivity workflows and esports precision."
        )

        specs = {
            "sensor_dpi": dpi,
            "weight_g": weight,
            "connectivity": "Wireless 2.4GHz / Bluetooth" if is_wireless else "Wired USB",
            "programmable_buttons": random.randint(5, 11),
            "polling_rate_hz": 1000
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Mice",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.2, 4.8), 1),
            "review_count": random.randint(90, 2100),
            "availability_status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_tablets(count: int = 100) -> List[Dict[str, Any]]:
    brands = [
        ("Apple", ["iPad Air (M2)", "iPad Pro 11 (M4)", "iPad 10th Gen", "iPad mini 6"]),
        ("Samsung", ["Galaxy Tab S9", "Galaxy Tab S9 Ultra", "Galaxy Tab S9 FE", "Galaxy Tab A9+"]),
        ("Lenovo", ["Tab P12 Pro", "Tab M11", "Legion Y700"]),
        ("Xiaomi", ["Pad 6", "Pad 6 Pro"]),
        ("OnePlus", ["OnePlus Pad", "OnePlus Pad Go"]),
    ]
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        ram = random.choice([4, 6, 8, 8, 12, 16])
        storage = random.choice([64, 128, 256, 512])
        size = round(random.uniform(10.2, 12.9), 1)
        base_price = random.randint(23000, 115000)
        
        prod_id = f"PROD-TAB-{i:03d}"
        full_name = f"{brand} {model} ({size}\", {ram} GB RAM, {storage} GB Storage)"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        desc = (
            f"Versatile {size}-inch tablet computer by {brand}. Equipped with {ram} GB RAM and {storage} GB storage. "
            f"Supports active stylus input for note taking, digital illustration, reading, student study, and media consumption."
        )

        specs = {
            "screen_size_inch": size,
            "ram_gb": ram,
            "storage_gb": storage,
            "stylus_support": True,
            "cellular_5g": random.choice([True, False])
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Tablets",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.1, 4.8), 1),
            "review_count": random.randint(60, 1600),
            "availability_status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_gaming_accessories(count: int = 90) -> List[Dict[str, Any]]:
    brands = [
        ("Sony", ["DualSense Wireless Controller", "DualSense Edge Wireless Controller", "Pulse 3D Wireless Headset"]),
        ("Microsoft", ["Xbox Wireless Controller", "Xbox Elite Series 2 Controller"]),
        ("Elgato", ["Stream Deck MK.2", "HD60 X Capture Card", "Wave:3 USB Microphone"]),
        ("HyperX", ["Cloud III Wireless Gaming Headset", "QuadCast S USB Microphone"]),
        ("SteelSeries", ["Arctis Nova 7 Wireless", "Apex Pro TKL Wireless"]),
    ]
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        base_price = random.randint(4500, 24000)
        
        prod_id = f"PROD-GAM-{i:03d}"
        full_name = f"{brand} {model} (Gaming Edition)"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        desc = (
            f"High-tier gaming accessory from {brand}. Provides responsive haptic feedback, "
            f"low latency wireless performance, and robust build quality for competitive console and PC gamers."
        )

        specs = {
            "platform": "PC / PS5 / Xbox Universal",
            "connectivity": "Wireless + USB-C Wired",
            "feature": "Low latency gaming response"
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Gaming Accessories",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.2, 4.9), 1),
            "review_count": random.randint(110, 2400),
            "availability_status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_storage(count: int = 90) -> List[Dict[str, Any]]:
    brands = [
        ("Samsung", ["990 PRO NVMe SSD", "T7 Shield Portable SSD", "T9 Portable SSD 2TB", "980 NVMe SSD"]),
        ("Crucial", ["T700 Gen5 NVMe SSD", "P3 Plus Gen4 NVMe", "X9 Pro Portable SSD"]),
        ("Western Digital", ["WD_BLACK SN850X NVMe SSD", "My Passport External Drive", "SanDisk Extreme Portable SSD V2"]),
        ("Kingston", ["KC3000 PCIe 4.0 NVMe", "XS2000 External SSD"]),
    ]
    capacities = [500, 1000, 2000, 4000]
    
    items = []
    for i in range(1, count + 1):
        brand, model_list = random.choice(brands)
        model = random.choice(model_list)
        cap = random.choice(capacities)
        is_portable = "Portable" in model or "Shield" in model or "Passport" in model
        storage_type = "Portable External SSD" if is_portable else "Internal PCIe NVMe SSD"
        speed = random.randint(1050, 2000) if is_portable else random.randint(5000, 7450)
        base_price = 4500
        if cap == 1000: base_price += 4000
        elif cap == 2000: base_price += 9500
        elif cap == 4000: base_price += 22000
        if speed > 7000: base_price += 3000
        
        prod_id = f"PROD-STR-{i:03d}"
        cap_str = f"{cap // 1000} TB" if cap >= 1000 else f"{cap} GB"
        full_name = f"{brand} {model} ({cap_str}, up to {speed} MB/s)"
        orig_price = round(base_price * random.uniform(1.10, 1.25), -2)
        
        desc = (
            f"Blazing-fast {storage_type} by {brand} with {cap_str} capacity. Delivers sequential read speeds "
            f"up to {speed} MB/s. Perfect for fast game load times, video editing scratch disks, OS boot drives, and reliable file backup."
        )

        specs = {
            "type": storage_type,
            "capacity_gb": cap,
            "read_speed_mbps": speed,
            "interface": "USB 3.2 Gen 2x2" if is_portable else "PCIe 4.0 x4 M.2 NVMe"
        }

        items.append({
            "id": prod_id,
            "name": full_name,
            "brand": brand,
            "category": "Storage Devices",
            "description": desc,
            "price": float(base_price),
            "original_price": float(orig_price),
            "rating": round(random.uniform(4.3, 4.9), 1),
            "review_count": random.randint(80, 2900),
            "availability_status": "In Stock",
            "image_url": "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=500&auto=format&fit=crop&q=60",
            "source": "synthetic_catalogue",
            "is_demo": True,
            "specifications": specs
        })
    return items

def generate_catalogue_dataset(output_path: Path = None) -> List[Dict[str, Any]]:
    """Generate 1,100+ rich synthetic products and write them to CSV."""
    if output_path is None:
        output_path = settings.PRODUCTS_CSV_PATH
        
    all_products = []
    all_products.extend(generate_laptops(150))
    all_products.extend(generate_smartphones(150))
    all_products.extend(generate_headphones(120))
    all_products.extend(generate_smartwatches(100))
    all_products.extend(generate_monitors(100))
    all_products.extend(generate_keyboards(100))
    all_products.extend(generate_mice(100))
    all_products.extend(generate_tablets(100))
    all_products.extend(generate_gaming_accessories(90))
    all_products.extend(generate_storage(90))

    logger.info(f"Generated {len(all_products)} realistic demonstration products.")

    # Write to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "id", "name", "brand", "category", "description",
        "price", "original_price", "rating", "review_count",
        "availability_status", "image_url", "source", "is_demo", "specifications"
    ]
    
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in all_products:
            row = dict(p)
            row["specifications"] = json.dumps(p["specifications"])
            writer.writerow(row)
            
    logger.info(f"Saved dataset CSV to {output_path}")
    return all_products

if __name__ == "__main__":
    products = generate_catalogue_dataset()
    print(f"Successfully generated {len(products)} products in {settings.PRODUCTS_CSV_PATH}")
