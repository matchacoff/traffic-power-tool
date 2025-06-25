from random import choice, randint, uniform, choices
from typing import Dict, List, Optional, Tuple, Union

class BrowserFingerprint:

    DESKTOP_OS_FINGERPRINTS = {
        "Windows": {
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 OPR/110.0.0.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
            ],
            "viewports": [{"width": 1920, "height": 1080}, {"width": 1536, "height": 864}, {"width": 1366, "height": 768}],
            "timezones": ["America/New_York", "Europe/London", "Asia/Tokyo", "Asia/Jakarta", "Australia/Sydney"],
            "hardware_concurrency_range": (4, 16),
            "device_memory_range": (4, 16),
        },
        "macOS": {
            "user_agents": [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6.0 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            ],
            "viewports": [{"width": 1440, "height": 900}, {"width": 1920, "height": 1080}, {"width": 2560, "height": 1440}],
            "timezones": ["America/Los_Angeles", "Europe/London", "Asia/Shanghai"],
            "hardware_concurrency_range": (6, 16),
            "device_memory_range": (8, 16),
        },
        "Linux": {
            "user_agents": [
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:127.0) Gecko/20100101 Firefox/127.0",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            ],
            "viewports": [{"width": 1600, "height": 900}, {"width": 1280, "height": 800}],
            "timezones": ["Europe/Berlin", "America/Chicago"],
            "hardware_concurrency_range": (2, 8),
            "device_memory_range": (4, 8),
        },
    }

    MOBILE_FINGERPRINTS = {
        "iPhone": {
            "devices": [
                {"name": "iPhone 15 Pro Max", "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1", "viewport": {"width": 430, "height": 932}, "pixel_ratio": 3},
                {"name": "iPhone 14", "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "viewport": {"width": 390, "height": 844}, "pixel_ratio": 3},
                {"name": "iPhone 13 Pro", "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1", "viewport": {"width": 390, "height": 844}, "pixel_ratio": 3},
                {"name": "iPhone 12", "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1", "viewport": {"width": 390, "height": 844}, "pixel_ratio": 3},
            ],
            "hardware_concurrency_range": (4, 8),
            "device_memory_range": (4, 8),
        },
        "Android": {
            "devices": [
                {"name": "Samsung Galaxy S24 Ultra", "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36", "viewport": {"width": 412, "height": 915}, "pixel_ratio": 3.5},
                {"name": "Google Pixel 8", "user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36", "viewport": {"width": 384, "height": 854}, "pixel_ratio": 2.75},
                {"name": "Xiaomi 13 Pro", "user_agent": "Mozilla/5.0 (Linux; Android 13; 2210132C) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36", "viewport": {"width": 393, "height": 852}, "pixel_ratio": 3},
                {"name": "Oppo Find X5", "user_agent": "Mozilla/5.0 (Linux; Android 12; CPH2307) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36", "viewport": {"width": 412, "height": 920}, "pixel_ratio": 3},
            ],
            "hardware_concurrency_range": (6, 8),
            "device_memory_range": (6, 12),
        },
    }

    TABLET_FINGERPRINTS = {
        "iPad": {
            "devices": [
                {"name": "iPad Pro 12.9", "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1", "viewport": {"width": 1024, "height": 1366}, "pixel_ratio": 2},
                {"name": "iPad Air", "user_agent": "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1", "viewport": {"width": 820, "height": 1180}, "pixel_ratio": 2},
            ],
            "hardware_concurrency_range": (4, 8),
            "device_memory_range": (4, 8),
        },
        "Android Tablet": {
            "devices": [
                {"name": "Samsung Galaxy Tab S9", "user_agent": "Mozilla/5.0 (Linux; Android 14; SM-X710) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", "viewport": {"width": 800, "height": 1280}, "pixel_ratio": 2},
            ],
            "hardware_concurrency_range": (4, 8),
            "device_memory_range": (4, 8),
        },
    }

    # Country-specific locale and timezone mappings
    COUNTRY_DATA = {
        "United States": {
            "locales": ["en-US,en;q=0.9"],
            "timezones": ["America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"],
            "weight": 20
        },
        "Indonesia": {
            "locales": ["id-ID,id;q=0.9,en;q=0.8"],
            "timezones": ["Asia/Jakarta", "Asia/Makassar", "Asia/Jayapura"],
            "weight": 15
        },
        "Japan": {
            "locales": ["ja-JP,ja;q=0.9,en;q=0.8"],
            "timezones": ["Asia/Tokyo"],
            "weight": 10
        },
        "Spain": {
            "locales": ["es-ES,es;q=0.9,en;q=0.8"],
            "timezones": ["Europe/Madrid"],
            "weight": 8
        },
        "France": {
            "locales": ["fr-FR,fr;q=0.9,en;q=0.8"],
            "timezones": ["Europe/Paris"],
            "weight": 8
        },
        "Germany": {
            "locales": ["de-DE,de;q=0.9,en;q=0.8"],
            "timezones": ["Europe/Berlin"],
            "weight": 10
        },
        "United Kingdom": {
            "locales": ["en-GB,en;q=0.9"],
            "timezones": ["Europe/London"],
            "weight": 10
        },
        "Brazil": {
            "locales": ["pt-BR,pt;q=0.9,en;q=0.8"],
            "timezones": ["America/Sao_Paulo"],
            "weight": 8
        },
        "India": {
            "locales": ["en-IN,en;q=0.9", "hi-IN,hi;q=0.9,en;q=0.8"],
            "timezones": ["Asia/Kolkata"],
            "weight": 15
        },
        "Australia": {
            "locales": ["en-AU,en;q=0.9"],
            "timezones": ["Australia/Sydney", "Australia/Perth", "Australia/Melbourne"],
            "weight": 8
        },
        "Canada": {
            "locales": ["en-CA,en;q=0.9", "fr-CA,fr;q=0.9,en;q=0.8"],
            "timezones": ["America/Toronto", "America/Vancouver"],
            "weight": 8
        },
        "Mexico": {
            "locales": ["es-MX,es;q=0.9,en;q=0.8"],
            "timezones": ["America/Mexico_City"],
            "weight": 7
        },
        "Russia": {
            "locales": ["ru-RU,ru;q=0.9,en;q=0.8"],
            "timezones": ["Europe/Moscow"],
            "weight": 8
        },
        "China": {
            "locales": ["zh-CN,zh;q=0.9,en;q=0.8"],
            "timezones": ["Asia/Shanghai", "Asia/Hong_Kong"],
            "weight": 15
        },
        "South Korea": {
            "locales": ["ko-KR,ko;q=0.9,en;q=0.8"],
            "timezones": ["Asia/Seoul"],
            "weight": 8
        }
    }
    
    # Fallback locales if no specific country is selected
    LOCALES = [
        "en-US,en;q=0.9", "id-ID,id;q=0.9,en;q=0.8", "ja-JP,ja;q=0.9,en;q=0.8",
        "es-ES,es;q=0.9,en;q=0.8", "fr-FR,fr;q=0.9,en;q=0.8", "de-DE,de;q=0.9,en;q=0.8"
    ]

    COLOR_SCHEMES = ["light", "dark", "no-preference"]

    REDUCED_MOTION_PREFERENCES = ["no-preference", "reduce"]

    @staticmethod
    def get_random_fingerprint(device_type: str = "Desktop", country: Optional[str] = None, age_range: Optional[Tuple[int, int]] = None) -> dict:
        """
        Generate a random browser fingerprint based on device type, country, and age range.
        
        Args:
            device_type: The type of device ("Desktop", "Mobile", or "Tablet")
            country: Optional country to use for locale and timezone
            age_range: Optional age range tuple (min_age, max_age)
            
        Returns:
            A dictionary containing the browser fingerprint
        """
        if device_type == "Mobile":
            fingerprint = BrowserFingerprint._get_mobile(country)
        elif device_type == "Tablet":
            fingerprint = BrowserFingerprint._get_tablet(country)
        else:
            fingerprint = BrowserFingerprint._get_desktop(country)
            
        # Add age information if provided
        if age_range:
            fingerprint["age"] = randint(age_range[0], age_range[1])
            
        return fingerprint

    @staticmethod
    def _get_country_data(country: Optional[str] = None) -> Tuple[str, str]:
        """Get locale and timezone for a specific country or random country"""
        if country and country in BrowserFingerprint.COUNTRY_DATA:
            # Use the specified country
            country_info = BrowserFingerprint.COUNTRY_DATA[country]
            locale = choice(country_info["locales"])
            timezone = choice(country_info["timezones"])
        elif country == "Random" or country is None:
            # Select a random country based on weights
            countries, weights = zip(*[(k, v["weight"]) for k, v in BrowserFingerprint.COUNTRY_DATA.items()])
            selected_country = choices(countries, weights=weights, k=1)[0]
            country_info = BrowserFingerprint.COUNTRY_DATA[selected_country]
            locale = choice(country_info["locales"])
            timezone = choice(country_info["timezones"])
        else:
            # Fallback to random locale and timezone
            locale = choice(BrowserFingerprint.LOCALES)
            timezone = "America/New_York"  # Default fallback
            
        return locale, timezone

    @staticmethod
    def _get_desktop(country: Optional[str] = None) -> dict:
        os_name, os_details = choice(list(BrowserFingerprint.DESKTOP_OS_FINGERPRINTS.items()))
        locale, timezone = BrowserFingerprint._get_country_data(country)
        
        return {
            "device_name": os_name,
            "user_agent": choice(os_details["user_agents"]),
            "viewport": choice(os_details["viewports"]),
            "locale": locale,
            "timezone_id": timezone,
            "is_mobile": False,
            "has_touch": False,
            "device_scale_factor": 1,
            "color_scheme": choice(BrowserFingerprint.COLOR_SCHEMES),
            "reduced_motion": choice(BrowserFingerprint.REDUCED_MOTION_PREFERENCES),
            "hardware_concurrency": randint(*os_details["hardware_concurrency_range"]),
            "device_memory": randint(*os_details["device_memory_range"]),
            "country": country if country and country != "Random" else None,
        }

    @staticmethod
    def _get_mobile(country: Optional[str] = None) -> dict:
        brand, details = choice(list(BrowserFingerprint.MOBILE_FINGERPRINTS.items()))
        device_info = choice(details["devices"])
        locale, timezone = BrowserFingerprint._get_country_data(country)
        
        return {
            "device_name": device_info["name"],
            "user_agent": device_info["user_agent"],
            "viewport": device_info["viewport"],
            "locale": locale,
            "timezone_id": timezone,
            "is_mobile": True,
            "has_touch": True,
            "device_scale_factor": device_info["pixel_ratio"],
            "color_scheme": choice(BrowserFingerprint.COLOR_SCHEMES),
            "reduced_motion": choice(BrowserFingerprint.REDUCED_MOTION_PREFERENCES),
            "hardware_concurrency": randint(*details["hardware_concurrency_range"]),
            "device_memory": randint(*details["device_memory_range"]),
            "country": country if country and country != "Random" else None,
        }

    @staticmethod
    def _get_tablet(country: Optional[str] = None) -> dict:
        brand, details = choice(list(BrowserFingerprint.TABLET_FINGERPRINTS.items()))
        device_info = choice(details["devices"])
        locale, timezone = BrowserFingerprint._get_country_data(country)
        
        return {
            "device_name": device_info["name"],
            "user_agent": device_info["user_agent"],
            "viewport": device_info["viewport"],
            "locale": locale,
            "timezone_id": timezone,
            "is_mobile": True,
            "has_touch": True,
            "device_scale_factor": device_info["pixel_ratio"],
            "color_scheme": choice(BrowserFingerprint.COLOR_SCHEMES),
            "reduced_motion": choice(BrowserFingerprint.REDUCED_MOTION_PREFERENCES),
            "hardware_concurrency": randint(*details["hardware_concurrency_range"]),
            "device_memory": randint(*details["device_memory_range"]),
            "country": country if country and country != "Random" else None,
        }

    @staticmethod
    def add_realistic_delays() -> dict:
        return {
            "typing_delay": randint(50, 150),
            "click_delay": randint(100, 300),
            "scroll_delay": uniform(0.5, 2.0),
            "page_load_wait_min": uniform(2.0, 5.0),
            "page_load_wait_max": uniform(5.0, 10.0),
            "interaction_pause": uniform(1.0, 3.0),
            "human_pause": uniform(0.5, 1.5),
        }
