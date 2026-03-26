# FlexoFind — Technician Proximity Finder

> **Find the right technician, closest to your customer, in seconds.**

![FlexoFind Logo](Logo.jpeg)

**Live Demo:** https://emehub-flexofind-webapp.streamlit.app

---

## What Is FlexoFind?

Imagine you run a service company. A customer calls and says their **phone screen is cracked** and they need someone to fix it **today**. You have 15 technicians scattered across the city. Which one do you send?

Without a tool like FlexoFind, you'd be calling each technician one by one, asking where they are, checking who's free — wasting precious time while your customer waits.

**FlexoFind solves this.** You type in the customer's address, select the service they need, and the system instantly shows you every available technician ranked from the **closest to the farthest** — so you can dispatch the right person in under a minute.

---

## Real-World Use Case

**Scenario:** A customer in Osu, Accra calls your company needing a plumber urgently. A pipe has burst.

1. You open FlexoFind on your computer or phone.
2. You type **"Osu, Accra"** in the location field.
3. You select **Plumbing Services** from the filter.
4. FlexoFind instantly shows you all available plumbers, sorted by how far each one is from Osu — with exact distances in kilometres.
5. You call the closest available one and dispatch them immediately.

No guessing. No wasted calls. Faster response for your customer.

---

## Services Covered

FlexoFind currently supports dispatching technicians for the following services:

| Service | Description |
|---|---|
| 📱 Phone Repairs | Cracked screens, battery replacements, software issues |
| 💻 Laptop Repairs | Hardware faults, screen replacements, virus removal |
| 🔧 Plumbing Services | Burst pipes, leaks, installations, drainage issues |
| 🚗 Mechanic Services | Vehicle breakdowns, servicing, fault diagnosis |
| 🪚 Carpentry Works | Furniture repairs, installations, woodwork |

---

## Key Features

### 🗺️ Location-Based Search
Type any address (street, area, city) and FlexoFind converts it to map coordinates automatically using the **Nominatim geocoder** — the same technology behind OpenStreetMap. You don't need to know GPS coordinates; plain language addresses work perfectly.

### 📏 Distance Ranking
Every technician is ranked by their real-world distance from the customer's location using the **geodesic formula** — which accounts for the curvature of the Earth, giving accurate distances even across long ranges.

### ✅ Live Availability Filter
Each technician has one of three statuses:
- **Available** — Ready to take a job right now
- **On-Site** — Currently working at another location
- **Off-Duty** — Not working at this time

You can filter by status so you only see technicians who can actually respond.

### 🏆 Closest Technician Highlight
The single closest available technician is always highlighted at the top of the results with their name, phone number, specialty, and distance — so you can make a dispatch decision instantly.

### ➕ Add New Technicians
A built-in form lets you register new technicians directly in the app. Enter their name, phone, specialty, and either their address or GPS coordinates. They are saved immediately to the database.

### ❌ Remove Technicians
You can also remove technicians who have left the company, with a confirmation step to prevent accidental deletions.

### 🎨 Dark & Light Mode
The dashboard supports both a dark theme (easy on the eyes at night) and a light theme — switchable from the sidebar.

### 📍 Max Distance Filter
A slider lets you set the maximum radius (in kilometres) you want to search within — useful when you only want to show technicians who can realistically reach a customer quickly.

---

## How It Works — Step by Step

```
Customer calls in with a request
        ↓
Admin opens FlexoFind
        ↓
Enters customer address → app converts to GPS coordinates
        ↓
Selects service type and availability filter
        ↓
App calculates distance from each technician to the customer
        ↓
Results displayed from closest → farthest
        ↓
Admin calls the closest available technician and dispatches
```

---

## Project Structure

```
flexofind_webapp/
│
├── app.py               ← The entire application (UI + logic)
├── technicians.csv      ← The technician database (name, phone, location, status)
├── requirements.txt     ← Python packages needed to run the app
├── Logo.jpeg            ← FlexoFind brand logo
└── .streamlit/
    └── config.toml      ← Streamlit server configuration
```

### technicians.csv — The Database

This CSV file acts as the app's database. Each row represents one technician:

| Column | Description |
|---|---|
| Tech_ID | Unique ID e.g. `TECH-001` |
| Name | Full name of the technician |
| Phone | Contact number |
| Specialty | Service they provide |
| Latitude | GPS latitude of their location |
| Longitude | GPS longitude of their location |
| Status | Available / On-Site / Off-Duty |

---

## Tech Stack

| Technology | Purpose |
|---|---|
| [Python](https://python.org) | Programming language |
| [Streamlit](https://streamlit.io) | Web app framework — turns Python scripts into interactive web dashboards |
| [Pandas](https://pandas.pydata.org) | Reading and filtering the technician data |
| [Geopy](https://geopy.readthedocs.io) | Converting addresses to GPS coordinates + calculating distances |
| [Nominatim](https://nominatim.org) | Free address geocoding (OpenStreetMap) |

---

## Running Locally

### Requirements
- Python 3.8 or higher
- Internet connection (for address geocoding)

### Setup

```powershell
# 1. Clone the repository
git clone https://github.com/Emehub/flexofind_webapp.git
cd flexofind_webapp

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
python -m streamlit run app.py
```

Then open your browser at **http://localhost:8501**

---

## Deployment

The app is deployed on **Streamlit Community Cloud** (free hosting for Streamlit apps).

To redeploy after making changes:

```powershell
git add .
git commit -m "describe your changes"
git push
```

Streamlit Cloud automatically detects the push and redeploys within seconds.

---

## Future Improvements

- 🔐 Admin login / password protection
- 📲 WhatsApp or SMS notification to the dispatched technician
- 🗺️ Interactive map showing all technician pins
- 📊 Analytics dashboard (jobs completed, response times)
- 📱 Mobile-optimised layout
- 🔄 Real-time technician location updates via mobile app

---

## About

FlexoFind was built to help service businesses in Ghana and across Africa dispatch field technicians faster and smarter — reducing response times and improving customer satisfaction.

Built with ❤️ using Python and Streamlit.
