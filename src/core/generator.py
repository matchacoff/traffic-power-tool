import asyncio
import logging
import os
import time
import traceback
from random import choice, choices, randint, uniform
from typing import Optional

from playwright.async_api import (
    Browser,
    BrowserContext,
    Error as PlaywrightError,
    Playwright,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from .behavior import IntelligentBehaviorSimulator
from .config import TrafficConfig
from .fingerprint import BrowserFingerprint

logger = logging.getLogger(__name__)


class AdvancedTrafficGenerator:
    """Kelas utama untuk menjalankan simulasi lalu lintas."""

    def __init__(self, config: TrafficConfig, status_queue=None, stop_event=None):
        self.config = config
        self.behavior_simulator = IntelligentBehaviorSimulator(
            config, mode_type=config.mode_type
        )
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.proxies = self._load_proxies()
        self.status_queue = status_queue
        self.stop_event = stop_event
        self.session_stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "completed": 0,
            "total_duration": 0.0,
        }

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
            "55+": (55, 75),  # Batas atas 75 untuk rentang 55+
            "18-75": (18, 75),  # Tambahkan untuk mode Random Usia
        }
        age_groups, age_weights = zip(*self.config.age_distribution.items())
        selected_age_group = choices(age_groups, weights=age_weights, k=1)[0]
        age_range = age_ranges.get(
            selected_age_group, (18, 65)
        )  # Default jika tidak ada di mapping

        # Cek profil yang ada untuk pengunjung lama
        profile_dir = self.config.project_root / "output" / "profiles"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        existing_profiles = [
            d for d in os.listdir(profile_dir) if os.path.isdir(profile_dir / d)
        ]

        if is_returning and existing_profiles:
            return (
                "Returning",
                choice(existing_profiles),
                device_type,
                country,
                age_range,
            )

        return (
            "New",
            f"user_{int(time.time())}_{randint(1000, 9999)}",
            device_type,
            country,
            age_range,
        )

    async def _create_browser_context(
        self,
        playwright: Playwright,
        profile_id: str,
        device_type: str,
        country: str = None,
        age_range: tuple[int, int] = None,
    ) -> tuple[Optional[Browser], Optional[BrowserContext]]:
        """Membuat konteks browser dengan profil, sidik jari, dan referrer yang sesuai."""
        profile_path = self.config.project_root / "output" / "profiles" / profile_id
        os.makedirs(profile_path, exist_ok=True)

        fingerprint = BrowserFingerprint.get_random_fingerprint(
            device_type, country, age_range
        )

        valid_context_args = [
            "user_agent",
            "viewport",
            "locale",
            "timezone_id",
            "is_mobile",
            "has_touch",
            "device_scale_factor",
            "color_scheme",
            "reduced_motion",
        ]
        context_args = {k: v for k, v in fingerprint.items() if k in valid_context_args}
        context_args["permissions"] = ["geolocation"]

        if self.config.referrer_sources:
            context_args["extra_http_headers"] = {
                "Referer": choice(self.config.referrer_sources)
            }

        state_path = profile_path / "state.json"
        if os.path.exists(state_path):
            context_args["storage_state"] = str(state_path)

        proxy = choice(self.proxies) if self.proxies else None

        try:
            browser = await playwright.chromium.launch(
                headless=self.config.headless, proxy=proxy
            )
            context = await browser.new_context(**context_args)

            # Network throttling (This is a simplified example)
            if (
                hasattr(self.config, "network_type")
                and self.config.network_type
                and self.config.network_type != "Default"
            ):
                if self.config.network_type == "Offline":
                    await context.set_offline(True)
                else:
                    # Simulation for slow networks
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

    async def _execute_and_process_session(
        self,
        playwright: Playwright,
        profile_id: str,
        device_type: str,
        persona,
        country: str = None,
        age_range: tuple[int, int] = None,
    ) -> tuple[str, dict]:
        """Menjalankan logika inti satu sesi dalam blok try-catch."""
        browser, context, page = None, None, None
        ga4_events = []
        goal_result = {}
        try:
            browser, context = await self._create_browser_context(
                playwright, profile_id, device_type, country, age_range
            )
            if not context:
                raise PlaywrightError("Konteks tidak dapat dibuat.")

            page = await context.new_page()
            await page.goto(
                self.config.target_url,
                wait_until="domcontentloaded",
                timeout=self.config.navigation_timeout,
            )
            await page.wait_for_load_state("networkidle")

            # This part seems to call a method that is not in this class, assuming it exists in behavior_simulator
            # await self.behavior_simulator._capture_ga4_event(page, profile_id, ga4_events, "page_view")
            goal_result = await self.behavior_simulator.run_goal_oriented_session(
                page, persona, profile_id, ga4_events
            )

            await context.storage_state(
                path=str(
                    self.config.project_root
                    / "output"
                    / "profiles"
                    / profile_id
                    / "state.json"
                )
            )
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

            visitor_type, profile_id, device_type, country, age_range = (
                self._get_user_profile()
            )

            persona = choice(self.config.personas)

            genders, gender_weights = zip(*self.config.gender_distribution.items())
            selected_gender = choices(genders, weights=gender_weights, k=1)[0]
            # Assuming persona object can have gender and age_range assigned
            if hasattr(persona, "gender"):
                persona.gender = selected_gender
            if hasattr(persona, "age_range"):
                persona.age_range = age_range

            log_prefix = f"Sesi {session_id:03d} [{visitor_type[0]}/{device_type}/{getattr(persona, 'name', 'N/A')}/{getattr(persona, 'gender', 'N/A')}/{age_range[0]}-{age_range[1]}]"
            if country and country != "Random":
                log_prefix += f"/{country}"

            session_status = "failed"
            goal_result = {}

            for attempt in range(self.config.max_retries_per_session + 1):
                try:
                    if self.stop_event and self.stop_event.is_set():
                        break
                    self._log(f"{log_prefix}: Memulai (Percobaan {attempt + 1})")
                    session_status, goal_result = (
                        await self._execute_and_process_session(
                            playwright,
                            profile_id,
                            device_type,
                            persona,
                            country,
                            age_range,
                        )
                    )
                    self.session_stats["successful"] += 1
                    self._log(
                        f"{log_prefix}: Sukses (durasi: {time.time() - start_time:.1f}s)"
                    )
                    break
                except (PlaywrightTimeoutError, PlaywrightError) as e:
                    msg = str(e).splitlines()[0]
                    self._log(
                        f"{log_prefix}: Gagal (Percobaan {attempt + 1}) - {type(e).__name__}: {msg}",
                        level="warning",
                    )
                    if attempt == self.config.max_retries_per_session:
                        self.session_stats["failed"] += 1
                        self._log(
                            f"{log_prefix}: Batas percobaan ulang tercapai.",
                            level="error",
                        )
                except Exception:
                    self.session_stats["failed"] += 1
                    self._log(
                        f"{log_prefix}: Gagal Kritis - {traceback.format_exc(limit=1)}",
                        level="error",
                    )
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
                            "persona": getattr(persona, "name", "N/A"),
                            "device_type": device_type,
                            "visitor_type": visitor_type,
                            "gender": getattr(persona, "gender", "N/A"),
                            "age_range": f"{age_range[0]}-{age_range[1]}",
                            "country": country,
                            "goal_result": goal_result,
                        },
                    }
                )
            self.session_stats["completed"] += 1

    async def run(self):
        """Memicu eksekusi semua sesi yang telah dikonfigurasi dengan fungsi stop yang responsif."""
        self._log("Memulai proses generator...")
        async with async_playwright() as playwright:
            # Membuat semua task sesi tanpa menunggunya secara langsung.
            # Ini memberikan kita kendali atas setiap task.
            session_tasks = {
                asyncio.create_task(self._run_single_session(playwright, i + 1))
                for i in range(self.config.total_sessions)
            }

            # Task Watcher: sebuah task khusus yang hanya menunggu stop_event.
            # Ketika event diaktifkan, ia akan membatalkan semua task sesi lainnya.
            async def watcher(tasks_to_cancel):
                if (
                    not self.stop_event
                ):  # Jika tidak ada stop_event, watcher tidak diperlukan.
                    return
                try:
                    # Menunggu secara asinkron hingga event diaktifkan.
                    # Menggunakan asyncio.to_thread karena stop_event.wait() adalah blocking.
                    await asyncio.to_thread(self.stop_event.wait)
                    self._log(
                        "Perintah berhenti diterima, membatalkan sesi yang berjalan...",
                        level="warning",
                    )
                    for task in tasks_to_cancel:
                        task.cancel()  # Membatalkan setiap task sesi
                except asyncio.CancelledError:
                    # Watcher itu sendiri dapat dibatalkan jika semua tugas selesai secara normal
                    pass

            # Membuat task watcher
            watcher_task = asyncio.create_task(watcher(session_tasks))

            # Menjalankan semua task sesi dan task watcher secara bersamaan.
            # `return_exceptions=True` penting agar pembatalan (CancelledError) tidak menghentikan `gather`.
            all_tasks = list(session_tasks) + [watcher_task]
            await asyncio.gather(*all_tasks, return_exceptions=True)

        self._log("Semua sesi telah selesai atau dihentikan.")
