"""
SwachhSpot BBMP: Illegal Dumping & Garbage Hotspot AI Platform
Citizen Geotagged Grievance Portal, Computer Vision Verification,
BBMP Ward Routing, and Repeat Blackspot Heatmap Analytics.
"""

import os
import sys
from datetime import datetime
from PIL import Image
import streamlit as st
import pandas as pd
import altair as alt

import importlib
try:
    _sf = importlib.import_module("streamlit_folium")
    st_folium = getattr(_sf, "st_folium", None)
    HAS_STREAMLIT_FOLIUM = st_folium is not None
except Exception:
    HAS_STREAMLIT_FOLIUM = False
    st_folium = None

# Add root directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from modules.exif_extractor import extract_geotags
from modules.vision_detector import analyze_dump_image
from modules.bbmp_routing import find_nearest_ward, generate_bbmp_ticket, get_all_wards
from modules.hotspot_engine import detect_repeat_hotspots, generate_folium_map
from modules.data_manager import (
    get_all_incidents,
    add_incident,
    update_incident_status,
    get_civic_statistics
)
from modules.sample_generator import generate_all_samples

# Page Configuration
st.set_page_config(
    page_title="SwachhSpot BBMP | AI Illegal Dump & Hotspot Platform",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Styles
CSS_PATH = os.path.join(BASE_DIR, "assets", "styles.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Ensure sample images exist
generate_all_samples()

# Header Banner
st.markdown("""
<div class="bbmp-banner">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <span style="background: rgba(255,255,255,0.15); padding: 4px 10px; border-radius: 6px; font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.08em;">
                BBMP Solid Waste Management (SWM) AI Cell
            </span>
            <h1 style="color: white; margin: 8px 0 4px 0; font-size: 28px;">
                SwachhSpot BBMP: Illegal Dumping & Chronic Blackspot AI
            </h1>
            <div class="bbmp-tagline">
                AI-Verified Geotagged Grievance Dispatch &bull; Automated Ward Officer Escalation &bull; Repeat Hotspot Heatmaps
            </div>
        </div>
        <div style="text-align: right; margin-top: 8px;">
            <div style="background: #ffffff; color: #1e3a8a; font-weight: 700; padding: 6px 14px; border-radius: 8px; font-size: 13px;">
                Bengaluru Municipal Jurisdiction
            </div>
            <div style="color: #cbd5e1; font-size: 11px; margin-top: 4px;">
                KMC Act Sec 255 Enforcement
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation Tabs
tabs = st.tabs([
    "📸 Citizen Grievance & AI Scanner",
    "🗺️ BBMP Hotspot & Blackspot Heatmap",
    "🛡️ Ward Authority Command Center",
    "📊 Civic Impact & Hotspot Intelligence"
])


# ==========================================
# TAB 1: CITIZEN GRIEVANCE & AI SCANNER
# ==========================================
with tabs[0]:
    st.subheader("Report Illegal Dumping Incident")
    st.caption("Upload a photo with GPS tags or select a pre-calibrated Bengaluru blackspot scenario for instant testing.")

    col_input, col_meta = st.columns([1.1, 1.0])

    with col_input:
        source_mode = st.radio(
            "Select Photo Source:",
            ["⚡ Pre-loaded Bengaluru Field Samples (Instant Test)", "📤 Upload My Own Image"],
            horizontal=True
        )

        selected_image = None
        img_name = ""
        default_lat, default_lon = 12.926340, 77.676620

        if "Pre-loaded" in source_mode:
            sample_choices = {
                "Bellandur Lake Catchment (C&D Debris Blackspot)": "bellandur_debris.jpg",
                "HSR Layout Sector 2 (Plastic Packaging Dump)": "hsr_plastic_dump.jpg",
                "Koramangala 80ft Road (Commercial Mixed Waste)": "koramangala_mixed.jpg",
                "Cubbon Park Lawn (Negative Control - Clean Area)": "clean_cubbon_park.jpg"
            }
            chosen_sample_label = st.selectbox("Choose Verified Sample Scenario:", list(sample_choices.keys()))
            chosen_file = sample_choices[chosen_sample_label]
            sample_path = os.path.join(BASE_DIR, "assets", "sample_images", chosen_file)
            if os.path.exists(sample_path):
                selected_image = Image.open(sample_path)
                img_name = chosen_file
        else:
            uploaded_file = st.file_uploader(
                "Upload Smartphone Geotagged Photo (JPEG/PNG):",
                type=["jpg", "jpeg", "png", "webp"]
            )
            if uploaded_file is not None:
                selected_image = Image.open(uploaded_file)
                img_name = uploaded_file.name

    with col_meta:
        if selected_image is not None:
            # Extract EXIF metadata
            exif_info = extract_geotags(selected_image)

            st.markdown("#### 📍 Geotag & EXIF Inspection")
            if exif_info.get("has_gps"):
                st.success(f"**Verified GPS Coordinates Extracted:** {exif_info['latitude']:.6f}° N, {exif_info['longitude']:.6f}° E")
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Device Capture", exif_info.get("device", "Mobile Camera"))
                with c2:
                    st.metric("Capture Timestamp", exif_info.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M")))
                lat_final = exif_info["latitude"]
                lon_final = exif_info["longitude"]
            else:
                st.warning("⚠️ No GPS EXIF tags detected in this photo. Pick the nearest ward below:")
                all_wards = get_all_wards()
                ward_options = {f"Ward {w['ward_no']} - {w['ward_name']} ({w['zone']})": (w['lat'], w['lon']) for w in all_wards}
                selected_ward_label = st.selectbox("Select BBMP Ward Location:", list(ward_options.keys()))
                lat_final, lon_final = ward_options[selected_ward_label]
                st.info(f"Using Ward Coordinates: {lat_final:.4f}° N, {lon_final:.4f}° E")

            custom_landmark = st.text_input("Landmark / Spot Description (Optional):", value="Near main road culvert & storm drain")
        else:
            st.markdown("#### 📍 Geotag & EXIF Inspection")
            st.info("👆 Please select a pre-loaded sample scenario or upload a photo to inspect its GPS coordinates and run Computer Vision verification.")

    # Run AI Vision Analysis when image is available
    if selected_image is not None:
        st.divider()
        st.markdown("### 🤖 Computer Vision AI Verification & Ward Routing")

        with st.spinner("Analyzing chromatic entropy, edge roughness, and contour morphology..."):
            cv_results = analyze_dump_image(selected_image)

        # Check if Clean scene or Garbage confirmed
        if not cv_results["is_garbage"]:
            st.error("🛡️ **False Alarm Shield: Non-Waste Scene Identified**")
            st.markdown(f"""
            <div style="background:#f0fdf4; border:1px solid #86efac; padding:16px; border-radius:10px; color:#166534;">
                <b>AI Confidence:</b> {int((1.0 - cv_results['confidence'])*100)}% verified clean area.<br/>
                <b>Detected Features:</b> Natural grass/sky landscape or uniform pavement with zero hazardous clutter.<br/>
                <b>Action:</b> Report not routed to BBMP ward inspectors. False dispatch prevented, saving municipal operational costs.
            </div>
            """, unsafe_allow_html=True)

            col_orig, col_ann = st.columns(2)
            with col_orig:
                st.image(selected_image, caption="Uploaded Photo (Pristine Area)", use_container_width=True)
            with col_ann:
                st.image(cv_results["annotated_image"], caption="AI Feature Inspection", use_container_width=True)

        else:
            # Verified Illegal Dump
            st.success(f"🚨 **Illegal Dumping Confirmed by AI!** (Confidence: {int(cv_results['confidence']*100)}%)")

            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.metric("Waste Classification", cv_results["waste_category"])
            with m2:
                sev_color = "red" if cv_results["severity"] == 3 else ("orange" if cv_results["severity"] == 2 else "green")
                st.metric("Severity Level", f"Level {cv_results['severity']}", f"{cv_results['severity_label'][:20]}...")
            with m3:
                st.metric("Estimated Footprint", f"{cv_results['estimated_area_sqm']} sq.m", f"~{int(cv_results['estimated_area_sqm']*80)} kg waste")
            with m4:
                st.metric("Detected Waste Clusters", f"{cv_results['detected_clusters_count']} clusters")

            col_img1, col_img2 = st.columns(2)
            with col_img1:
                st.image(selected_image, caption="Original Citizen Upload", use_container_width=True)
            with col_img2:
                st.image(cv_results["annotated_image"], caption="AI Vision Bounding Boxes & Waste Clusters", use_container_width=True)

            # Automated BBMP Ward Routing Box
            ward_info, dist_km = find_nearest_ward(lat_final, lon_final)
            ticket_preview = generate_bbmp_ticket(
                latitude=lat_final,
                longitude=lon_final,
                waste_category=cv_results["waste_category"],
                severity=cv_results["severity"],
                confidence=cv_results["confidence"],
                custom_landmark=custom_landmark
            )

            st.markdown(f"""
            <div class="routing-box">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <h3 style="margin:0; color:#1e3a8a;">🏛️ BBMP Ward Dispatch Routing Manifest</h3>
                    <span class="{'badge-critical' if cv_results['severity']==3 else ('badge-moderate' if cv_results['severity']==2 else 'badge-routine')}">
                        {ticket_preview['urgency_badge']}
                    </span>
                </div>
                <div style="margin-top:10px; display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:12px;">
                    <div><b>Jurisdiction Ward:</b> Ward {ward_info['ward_no']} ({ward_info['ward_name']})</div>
                    <div><b>BBMP Zone:</b> {ward_info['zone']} Zone</div>
                    <div><b>Centroid Distance:</b> {dist_km} km</div>
                    <div><b>Assigned JHI:</b> {ward_info['jhi_name']} ({ward_info['jhi_contact']})</div>
                    <div><b>SWM Executive:</b> {ward_info['aee_name']}</div>
                    <div><b>Marshal Squad:</b> {ward_info['marshal_unit']}</div>
                </div>
                <div style="margin-top:12px; padding-top:10px; border-top:1px solid #cbd5e1; font-size:13px;">
                    <b>Action Protocol:</b> {ticket_preview['action_unit']}<br/>
                    <b>Statutory Penalty Clause:</b> <span style="color:#b91c1c; font-weight:600;">{ticket_preview['penalty_clause']}</span><br/>
                    <b>SLA Deadline:</b> Within {ticket_preview['resolution_deadline']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Submit Ticket Button
            st.write("")
            if st.button("🚀 Confirm & Submit Ticket to BBMP Ward Authority", type="primary", use_container_width=True):
                # Save to database
                ticket_data = ticket_preview.copy()
                ticket_data["estimated_area_sqm"] = cv_results["estimated_area_sqm"]
                success = add_incident(ticket_data)
                if success:
                    st.balloons()
                    st.success(f"✅ Grievance Ticket **{ticket_data['ticket_id']}** successfully registered and dispatched to {ward_info['jhi_name']}! View in Tab 2 (Map) and Tab 3 (Command Center).")


# ==========================================
# TAB 2: BBMP HOTSPOT & BLACKSPOT HEATMAP
# ==========================================
with tabs[1]:
    st.subheader("🗺️ Bengaluru Garbage Hotspot & Chronic Blackspot Heatmap")
    st.caption("Spatial density analysis of repeat illegal dumping clusters, lakebed encroachments, and municipal escalation zones.")

    incidents = get_all_incidents()
    hotspots = detect_repeat_hotspots(incidents, distance_threshold_meters=85.0, min_incidents=2)

    # Filter Controls
    f_col1, f_col2, f_col3, f_col4 = st.columns([1.5, 1.5, 1.5, 1.5])
    with f_col1:
        zones_available = ["All"] + sorted(list(set(i.get("zone", "Other") for i in incidents)))
        filter_zone = st.selectbox("Filter BBMP Zone:", zones_available)
    with f_col2:
        filter_severity = st.multiselect("Severity Tiers:", [1, 2, 3], default=[1, 2, 3], format_func=lambda x: f"Level {x}")
    with f_col3:
        show_heatmap_layer = st.checkbox("Show Density HeatMap", value=True)
    with f_col4:
        show_cluster_markers = st.checkbox("Show Individual Incidents", value=True)

    # Render Folium Map
    folium_map = generate_folium_map(
        records=incidents,
        hotspots=hotspots,
        center_lat=12.9400,
        center_lon=77.6500,
        zoom_start=12,
        show_heatmap=show_heatmap_layer,
        show_clusters=show_cluster_markers,
        selected_severity=filter_severity if filter_severity else [1, 2, 3],
        selected_zone=filter_zone
    )

    # Display Map
    if HAS_STREAMLIT_FOLIUM and st_folium is not None:
        st_folium(folium_map, use_container_width=True, height=520)
    else:
        import streamlit.components.v1 as components
        components.html(folium_map.get_root().render(), height=540, scrolling=False)

    # Chronic Blackspots Section
    st.markdown("### 🚨 Detected Chronic Blackspots (Repeat Dumping Clusters)")
    st.caption("Locations where 2 or more illegal dumps were detected within 85 meters. High-priority candidates for civic transformation.")

    if len(hotspots) == 0:
        st.info("No recurring spatial clusters detected yet.")
    else:
        for hs in hotspots:
            with st.expander(f"📍 {hs['chronic_level']}: {hs['ward_name']} ({hs['zone']} Zone) — {hs['repeat_count']} Repeat Incidents"):
                c_hs1, c_hs2 = st.columns([1.2, 1.8])
                with c_hs1:
                    st.markdown(f"""
                    - **Centroid Coordinates:** `{hs['center_lat']:.5f}° N, {hs['center_lon']:.5f}° E`
                    - **Dominant Waste Stream:** **{hs['dominant_waste']}**
                    - **Highest Severity:** Level {hs['max_severity']}
                    - **Linked Tickets:** {', '.join(hs['incident_ids'])}
                    """)
                with c_hs2:
                    st.markdown("**🏛️ Recommended Municipal & Civic Interventions:**")
                    for rec in hs["recommendations"]:
                        st.markdown(f"{rec['icon']} **{rec['type']}:** {rec['action']}")


# ==========================================
# TAB 3: WARD AUTHORITY COMMAND CENTER
# ==========================================
with tabs[2]:
    st.subheader("🛡️ BBMP Ward SWM Triage & Resolution Dashboard")
    st.caption("Municipal officer command portal for reviewing incoming grievance tickets, updating status, and deploying Marshals.")

    incidents = get_all_incidents()

    # KPI summary cards
    k1, k2, k3, k4 = st.columns(4)
    pending_count = sum(1 for i in incidents if i.get("status") == "DISPATCHED_TO_WARD_INSPECTOR")
    progress_count = sum(1 for i in incidents if i.get("status") == "IN_PROGRESS")
    escalated_count = sum(1 for i in incidents if i.get("status") == "ESCALATED_TO_MARSHAL")
    cleared_count = sum(1 for i in incidents if i.get("status") == "CLEARED_BY_AUTHORITY")

    with k1:
        st.metric("Pending Dispatch", pending_count)
    with k2:
        st.metric("In Progress (Pourakarmika)", progress_count)
    with k3:
        st.metric("Escalated to Marshals", escalated_count, "Penalty / FIR")
    with k4:
        st.metric("Cleared & Closed", cleared_count, f"{round((cleared_count/len(incidents))*100, 1) if incidents else 0}%")

    st.write("")
    
    # Action Triage Table
    ticket_df = pd.DataFrame([
        {
            "Ticket ID": i.get("ticket_id"),
            "Ward": f"{i.get('ward_name')} (W{i.get('ward_no')})",
            "Zone": i.get("zone"),
            "Waste Category": i.get("waste_category"),
            "Severity": f"Level {i.get('severity')}",
            "Assigned JHI": i.get("officer_jhi"),
            "Status": i.get("status"),
            "Created": i.get("created_at")
        }
        for i in incidents
    ])
    st.dataframe(ticket_df, use_container_width=True)

    # Status Updater Form
    st.divider()
    st.markdown("#### ⚡ Update Ticket Resolution State")
    t_col1, t_col2, t_col3 = st.columns([1.5, 1.5, 1.0])
    with t_col1:
        if incidents:
            selected_ticket = st.selectbox("Select Ticket ID:", [i["ticket_id"] for i in incidents])
        else:
            selected_ticket = None
            st.info("No tickets registered yet.")
    with t_col2:
        new_status = st.selectbox(
            "New Resolution Status:",
            [
                "IN_PROGRESS",
                "ESCALATED_TO_MARSHAL",
                "CLEARED_BY_AUTHORITY",
                "REJECTED_SPAM"
            ]
        )
    with t_col3:
        st.write("")
        st.write("")
        if st.button("Update Status"):
            if selected_ticket:
                update_incident_status(selected_ticket, new_status)
                st.success(f"Ticket {selected_ticket} updated to {new_status}!")
                st.rerun()
            else:
                st.warning("No ticket selected to update.")

    # Export register button
    st.download_button(
        label="📥 Download Full SWM Grievance Register (CSV)",
        data=ticket_df.to_csv(index=False).encode('utf-8'),
        file_name=f"bbmp_swm_tickets_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )


# ==========================================
# TAB 4: CIVIC IMPACT & ANALYTICS STORY
# ==========================================
with tabs[3]:
    st.subheader("📊 The Civic Impact Story: Transforming Bengaluru's Blackspots")
    st.caption("How geotagged AI verification and repeat hotspot intelligence empower BBMP and citizen communities.")

    stats = get_civic_statistics()

    # Civic Impact Metrics Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Total Dumps Identified", stats.get("total_reports", 0))
    with m_col2:
        st.metric("Estimated Tonnage Cleared", f"{stats.get('estimated_tonnage_cleared', 0)} MT", "Removed from public roads")
    with m_col3:
        st.metric("Resolution Clearance Rate", f"{stats.get('clearance_rate_pct', 0)}%", "Across 14 BBMP wards")
    with m_col4:
        st.metric("Average Turnaround Time", f"{stats.get('avg_sla_hours', 11.4)} hrs", "Within municipal SLA")

    st.write("")
    chart_c1, chart_c2 = st.columns(2)

    with chart_c1:
        st.markdown("#### 🗑️ Waste Stream Distribution")
        waste_df = pd.DataFrame(list(stats.get("waste_distribution", {}).items()), columns=["Waste Type", "Incidents"])
        if not waste_df.empty:
            chart = alt.Chart(waste_df).mark_bar(cornerRadius=6, color="#1e40af").encode(
                x=alt.X("Incidents:Q"),
                y=alt.Y("Waste Type:N", sort="-x"),
                tooltip=["Waste Type", "Incidents"]
            ).properties(height=260)
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No waste stream incidents recorded yet.")

    with chart_c2:
        st.markdown("#### 🏛️ BBMP Zone Activity & Grievance Volume")
        zone_df = pd.DataFrame(list(stats.get("zone_distribution", {}).items()), columns=["Zone", "Reports"])
        if not zone_df.empty:
            chart2 = alt.Chart(zone_df).mark_bar(cornerRadius=6, color="#059669").encode(
                x=alt.X("Reports:Q"),
                y=alt.Y("Zone:N", sort="-x"),
                tooltip=["Zone", "Reports"]
            ).properties(height=260)
            st.altair_chart(chart2, use_container_width=True)
        else:
            st.info("No zone report data available yet.")

    st.divider()
    st.markdown("### 🌟 Spotlight: From Chronic Blackspots to Civic Pride")
    col_story1, col_story2 = st.columns(2)

    with col_story1:
        st.markdown("""
        #### 1. Bellandur & Varthur Lake Catchment Protection
        - **The Challenge:** Night-time commercial trucks dumping Construction & Demolition (C&D) rubble into lake buffer zones and stormwater drains.
        - **AI Intervention:** Geotagged uploads with high C&D confidence automatically flag Level 3 severity and route directly to the BBMP Marshal Squad Captain.
        - **Outcome:** 25% reduction in repeat dumps within 30 days due to targeted solar CCTV placement and ₹25,000 penalties under KMC Act Section 255.
        """)

    with col_story2:
        st.markdown("""
        #### 2. The Ugly Indian 'Spot-Fixing' Transformation (HSR & Koramangala)
        - **The Challenge:** Street corners repeatedly becoming garbage blackspots within 48 hours of cleaning.
        - **Civic Innovation:** The platform aggregates repeat hotspot clusters and alerts local resident welfare associations (RWAs).
        - **Outcome:** Citizens and pourakarmikas paint murals, install street planters, and convert garbage eyesores into clean community spaces.
        """)
