# File: src/core/generator.py

import asyncio
import logging
import os
import time
import traceback
from random import choice, choices, randint, uniform
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Error as PlaywrightError, Playwright, TimeoutError as PlaywrightTimeoutError, async_playwright

from .behavior import IntelligentBehaviorSimulator
from .config import TrafficConfig
from .fingerprint import BrowserFingerprint

logger = logging.getLogger(__name__)


class AdvancedTrafficGenerator:
    """Kelas utama untuk menjalankan simulasi lalu lintas."""

    def __init__(self, config: TrafficConfig, status_queue=None, stop_event=None):
        self.config = config
        self.behavior_simulator = IntelligentBehaviorSimulator(config, mode_type=config.mode_type)
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.proxies = self._load_proxies()
        self.status_queue = status_queue
        self.stop_event = stop_event
        self.session_stats = {"total": 0, "successful": 0, "failed": 0, "completed": 0, "total_duration": 0.0}

    def _log(self, message: str, level: str = "info"):
        """Mengirim log ke logger dan queue status untuk UI."""
        if self.status_queue:
            self.status_queue.put({"type": "log", "data": message})
        getattr(logger, level, logger.info)(message)

    def _load_proxies(self) -> list:
        """Memuat daftar proksi dari file jika disediakan."""
        if not self.config.proxy_file:
            return []
        try:
            with open(self.config.proxy_file) as f:
                return [{"server": line.strip()} for line in f if line.strip()]
        except Exception as e:
            self._log(f"Gagal memuat proksi: {e}", level="error")
            return []

    def _get_user_profile(self) -> tuple[str, str, str, str, tuple[int, int]]:
        """
        Menentukan profil pengguna untuk sesi, termasuk:
        - Tipe pengunjung (baru/lama)
        - ID profil
        - Tipe perangkat
        - Negara
        - Rentang usia
        """
        # Tentukan apakah pengunjung baru atau lama
        is_returning = uniform(0, 100) < self.config.returning_visitor_rate
        
        # Pilih tipe perangkat berdasarkan distribusi
        devices, weights = zip(*self.config.device_distribution.items())
        device_type = choices(devices, weights=weights, k=1)[0]
        
        # Pilih negara berdasarkan distribusi
        countries, country_weights = zip(*self.config.country_distribution.items())
        country = choices(countries, weights=country_weights, k=1)[0]
        
        # Tentukan rentang usia berdasarkan distribusi
        age_ranges = {
            "18-24": (18, 24),
            "25-34": (25, 34),
            "35-44": (35, 44),
            "45-54": (45, 54),
            "55+": (55, 75)  # Batas atas 75 untuk rentang 55+
        }
        age_groups, age_weights = zip(*self.config.age_distribution.items())
        selected_age_group = choices(age_groups, weights=age_weights, k=1)[0]
        age_range = age_ranges.get(selected_age_group, (18, 65))  # Default jika tidak ada di mapping
        
        # Cek profil yang ada untuk pengunjung lama
        profile_dir = self.config.project_root / "output" / "profiles"
        existing_profiles = [d for d in os.listdir(profile_dir) if os.path.isdir(profile_dir / d)]

        if is_returning and existing_profiles:
            return "Returning", choice(existing_profiles), device_type, country, age_range
        
        return "New", f"user_{int(time.time())}_{randint(1000, 9999)}", device_type, country, age_range

    async def _create_browser_context(self, playwright: Playwright, profile_id: str, device_type: str, country: str = None, age_range: tuple[int, int] = None) -> tuple[Optional[Browser], Optional[BrowserContext]]:
        """Membuat konteks browser dengan profil, sidik jari, dan referrer yang sesuai."""
        profile_path = self.config.project_root / "output" / "profiles" / profile_id
        os.makedirs(profile_path, exist_ok=True)

        fingerprint = BrowserFingerprint.get_random_fingerprint(device_type, country, age_range)

        valid_context_args = ["user_agent", "viewport", "locale", "timezone_id", "is_mobile", "has_touch", "device_scale_factor", "color_scheme", "reduced_motion"]
        context_args = {k: v for k, v in fingerprint.items() if k in valid_context_args}
        context_args["permissions"] = ["geolocation"]

        if self.config.referrer_sources:
            context_args["extra_http_headers"] = {"Referer": choice(self.config.referrer_sources)}

        state_path = profile_path / "state.json"
        if os.path.exists(state_path):
            context_args["storage_state"] = str(state_path)

        proxy = choice(self.proxies) if self.proxies else None

        try:
            browser = await playwright.chromium.launch(headless=self.config.headless, proxy=proxy)
            context = await browser.new_context(**context_args)

            # Network throttling
            if hasattr(self.config, 'network_type') and self.config.network_type and self.config.network_type != "Default":
                # Playwright tidak punya API langsung, gunakan route untuk lambatkan request atau set offline
                if self.config.network_type == "Offline":
                    await context.set_offline(True)
                else:
                    # Simulasi lambat dengan route (hanya contoh, bisa dioptimalkan)
                    throttle_map = {
                        "3G": {"download": 750 * 1024 / 8, "upload": 250 * 1024 / 8, "latency": 100},
                        "4G": {"download": 4000 * 1024 / 8, "upload": 3000 * 1024 / 8, "latency": 40},
                        "WiFi Lambat": {"download": 1500 * 1024 / 8, "upload": 1000 * 1024 / 8, "latency": 80},
                    }
                    throttle = throttle_map.get(self.config.network_type)
                    if throttle:
                        try:
                            await context.route("**/*", lambda route: route.continue_())
                            await context.set_network_conditions(
                                download=throttle["download"],
                                upload=throttle["upload"],
                                latency=throttle["latency"]
                            )
                        except Exception:
                            pass

            init_script = f"""
                Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});
                Object.defineProperty(navigator, 'hardwareConcurrency', {{ get: () => {fingerprint.get("hardware_concurrency", 4)} }});
                Object.defineProperty(navigator, 'deviceMemory', {{ get: () => {fingerprint.get("device_memory", 8)} }});
            """
            await context.add_init_script(init_script)
            return browser, context
        except Exception as e:
            self._log(f"Gagal membuat konteks: {e}", level="error")
            logger.error(traceback.format_exc())
            return None, None

    async def _execute_and_process_session(self, playwright: Playwright, profile_id: str, device_type: str, persona, country: str = None, age_range: tuple[int, int] = None) -> tuple[str, dict]:
        """Menjalankan logika inti satu sesi dalam blok try-catch."""
        browser, context, page = None, None, None
        ga4_events = []
        goal_result = {}
        try:
            browser, context = await self._create_browser_context(playwright, profile_id, device_type, country, age_range)
            if not context:
                raise PlaywrightError("Konteks tidak dapat dibuat.")

            page = await context.new_page()
            await page.goto(self.config.target_url, wait_until="domcontentloaded", timeout=self.config.navigation_timeout)
            await page.wait_for_load_state("networkidle")

            await self.behavior_simulator._capture_ga4_event(page, profile_id, ga4_events, "page_view")
            goal_result = await self.behavior_simulator.run_goal_oriented_session(page, persona, profile_id, ga4_events)

            await context.storage_state(path=str(self.config.project_root / "output" / "profiles" / profile_id / "state.json"))
            return "successful", goal_result
        finally:
            if context:
                await context.close()
            if browser:
                await browser.close()

    async def _run_single_session(self, playwright: Playwright, session_id: int):
        """Orkestrator untuk satu sesi, menangani percobaan ulang dan logging."""
        if self.stop_event and self.stop_event.is_set():
            return
        async with self.semaphore:
            if self.stop_event and self.stop_event.is_set():
                return

            self.session_stats["total"] += 1
            start_time = time.time()
            
            # Dapatkan profil pengguna dengan informasi tambahan (negara dan usia)
            visitor_type, profile_id, device_type, country, age_range = self._get_user_profile()
            
            # Pilih persona dan tentukan gender berdasarkan distribusi
            persona = choice(self.config.personas)
            
            # Tentukan gender berdasarkan distribusi gender
            genders, gender_weights = zip(*self.config.gender_distribution.items())
            selected_gender = choices(genders, weights=gender_weights, k=1)[0]
            persona.gender = selected_gender
            
            # Tentukan rentang usia untuk persona
            persona.age_range = age_range
            
            # Buat log prefix dengan informasi tambahan
            log_prefix = f"Sesi {session_id:03d} [{visitor_type[0]}/{device_type}/{persona.name}/{persona.gender}/{age_range[0]}-{age_range[1]}]"
            if country and country != "Random":
                log_prefix += f"/{country}"
                
            session_status = "failed"
            goal_result = {}

            for attempt in range(self.config.max_retries_per_session + 1):
                try:
                    if self.stop_event and self.stop_event.is_set():
                        break
                    self._log(f"{log_prefix}: Memulai (Percobaan {attempt + 1})")
                    session_status, goal_result = await self._execute_and_process_session(playwright, profile_id, device_type, persona, country, age_range)
                    self.session_stats["successful"] += 1
                    self._log(f"{log_prefix}: Sukses (durasi: {time.time() - start_time:.1f}s)")
                    break
                except (PlaywrightTimeoutError, PlaywrightError) as e:
                    msg = str(e).splitlines()[0]
                    self._log(f"{log_prefix}: Gagal (Percobaan {attempt + 1}) - {type(e).__name__}: {msg}", level="warning")
                    if attempt == self.config.max_retries_per_session:
                        self.session_stats["failed"] += 1
                        self._log(f"{log_prefix}: Batas percobaan ulang tercapai.", level="error")
                except Exception:
                    self.session_stats["failed"] += 1
                    self._log(f"{log_prefix}: Gagal Kritis - {traceback.format_exc(limit=1)}", level="error")
                    break

            duration = time.time() - start_time
            if session_status == "successful":
                self.session_stats["total_duration"] += duration

            if self.status_queue:
                self.status_queue.put(
                    {
                        "type": "live_update",
                        "data": {
                            "status": session_status,
                            "duration": duration,
                            "persona": persona.name,
                            "device_type": device_type,
                            "visitor_type": visitor_type,
                            "gender": persona.gender,
                            "age_range": f"{age_range[0]}-{age_range[1]}",
                            "country": country,
                            "goal_result": goal_result,
                        },
                    }
                )
            self.session_stats["completed"] += 1

    async def run(self):
        """Memicu eksekusi semua sesi yang telah dikonfigurasi."""
        self._log("Memulai proses generator...")
        async with async_playwright() as playwright:
            tasks = [self._run_single_session(playwright, i + 1) for i in range(self.config.total_sessions) if not self.stop_event or not self.stop_event.is_set()]
            await asyncio.gather(*tasks)
        self._log("Semua sesi telah selesai.")
