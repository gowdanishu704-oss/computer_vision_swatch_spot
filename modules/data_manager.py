"""
Data Persistence and Civic Statistics Manager.
Maintains historical dumping logs, pre-seeded BBMP blackspots,
ticket lifecycle states, and civic impact metrics.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
DATA_FILE = os.path.join(DATA_DIR, "incidents.json")


# Realistic historical incidents across Bengaluru BBMP wards
# Formatted to create realistic hotspot clusters (e.g. multiple dumps around Bellandur Lake, HSR, Koramangala)
SEED_INCIDENTS: List[Dict[str, Any]] = [
    # Bellandur Cluster (Chronic Blackspot 1 - Lake Catchment C&D & Plastic)
    {
        "ticket_id": "BBMP-SWM-2026-W150-8192",
        "ward_no": 150,
        "ward_name": "Bellandur",
        "zone": "Mahadevapura",
        "latitude": 12.9265,
        "longitude": 77.6768,
        "landmark": "Near Bellandur Lake Bed & Green Glen Road",
        "waste_category": "Construction & Demolition (C&D) Debris",
        "severity": 3,
        "ai_confidence": 0.96,
        "action_unit": "EMERGENCY: BBMP Marshal Squad + JCB/Heavy Compactor Deployment",
        "penalty_clause": "₹25,000 fine under KMC Act Section 255",
        "urgency_badge": "CRITICAL (4-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=2) + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "DISPATCHED_TO_WARD_INSPECTOR",
        "officer_jhi": "R. Manjunath (JHI)",
        "officer_jhi_contact": "+91 94806 85150",
        "estimated_area_sqm": 16.5
    },
    {
        "ticket_id": "BBMP-SWM-2026-W150-8401",
        "ward_no": 150,
        "ward_name": "Bellandur",
        "zone": "Mahadevapura",
        "latitude": 12.9268,
        "longitude": 77.6772,
        "landmark": "Green Glen Layout Periphery Culvert",
        "waste_category": "Plastic & Polymer Packaging (Single-Use Plastic)",
        "severity": 3,
        "ai_confidence": 0.94,
        "action_unit": "EMERGENCY: BBMP Marshal Squad + JCB/Heavy Compactor Deployment",
        "penalty_clause": "₹25,000 fine under KMC Act Section 255",
        "urgency_badge": "CRITICAL (4-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=5) + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "IN_PROGRESS",
        "officer_jhi": "R. Manjunath (JHI)",
        "officer_jhi_contact": "+91 94806 85150",
        "estimated_area_sqm": 14.0
    },
    {
        "ticket_id": "BBMP-SWM-2026-W150-7193",
        "ward_no": 150,
        "ward_name": "Bellandur",
        "zone": "Mahadevapura",
        "latitude": 12.9262,
        "longitude": 77.6760,
        "landmark": "Outer Ring Road Underpass Access Lane",
        "waste_category": "Mixed Municipal Solid Waste (MSW)",
        "severity": 2,
        "ai_confidence": 0.91,
        "action_unit": "Auto-Tipper + Pourakarmika Gang Leader Intervention",
        "penalty_clause": "₹2,000 fine for chronic commercial littering",
        "urgency_badge": "MODERATE (12-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=7) + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CLEARED_BY_AUTHORITY",
        "officer_jhi": "R. Manjunath (JHI)",
        "officer_jhi_contact": "+91 94806 85150",
        "estimated_area_sqm": 7.2
    },

    # HSR Layout Cluster (Chronic Blackspot 2 - Sector 2 commercial dump)
    {
        "ticket_id": "BBMP-SWM-2026-W174-3201",
        "ward_no": 174,
        "ward_name": "HSR Layout",
        "zone": "Bommanahalli",
        "latitude": 12.9125,
        "longitude": 77.6449,
        "landmark": "27th Main Commercial Corner, Sector 2",
        "waste_category": "Plastic & Polymer Packaging (Single-Use Plastic)",
        "severity": 2,
        "ai_confidence": 0.93,
        "action_unit": "Auto-Tipper + Pourakarmika Gang Leader Intervention",
        "penalty_clause": "₹2,000 fine for chronic commercial littering",
        "urgency_badge": "MODERATE (12-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=1) + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "DISPATCHED_TO_WARD_INSPECTOR",
        "officer_jhi": "K. Venkatesh (JHI)",
        "officer_jhi_contact": "+91 94806 85174",
        "estimated_area_sqm": 6.8
    },
    {
        "ticket_id": "BBMP-SWM-2026-W174-3215",
        "ward_no": 174,
        "ward_name": "HSR Layout",
        "zone": "Bommanahalli",
        "latitude": 12.9128,
        "longitude": 77.6452,
        "landmark": "27th Main Service Lane Drain Culvert",
        "waste_category": "Organic / Perishable Wet Waste",
        "severity": 2,
        "ai_confidence": 0.89,
        "action_unit": "Auto-Tipper + Pourakarmika Gang Leader Intervention",
        "penalty_clause": "₹2,000 fine for chronic commercial littering",
        "urgency_badge": "MODERATE (12-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=4) + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CLEARED_BY_AUTHORITY",
        "officer_jhi": "K. Venkatesh (JHI)",
        "officer_jhi_contact": "+91 94806 85174",
        "estimated_area_sqm": 5.4
    },
    {
        "ticket_id": "BBMP-SWM-2026-W174-3290",
        "ward_no": 174,
        "ward_name": "HSR Layout",
        "zone": "Bommanahalli",
        "latitude": 12.9122,
        "longitude": 77.6444,
        "landmark": "HSR Sector 3 Park Boundary Wall",
        "waste_category": "Mixed Municipal Solid Waste (MSW)",
        "severity": 1,
        "ai_confidence": 0.87,
        "action_unit": "Daily Beat Pourakarmika Sweep & Desilting",
        "penalty_clause": "₹500 public littering penalty",
        "urgency_badge": "ROUTINE (24-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=3) + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CLEARED_BY_AUTHORITY",
        "officer_jhi": "K. Venkatesh (JHI)",
        "officer_jhi_contact": "+91 94806 85174",
        "estimated_area_sqm": 1.9
    },

    # Koramangala Cluster (Chronic Blackspot 3 - 80ft Road)
    {
        "ticket_id": "BBMP-SWM-2026-W151-5102",
        "ward_no": 151,
        "ward_name": "Koramangala",
        "zone": "South",
        "latitude": 12.9355,
        "longitude": 77.6248,
        "landmark": "80ft Road, 4th Block Market Corner",
        "waste_category": "Plastic & Polymer Packaging (Single-Use Plastic)",
        "severity": 3,
        "ai_confidence": 0.95,
        "action_unit": "EMERGENCY: BBMP Marshal Squad + JCB/Heavy Compactor Deployment",
        "penalty_clause": "₹15,000 fine under KMC Act Section 255",
        "urgency_badge": "CRITICAL (4-Hour SLA)",
        "created_at": (datetime.now() - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "DISPATCHED_TO_WARD_INSPECTOR",
        "officer_jhi": "S. Nagaraj (JHI)",
        "officer_jhi_contact": "+91 94806 85151",
        "estimated_area_sqm": 11.8
    },
    {
        "ticket_id": "BBMP-SWM-2026-W151-5129",
        "ward_no": 151,
        "ward_name": "Koramangala",
        "zone": "South",
        "latitude": 12.9358,
        "longitude": 77.6251,
        "landmark": "NGV Complex Rear Storm Drain Edge",
        "waste_category": "Organic / Perishable Wet Waste",
        "severity": 2,
        "ai_confidence": 0.92,
        "action_unit": "Auto-Tipper + Pourakarmika Gang Leader Intervention",
        "penalty_clause": "₹2,000 fine for chronic commercial littering",
        "urgency_badge": "MODERATE (12-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=2) + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "IN_PROGRESS",
        "officer_jhi": "S. Nagaraj (JHI)",
        "officer_jhi_contact": "+91 94806 85151",
        "estimated_area_sqm": 8.0
    },

    # Whitefield & Varthur C&D Debris Dumps
    {
        "ticket_id": "BBMP-SWM-2026-W149-9022",
        "ward_no": 149,
        "ward_name": "Varthur",
        "zone": "Mahadevapura",
        "latitude": 12.9410,
        "longitude": 77.7475,
        "landmark": "Varthur Kodi Wetland Buffer Boundary",
        "waste_category": "Construction & Demolition (C&D) Debris",
        "severity": 3,
        "ai_confidence": 0.97,
        "action_unit": "EMERGENCY: BBMP Marshal Squad + JCB/Heavy Compactor Deployment",
        "penalty_clause": "₹25,000 fine under KMC Act Section 255",
        "urgency_badge": "CRITICAL (4-Hour SLA)",
        "created_at": (datetime.now() - timedelta(hours=6)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "ESCALATED_TO_MARSHAL",
        "officer_jhi": "T. Chandrashekhar (JHI)",
        "officer_jhi_contact": "+91 94806 85149",
        "estimated_area_sqm": 22.0
    },
    {
        "ticket_id": "BBMP-SWM-2026-W84-4109",
        "ward_no": 84,
        "ward_name": "Hagadur / Whitefield",
        "zone": "Mahadevapura",
        "latitude": 12.9702,
        "longitude": 77.7505,
        "landmark": "Whitefield Railway Station Backroad",
        "waste_category": "Construction & Demolition (C&D) Debris",
        "severity": 2,
        "ai_confidence": 0.91,
        "action_unit": "Auto-Tipper + Pourakarmika Gang Leader Intervention",
        "penalty_clause": "₹2,000 fine for chronic commercial littering",
        "urgency_badge": "MODERATE (12-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=3) + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "CLEARED_BY_AUTHORITY",
        "officer_jhi": "N. Muniraju (JHI)",
        "officer_jhi_contact": "+91 94806 85084",
        "estimated_area_sqm": 7.5
    },

    # Indiranagar & Domlur
    {
        "ticket_id": "BBMP-SWM-2026-W80-2011",
        "ward_no": 80,
        "ward_name": "Indiranagar (Hoysala Nagar)",
        "zone": "East",
        "latitude": 12.9788,
        "longitude": 77.6412,
        "landmark": "100ft Road Metro Pillar 124 Footpath",
        "waste_category": "Plastic & Polymer Packaging (Single-Use Plastic)",
        "severity": 2,
        "ai_confidence": 0.90,
        "action_unit": "Auto-Tipper + Pourakarmika Gang Leader Intervention",
        "penalty_clause": "₹2,000 fine for chronic commercial littering",
        "urgency_badge": "MODERATE (12-Hour SLA)",
        "created_at": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(days=1) + timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "DISPATCHED_TO_WARD_INSPECTOR",
        "officer_jhi": "P. Ramesh (JHI)",
        "officer_jhi_contact": "+91 94806 85080",
        "estimated_area_sqm": 4.5
    },

    # Hebbal Flyover
    {
        "ticket_id": "BBMP-SWM-2026-W18-1055",
        "ward_no": 18,
        "ward_name": "Radhakrishna Temple (Hebbal)",
        "zone": "Yelahanka",
        "latitude": 13.0362,
        "longitude": 77.5975,
        "landmark": "Hebbal Flyover Loop Underpass Service Lane",
        "waste_category": "Mixed Municipal Solid Waste (MSW)",
        "severity": 3,
        "ai_confidence": 0.94,
        "action_unit": "EMERGENCY: BBMP Marshal Squad + JCB/Heavy Compactor Deployment",
        "penalty_clause": "₹15,000 fine under KMC Act Section 255",
        "urgency_badge": "CRITICAL (4-Hour SLA)",
        "created_at": (datetime.now() - timedelta(hours=18)).strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": (datetime.now() - timedelta(hours=14)).strftime("%Y-%m-%d %H:%M:%S"),
        "status": "ESCALATED_TO_MARSHAL",
        "officer_jhi": "K. Govindappa (JHI)",
        "officer_jhi_contact": "+91 94806 85018",
        "estimated_area_sqm": 15.0
    }
]


def init_storage():
    """Initializes JSON data storage with seed records if not already created."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(SEED_INCIDENTS, f, indent=2)


def get_all_incidents() -> List[Dict[str, Any]]:
    """Retrieves all registered dumping incidents."""
    init_storage()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return SEED_INCIDENTS


def add_incident(incident: Dict[str, Any]) -> bool:
    """Appends a newly verified citizen report to the database."""
    init_storage()
    incidents = get_all_incidents()
    incidents.insert(0, incident) # Insert newest first
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(incidents, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving incident: {e}")
        return False


def update_incident_status(ticket_id: str, new_status: str, notes: str = "") -> bool:
    """Updates the resolution lifecycle status of a ticket."""
    init_storage()
    incidents = get_all_incidents()
    updated = False
    for inc in incidents:
        if inc.get("ticket_id") == ticket_id:
            inc["status"] = new_status
            inc["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if notes:
                inc["authority_notes"] = notes
            updated = True
            break
    if updated:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(incidents, f, indent=2)
    return updated


def get_civic_statistics() -> Dict[str, Any]:
    """Computes high-impact civic metrics across all BBMP wards."""
    incidents = get_all_incidents()
    total = len(incidents)
    if total == 0:
        return {}

    cleared = sum(1 for i in incidents if i.get("status") == "CLEARED_BY_AUTHORITY")
    in_progress = sum(1 for i in incidents if i.get("status") in ["IN_PROGRESS", "DISPATCHED_TO_WARD_INSPECTOR"])
    escalated = sum(1 for i in incidents if i.get("status") == "ESCALATED_TO_MARSHAL")

    total_sqm = sum(i.get("estimated_area_sqm", 5.0) for i in incidents)
    # Estimated waste mass: ~80 kg per sq.m of mixed dump
    estimated_metric_tons = round((total_sqm * 80) / 1000.0, 1)

    # Waste breakdown
    waste_counts = {}
    for i in incidents:
        cat = i.get("waste_category", "Mixed")
        waste_counts[cat] = waste_counts.get(cat, 0) + 1

    # Zone breakdown
    zone_counts = {}
    for i in incidents:
        z = i.get("zone", "Other")
        zone_counts[z] = zone_counts.get(z, 0) + 1

    # Resolution rate
    clearance_rate = round((cleared / total) * 100, 1)

    return {
        "total_reports": total,
        "cleared_reports": cleared,
        "in_progress_reports": in_progress,
        "escalated_to_marshal": escalated,
        "clearance_rate_pct": clearance_rate,
        "total_waste_area_sqm": round(total_sqm, 1),
        "estimated_tonnage_cleared": estimated_metric_tons,
        "waste_distribution": waste_counts,
        "zone_distribution": zone_counts,
        "avg_sla_hours": 11.4
    }
