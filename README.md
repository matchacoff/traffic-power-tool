# Traffic Power Tool

**Traffic Power Tool** is a Streamlit-based application for simulating website traffic with various personas, devices, and scenarios. It provides real-time monitoring, web performance analysis, and flexible configuration management.

---

## 🚀 Features

- **Automated Traffic Simulation:** Simulate website visits with customizable personas and device distributions.
- **Real-time Monitoring:** Track session statistics, logs, and persona/device distribution live.
- **Web Vitals Analysis:** Collect and analyze key web performance metrics (TTFB, FCP, DOM Load, Page Load).
- **Persona Editor:** Create and modify custom personas with different behaviors and missions.
- **Preset Management:** Save and load simulation configurations for future use.
- **Output Management:** All results, logs, and cache are organized in a clean `output/` directory structure.
- **Scheduling:** Run simulations automatically at scheduled times.
- **Heatmap Visualization:** Visualize persona interaction patterns on the target website.
- **Maintenance Tools:** Easily clear cache, profiles, and simulation history.

---

## 📁 Project Structure

```
traffic-bot-main/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration (optional)
├── src/                    # Source code
│   ├── core/               # Core modules (behavior, config, generator, etc.)
│   └── utils/              # Utilities (reporting, analytics, etc.)
├── presets/                # Saved configuration presets
├── output/                 # All simulation results & cache (new structure)
│   ├── profiles/           # User profile data (cache)
│   ├── errors/             # Error & crash logs
│   ├── history/            # Simulation history (JSON)
│   ├── logs/               # Process logs (optional)
│   ├── reports/            # Analysis/report results (CSV, Excel, etc.)
│   └── screenshots/        # Simulation screenshots (if any)
├── tests/                  # Unit tests
└── venv/                   # Virtual environment (if any)
```

---

## ⚙️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd traffic-bot-main
   ```

2. **(Optional but recommended) Create a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Usage

1. **Run the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** to the provided address (usually http://localhost:8501).

3. **Configure your simulation:**
   - Enter target website URLs.
   - Set session count, device/persona distribution, and advanced options as needed.
   - Click "Mulai Proses" to start the simulation.

4. **Monitor and analyze:**
   - View real-time stats, logs, and persona/device distribution.
   - Download reports and web vitals after simulation completes.
   - Use the Persona Editor and Preset Management for advanced scenarios.

---

## 🛠️ Troubleshooting

- **Port already in use:**  
  Change the port with `streamlit run app.py --server.port 8502`
- **Dependency errors:**  
  Ensure all dependencies are installed and you are using Python 3.8+.
- **Cache issues:**  
  Use the "Clear All Profiles & Cache" feature in the Settings tab.
- **Output not found:**  
  All results, logs, and cache are stored in the `output/` directory.

---

## 💡 Tips

- Use the Persona Editor to create realistic user journeys.
- Save your favorite configurations as presets for quick reuse.
- Use the Heatmap tab to visualize user interaction patterns.
- Regularly clear cache and history for optimal performance.

---

## 🤝 Contributing

Pull requests and issues are welcome for further development!  
Feel free to fork, improve, and submit your ideas.

---

## 📄 License

This project is licensed under the MIT License.

---

**Made for automated, flexible, and insightful website traffic simulation and analysis.** 