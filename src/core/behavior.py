# File: src/core/behavior.py

import asyncio
import logging
import time
from random import choices, randint, random, uniform
from typing import Any
from urllib.parse import urljoin, urlparse

from faker import Faker
from playwright.async_api import ElementHandle, Locator, Page

from .config import Persona, TrafficConfig
from .fingerprint import BrowserFingerprint

logger = logging.getLogger(__name__)


class IntelligentBehaviorSimulator:
    """Mensimulasikan perilaku pengguna berdasarkan persona yang diberikan."""

    def __init__(self, config: TrafficConfig, mode_type: str = "Bot"):
        self.config = config
        self.mode_type = mode_type or getattr(config, 'mode_type', 'Bot')
        self.faker = Faker("id_ID" if random() > 0.5 else "en_US")
        if self.mode_type == "Human":
            self.delays = BrowserFingerprint.add_realistic_delays()
        else:
            # Bot: delay minimal
            self.delays = {
                "typing_delay": 10,
                "click_delay": 10,
                "scroll_delay": 0.01,
                "page_load_wait_min": 0.1,
                "page_load_wait_max": 0.2,
                "interaction_pause": 0.01,
                "human_pause": 0.01,
            }

    async def _capture_ga4_event(self, page: Page, profile_id: str, events_list: list, event_name: str, extra_params: dict = {}):
        """Merekam event yang kompatibel dengan GA4 Measurement Protocol."""
        params = {"page_location": page.url, "page_title": await page.title(), "engagement_time_msec": str(int(uniform(1000, 15000)))}
        params.update(extra_params)
        events_list.append({"client_id": profile_id, "timestamp_micros": int(time.time() * 1_000_000), "event_name": event_name, "params": params})

    async def _score_links(self, page: Page, persona: Persona):
        """Menilai dan memberi skor pada tautan yang terlihat berdasarkan relevansinya dengan persona."""
        visible_links = await page.locator("a[href]:visible").all()
        scored_links = []
        base_netloc = urlparse(self.config.target_url).netloc
        keywords_to_check = {**persona.goal_keywords, **persona.generic_keywords}
        for link in visible_links:
            href = await link.get_attribute("href")
            if not href or href.startswith(("mailto:", "tel:")):
                continue
            full_url = urljoin(page.url, href)
            if urlparse(full_url).netloc != base_netloc:
                continue
            link_text = (await link.text_content() or "").lower()
            score = 1
            for keyword, weight in keywords_to_check.items():
                if keyword in link_text or keyword in full_url.lower():
                    score += weight
            if score > 1:
                scored_links.append((link, score))
        return scored_links

    async def _fill_input_element(self, input_elem: Locator):
        """Mengisi satu elemen input dengan data dari Faker."""
        if not await input_elem.is_visible():
            return
        input_name = (await input_elem.get_attribute("name") or "").lower()
        fill_value = ""
        if "email" in input_name or await input_elem.get_attribute("type") == "email":
            fill_value = self.faker.email()
        elif "name" in input_name:
            fill_value = self.faker.name()
        else:
            # Cek apakah ini textarea
            tag = await input_elem.evaluate("el => el.tagName.toLowerCase()")
            if tag == "textarea":
                fill_value = self.faker.paragraph(nb_sentences=3)
            else:
                fill_value = self.faker.company()
        await input_elem.fill(fill_value, timeout=5000)
        await asyncio.sleep(self.delays["typing_delay"] / 1000)

    async def _handle_form_interaction(self, page: Page, selector: str = ""):
        """Mencari, mengisi, dan mengirimkan form. Mengembalikan True jika berhasil."""
        try:
            if selector:
                forms = await page.locator(selector).all()
            else:
                forms = await page.locator("form:visible").all()
            if not forms:
                logger.debug("Tidak ada form yang terdeteksi.")
                return False
            
            logger.info("Form terdeteksi, mencoba untuk berinteraksi.")
            chosen_form = choices(forms)[0]
            
            # Mengisi elemen input dalam form
            for input_type in ["input[type='text']", "input[type='email']", "textarea"]:
                for input_elem in await chosen_form.locator(input_type).all():
                    await self._fill_input_element(input_elem)

            # Mencari dan mengklik tombol submit
            submit_button = chosen_form.locator("button[type='submit'], input[type='submit']")
            if await submit_button.count() > 0:
                first_button: ElementHandle = await submit_button.first.element_handle()
                if first_button and await first_button.is_visible():
                    logger.info("Mengirimkan form...")
                    await first_button.click(delay=self.delays["click_delay"])
                    await page.wait_for_load_state("networkidle", timeout=15000)
                    logger.info("Form berhasil dikirim.")
                    return True
            logger.debug("Tombol submit tidak ditemukan atau tidak terlihat pada form.")
        except Exception as e:
            logger.warning(f"Gagal berinteraksi dengan form: {e}")
        return False

    async def _execute_goal_collect_web_vitals(self, page: Page) -> dict[str, Any]:
        """Mengevaluasi metrik kinerja halaman dan mengembalikannya."""
        try:
            js_script = """
            () => {
                const nav = performance.getEntriesByType('navigation')[0];
                if (!nav) return null;
                const fcpEntry = performance.getEntriesByName('first-contentful-paint')[0];
                return {
                    ttfb: nav.responseStart - nav.requestStart,
                    fcp: fcpEntry ? fcpEntry.startTime : null,
                    domLoad: nav.domContentLoadedEventEnd - nav.startTime,
                    pageLoad: nav.loadEventEnd - nav.startTime
                };
            }
            """
            vitals = await page.evaluate(js_script)
            if vitals and all(v is not None for v in vitals.values()):
                logger.info(f"Web vitals terkumpul: TTFB={vitals.get('ttfb'):.0f}ms, FCP={vitals.get('fcp'):.0f}ms")
                vitals["url"] = page.url
                return vitals
        except Exception as e:
            logger.warning(f"Gagal mengumpulkan web vitals: {e}")
        return {}

    async def _execute_mission(self, page: Page, persona: Persona, ga4_events: list, profile_id: str) -> dict:
        """Menjalankan misi spesifik dari persona. Mengembalikan hasil misi."""
        goal = persona.goal if hasattr(persona, 'goal') else None
        goal_result = {"status": "failed", "details": {"error_message": "Misi gagal karena alasan tidak diketahui."}}
        mission_accomplished = False
        logger.info(f"Memulai misi '{goal.get('type', 'Tipe Misi Tidak Diketahui') if isinstance(goal, dict) else 'Tipe Misi Tidak Diketahui'}' untuk persona '{persona.name}'.")

        try:
            if isinstance(goal, dict) and goal.get("type") == "collect_web_vitals":
                all_vitals = []
                pages_to_visit = goal.get("pages_to_visit", 3)
                for i in range(pages_to_visit):
                    vitals = await self._execute_goal_collect_web_vitals(page)
                    if vitals:
                        all_vitals.append(vitals)
                    
                    if i < pages_to_visit - 1: # Jangan mencoba navigasi setelah halaman terakhir
                        scored_links = await self._score_links(page, persona)
                        if not scored_links:
                            logger.info("Tidak ada tautan relevan untuk melanjutkan 'collect_web_vitals'.")
                            break
                        links, weights = zip(*scored_links)
                        chosen_link = choices(links, weights=weights, k=1)[0]
                        await chosen_link.click(delay=self.delays["click_delay"])
                        await page.wait_for_load_state("networkidle", timeout=self.config.navigation_timeout)
                        await self._capture_ga4_event(page, profile_id, ga4_events, "page_view")
                
                goal_result["status"] = "completed"
                goal_result["details"]["web_vitals"] = all_vitals
                logger.info(f"Misi 'collect_web_vitals' selesai. {len(all_vitals)} halaman dianalisis.")
                mission_accomplished = True

            elif isinstance(goal, dict) and goal.get("type") == "find_and_click":
                target_text = goal.get("target_text", "")
                if not target_text:
                    goal_result["details"]["error_message"] = "Target teks untuk 'find_and_click' tidak ditentukan."
                    logger.warning(goal_result["details"]["error_message"])
                    return goal_result

                target_locator = page.locator(f'a:text-matches("{target_text}", "i"), button:text-matches("{target_text}", "i")').first
                if await target_locator.is_visible(timeout=5000):
                    logger.info(f"Target '{target_text}' ditemukan, mengklik...")
                    await target_locator.click(delay=self.delays["click_delay"])
                    await page.wait_for_load_state("networkidle", timeout=self.config.navigation_timeout)
                    goal_result["status"] = "completed"
                    mission_accomplished = True
                else:
                    goal_result["details"]["error_message"] = f"Target '{target_text}' tidak ditemukan atau tidak terlihat."
                    logger.warning(goal_result["details"]["error_message"])

            elif isinstance(goal, dict) and goal.get("type") == "fill_form":
                selector = goal.get("target_selector")
                if selector is not None:
                    result = await self._handle_form_interaction(page, selector)
                else:
                    result = await self._handle_form_interaction(page)
                if result:
                    goal_result["status"] = "completed"
                    mission_accomplished = True
            else:
                goal_type = goal["type"] if isinstance(goal, dict) and "type" in goal else 'None'
                goal_result["details"]["error_message"] = f"Tipe misi tidak dikenal: {goal_type}"
                logger.warning(goal_result["details"]["error_message"])

        except Exception as e:
            goal_result["details"]["error_message"] = f"Terjadi kesalahan saat menjalankan misi: {e}"
            logger.error(goal_result["details"]["error_message"], exc_info=True)

        goal_result["mission_accomplished"] = mission_accomplished
        return goal_result

    async def _human_like_mouse_move(self, page: Page, viewport: dict):
        """Simulasikan pergerakan mouse manusia secara acak di area viewport."""
        if self.mode_type == "Bot":
            return  # Bot tidak perlu mouse move
        import random
        width, height = viewport.get('width', 1920), viewport.get('height', 1080)
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            await page.mouse.move(x, y, steps=random.randint(5, 20))
            await asyncio.sleep(uniform(0.1, 0.4))

    async def _human_like_scroll(self, page: Page, viewport: dict):
        """Simulasikan scroll manusia dengan jarak dan delay acak."""
        if self.mode_type == "Bot":
            return  # Bot tidak perlu scroll
        import random
        max_scroll = viewport.get('height', 1080) * random.uniform(1.0, 2.5)
        scroll_pos = 0
        while scroll_pos < max_scroll:
            scroll_by = random.randint(80, 300)
            await page.mouse.wheel(0, scroll_by)
            scroll_pos += scroll_by
            await asyncio.sleep(uniform(0.2, 0.7))

    async def run_standard_navigation(self, page: Page, persona: Persona, profile_id: str, ga4_events: list):
        """Menjalankan navigasi standar berbasis kata kunci dengan interaksi human-like."""
        logger.info("Memulai navigasi standar untuk persona.")
        # Ambil viewport dari context jika ada, fallback default
        try:
            raw_viewport = page.viewport_size if hasattr(page, 'viewport_size') and page.viewport_size else {'width': 1920, 'height': 1080}
            # Pastikan raw_viewport adalah dict
            if not isinstance(raw_viewport, dict):
                viewport = {'width': raw_viewport.width, 'height': raw_viewport.height}
            else:
                viewport = raw_viewport
        except Exception:
            viewport = {'width': 1920, 'height': 1080}
        for i in range(randint(*persona.navigation_depth)):
            # Simulasi delay manusia sebelum aksi
            await asyncio.sleep(uniform(*persona.avg_time_per_page))
            # Interaksi mouse acak
            safe_viewport = viewport
            # Pastikan safe_viewport adalah dict dengan key 'width' dan 'height' bertipe int
            if not isinstance(safe_viewport, dict):
                safe_viewport = {'width': getattr(viewport, 'width', 1920), 'height': getattr(viewport, 'height', 1080)}
            else:
                # Cek dan konversi jika value bukan int
                w = safe_viewport.get('width', 1920)
                h = safe_viewport.get('height', 1080)
                try:
                    w = int(w)
                except Exception:
                    w = 1920
                try:
                    h = int(h)
                except Exception:
                    h = 1080
                safe_viewport = {'width': w, 'height': h}
            await self._human_like_mouse_move(page, safe_viewport)
            # Scroll acak
            await self._human_like_scroll(page, safe_viewport)
            await asyncio.sleep(self.delays["scroll_delay"])
            # Peluang untuk berinteraksi dengan form secara acak
            if persona.can_fill_forms and random() < 0.25:
                logger.debug("Mencoba interaksi form acak.")
                await self._handle_form_interaction(page)
                await asyncio.sleep(self.delays["interaction_pause"])
            scored_links = await self._score_links(page, persona)
            if not scored_links:
                logger.info(f"Tidak ada tautan relevan untuk navigasi lebih lanjut pada iterasi {i+1}.")
                break
            links, weights = zip(*scored_links)
            chosen_link = choices(links, weights=weights, k=1)[0]
            try:
                link_href = await chosen_link.get_attribute("href")
                logger.info(f"Mengklik tautan: {link_href}")
                await chosen_link.hover()
                await asyncio.sleep(uniform(0.2, 0.7))
                await chosen_link.click(delay=self.delays["click_delay"])
                await page.wait_for_load_state("networkidle", timeout=self.config.navigation_timeout)
                await self._capture_ga4_event(page, profile_id, ga4_events, "page_view")
            except Exception as e:
                logger.warning(f"Gagal mengklik tautan atau memuat halaman: {e}. Menghentikan navigasi standar.")
                break
        logger.info("Navigasi standar selesai.")

    async def run_goal_oriented_session(self, page: Page, persona: Persona, profile_id: str, ga4_events: list) -> dict:
        """Menjalankan sesi berdasarkan misi. Jika misi gagal, lanjutkan dengan navigasi standar kecuali ditentukan."""
        goal_result = {}
        if persona.goal:
            goal_result = await self._execute_mission(page, persona, ga4_events, profile_id)
            
            if not goal_result.get("mission_accomplished"):
                error_msg = goal_result.get("details", {}).get("error_message", "Alasan tidak spesifik.")
                logger.warning(f"Misi '{persona.goal.get('type', 'Tidak Diketahui')}' gagal. Alasan: {error_msg}. Melanjutkan dengan navigasi standar.")
                await self.run_standard_navigation(page, persona, profile_id, ga4_events)
        else:
            logger.info("Tidak ada misi spesifik yang ditentukan. Menjalankan navigasi standar.")
            await self.run_standard_navigation(page, persona, profile_id, ga4_events)
            goal_result["status"] = "no_goal_specified"
        
        return goal_result