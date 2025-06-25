# File: app.py

import asyncio
import json
import logging
import os
import queue
import re
import shutil
import threading
import time
from collections import Counter
from io import StringIO
from pathlib import Path
import uuid
import sys

import pandas as pd
import streamlit as st
import plotly.express as px

from src.core.config import (
    DEFAULT_PERSONAS,
    Persona,
    TrafficConfig,
    INTERNATIONAL_COUNTRIES,
)
from src.core.generator import AdvancedTrafficGenerator
from src.utils.reporting import (
    create_ga4_compatible_csv,
    create_report_excel,
    parse_keywords_from_string,
)

# --- KONFIGURASI DAN FUNGSI HELPER ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
PROJECT_ROOT = Path(__file__).parent
OUTPUT_ROOT = PROJECT_ROOT / "output"
for dirname in [
    "logs",
    "reports",
    "screenshots",
    "profiles",
    "errors",
    "history",
    "presets",
]:
    os.makedirs(OUTPUT_ROOT / dirname, exist_ok=True)

if sys.platform.startswith("win") and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


def run_generator_in_thread(config, stop_event, log_queue):
    """Menjalankan generator dalam thread terpisah agar tidak memblokir UI."""
    try:
        generator = AdvancedTrafficGenerator(config, log_queue, stop_event)
        asyncio.run(generator.run())
    except Exception as e:
        logging.error(f"Error fatal di thread: {e}", exc_info=True)
        log_queue.put({"type": "log", "data": f"ERROR FATAL DI THREAD: {e}"})
    finally:
        log_queue.put({"type": "status", "data": "finished"})


def initialize_live_stats():
    """Menginisialisasi atau mereset state untuk dasbor real-time."""
    st.session_state.live_stats = {
        "completed": 0,
        "successful": 0,
        "failed": 0,
        "total_duration": 0.0,
        "missions_accomplished": 0,
        "persona_counts": Counter(),
        "device_counts": Counter(),
        "visitor_counts": Counter(),
        "web_vitals": [],
        "clicks": [],
        "gender_counts": Counter(),
        "country_counts": Counter(),
        "age_counts": Counter(),  # Tambahkan age_counts
    }
    st.session_state.log_messages = ["Menunggu proses dimulai..."]
    st.session_state.all_ga4_events = []
    st.session_state.show_results = False
    st.session_state.final_stats = None


def display_colorized_log(log_container, messages, filter_text=""):
    """Menampilkan log dengan warna dan filter."""
    log_html = ""
    filtered_messages = [msg for msg in messages if filter_text.lower() in msg.lower()]
    for msg in reversed(filtered_messages):
        color = "#FFFFFF"  # Putih default
        if "ERROR" in msg or "Gagal Kritis" in msg:
            color = "#FF4B4B"  # Merah
        elif "WARNING" in msg or "Batas percobaan ulang" in msg:
            color = "#FFDB58"  # Kuning
        elif "Sukses" in msg:
            color = "#32CD32"  # Hijau
        elif "Misi" in msg:
            color = "#87CEEB"  # Biru langit
        log_html += f'<p style="color:{color}; margin: 0; font-family: monospace; font-size: 13px;">{msg}</p>'
    log_container.html(
        f'<div style="height: 400px; overflow-y: scroll; background-color: #0e1117; padding: 10px; border-radius: 5px; border: 1px solid #333;">{log_html}</div>'
    )


def save_simulation_history(stats):
    """Simpan hasil simulasi ke file JSON di folder history/."""
    from datetime import datetime

    history_dir = OUTPUT_ROOT / "history"
    os.makedirs(history_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"sim_{ts}_{uuid.uuid4().hex[:6]}.json"
    with open(history_dir / fname, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    return str(history_dir / fname)


def load_simulation_history_list():
    """Muat daftar file history dan metadata singkat."""
    history_dir = OUTPUT_ROOT / "history"
    if not os.path.exists(history_dir):
        return []
    files = sorted(
        [f for f in os.listdir(history_dir) if f.endswith(".json")], reverse=True
    )
    result = []
    for fname in files:
        fpath = history_dir / fname
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = {
                "file": fname,
                "completed": data.get("completed", 0),
                "successful": data.get("successful", 0),
                "failed": data.get("failed", 0),
                "date": fname[4:19].replace("_", " "),
            }
            result.append(meta)
        except Exception:
            continue
    return result


# --- INISIALISASI STREAMLIT APP ---
st.set_page_config(page_title="Traffic Power Tool", page_icon="⚡", layout="wide")
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "log_queue" not in st.session_state:
    st.session_state.log_queue = queue.Queue()
if "stop_event" not in st.session_state:
    st.session_state.stop_event = None
if "custom_personas" not in st.session_state:
    st.session_state.custom_personas = [p.__dict__ for p in DEFAULT_PERSONAS]
if "live_stats" not in st.session_state:
    initialize_live_stats()

st.title("⚡ Traffic Power Tool")
st.caption("Platform Simulasi Intensi & Analisis Kinerja v2.0")


# --- HALAMAN UTAMA (TAB) ---
main_tabs = st.tabs(
    [
        "🚀 Eksekusi & Monitoring",
        "🎭 Editor Persona",
        "💾 Pengaturan & Preset",
        "📚 Riwayat",
        "🔥 Heatmap",
        "💡 Tips & Panduan",
    ]
)

with main_tabs[0]:
    # --- Tampilan Halaman Hasil Analisis ---
    if st.session_state.get("show_results", False):
        st.header("📊 Hasil Analisis Sesi")
        if st.button("⬅️ Kembali ke Konfigurasi"):
            initialize_live_stats()
            st.rerun()

        final_stats = st.session_state.final_stats

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sesi Selesai", final_stats.get("completed", 0))
        m2.metric("Sesi Sukses", final_stats.get("successful", 0))
        m3.metric("Sesi Gagal Total", final_stats.get("failed", 0))
        avg_dur = final_stats.get("total_duration", 0) / (
            final_stats.get("successful", 1) or 1
        )
        m4.metric("Rata-rata Durasi", f"{avg_dur:.2f} s")

        result_tabs = st.tabs(
            ["Statistik Detail", "Log Interaktif", "Kinerja Web (Vitals)"]
        )
        with result_tabs[0]:
            st.write("Rincian sesi berdasarkan berbagai kategori.")
            d1, d2, d3, d4, d5, d6 = st.columns(6)
            for col, key, title in [
                (d1, "persona_counts", "Persona"),
                (d2, "device_counts", "Perangkat"),
                (d3, "visitor_counts", "Tipe Pengunjung"),
                (d4, "gender_counts", "Gender"),
                (d5, "country_counts", "Negara"),
                (d6, "age_counts", "Usia"),
            ]:
                if final_stats.get(key):
                    items = list(final_stats[key].items())
                    if items:
                        df = pd.DataFrame(items)
                        df.columns = [title, "Jumlah"]
                        df = df.sort_values("Jumlah", ascending=False).reset_index(
                            drop=True
                        )
                        col.write(f"**Berdasarkan {title}:**")
                        col.dataframe(df, use_container_width=True, hide_index=True)
                        col.download_button(
                            f"Unduh Data {title}",
                            df.to_csv(index=False).encode("utf-8"),
                            f"{title.lower()}_stats.csv",
                            "text/csv",
                        )
                        # Visualisasi pie chart untuk gender, country, dan age
                        if (
                            key in ["gender_counts", "country_counts", "age_counts"]
                            and len(df) > 0
                        ):
                            if key == "country_counts":
                                # Untuk country, ambil top 10 saja agar chart tidak terlalu penuh
                                df_chart = df.head(10)
                            else:
                                df_chart = df
                            fig = px.pie(
                                df_chart,
                                names=title,
                                values="Jumlah",
                                title=f"Distribusi {title}",
                            )
                            col.plotly_chart(fig, use_container_width=True)

        with result_tabs[1]:
            st.write("Cari dan filter log sesi yang telah selesai.")
            log_filter = st.text_input(
                "Filter log berdasarkan kata kunci (contoh: Sesi 005, Gagal, Misi)",
                key="log_filter_final",
            )
            display_colorized_log(
                st.container(), st.session_state.log_messages, log_filter
            )

        with result_tabs[2]:
            st.write(
                "Data kinerja halaman yang dikumpulkan oleh persona 'Performance Analyst'."
            )
            if final_stats["web_vitals"]:
                vitals_df = pd.DataFrame(final_stats["web_vitals"])
                st.dataframe(vitals_df, use_container_width=True)
                st.download_button(
                    "Unduh Data Web Vitals",
                    vitals_df.to_csv(index=False).encode("utf-8"),
                    "web_vitals.csv",
                    "text/csv",
                )
            else:
                st.info("Tidak ada data kinerja web yang terkumpul di sesi ini.")

        # Export ke Google Sheets (placeholder)
        if st.button("Export ke Google Sheets"):
            from src.utils.google_sheets import export_to_google_sheets

            df_export = (
                pd.DataFrame(st.session_state.final_stats["web_vitals"])
                if st.session_state.final_stats
                and st.session_state.final_stats.get("web_vitals")
                else pd.DataFrame()
            )
            export_to_google_sheets(df_export, "TrafficBot Results")
            st.success("Export ke Google Sheets (placeholder)")
        # Notifikasi Email (placeholder)
        if st.button("Kirim Notifikasi Email"):
            from src.utils.email_notify import send_email_notification

            send_email_notification(
                "Simulasi Selesai", "Simulasi telah selesai.", "youremail@example.com"
            )
            st.success("Notifikasi email dikirim (placeholder)")

    # --- Tampilan Konfigurasi & Dasbor Real-time ---
    else:
        col_config, col_monitoring = st.columns([1, 2], gap="large")
        with col_config:
            st.markdown("<b>Konfigurasi Simulasi</b>", unsafe_allow_html=True)
            st.caption(
                "Isi URL target dan parameter utama. Pengaturan lanjutan bisa dibuka jika perlu."
            )

            # --- PENGATURAN DI LUAR FORM ---
            st.markdown("<b>🌍 Pengaturan Region/Country</b>", unsafe_allow_html=True)
            region_mode = st.radio(
                "Mode Region:",
                [
                    "🌐 Random International",
                    "🎯 Pilih Negara Tertentu",
                    "🇮🇩 Indonesia Only",
                ],
                help="Pilih bagaimana bot akan mendistribusikan traffic berdasarkan negara",
            )

            country_distribution = {}

            if region_mode == "🌐 Random International":
                st.info(
                    "Bot akan menggunakan distribusi internasional yang realistis (US, Indonesia, India, China, dll)"
                )
                country_distribution = INTERNATIONAL_COUNTRIES

            elif region_mode == "🎯 Pilih Negara Tertentu":
                st.info("Pilih negara-negara target dan bobot distribusinya")
                popular_countries = [
                    "United States",
                    "Indonesia",
                    "India",
                    "China",
                    "Brazil",
                    "United Kingdom",
                    "Germany",
                    "Japan",
                    "France",
                    "Canada",
                    "Australia",
                    "Mexico",
                    "Spain",
                    "Italy",
                    "South Korea",
                    "Russia",
                    "Netherlands",
                    "Turkey",
                    "Poland",
                    "Argentina",
                ]

                selected_countries = st.multiselect(
                    "Pilih Negara Target:",
                    popular_countries,
                    default=["United States", "Indonesia", "India"],
                    help="Pilih negara-negara yang ingin dijadikan target traffic",
                )

                if selected_countries:
                    st.write("**Atur Bobot Distribusi:**")
                    for country in selected_countries:
                        weight = st.slider(
                            f"Bobot {country}",
                            1,
                            50,
                            10,
                            help=f"Semakin tinggi bobot, semakin sering bot dari {country}",
                        )
                        country_distribution[country] = weight
                else:
                    st.warning("Pilih minimal satu negara!")

            elif region_mode == "🇮🇩 Indonesia Only":
                st.info("Bot akan fokus hanya pada traffic dari Indonesia")
                country_distribution = {"Indonesia": 100}

            if country_distribution:
                total_weight = sum(country_distribution.values())
                if total_weight > 0:
                    st.write("**Preview Distribusi Negara:**")
                    preview_data = []
                    for country, weight in country_distribution.items():
                        percentage = (weight / total_weight) * 100
                        preview_data.append(
                            {
                                "Negara": country,
                                "Bobot": weight,
                                "Persentase": f"{percentage:.1f}%",
                            }
                        )

                    preview_df = pd.DataFrame(preview_data)
                    st.dataframe(preview_df, use_container_width=True, hide_index=True)

            st.markdown("<b>🎭 Pengaturan Persona</b>", unsafe_allow_html=True)
            enable_random_personas = st.toggle(
                "Aktifkan Random Persona Generator",
                value=True,
                help="Generate persona random dengan karakteristik internasional",
            )

            if enable_random_personas:
                random_persona_count = st.number_input(
                    "Jumlah Random Persona",
                    1,
                    20,
                    5,
                    help="Berapa banyak persona random yang akan di-generate",
                )

                persona_templates = st.multiselect(
                    "Template Persona yang Digunakan:",
                    [
                        "Global Explorer",
                        "Digital Nomad",
                        "Cultural Enthusiast",
                        "Tech Innovator",
                        "Eco Activist",
                    ],
                    default=["Global Explorer", "Digital Nomad", "Tech Innovator"],
                    help="Pilih jenis persona yang akan di-generate secara random",
                )

                if st.button("🔄 Generate Random Personas"):
                    from src.core.config import generate_random_personas

                    if country_distribution:
                        selected_countries_for_persona = list(
                            country_distribution.keys()
                        )
                        random_personas = generate_random_personas(
                            random_persona_count, selected_countries_for_persona
                        )
                        st.session_state.custom_personas = [
                            p.__dict__ for p in random_personas
                        ]
                        st.success(
                            f"Berhasil generate {len(random_personas)} persona random!"
                        )
                        st.rerun()
                    else:
                        st.error("Pilih negara terlebih dahulu!")

            # --- START FORM ---
            with st.form("traffic_form"):
                target_urls = st.text_area(
                    "URL Website Target",
                    "https://example.com",
                    help="Satu URL per baris. Contoh: https://namasitus.com",
                    placeholder="https://namasitus.com",
                )
                url_list = [u.strip() for u in target_urls.splitlines() if u.strip()]
                import re as _re

                url_pattern = _re.compile(
                    r"^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+", _re.IGNORECASE
                )
                invalid_urls = [u for u in url_list if not url_pattern.match(u)]
                if invalid_urls:
                    st.error(f"Terdapat URL tidak valid: {', '.join(invalid_urls)}.")

                st.markdown("---")
                st.markdown("<b>Parameter Simulasi</b>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                total_sessions = c1.number_input(
                    "Jumlah Sesi",
                    1,
                    10000,
                    st.session_state.get("total_sessions", 50),
                    10,
                    help="Total kunjungan yang akan disimulasikan.",
                )
                max_concurrent = c2.number_input(
                    "Paralel",
                    1,
                    100,
                    st.session_state.get("max_concurrent", 10),
                    1,
                    help="Berapa banyak kunjungan berjalan bersamaan.",
                )
                max_retries = c3.number_input(
                    "Retry Maksimum",
                    0,
                    5,
                    2,
                    1,
                    help="Berapa kali dicoba ulang jika gagal.",
                )

                st.markdown("---")
                st.markdown("<b>Pengunjung & Perangkat</b>", unsafe_allow_html=True)
                returning_rate = st.slider(
                    "% Pengunjung Kembali",
                    0,
                    100,
                    30,
                    help="Persentase kunjungan dari pengunjung lama.",
                )

                d1, d2, d3 = st.columns(3)
                desktop_dist = d1.number_input(
                    "Desktop (%)", 0, 100, 60, key="dist_desktop"
                )
                mobile_dist = d2.number_input(
                    "Mobile (%)", 0, 100, 30, key="dist_mobile"
                )
                tablet_dist = d3.number_input(
                    "Tablet (%)", 0, 100, 10, key="dist_tablet"
                )
                total_device = desktop_dist + mobile_dist + tablet_dist
                if total_device != 100:
                    st.error(
                        f"Total distribusi perangkat harus 100%. Saat ini: {total_device}%."
                    )

                male_dist = st.slider(
                    "% Pengunjung Pria", 0, 100, 50, help="Sisanya otomatis wanita."
                )

                st.markdown("<b>👥 Pengaturan Usia</b>", unsafe_allow_html=True)
                age_mode = st.radio(
                    "Mode Distribusi Usia:",
                    ["📊 Distribusi Standar", "🎯 Kustom Distribusi", "🎲 Random Usia"],
                    help="Pilih bagaimana bot akan mendistribusikan usia pengunjung",
                )

                age_distribution = {}
                if age_mode == "📊 Distribusi Standar":
                    st.info("Menggunakan distribusi usia yang realistis secara global")
                    age_distribution = {
                        "18-24": 20,
                        "25-34": 30,
                        "35-44": 25,
                        "45-54": 15,
                        "55+": 10,
                    }
                elif age_mode == "🎯 Kustom Distribusi":
                    st.info("Atur distribusi usia sesuai kebutuhan target audience")
                    age_18_24 = st.slider("Usia 18-24 tahun (%)", 0, 100, 20)
                    age_25_34 = st.slider("Usia 25-34 tahun (%)", 0, 100, 30)
                    age_35_44 = st.slider("Usia 35-44 tahun (%)", 0, 100, 25)
                    age_45_54 = st.slider("Usia 45-54 tahun (%)", 0, 100, 15)
                    age_55_plus = st.slider("Usia 55+ tahun (%)", 0, 100, 10)
                    total_age = (
                        age_18_24 + age_25_34 + age_35_44 + age_45_54 + age_55_plus
                    )
                    if total_age != 100:
                        st.error(
                            f"Total distribusi usia harus 100%. Saat ini: {total_age}%"
                        )
                    else:
                        age_distribution = {
                            "18-24": age_18_24,
                            "25-34": age_25_34,
                            "35-44": age_35_44,
                            "45-54": age_45_54,
                            "55+": age_55_plus,
                        }
                elif age_mode == "🎲 Random Usia":
                    st.info("Usia akan di-random secara merata dari 18-75 tahun")
                    age_distribution = {"18-75": 100}

                if age_distribution:
                    st.write("**Preview Distribusi Usia:**")
                    age_preview_data = [
                        {"Grup Usia": age_group, "Persentase": f"{weight}%"}
                        for age_group, weight in age_distribution.items()
                    ]
                    age_preview_df = pd.DataFrame(age_preview_data)
                    st.dataframe(
                        age_preview_df, use_container_width=True, hide_index=True
                    )

                st.caption(
                    "Pengaturan lanjutan bisa dibuka jika ingin mengubah mode, proxy, dsb."
                )
                with st.expander("Pengaturan Lanjutan", expanded=False):
                    uploaded_proxy_file = st.file_uploader(
                        "File Proksi (.txt)", type="txt"
                    )
                    headless_mode = st.toggle(
                        "Mode Headless", st.session_state.get("headless_mode", True)
                    )
                    network_type = st.selectbox(
                        "Simulasi Jaringan",
                        ["Default", "3G", "4G", "WiFi Lambat", "Offline"],
                        index=["Default", "3G", "4G", "WiFi Lambat", "Offline"].index(
                            st.session_state.get("network_type", "Default")
                        ),
                    )
                    custom_js = st.text_area("Custom JavaScript (opsional)", "")
                    mode_type = st.selectbox(
                        "Mode Simulasi",
                        ["Bot", "Human"],
                        index=["Bot", "Human"].index(
                            st.session_state.get("mode_type", "Bot")
                        ),
                    )
                    enable_schedule = st.toggle("Penjadwalan Simulasi", value=False)
                    schedule_time = None
                    if enable_schedule:
                        schedule_time = st.time_input("Waktu Penjadwalan")

                submitted = st.form_submit_button(
                    "🚀 Mulai Proses",
                    type="primary",
                    use_container_width=True,
                    disabled=st.session_state.is_running or total_device != 100,
                )

        with col_monitoring:
            st.subheader("📈 Dasbor Monitoring Real-time")
            stop_button = st.button(
                "⏹️ Hentikan Proses",
                use_container_width=True,
                disabled=not st.session_state.is_running,
                type="secondary",
            )
            progress_placeholder = st.empty()
            metric_placeholder = st.empty()
            vitals_placeholder = st.empty()
            charts_placeholder = st.empty()
            log_placeholder = st.empty()

        if submitted:
            if not invalid_urls:
                st.session_state.is_running = True
                initialize_live_stats()
                st.session_state.stop_event = threading.Event()
                proxy_path = None
                if uploaded_proxy_file:
                    proxy_path = OUTPUT_ROOT / "proxies_temp.txt"
                    with open(proxy_path, "w") as f:
                        f.write(
                            StringIO(
                                uploaded_proxy_file.getvalue().decode("utf-8")
                            ).read()
                        )

                config = TrafficConfig(
                    project_root=PROJECT_ROOT,
                    target_url=target_urls,
                    total_sessions=total_sessions,
                    max_concurrent=max_concurrent,
                    headless=headless_mode,
                    returning_visitor_rate=returning_rate,
                    max_retries_per_session=max_retries,
                    proxy_file=str(proxy_path) if proxy_path else None,
                    personas=[Persona(**p) for p in st.session_state.custom_personas],
                    gender_distribution={"Male": male_dist, "Female": 100 - male_dist},
                    device_distribution={
                        "Desktop": desktop_dist,
                        "Mobile": mobile_dist,
                        "Tablet": tablet_dist,
                    },
                    country_distribution=country_distribution,
                    age_distribution=age_distribution,
                    network_type=network_type,
                    mode_type=mode_type,
                    schedule_time=(
                        str(schedule_time)
                        if enable_schedule and schedule_time
                        else None
                    ),
                    enable_random_personas=enable_random_personas,
                    random_persona_count=(
                        random_persona_count if enable_random_personas else 5
                    ),
                )

                import datetime

                now = datetime.datetime.now().time()
                if schedule_time and str(schedule_time) != str(now):
                    target_time = schedule_time
                    if isinstance(target_time, str):
                        target_time = datetime.datetime.strptime(
                            target_time, "%H:%M:%S"
                        ).time()
                    now_dt = datetime.datetime.combine(datetime.date.today(), now)
                    target_dt = datetime.datetime.combine(
                        datetime.date.today(), target_time
                    )
                    if target_dt < now_dt:
                        target_dt += datetime.timedelta(days=1)
                    wait_seconds = (target_dt - now_dt).total_seconds()
                    st.info(
                        f"Simulasi akan dijalankan otomatis pada {target_time.strftime('%H:%M:%S')} (dalam {int(wait_seconds)} detik)"
                    )

                    def delayed_run():
                        time.sleep(wait_seconds)
                        run_generator_in_thread(
                            config,
                            st.session_state.stop_event,
                            st.session_state.log_queue,
                        )

                    threading.Thread(target=delayed_run).start()
                else:
                    threading.Thread(
                        target=run_generator_in_thread,
                        args=(
                            config,
                            st.session_state.stop_event,
                            st.session_state.log_queue,
                        ),
                    ).start()
                st.rerun()
            else:
                st.error("Perbaiki URL yang tidak valid sebelum memulai.")

        if stop_button:
            if st.session_state.stop_event:
                st.session_state.stop_event.set()
                st.toast("Perintah berhenti telah dikirim!")

        if st.session_state.is_running:
            while not st.session_state.log_queue.empty():
                item = st.session_state.log_queue.get()
                if isinstance(item, dict):
                    msg_type, msg_data = item.get("type"), item.get("data")
                    if msg_type == "log":
                        st.session_state.log_messages.append(msg_data)
                    elif msg_type == "live_update":
                        stats = st.session_state.live_stats
                        if stats is not None and msg_data is not None:
                            stats["completed"] += 1
                            if msg_data.get("status") == "successful":
                                stats["successful"] += 1
                                stats["total_duration"] += msg_data.get("duration", 0)
                            else:
                                stats["failed"] += 1
                            for key, counter in [
                                ("persona", "persona_counts"),
                                ("device_type", "device_counts"),
                                ("visitor_type", "visitor_counts"),
                                ("country", "country_counts"),
                                ("age_range", "age_counts"),
                            ]:
                                if (
                                    key in msg_data
                                    and counter in stats
                                    and stats[counter] is not None
                                ):
                                    stats[counter].update([msg_data[key]])
                            if "gender" in msg_data:
                                stats["gender_counts"].update([msg_data["gender"]])
                            goal_result = (
                                msg_data.get("goal_result", {})
                                if isinstance(msg_data, dict)
                                else {}
                            )
                            if goal_result.get("mission_accomplished"):
                                stats["missions_accomplished"] += 1
                            if goal_result.get(
                                "status"
                            ) == "completed" and "web_vitals" in goal_result.get(
                                "details", {}
                            ):
                                stats["web_vitals"].extend(
                                    goal_result["details"]["web_vitals"]
                                )
                            if "clicks" in msg_data:
                                stats["clicks"].extend(msg_data["clicks"])
                    elif msg_type == "status" and msg_data == "finished":
                        st.session_state.is_running = False
                        st.session_state.final_stats = st.session_state.live_stats
                        st.session_state.show_results = True
                        save_simulation_history(st.session_state.final_stats)
                        st.rerun()

            stats = st.session_state.live_stats
            with progress_placeholder.container():
                completed_count = stats["completed"]
                if (
                    "total_sessions" in locals()
                    and total_sessions > 0
                    and completed_count > 0
                ):
                    progress_percent = completed_count / total_sessions
                    st.progress(
                        progress_percent,
                        text=f"Sesi: {completed_count}/{total_sessions}",
                    )
                    avg_time = stats["total_duration"] / completed_count
                    etr_seconds = (total_sessions - completed_count) * avg_time
                    etr_str = (
                        time.strftime("%H:%M:%S", time.gmtime(etr_seconds))
                        if etr_seconds > 0
                        else "Selesai"
                    )
                    st.caption(
                        f"Rata-rata waktu per sesi: {avg_time:.2f} detik | Estimasi waktu tersisa (ETR): {etr_str}"
                    )
            with metric_placeholder.container():
                completed_count = stats["completed"]
                m1, m2, m3, m4 = st.columns(4)
                m1.metric(
                    "Tingkat Sukses",
                    f"{(stats['successful']/completed_count*100) if completed_count>0 else 0:.1f}%",
                    f"{stats['failed']} Gagal",
                )
                m2.metric("Misi Berhasil", f"{stats['missions_accomplished']}")
                m3.metric(
                    "Rata-rata Durasi",
                    f"{(stats['total_duration']/stats['successful']) if stats['successful']>0 else 0:.2f} s",
                )
                if "total_sessions" in locals() and "max_concurrent" in locals():
                    m4.metric(
                        "Sesi Aktif (Est.)",
                        f"~{min(max_concurrent, total_sessions - completed_count)}",
                    )
            with vitals_placeholder.container():
                if stats["web_vitals"]:
                    st.subheader("Analisis Kinerja Halaman (Avg.)")
                    df_vitals = pd.DataFrame(stats["web_vitals"])
                    if len(df_vitals) > 0:
                        avg_vitals = df_vitals[
                            ["ttfb", "fcp", "domLoad", "pageLoad"]
                        ].mean()
                        if isinstance(avg_vitals, pd.Series):
                            avg_vitals_dict = avg_vitals.to_dict()
                        else:
                            avg_vitals_dict = {
                                k: avg_vitals
                                for k in ["ttfb", "fcp", "domLoad", "pageLoad"]
                            }
                        v1, v2, v3, v4 = st.columns(4)
                        ttfb, fcp, domLoad, pageLoad = (
                            avg_vitals_dict.get("ttfb"),
                            avg_vitals_dict.get("fcp"),
                            avg_vitals_dict.get("domLoad"),
                            avg_vitals_dict.get("pageLoad"),
                        )
                        if isinstance(ttfb, (float, int)) and pd.notna(ttfb):
                            v1.metric("TTFB", f"{ttfb:.0f} ms")
                        if isinstance(fcp, (float, int)) and pd.notna(fcp):
                            v2.metric("FCP", f"{fcp:.0f} ms")
                        if isinstance(domLoad, (float, int)) and pd.notna(domLoad):
                            v3.metric("DOM Load", f"{domLoad:.0f} ms")
                        if isinstance(pageLoad, (float, int)) and pd.notna(pageLoad):
                            v4.metric("Page Load", f"{pageLoad:.0f} ms")
            with charts_placeholder.container():
                st.subheader("Distribusi Sesi (Live)")
                chart_cols = st.columns(5)
                for i, (key, title) in enumerate(
                    [
                        ("persona_counts", "Persona"),
                        ("device_counts", "Perangkat"),
                        ("visitor_counts", "Tipe Pengunjung"),
                        ("country_counts", "Negara (Top 10)"),
                        ("age_counts", "Usia"),
                    ]
                ):
                    counts = stats.get(key)
                    if counts:
                        items = list(counts.items())
                        if items:
                            df = pd.DataFrame(items)
                            df.columns = [title.split(" ")[0], "Jumlah"]
                            if key == "country_counts":
                                df = df.nlargest(10, "Jumlah")
                            fig_class = (
                                px.bar
                                if key
                                in ["visitor_counts", "country_counts", "age_counts"]
                                else px.pie
                            )
                            if fig_class == px.pie:
                                fig = fig_class(
                                    df,
                                    names=title.split(" ")[0],
                                    values="Jumlah",
                                    title=f"Distribusi {title.split(' ')[0]}",
                                )
                            else:
                                fig = fig_class(
                                    df,
                                    x=title.split(" ")[0],
                                    y="Jumlah",
                                    title=f"Distribusi {title.split(' ')[0]}",
                                )
                            chart_cols[i].plotly_chart(fig, use_container_width=True)
            display_colorized_log(log_placeholder, st.session_state.log_messages)
            time.sleep(1)
            st.rerun()


with main_tabs[1]:
    st.header("🎭 Editor Persona Kustom")
    st.info("Definisikan perilaku dan misi untuk setiap persona.")
    for i, p in enumerate(st.session_state.custom_personas):
        with st.expander(f"**{p['name']}**"):
            p["name"] = st.text_input("Nama Persona", value=p["name"], key=f"name_{i}")
            p["can_fill_forms"] = st.toggle(
                "Dapat Mengisi Form?",
                value=p.get("can_fill_forms", False),
                key=f"form_{i}",
            )
            st.subheader("Misi Persona")
            mission_types = [
                "find_and_click",
                "fill_form",
                "collect_web_vitals",
                "none",
            ]
            current_type = (
                p.get("goal", {}).get("type")
                if isinstance(p.get("goal"), dict)
                else "none"
            )
            mission_type = st.selectbox(
                "Tipe Misi",
                mission_types,
                index=(
                    mission_types.index(current_type)
                    if current_type in mission_types
                    else 3
                ),
                key=f"mission_type_{i}",
            )
            mission_goal = {}
            if mission_type == "find_and_click":
                target_text = st.text_input(
                    "Teks/Label Target untuk Diklik",
                    value=p.get("goal", {}).get("target_text", ""),
                    key=f"target_text_{i}",
                    help="Contoh: download, unduh, get now",
                )
                mission_goal = {
                    "type": "find_and_click",
                    "target_text": target_text,
                    "case_sensitive": False,
                }
            elif mission_type == "fill_form":
                target_selector = st.text_input(
                    "Selector Form (opsional)",
                    value=p.get("goal", {}).get("target_selector", ""),
                    key=f"target_selector_{i}",
                    help="Contoh: form#contact-form",
                )
                mission_goal = {"type": "fill_form", "target_selector": target_selector}
            elif mission_type == "collect_web_vitals":
                pages_to_visit = st.number_input(
                    "Jumlah Halaman untuk Analisis Web Vitals",
                    1,
                    20,
                    int(p.get("goal", {}).get("pages_to_visit", 3)),
                    key=f"pages_to_visit_{i}",
                )
                mission_goal = {
                    "type": "collect_web_vitals",
                    "pages_to_visit": pages_to_visit,
                }
            else:
                mission_goal = None
            p["goal"] = mission_goal
            pc1, pc2 = st.columns(2)
            p["navigation_depth"] = pc1.slider(
                "Kedalaman Navigasi",
                1,
                20,
                value=p["navigation_depth"],
                key=f"depth_{i}",
            )
            p["avg_time_per_page"] = pc2.slider(
                "Waktu per Halaman (detik)",
                5,
                120,
                value=p["avg_time_per_page"],
                key=f"time_{i}",
            )
            p["goal_keywords"] = parse_keywords_from_string(
                st.text_area(
                    "Kata Kunci Tujuan",
                    ", ".join(
                        [f"{k}:{v}" for k, v in p.get("goal_keywords", {}).items()]
                    ),
                    key=f"goal_kw_{i}",
                )
            )
            p["generic_keywords"] = parse_keywords_from_string(
                st.text_area(
                    "Kata Kunci Generik",
                    ", ".join(
                        [f"{k}:{v}" for k, v in p.get("generic_keywords", {}).items()]
                    ),
                    key=f"gen_kw_{i}",
                )
            )
            if st.button("Hapus Persona Ini", key=f"del_{i}", type="secondary"):
                st.session_state.custom_personas.pop(i)
                st.rerun()
    if st.button("➕ Tambah Persona Baru"):
        st.session_state.custom_personas.append(DEFAULT_PERSONAS[0].__dict__.copy())
        st.rerun()

with main_tabs[2]:
    st.header("💾 Manajemen Preset")
    st.info(
        "Simpan semua konfigurasi (termasuk persona) untuk digunakan kembali nanti."
    )
    with st.form("save_preset_form"):
        preset_name = st.text_input("Nama Preset Baru")
        if st.form_submit_button("Simpan Konfigurasi"):
            if preset_name:
                config_to_save = {
                    "target_url": st.session_state.get(
                        "target_urls", "https://example.com"
                    ),
                    "total_sessions": st.session_state.get("total_sessions", 50),
                    "max_concurrent": st.session_state.get("max_concurrent", 10),
                    "returning_visitor_rate": st.session_state.get(
                        "returning_rate", 30
                    ),
                    "headless_mode": st.session_state.get("headless_mode", True),
                    "max_retries_per_session": st.session_state.get("max_retries", 2),
                    "custom_personas": st.session_state.get(
                        "custom_personas", [p.__dict__ for p in DEFAULT_PERSONAS]
                    ),
                    "gender_distribution": st.session_state.get(
                        "gender_dist", {"Male": 50, "Female": 50}
                    ),
                    "device_distribution": st.session_state.get(
                        "device_dist", {"Desktop": 60, "Mobile": 30, "Tablet": 10}
                    ),
                }
                with open(
                    OUTPUT_ROOT / "presets" / f"{preset_name.replace(' ','_')}.json",
                    "w",
                ) as f:
                    json.dump(config_to_save, f, indent=4)
                st.success(f"Preset '{preset_name}' berhasil disimpan!")
            else:
                st.warning("Nama preset tidak boleh kosong.")
    st.divider()
    st.header("📂 Load Preset Konfigurasi")
    import glob

    preset_files = glob.glob(str(OUTPUT_ROOT / "presets" / "*.json"))
    preset_names = [os.path.basename(f) for f in preset_files]
    selected_preset = st.selectbox("Pilih preset untuk dimuat:", ["-"] + preset_names)
    if selected_preset and selected_preset != "-":
        if st.button("Muat Preset Ini"):
            with open(
                OUTPUT_ROOT / "presets" / selected_preset, "r", encoding="utf-8"
            ) as f:
                preset_data = json.load(f)
            st.session_state["target_urls"] = preset_data.get(
                "target_url", "https://example.com"
            )
            st.session_state["total_sessions"] = preset_data.get("total_sessions", 50)
            st.session_state["max_concurrent"] = preset_data.get("max_concurrent", 10)
            st.session_state["returning_rate"] = preset_data.get(
                "returning_visitor_rate", 30
            )
            st.session_state["headless_mode"] = preset_data.get("headless_mode", True)
            st.session_state["max_retries"] = preset_data.get(
                "max_retries_per_session", 2
            )
            st.session_state["custom_personas"] = preset_data.get(
                "custom_personas", [p.__dict__ for p in DEFAULT_PERSONAS]
            )
            st.session_state["gender_dist"] = preset_data.get(
                "gender_distribution", {"Male": 50, "Female": 50}
            )
            st.session_state["device_dist"] = preset_data.get(
                "device_distribution", {"Desktop": 60, "Mobile": 30, "Tablet": 10}
            )
            st.success(
                f"Preset '{selected_preset}' berhasil dimuat! Silakan cek dan jalankan di tab Eksekusi."
            )
            st.rerun()
    st.divider()
    st.header("🛠️ Maintenance")
    st.warning(
        "Tindakan ini akan menghapus semua data sesi tersimpan (kunjungan kembali) dan log screenshot."
    )
    if st.button("Hapus Semua Profil & Cache", type="secondary"):
        try:
            for dir_path in [OUTPUT_ROOT / "profiles", OUTPUT_ROOT / "errors"]:
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                    os.makedirs(dir_path)
            st.success("Cache berhasil dihapus!")
            st.balloons()
            time.sleep(2)
            st.rerun()
        except Exception as e:
            st.error(f"Gagal menghapus cache: {e}")

with main_tabs[3]:
    st.header("📚 Riwayat Simulasi")
    if st.button("🗑️ Hapus Semua Riwayat Simulasi", type="secondary"):
        history_dir = OUTPUT_ROOT / "history"
        try:
            if os.path.exists(history_dir):
                shutil.rmtree(history_dir)
                os.makedirs(history_dir)
            st.success("Semua riwayat simulasi berhasil dihapus!")
            st.rerun()
        except Exception as e:
            st.error(f"Gagal menghapus riwayat: {e}")
    history_list = load_simulation_history_list()
    if not history_list:
        st.info("Belum ada riwayat simulasi.")
    else:
        df_hist = pd.DataFrame(history_list)
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        selected = st.selectbox(
            "Pilih file untuk detail:", [h["file"] for h in history_list]
        )
        if selected:
            fpath = OUTPUT_ROOT / "history" / selected
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.subheader(f"Detail Simulasi: {selected}")
            st.json(data)
            if "web_vitals" in data and data["web_vitals"]:
                st.download_button(
                    "Unduh Web Vitals",
                    pd.DataFrame(data["web_vitals"])
                    .to_csv(index=False)
                    .encode("utf-8"),
                    "web_vitals.csv",
                    "text/csv",
                )

with main_tabs[4]:
    st.header("🔥 Heatmap Interaksi Persona")
    stats = (
        st.session_state.final_stats
        if st.session_state.show_results
        else st.session_state.live_stats
    )
    clicks = stats.get("clicks", []) if stats else []
    if not clicks:
        st.info("Belum ada data klik/interaksi untuk divisualisasikan.")
    else:
        st.write(f"Total klik/interaksi tercatat: {len(clicks)}")
        df_clicks = pd.DataFrame()
        if (
            clicks
            and isinstance(clicks[0], dict)
            and "x" in clicks[0]
            and "y" in clicks[0]
        ):
            df_clicks = pd.DataFrame(clicks)
        elif clicks and isinstance(clicks[0], (list, tuple)) and len(clicks[0]) == 2:
            df_clicks = pd.DataFrame(clicks, columns=["x", "y"])
        if not df_clicks.empty:
            fig = px.density_heatmap(
                df_clicks,
                x="x",
                y="y",
                nbinsx=30,
                nbinsy=30,
                title="Heatmap Interaksi Persona",
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Format data klik tidak valid untuk divisualisasikan.")

with main_tabs[5]:
    st.header("💡 Tips & Panduan Penggunaan Aplikasi")
    st.markdown(
        """
### **Tips Penggunaan Traffic Power Tool**

1. **Konfigurasi Simulasi**
   - Masukkan URL target, atur jumlah sesi, distribusi perangkat, dan persona sesuai kebutuhan.
   - Gunakan fitur penjadwalan untuk menjalankan simulasi otomatis di waktu tertentu.

2. **Monitoring Real-time**
   - Pantau progres simulasi, statistik, dan log secara langsung di tab Eksekusi & Monitoring.
   - Gunakan filter log untuk mencari sesi atau error tertentu.

3. **Analisis Hasil**
   - Setelah simulasi selesai, cek tab hasil analisis untuk melihat performa web, distribusi persona, dan perangkat.
   - Unduh data hasil simulasi dalam format CSV untuk analisis lebih lanjut.

4. **Manajemen Persona & Preset**
   - Buat persona kustom dengan perilaku dan misi berbeda di tab Editor Persona.
   - Simpan konfigurasi favorit sebagai preset agar bisa digunakan ulang dengan mudah.

5. **Maintenance & Riwayat**
   - Hapus cache, profil, dan riwayat simulasi secara berkala untuk menjaga performa aplikasi.
   - Cek riwayat simulasi untuk membandingkan hasil antar percobaan.

6. **Visualisasi & Heatmap**
   - Gunakan tab Heatmap untuk melihat pola interaksi persona di halaman web target.

---
**Selamat mencoba!**
    """
    )
