# ♻️ SwachhSpot BBMP: Illegal Dumping & Garbage-Hotspot AI Platform

An intelligent civic technology system for Bruhat Bengaluru Mahanagara Palike (BBMP) that empowers citizens to upload geotagged photos of garbage dumps. The Computer Vision AI confirms illegal dumping, classifies waste categories, scores severity, and automatically routes enforcement tickets to the responsible BBMP Ward Inspector. Interactive geospatial heatmaps detect recurring blackspots to drive measurable civic impact and urban spot-fixing.

---

## 🌟 Key Features

1. **Citizen Upload & Geotag Extraction**:
   - Reads real EXIF GPS latitude and longitude metadata, device model, and capture timestamp from uploaded photos using `piexif` and `PIL`.
   - Automatic fallback to interactive BBMP ward selection if photo GPS tags were stripped by messaging platforms.
   - 4 pre-calibrated Bengaluru blackspot test scenarios for 1-click instant demonstration.

2. **Computer Vision AI Verification**:
   - **Illegal Dump vs Clean Scene**: Computes chromatic dispersion, edge entropy (Canny & Laplacian variance), and contour irregularity to reject false alarms (e.g. pristine parks or clean roads) and protect municipal resources.
   - **Waste Category Segregation**:
     - 🏗️ *Construction & Demolition (C&D) Debris* (Rubble, concrete, bricks)
     - 🛍️ *Plastic & Polymer Packaging* (Single-use polybags, PET bottles, multilayer plastics)
     - 🥗 *Organic & Perishable Wet Waste* (Market refuse, food waste sludge)
     - 📦 *Mixed Municipal Solid Waste (MSW)*
   - **Severity Scoring & Footprint Estimation**:
     - *Level 1 (Minor)*: < 2 sq.m (Pourakarmika daily beat sweep)
     - *Level 2 (Moderate)*: 2–10 sq.m roadside pile (Auto-tipper dispatch)
     - *Level 3 (Critical)*: > 10 sq.m or lakebed/stormwater drain obstruction (JCB heavy compactor + BBMP Marshal Squad dispatch)
   - **Visual Bounding Boxes & Segmentation Masks**: Highlights garbage clusters directly on the photo with confidence scores.

3. **BBMP Ward Officer Auto-Routing**:
   - Geo-spatial mapping across major Bengaluru wards (Bellandur, HSR Layout, Koramangala, Indiranagar, Domlur, Whitefield, Varthur, Hebbal, Jayanagar, Malleshwaram, etc.).
   - Computes centroid distance and dispatches tickets to the assigned **Junior Health Inspector (JHI)** and **SWM Assistant Executive Engineer**.
   - Generates unique ticket tracking IDs (e.g., `BBMP-SWM-2026-W150-8192`) and calculates statutory penalties under Section 255 of the Karnataka Municipal Corporations (KMC) Act.

4. **Chronic Blackspot Heatmaps & Civic Impact**:
   - Spatial density clustering (DBSCAN) identifies repeat dumping hotspots within 85-meter radii.
   - High-resolution Folium Heatmap with customizable zone and severity filters.
   - Generates targeted municipal intervention strategies:
     - 📹 Solar AI-CCTV surveillance at drain culverts
     - 🚨 BBMP Marshal night patrols
     - 🎨 Citizen "Spot-Fixing" and wall mural transformations (The Ugly Indian civic model)
     - ♻️ Decentralized Dry Waste Collection Centre (DWCC) kiosks

---

## 📁 Project Structure

```
c:\Users\gowda\OneDrive\Desktop\cv\
├── app.py                      # Streamlit application entrypoint
├── modules/
│   ├── __init__.py
│   ├── exif_extractor.py       # EXIF metadata parser & GPS rational-to-decimal converter
│   ├── vision_detector.py      # OpenCV computer vision pipeline, classifier & bounding box generator
│   ├── bbmp_routing.py         # BBMP wards database, centroid distance calculation & ticket dispatch
│   ├── hotspot_engine.py       # DBSCAN spatial clustering, chronic blackspot detection & Folium map
│   ├── data_manager.py         # Persistent incident store, pre-seeded BBMP blackspots & civic metrics
│   └── sample_generator.py     # Synthetic test scene generator with embedded EXIF GPS tags
├── assets/
│   ├── styles.css              # Custom styling & civic design system
│   └── sample_images/          # Pre-bundled geotagged test scenes (Bellandur, HSR, Koramangala, Cubbon Park)
├── data/
│   └── incidents.json          # Live persistent grievance records
└── README.md
```

---

## 🚀 How to Run

1. **Activate Environment & Dependencies**:
   ```bash
   pip install streamlit folium streamlit-folium piexif geopy opencv-python-headless scikit-learn matplotlib
   ```

2. **Launch the Dashboard**:
   ```bash
   streamlit run app.py
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:8501` to test citizen uploads, review the BBMP Hotspot Heatmap, and interact with the Ward Authority Command Center.
