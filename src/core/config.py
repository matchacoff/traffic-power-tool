# src/core/config.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
DEFAULT_REFERRER_SOURCES = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://t.co/",
    "https://www.facebook.com/",
    "https://linkedin.com/",
    "https://reddit.com/",
    "https://news.ycombinator.com/",
    "https://medium.com/",
    "https://www.youtube.com/",
    "https://www.instagram.com/",
    "https://www.pinterest.com/",
    "https://www.tiktok.com/",
    "https://twitter.com/",
    "https://mail.google.com/",
    "https://outlook.live.com/",
    "https://web.whatsapp.com/",
    "https://l.instagram.com/",
    "https://www.baidu.com/",
    "https://www.yahoo.com/",
]

@dataclass
class Persona:
    name: str
    goal_keywords: dict[str, int] = field(default_factory=dict)
    generic_keywords: dict[str, int] = field(default_factory=dict)
    navigation_depth: tuple[int, int] = (3, 6)
    avg_time_per_page: tuple[int, int] = (20, 60)
    gender: str = "Neutral"
    age_range: tuple[int, int] = (18, 65)  # Default age range
    can_fill_forms: bool = False
    goal: Optional[dict[str, Any]] = None
    scroll_probability: float = 0.85
    form_interaction_probability: float = 0.25

@dataclass
class TrafficConfig:
    project_root: Path
    target_url: str
    total_sessions: int
    max_concurrent: int
    headless: bool = True
    proxy_file: Optional[str] = None
    returning_visitor_rate: int = 30
    navigation_timeout: int = 60000
    max_retries_per_session: int = 2
    personas: list[Persona] = field(default_factory=list)
    gender_distribution: dict[str, int] = field(default_factory=lambda: {"Male": 50, "Female": 50})
    device_distribution: dict[str, int] = field(default_factory=lambda: {"Desktop": 60, "Mobile": 30, "Tablet": 10})
    country_distribution: dict[str, int] = field(default_factory=lambda: {"Random": 100})  # Default to random countries
    age_distribution: dict[str, int] = field(default_factory=lambda: {"18-24": 20, "25-34": 30, "35-44": 25, "45-54": 15, "55+": 10})
    referrer_sources: list[str] = field(default_factory=lambda: DEFAULT_REFERRER_SOURCES)
    session_duration_range: tuple[int, int] = (120, 600)
    bounce_rate_target: float = 0.3
    user_agent_strategy: str = "random"
    network_type: str = "Default"
    mode_type: str = "Bot"
    schedule_time: Optional[str] = None

DEFAULT_PERSONAS = [
    Persona(
        name="Methodical Customer",
        goal_keywords={"contact": 10, "price": 10, "demo": 9, "signup": 8, "form": 7},
        generic_keywords={"faq": 6, "testimonial": 7, "about us": 5},
        navigation_depth=(4, 7),
        avg_time_per_page=(40, 75),
        can_fill_forms=True,
        goal={"type": "fill_form", "target_selector": "form#contact-form, form[name*='contact'], form[class*='contact']"},
    ),
    Persona(
        name="Deep Researcher",
        goal_keywords={"whitepaper": 12, "case study": 12, "report": 10, "data": 9, "analisa": 8},
        generic_keywords={"blog": 5, "resources": 8, "library": 7, "artikel": 6},
        navigation_depth=(6, 10),
        avg_time_per_page=(50, 90),
        can_fill_forms=False,
        goal={"type": "find_and_click", "target_text": "download|unduh|get now", "case_sensitive": False},
    ),
    Persona(
        name="Performance Analyst",
        goal_keywords={"home": 10, "about": 8, "products": 9, "blog": 7, "kinerja": 11},
        generic_keywords={"news": 5, "contact": 6, "statistik": 7},
        navigation_depth=(5, 8),
        avg_time_per_page=(10, 20),
        can_fill_forms=False,
        goal={"type": "collect_web_vitals", "pages_to_visit": 5, "min_vitals_to_collect": 3},
    ),
    Persona(
        name="Quick Browser",
        goal_keywords={"home": 8, "products": 7, "services": 6},
        generic_keywords={"blog": 3, "news": 4},
        navigation_depth=(2, 4),
        avg_time_per_page=(15, 30),
        can_fill_forms=False,
        goal=None,
    ),
    Persona(
        name="Job Seeker",
        goal_keywords={"career": 12, "job": 10, "hiring": 9, "lowongan": 11, "vacancies": 9},
        generic_keywords={"about": 6, "company": 8, "team": 7},
        navigation_depth=(6, 10),
        avg_time_per_page=(45, 90),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "apply|daftar sekarang|lamar", "case_sensitive": False},
    ),
    Persona(
        name="Content Consumer",
        goal_keywords={"artikel": 10, "berita": 9, "blog": 8, "panduan": 7, "video": 6},
        generic_keywords={"category": 5, "tag": 4, "author": 3, "media": 5},
        navigation_depth=(5, 8),
        avg_time_per_page=(60, 120),
        can_fill_forms=False,
        goal=None,
    ),
    Persona(
        name="Product Explorer",
        goal_keywords={"product": 10, "fitur": 9, "harga": 8, "buy": 7, "beli": 7},
        generic_keywords={"review": 6, "galeri": 5, "spec": 4},
        navigation_depth=(3, 6),
        avg_time_per_page=(30, 90),
        can_fill_forms=False,
        goal={"type": "find_and_click", "target_text": "add to cart|beli sekarang", "case_sensitive": False},
    ),
    Persona(
        name="Social Media Marketer",
        goal_keywords={"share": 10, "social": 9, "twitter": 8, "facebook": 8, "instagram": 8, "like": 7, "follow": 7},
        generic_keywords={"campaign": 6, "ads": 5, "influencer": 5},
        navigation_depth=(3, 6),
        avg_time_per_page=(20, 40),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "share|bagikan|like|follow", "case_sensitive": False},
        gender="Female",
    ),
    Persona(
        name="Mobile Gamer",
        goal_keywords={"game": 12, "play": 10, "download": 9, "score": 8, "leaderboard": 7},
        generic_keywords={"review": 5, "update": 4, "event": 4},
        navigation_depth=(2, 5),
        avg_time_per_page=(30, 60),
        can_fill_forms=False,
        goal={"type": "find_and_click", "target_text": "play now|main sekarang|download", "case_sensitive": False},
        gender="Male",
    ),
    Persona(
        name="News Reader",
        goal_keywords={"news": 12, "headline": 10, "breaking": 9, "update": 8, "artikel": 7},
        generic_keywords={"opini": 5, "kolom": 4, "editorial": 4},
        navigation_depth=(5, 10),
        avg_time_per_page=(40, 90),
        can_fill_forms=False,
        goal=None,
        gender="Neutral",
    ),
    Persona(
        name="Tech Enthusiast",
        goal_keywords={"gadget": 10, "review": 9, "spec": 8, "launch": 7, "update": 7, "technology": 8},
        generic_keywords={"forum": 5, "komunitas": 4, "event": 4},
        navigation_depth=(4, 8),
        avg_time_per_page=(30, 70),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "review|spec|forum|komunitas", "case_sensitive": False},
        gender="Male",
    ),
    
    # NEW PERSONAS ADDED BELOW
    Persona(
        name="E-commerce Shopper",
        goal_keywords={"shop": 12, "cart": 10, "checkout": 9, "sale": 8, "discount": 8, "promo": 7},
        generic_keywords={"kategori": 6, "brand": 5, "wishlist": 4},
        navigation_depth=(3, 7),
        avg_time_per_page=(25, 80),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "buy now|beli|add to cart|checkout", "case_sensitive": False},
        gender="Female",
        scroll_probability=0.9,
        form_interaction_probability=0.4,
    ),
    
    Persona(
        name="Educational Student",
        goal_keywords={"course": 12, "tutorial": 11, "learn": 10, "education": 9, "skill": 8, "training": 7},
        generic_keywords={"certificate": 6, "instructor": 5, "syllabus": 4},
        navigation_depth=(5, 12),
        avg_time_per_page=(60, 180),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "enroll|daftar|register|start course", "case_sensitive": False},
        gender="Neutral",
        scroll_probability=0.95,
    ),
    
    Persona(
        name="Health Seeker",
        goal_keywords={"health": 12, "medical": 10, "doctor": 9, "hospital": 8, "treatment": 7, "appointment": 6},
        generic_keywords={"symptoms": 5, "medicine": 4, "clinic": 4},
        navigation_depth=(4, 8),
        avg_time_per_page=(45, 120),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "book appointment|konsultasi|contact doctor", "case_sensitive": False},
        gender="Female",
        scroll_probability=0.8,
    ),
    
    Persona(
        name="Investment Researcher",
        goal_keywords={"invest": 12, "stock": 11, "finance": 10, "trading": 9, "portfolio": 8, "market": 7},
        generic_keywords={"analysis": 6, "chart": 5, "profit": 5, "risk": 4},
        navigation_depth=(6, 15),
        avg_time_per_page=(90, 300),
        can_fill_forms=False,
        goal={"type": "collect_web_vitals", "pages_to_visit": 8, "min_vitals_to_collect": 5},
        gender="Male",
        scroll_probability=0.9,
    ),
    
    Persona(
        name="Food Enthusiast",
        goal_keywords={"recipe": 12, "food": 11, "restaurant": 10, "menu": 9, "cooking": 8, "delivery": 7},
        generic_keywords={"ingredient": 6, "chef": 5, "cuisine": 4},
        navigation_depth=(3, 6),
        avg_time_per_page=(30, 90),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "order now|pesan|reserve|book table", "case_sensitive": False},
        gender="Female",
        scroll_probability=0.85,
    ),
    
    Persona(
        name="Travel Planner",
        goal_keywords={"travel": 12, "hotel": 11, "flight": 10, "destination": 9, "vacation": 8, "tour": 7},
        generic_keywords={"itinerary": 6, "guide": 5, "photo": 4, "review": 5},
        navigation_depth=(4, 10),
        avg_time_per_page=(40, 120),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "book now|reserve|pesan tiket", "case_sensitive": False},
        gender="Neutral",
        scroll_probability=0.9,
    ),
    
    Persona(
        name="Real Estate Buyer",
        goal_keywords={"property": 12, "house": 11, "apartment": 10, "price": 9, "location": 8, "mortgage": 7},
        generic_keywords={"bedroom": 5, "bathroom": 4, "area": 5, "neighborhood": 4},
        navigation_depth=(5, 12),
        avg_time_per_page=(60, 180),
        can_fill_forms=True,
        goal={"type": "fill_form", "target_selector": "form#contact-agent, form[name*='inquiry'], form[class*='property']"},
        gender="Male",
        scroll_probability=0.95,
    ),
    
    Persona(
        name="Fitness Tracker",
        goal_keywords={"fitness": 12, "workout": 11, "gym": 10, "exercise": 9, "diet": 8, "nutrition": 7},
        generic_keywords={"muscle": 5, "cardio": 4, "protein": 4, "calories": 5},
        navigation_depth=(3, 7),
        avg_time_per_page=(25, 75),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "join now|start workout|subscribe", "case_sensitive": False},
        gender="Male",
        scroll_probability=0.8,
    ),
    
    Persona(
        name="Beauty Consultant",
        goal_keywords={"beauty": 12, "skincare": 11, "makeup": 10, "cosmetic": 9, "treatment": 8, "salon": 7},
        generic_keywords={"brand": 6, "review": 5, "tutorial": 4, "tips": 5},
        navigation_depth=(4, 8),
        avg_time_per_page=(35, 90),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "buy now|shop|add to cart|book appointment", "case_sensitive": False},
        gender="Female",
        scroll_probability=0.9,
    ),
    
    Persona(
        name="Legal Advisor",
        goal_keywords={"legal": 12, "lawyer": 11, "law": 10, "consultation": 9, "advice": 8, "court": 7},
        generic_keywords={"case": 6, "document": 5, "contract": 4, "rights": 5},
        navigation_depth=(5, 10),
        avg_time_per_page=(60, 150),
        can_fill_forms=True,
        goal={"type": "fill_form", "target_selector": "form#consultation, form[name*='legal'], form[class*='contact']"},
        gender="Neutral",
        scroll_probability=0.85,
    ),
    
    Persona(
        name="Automotive Buyer",
        goal_keywords={"car": 12, "motor": 11, "vehicle": 10, "dealer": 9, "price": 8, "financing": 7},
        generic_keywords={"engine": 5, "fuel": 4, "brand": 5, "model": 6},
        navigation_depth=(4, 9),
        avg_time_per_page=(45, 120),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "test drive|quote|contact dealer", "case_sensitive": False},
        gender="Male",
        scroll_probability=0.8,
    ),
    
    Persona(
        name="Entertainment Seeker",
        goal_keywords={"movie": 12, "music": 11, "concert": 10, "event": 9, "ticket": 8, "show": 7},
        generic_keywords={"artist": 6, "venue": 5, "schedule": 4, "genre": 4},
        navigation_depth=(3, 6),
        avg_time_per_page=(20, 60),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "buy ticket|book now|stream|watch", "case_sensitive": False},
        gender="Neutral",
        scroll_probability=0.75,
    ),
    
    Persona(
        name="Pet Owner",
        goal_keywords={"pet": 12, "dog": 10, "cat": 10, "veterinary": 9, "food": 8, "care": 7},
        generic_keywords={"breed": 5, "health": 6, "training": 4, "toy": 4},
        navigation_depth=(3, 7),
        avg_time_per_page=(30, 80),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "shop|order|appointment|consult", "case_sensitive": False},
        gender="Female",
        scroll_probability=0.85,
    ),
    
    Persona(
        name="Financial Advisor",
        goal_keywords={"insurance": 12, "loan": 11, "credit": 10, "bank": 9, "savings": 8, "budget": 7},
        generic_keywords={"rate": 6, "calculator": 5, "plan": 5, "advisor": 4},
        navigation_depth=(5, 12),
        avg_time_per_page=(50, 140),
        can_fill_forms=True,
        goal={"type": "fill_form", "target_selector": "form#application, form[name*='loan'], form[class*='finance']"},
        gender="Male",
        scroll_probability=0.9,
    ),
    
    Persona(
        name="Home Improvement",
        goal_keywords={"renovation": 12, "contractor": 11, "design": 10, "furniture": 9, "interior": 8, "decor": 7},
        generic_keywords={"material": 6, "budget": 5, "style": 4, "room": 5},
        navigation_depth=(4, 8),
        avg_time_per_page=(40, 100),
        can_fill_forms=True,
        goal={"type": "find_and_click", "target_text": "quote|estimate|contact|buy", "case_sensitive": False},
        gender="Neutral",
        scroll_probability=0.9,
    ),
]
