# Traffic Power Tool

**Enterprise-Grade Website Traffic Simulation & Analytics Platform v2.0**

A sophisticated Streamlit-based application for simulating realistic website traffic with advanced international demographics, behavioral personas, and comprehensive analytics.

## 🌟 Key Features

### 🌍 **International Traffic Simulation**
- **200+ Countries** supported with realistic distribution weights
- **Geolocation-aware** fingerprinting (user agent, timezone, locale)
- **Country-specific** behavior patterns and preferences
- **Real-time monitoring** of traffic distribution by region

### 👥 **Advanced Demographics Management**
- **Age distribution** control (18-24, 25-34, 35-44, 45-54, 55+)
- **Gender targeting** with customizable ratios
- **Device distribution** (Desktop, Mobile, Tablet)
- **Returning vs New visitor** simulation

### 🎭 **Intelligent Persona System**
- **20+ Pre-built personas** with distinct behavioral patterns
- **Random persona generator** with international characteristics
- **Goal-oriented behavior** (form filling, clicking, web vitals collection)
- **Customizable persona** creation and editing

### 📊 **Real-time Analytics & Monitoring**
- **Live dashboard** with 5 interactive charts
- **Web vitals collection** (TTFB, FCP, DOM Load, Page Load)
- **Performance metrics** and success/failure tracking
- **Export capabilities** for all data types

### 🔧 **Enterprise Configuration Management**
- **Preset system** for saving and loading configurations
- **Scheduling capabilities** for automated runs
- **Proxy support** for IP rotation
- **Network simulation** (3G, 4G, WiFi, Offline)

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Installation
```bash
git clone <repository-url>
cd traffic-power-tool
streamlit run app.py
```

### Basic Usage
1. **Configure Target URL** - Enter your website URL
2. **Set Session Parameters** - Define number of sessions and concurrency
3. **Choose Demographics** - Select countries, age groups, and devices
4. **Configure Personas** - Use built-in or create custom personas
5. **Start Simulation** - Monitor real-time progress and results

## 📋 Detailed Features

### 🌍 International Traffic Control

#### **Region Selection Modes**
1. **🌐 Random International** - Realistic global distribution
   - Uses accurate global traffic data
   - Supports 200+ countries with proportional weights
   - Random traffic from various countries

2. **🎯 Specific Countries** - Full control over target countries
   - Select specific countries from popular list
   - Adjust distribution weights for each country
   - Preview distribution before execution

3. **🇺🇸 Single Country** - Focus on specific region
   - All traffic from selected country
   - Ideal for local market testing

#### **Supported Countries**
**Popular Markets:**
- United States, Indonesia, India, China, Brazil
- United Kingdom, Germany, Japan, France, Canada
- Australia, Mexico, Spain, Italy, South Korea
- Russia, Netherlands, Turkey, Poland, Argentina

**Asian Markets:**
- Thailand, Vietnam, Malaysia, Singapore, Philippines
- Pakistan, Bangladesh, Sri Lanka, Nepal, Myanmar
- Laos, Cambodia, Brunei, Mongolia, Kazakhstan

**European Markets:**
- Austria, Switzerland, Belgium, Ireland, Portugal
- Sweden, Norway, Denmark, Finland, Iceland
- Poland, Czech Republic, Hungary, Romania, Bulgaria

**African Markets:**
- South Africa, Nigeria, Kenya, Egypt, Morocco
- Ghana, Ethiopia, Uganda, Tanzania, Zimbabwe

### 👥 Demographics Management

#### **Age Distribution Modes**
1. **📊 Standard Distribution** - Realistic global age distribution
   - 18-24 years: 20%
   - 25-34 years: 30%
   - 35-44 years: 25%
   - 45-54 years: 15%
   - 55+ years: 10%

2. **🎯 Custom Distribution** - Full control over age groups
   - Adjust percentages for each age group
   - Match your target audience demographics
   - Preview distribution before execution

3. **🎲 Random Age** - Uniform distribution
   - Random age from 18-75 years
   - Ideal for unbiased testing

#### **Gender & Device Control**
- **Gender distribution** with customizable ratios
- **Device targeting** (Desktop, Mobile, Tablet)
- **Returning visitor rate** control
- **Network type simulation**

### 🎭 Persona System

#### **Built-in Personas**
- **Methodical Customer** - Form-filling, price-conscious
- **Deep Researcher** - Content consumption, downloads
- **Performance Analyst** - Web vitals collection
- **Quick Browser** - Fast navigation, minimal interaction
- **Job Seeker** - Career-focused, application forms
- **Content Consumer** - Article reading, media consumption
- **Product Explorer** - E-commerce behavior
- **Social Media Marketer** - Sharing, engagement
- **Mobile Gamer** - Gaming-focused behavior
- **News Reader** - News consumption patterns
- **Tech Enthusiast** - Technology-focused browsing
- **E-commerce Shopper** - Shopping behavior
- **Educational Student** - Learning-focused patterns
- **Health Seeker** - Healthcare information seeking
- **Investment Researcher** - Financial research patterns
- **Food Enthusiast** - Food and restaurant browsing
- **Travel Planner** - Travel booking behavior
- **Real Estate Buyer** - Property research patterns

#### **Random Persona Generator**
- **5 Template types** for international personas
- **Country-specific** language preferences
- **Age-appropriate** behavior patterns
- **Customizable** generation parameters

### 📊 Analytics & Monitoring

#### **Real-time Dashboard**
- **5 Interactive Charts**: Persona, Device, Visitor Type, Country, Age
- **Live Progress Tracking** with ETR (Estimated Time Remaining)
- **Success/Failure Metrics** with detailed breakdowns
- **Web Vitals Performance** monitoring

#### **Export Capabilities**
- **CSV Export** for all data types
- **Per-country analytics** export
- **Per-age group** analytics export
- **Web vitals data** export
- **Session history** export

#### **Visualization Types**
- **Pie Charts** for distribution analysis
- **Bar Charts** for comparison views
- **Heatmaps** for interaction patterns
- **Time Series** for performance trends

### 🔧 Advanced Configuration

#### **Network Simulation**
- **Default** - Normal network conditions
- **3G** - Slow mobile network simulation
- **4G** - Fast mobile network simulation
- **WiFi Slow** - Slow WiFi simulation
- **Offline** - Offline mode testing

#### **Proxy Support**
- **Proxy file upload** (.txt format)
- **IP rotation** for realistic traffic
- **Geolocation matching** with proxy locations

#### **Scheduling**
- **Automated execution** at specific times
- **Background processing** support
- **Stop/Resume** capabilities

## 🛠️ Technical Architecture

### **Core Components**
- **TrafficGenerator** - Main simulation engine
- **PersonaManager** - Persona behavior simulation
- **FingerprintManager** - Browser fingerprinting
- **AnalyticsEngine** - Data collection and processing
- **ConfigurationManager** - Settings and preset management

### **Technologies Used**
- **Streamlit** - Web interface
- **Playwright** - Browser automation
- **Pandas** - Data processing
- **Plotly** - Data visualization
- **Asyncio** - Concurrent processing

### **Data Flow**
1. **Configuration** → User settings and persona definitions
2. **Generation** → Traffic simulation with realistic behavior
3. **Collection** → Data gathering from browser sessions
4. **Processing** → Analytics and metrics calculation
5. **Visualization** → Real-time dashboard updates
6. **Export** → Data export for external analysis

## 📈 Use Cases

### **E-commerce & Retail**
- **Market testing** across different countries
- **Demographic targeting** validation
- **Conversion rate** optimization
- **User experience** testing

### **SaaS & Technology**
- **Global user simulation** for product testing
- **Localization testing** for international markets
- **Performance monitoring** across regions
- **Accessibility testing** for different demographics

### **Content & Media**
- **Audience behavior** analysis
- **Content performance** testing
- **SEO optimization** across regions
- **Engagement pattern** analysis

### **Healthcare & Education**
- **Target audience** validation
- **Accessibility compliance** testing
- **Localization** for different markets
- **User experience** optimization

## 🔒 Privacy & Compliance

### **Data Protection**
- **No real user data** collection
- **Simulated traffic** only
- **GDPR compliant** data handling
- **CCPA compliant** privacy practices

### **Ethical Usage**
- **Testing purposes** only
- **No malicious intent** supported
- **Respectful of websites** being tested
- **Rate limiting** to prevent overload

## 📝 Configuration Examples

### **Basic Configuration**
```python
from src.core.config import TrafficConfig, Persona

config = TrafficConfig(
    project_root=Path("./"),
    target_url="https://example.com",
    total_sessions=100,
    max_concurrent=10,
    country_distribution={"United States": 50, "United Kingdom": 30, "Canada": 20},
    age_distribution={"18-24": 25, "25-34": 35, "35-44": 25, "45-54": 10, "55+": 5},
    device_distribution={"Desktop": 60, "Mobile": 30, "Tablet": 10}
)
```

### **Advanced Persona Configuration**
```python
from src.core.config import generate_random_personas

# Generate 10 random personas for specific countries
personas = generate_random_personas(
    count=10,
    countries=["United States", "United Kingdom", "Germany"]
)
```

### **Custom Persona Creation**
```python
persona = Persona(
    name="Custom Shopper",
    goal_keywords={"buy": 10, "purchase": 9, "checkout": 8},
    generic_keywords={"product": 6, "price": 5},
    navigation_depth=(3, 7),
    avg_time_per_page=(30, 90),
    can_fill_forms=True,
    goal={"type": "find_and_click", "target_text": "add to cart|buy now"}
)
```

## 🚀 Performance & Scalability

### **Concurrent Processing**
- **Configurable concurrency** (1-100 sessions)
- **Resource optimization** with semaphore control
- **Background processing** for UI responsiveness
- **Graceful shutdown** with task cancellation

### **Memory Management**
- **Efficient data structures** for large datasets
- **Streaming data processing** for real-time analytics
- **Cache management** for browser profiles
- **Garbage collection** optimization

### **Error Handling**
- **Comprehensive error catching** and logging
- **Retry mechanisms** for failed sessions
- **Graceful degradation** for partial failures
- **Detailed error reporting** for debugging

## 📊 Monitoring & Analytics

### **Real-time Metrics**
- **Session completion rate**
- **Success/failure ratios**
- **Average session duration**
- **Web vitals performance**
- **Geographic distribution**
- **Demographic breakdown**

### **Historical Data**
- **Session history** tracking
- **Performance trends** over time
- **Comparative analysis** between runs
- **Export capabilities** for external analysis

## 🔧 Maintenance & Support

### **Cache Management**
- **Profile cleanup** for old sessions
- **Temporary file** management
- **Storage optimization** recommendations
- **Automatic cleanup** utilities

### **Logging & Debugging**
- **Comprehensive logging** at all levels
- **Error tracking** with stack traces
- **Performance monitoring** logs
- **Debug mode** for troubleshooting

## 📚 Documentation & Resources

### **API Reference**
- **Configuration classes** documentation
- **Persona system** API reference
- **Analytics methods** documentation
- **Export functions** reference

### **Tutorials & Guides**
- **Getting started** tutorial
- **Advanced configuration** guide
- **Persona creation** tutorial
- **Analytics interpretation** guide

## 🤝 Contributing

### **Development Setup**
```bash
git clone <repository-url>
cd traffic-power-tool
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### **Code Standards**
- **PEP 8** compliance
- **Type hints** for all functions
- **Comprehensive testing** coverage
- **Documentation** for all public APIs

### **Testing**
```bash
pytest tests/
pytest tests/ --cov=src
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** for the excellent web framework
- **Playwright** for robust browser automation
- **Plotly** for beautiful data visualizations
- **Pandas** for powerful data processing

---

**Traffic Power Tool v2.0** - Enterprise-Grade Traffic Simulation & Analytics Platform 🌍📊

*Built with ❤️ for professional web analytics and testing* 