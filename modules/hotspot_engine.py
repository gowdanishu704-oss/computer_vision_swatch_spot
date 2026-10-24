"""
Garbage Hotspot Analysis & Civic Impact Engine.
Calculates spatial recurrence, runs DBSCAN clustering to identify chronic blackspots,
and generates actionable civic impact intervention strategies for BBMP authorities.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.cluster import DBSCAN
import folium
from folium.plugins import HeatMap, MarkerCluster


def detect_repeat_hotspots(records: List[Dict[str, Any]], distance_threshold_meters: float = 80.0, min_incidents: int = 2) -> List[Dict[str, Any]]:
    """
    Identifies chronic blackspots using spatial clustering (DBSCAN).
    Groups incidents within `distance_threshold_meters` to find recurring dumping sites.
    """
    # Filter only records with valid numeric coordinates
    valid_records = [
        r for r in records
        if isinstance(r.get("latitude"), (int, float))
        and isinstance(r.get("longitude"), (int, float))
        and not (r.get("latitude") == 0 and r.get("longitude") == 0)
    ]

    if len(valid_records) < 2:
        return []

    # Earth radius in meters
    kms_per_radian = 6371.0088
    meters_per_radian = kms_per_radian * 1000.0
    epsilon = distance_threshold_meters / meters_per_radian

    coords = np.array([[math_rad(r["latitude"]), math_rad(r["longitude"])] for r in valid_records])

    db = DBSCAN(eps=epsilon, min_samples=min_incidents, metric='haversine')
    labels = db.fit_predict(coords)

    hotspots = []
    unique_labels = set(labels)
    unique_labels.discard(-1) # Discard noise points

    for cluster_id in unique_labels:
        cluster_indices = np.where(labels == cluster_id)[0]
        cluster_records = [valid_records[i] for i in cluster_indices]

        # Calculate cluster center
        avg_lat = float(np.mean([r["latitude"] for r in cluster_records]))
        avg_lon = float(np.mean([r["longitude"] for r in cluster_records]))

        # Common ward
        ward_names = [r.get("ward_name", "Unknown Ward") for r in cluster_records]
        dominant_ward = max(set(ward_names), key=ward_names.count)
        zones = [r.get("zone", "BBMP") for r in cluster_records]
        dominant_zone = max(set(zones), key=zones.count)

        # Waste types
        waste_types = [r.get("waste_category", "Mixed Waste") for r in cluster_records]
        dominant_waste = max(set(waste_types), key=waste_types.count)

        # Max severity
        max_severity = max([r.get("severity", 1) for r in cluster_records])

        # Civic impact recommendations
        recommendations = generate_civic_recommendations(
            repeat_count=len(cluster_records),
            dominant_waste=dominant_waste,
            severity=max_severity,
            ward_name=dominant_ward
        )

        hotspots.append({
            "cluster_id": int(cluster_id),
            "repeat_count": len(cluster_records),
            "center_lat": round(avg_lat, 6),
            "center_lon": round(avg_lon, 6),
            "ward_name": dominant_ward,
            "zone": dominant_zone,
            "dominant_waste": dominant_waste,
            "max_severity": max_severity,
            "incident_ids": [r.get("ticket_id") for r in cluster_records],
            "recommendations": recommendations,
            "chronic_level": "CHRONIC REPEAT OFFENDER" if len(cluster_records) >= 3 else "EMERGING HOTSPOT"
        })

    # Sort by repeat count descending
    hotspots.sort(key=lambda x: x["repeat_count"], reverse=True)
    return hotspots


def math_rad(degrees: float) -> float:
    return np.radians(degrees)


def generate_civic_recommendations(repeat_count: int, dominant_waste: str, severity: int, ward_name: str) -> List[Dict[str, str]]:
    """Generates concrete civic and municipal intervention protocols for repeat blackspots."""
    recs = []

    if "Construction" in dominant_waste:
        recs.append({
            "type": "CCTV & Enforcement",
            "icon": "📹",
            "action": "Deploy Solar AI-CCTV with automatic number plate recognition (ANPR) to capture night-time tipper trucks dumping C&D rubble."
        })
        recs.append({
            "type": "Legal Penalty",
            "icon": "⚖️",
            "action": "Invoke Section 255 of KMC Act: Vehicle impoundment and ₹25,000 fine on contractor/builder."
        })
    elif "Plastic" in dominant_waste:
        recs.append({
            "type": "Infrastructure",
            "icon": "♻️",
            "action": "Establish a decentralized Dry Waste Collection Centre (DWCC) kiosk and tie up with local scrap aggregator."
        })
        recs.append({
            "type": "Spot Transformation",
            "icon": "🎨",
            "action": "Launch Community 'Spot-Fixing' initiative (The Ugly Indian model): Clean, paint vibrant murals, and place planters to deter re-dumping."
        })
    else:
        recs.append({
            "type": "Beat Re-routing",
            "icon": "🧹",
            "action": "Reschedule BBMP Pourakarmika auto-tipper collection frequency to 2x daily (morning 7 AM & afternoon 2 PM)."
        })
        recs.append({
            "type": "Marshal Night Beat",
            "icon": "🚨",
            "action": "BBMP Marshal Squad night patrol checkpoint between 10 PM and 2 AM to stop commercial vendor dumping."
        })

    if repeat_count >= 3:
        recs.append({
            "type": "Permanent Deterrent",
            "icon": "🌳",
            "action": "Erect wire-mesh barricade along roadside shoulder with high-mast lighting and public warning signage."
        })

    return recs


def generate_folium_map(
    records: List[Dict[str, Any]],
    hotspots: List[Dict[str, Any]],
    center_lat: float = 12.9450,
    center_lon: float = 77.6500,
    zoom_start: int = 12,
    show_heatmap: bool = True,
    show_clusters: bool = True,
    selected_severity: List[int] = None,
    selected_zone: str = "All"
) -> folium.Map:
    """
    Renders an interactive Folium Map with HeatMap layer,
    severity-coded markers, and highlighted repeat chronic blackspot perimeters.
    """
    if selected_severity is None:
        selected_severity = [1, 2, 3]

    # Filter records
    filtered_records = []
    for r in records:
        if isinstance(r.get("latitude"), (int, float)) and isinstance(r.get("longitude"), (int, float)):
            if r.get("severity") in selected_severity:
                if selected_zone == "All" or r.get("zone") == selected_zone:
                    filtered_records.append(r)

    # Initialize map using open tiles
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles="OpenStreetMap",
        control_scale=True
    )

    # 1. HeatMap Layer
    if show_heatmap and len(filtered_records) > 0:
        heat_data = [
            [r["latitude"], r["longitude"], float(r.get("severity", 1)) * 1.5]
            for r in filtered_records
        ]
        HeatMap(
            heat_data,
            radius=22,
            blur=16,
            min_opacity=0.35,
            gradient={0.2: '#00c853', 0.5: '#ffd600', 0.8: '#ff6d00', 1.0: '#d50000'}
        ).add_to(m)

    # 2. Chronic Hotspot Perimeter Circles
    for hs in hotspots:
        folium.Circle(
            location=[hs["center_lat"], hs["center_lon"]],
            radius=110,
            color="#d50000" if hs["repeat_count"] >= 3 else "#ff6d00",
            fill=True,
            fill_color="#d50000" if hs["repeat_count"] >= 3 else "#ff6d00",
            fill_opacity=0.18,
            weight=2,
            dash_array="5, 5",
            popup=folium.Popup(
                f"""<div style='font-family:sans-serif; width:220px;'>
                    <b style='color:#d50000;'>🚨 {hs['chronic_level']}</b><br/>
                    <b>Ward:</b> {hs['ward_name']} ({hs['zone']} Zone)<br/>
                    <b>Repeat Dumps:</b> {hs['repeat_count']} incidents<br/>
                    <b>Dominant Waste:</b> {hs['dominant_waste']}<br/>
                    <b>Top Action:</b> {hs['recommendations'][0]['action'][:90]}...
                </div>""",
                max_width=250
            ),
            tooltip=f"Chronic Blackspot: {hs['ward_name']} ({hs['repeat_count']} dumps)"
        ).add_to(m)

    # 3. Incident Marker Cluster
    if show_clusters and len(filtered_records) > 0:
        marker_cluster = MarkerCluster(name="Reported Dumps").add_to(m)

        for r in filtered_records:
            sev = r.get("severity", 1)
            if sev == 3:
                icon_color = "red"
                icon_name = "fire"
            elif sev == 2:
                icon_color = "orange"
                icon_name = "warning"
            else:
                icon_color = "green"
                icon_name = "trash"

            popup_html = f"""
            <div style="font-family: 'Segoe UI', Arial, sans-serif; min-width: 200px; font-size: 13px;">
                <div style="font-weight: bold; color: #1e3a8a; font-size: 14px; border-bottom: 1px solid #e2e8f0; padding-bottom: 4px; margin-bottom: 6px;">
                    {r.get('ticket_id', 'TICKET')}
                </div>
                <div><b>Ward:</b> {r.get('ward_name', 'BBMP')} (Ward {r.get('ward_no', 'N/A')})</div>
                <div><b>Zone:</b> {r.get('zone', 'N/A')}</div>
                <div><b>Waste Type:</b> {r.get('waste_category', 'Mixed')}</div>
                <div><b>Severity:</b> Level {sev}</div>
                <div><b>AI Confidence:</b> {int(r.get('ai_confidence', 0.9)*100)}%</div>
                <div><b>Status:</b> <span style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-weight:600;">{r.get('status', 'PENDING')}</span></div>
                <div style="margin-top: 6px; font-size: 11px; color: #64748b;">Assigned JHI: {r.get('officer_jhi', 'Ward SWM Inspector')}</div>
            </div>
            """

            folium.Marker(
                location=[r["latitude"], r["longitude"]],
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"Ticket: {r.get('ticket_id')} | {r.get('ward_name')}",
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
            ).add_to(marker_cluster)

    return m
