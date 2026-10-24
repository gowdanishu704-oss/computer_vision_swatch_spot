"""
BBMP (Bruhat Bengaluru Mahanagara Palike) Ward Mapping & Routing Engine.
Routes verified illegal dumping reports to designated BBMP Ward Health Inspectors,
Solid Waste Management (SWM) Executive Engineers, and BBMP Marshal Squads.
"""

import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple


# BBMP Wards database with real Bengaluru coordinates, zones, and officer rosters
BBMP_WARDS: List[Dict[str, Any]] = [
    {
        "ward_no": 150,
        "ward_name": "Bellandur",
        "zone": "Mahadevapura",
        "lat": 12.9260,
        "lon": 77.6762,
        "jhi_name": "R. Manjunath (JHI)",
        "jhi_contact": "+91 94806 85150",
        "aee_name": "AEE Suresh Babu (SWM-MHD)",
        "marshal_unit": "Squad-MHD-04 (Bellandur Lake Buffer Watch)",
        "hotspot_sensitivity": "HIGH - Lake Catchment Buffer Zone",
        "jurisdiction_office": "BBMP Ward 150 Office, Green Glen Layout, Bellandur"
    },
    {
        "ward_no": 174,
        "ward_name": "HSR Layout",
        "zone": "Bommanahalli",
        "lat": 12.9121,
        "lon": 77.6446,
        "jhi_name": "K. Venkatesh (JHI)",
        "jhi_contact": "+91 94806 85174",
        "aee_name": "AEE Raghavendra (SWM-BMH)",
        "marshal_unit": "Squad-BMH-02 (27th Main Commercial Corridor)",
        "hotspot_sensitivity": "MODERATE - Sector 1-7 Zero-Waste Target",
        "jurisdiction_office": "BBMP Ward 174 Office, 14th Main, HSR Sector 3"
    },
    {
        "ward_no": 151,
        "ward_name": "Koramangala",
        "zone": "South",
        "lat": 12.9352,
        "lon": 77.6245,
        "jhi_name": "S. Nagaraj (JHI)",
        "jhi_contact": "+91 94806 85151",
        "aee_name": "AEE Anand Kumar (SWM-S)",
        "marshal_unit": "Squad-STH-01 (80ft Road & National Games Village)",
        "hotspot_sensitivity": "HIGH - Commercial Dining & Night Dump Hotspot",
        "jurisdiction_office": "BBMP Ward 151 Office, 5th Block, Koramangala"
    },
    {
        "ward_no": 80,
        "ward_name": "Indiranagar (Hoysala Nagar)",
        "zone": "East",
        "lat": 12.9784,
        "lon": 77.6408,
        "jhi_name": "P. Ramesh (JHI)",
        "jhi_contact": "+91 94806 85080",
        "aee_name": "AEE Girish (SWM-E)",
        "marshal_unit": "Squad-EST-03 (100ft Road Night Surveillance)",
        "hotspot_sensitivity": "MODERATE - Beverage & Packaging Refuse",
        "jurisdiction_office": "BBMP Ward 80 Office, CMH Road, Indiranagar"
    },
    {
        "ward_no": 112,
        "ward_name": "Domlur",
        "zone": "East",
        "lat": 12.9609,
        "lon": 77.6387,
        "jhi_name": "M. Shivanna (JHI)",
        "jhi_contact": "+91 94806 85112",
        "aee_name": "AEE Girish (SWM-E)",
        "marshal_unit": "Squad-EST-05 (Old Airport Road Corridor)",
        "hotspot_sensitivity": "MODERATE - Intermediate Flyover Underpass Hotspot",
        "jurisdiction_office": "BBMP Ward 112 Office, Domlur BDA Complex"
    },
    {
        "ward_no": 85,
        "ward_name": "Doddanekkundi",
        "zone": "Mahadevapura",
        "lat": 12.9734,
        "lon": 77.6974,
        "jhi_name": "B. Prabhakar (JHI)",
        "jhi_contact": "+91 94806 85085",
        "aee_name": "AEE Suresh Babu (SWM-MHD)",
        "marshal_unit": "Squad-MHD-08 (Outer Ring Road Tech-Park Periphery)",
        "hotspot_sensitivity": "HIGH - C&D Truck Dumping Along ORR Service Road",
        "jurisdiction_office": "BBMP Ward 85 Office, Doddanekkundi Main Road"
    },
    {
        "ward_no": 84,
        "ward_name": "Hagadur / Whitefield",
        "zone": "Mahadevapura",
        "lat": 12.9698,
        "lon": 77.7499,
        "jhi_name": "N. Muniraju (JHI)",
        "jhi_contact": "+91 94806 85084",
        "aee_name": "AEE Suresh Babu (SWM-MHD)",
        "marshal_unit": "Squad-MHD-11 (Varthur-Whitefield Link)",
        "hotspot_sensitivity": "HIGH - Construction Debris & Vacant Plot Dumping",
        "jurisdiction_office": "BBMP Ward 84 Office, Inner Circle, Whitefield"
    },
    {
        "ward_no": 149,
        "ward_name": "Varthur",
        "zone": "Mahadevapura",
        "lat": 12.9406,
        "lon": 77.7471,
        "jhi_name": "T. Chandrashekhar (JHI)",
        "jhi_contact": "+91 94806 85149",
        "aee_name": "AEE Suresh Babu (SWM-MHD)",
        "marshal_unit": "Squad-MHD-06 (Varthur Lake Wetland Patrol)",
        "hotspot_sensitivity": "CRITICAL - Lake Inflow Wetland Protection",
        "jurisdiction_office": "BBMP Ward 149 Office, Varthur Police Station Road"
    },
    {
        "ward_no": 168,
        "ward_name": "Pattabhiram Nagar (Jayanagar)",
        "zone": "South",
        "lat": 12.9250,
        "lon": 77.5838,
        "jhi_name": "H. Puttaraju (JHI)",
        "jhi_contact": "+91 94806 85168",
        "aee_name": "AEE Anand Kumar (SWM-S)",
        "marshal_unit": "Squad-STH-04 (Jayanagar 4th Block Market)",
        "hotspot_sensitivity": "LOW - Pourakarmika High-Compliance Zone",
        "jurisdiction_office": "BBMP Ward 168 Office, 32nd Cross, 7th Block Jayanagar"
    },
    {
        "ward_no": 179,
        "ward_name": "Shakambari Nagar (JP Nagar)",
        "zone": "South",
        "lat": 12.9077,
        "lon": 77.5855,
        "jhi_name": "D. Somanna (JHI)",
        "jhi_contact": "+91 94806 85179",
        "aee_name": "AEE Anand Kumar (SWM-S)",
        "marshal_unit": "Squad-STH-07 (Sarakki Lake Perimeter)",
        "hotspot_sensitivity": "MODERATE - Secondary Drain Bund Blackspot",
        "jurisdiction_office": "BBMP Ward 179 Office, 24th Main, JP Nagar 1st Phase"
    },
    {
        "ward_no": 121,
        "ward_name": "Malleshwaram",
        "zone": "West",
        "lat": 13.0031,
        "lon": 77.5643,
        "jhi_name": "G. Krishnappa (JHI)",
        "jhi_contact": "+91 94806 85121",
        "aee_name": "AEE Ramakrishna (SWM-W)",
        "marshal_unit": "Squad-WST-02 (8th Cross & Margosa Road)",
        "hotspot_sensitivity": "LOW - Heritage Residential Ward",
        "jurisdiction_office": "BBMP Ward 121 Office, 15th Cross Malleshwaram"
    },
    {
        "ward_no": 132,
        "ward_name": "Attiguppe (Vijayanagar)",
        "zone": "West",
        "lat": 12.9647,
        "lon": 77.5349,
        "jhi_name": "R. Gangadhar (JHI)",
        "jhi_contact": "+91 94806 85132",
        "aee_name": "AEE Ramakrishna (SWM-W)",
        "marshal_unit": "Squad-WST-06 (Metro Corridor Sanitation Beat)",
        "hotspot_sensitivity": "MODERATE - Storm Drain Culvert Dumping",
        "jurisdiction_office": "BBMP Ward 132 Office, Chord Road, Attiguppe"
    },
    {
        "ward_no": 18,
        "ward_name": "Radhakrishna Temple (Hebbal)",
        "zone": "Yelahanka",
        "lat": 13.0358,
        "lon": 77.5970,
        "jhi_name": "K. Govindappa (JHI)",
        "jhi_contact": "+91 94806 85018",
        "aee_name": "AEE Mohan Reddy (SWM-YLH)",
        "marshal_unit": "Squad-YLH-01 (Hebbal Flyover & Lake Junction)",
        "hotspot_sensitivity": "HIGH - Highway Transit Flyover Underpass",
        "jurisdiction_office": "BBMP Ward 18 Office, Geddalahalli, Sanjaynagar"
    },
    {
        "ward_no": 4,
        "ward_name": "Yelahanka Satellite Town",
        "zone": "Yelahanka",
        "lat": 13.1007,
        "lon": 77.5963,
        "jhi_name": "C. Srinivas (JHI)",
        "jhi_contact": "+91 94806 85004",
        "aee_name": "AEE Mohan Reddy (SWM-YLH)",
        "marshal_unit": "Squad-YLH-05 (Allalasandra Lake Sector)",
        "hotspot_sensitivity": "MODERATE - Industrial & Bulk Waste Periphery",
        "jurisdiction_office": "BBMP Ward 4 Office, Sector A, Yelahanka New Town"
    }
]


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in km."""
    R = 6371.0 # Earth's radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def find_nearest_ward(latitude: float, longitude: float) -> Tuple[Dict[str, Any], float]:
    """
    Finds the nearest BBMP ward to the given coordinates.
    Returns (ward_dict, distance_in_km).
    """
    best_ward = BBMP_WARDS[0]
    min_dist = float('inf')

    for ward in BBMP_WARDS:
        dist = haversine_distance_km(latitude, longitude, ward["lat"], ward["lon"])
        if dist < min_dist:
            min_dist = dist
            best_ward = ward

    return best_ward, round(min_dist, 2)


def generate_bbmp_ticket(
    latitude: float,
    longitude: float,
    waste_category: str,
    severity: int,
    confidence: float,
    custom_landmark: str = ""
) -> Dict[str, Any]:
    """
    Generates an official BBMP SWM Grievance & Enforcement Ticket.
    Assigns officers, determines SLA based on severity, and establishes action orders.
    """
    ward, dist_km = find_nearest_ward(latitude, longitude)
    
    # Generate unique ticket ID: e.g. BBMP-SWM-2026-W150-7492
    random_code = random.randint(1000, 9999)
    ticket_id = f"BBMP-SWM-2026-W{ward['ward_no']}-{random_code}"

    # SLA and escalation tier based on severity
    if severity >= 3:
        sla_hours = 4
        action_unit = "EMERGENCY: BBMP Marshal Squad + JCB/Heavy Compactor Deployment"
        penalty_applicable = "₹10,000 to ₹25,000 fine under KMC Act Section 255 (Bulk Dumping)"
        urgency_badge = "CRITICAL (4-Hour SLA)"
    elif severity == 2:
        sla_hours = 12
        action_unit = "Auto-Tipper + Pourakarmika Gang Leader Intervention"
        penalty_applicable = "₹2,000 fine for chronic commercial littering"
        urgency_badge = "MODERATE (12-Hour SLA)"
    else:
        sla_hours = 24
        action_unit = "Daily Beat Pourakarmika Sweep & Desilting"
        penalty_applicable = "₹500 public littering penalty / warning notice"
        urgency_badge = "ROUTINE (24-Hour SLA)"

    now = datetime.now()
    deadline = now + timedelta(hours=sla_hours)

    return {
        "ticket_id": ticket_id,
        "ward_no": ward["ward_no"],
        "ward_name": ward["ward_name"],
        "zone": ward["zone"],
        "distance_to_centroid_km": dist_km,
        "officer_jhi": ward["jhi_name"],
        "officer_jhi_contact": ward["jhi_contact"],
        "officer_aee": ward["aee_name"],
        "marshal_squad": ward["marshal_unit"],
        "jurisdiction_office": ward["jurisdiction_office"],
        "hotspot_sensitivity": ward["hotspot_sensitivity"],
        "latitude": latitude,
        "longitude": longitude,
        "landmark": custom_landmark or f"Near {ward['ward_name']} Sector Corridor",
        "waste_category": waste_category,
        "severity": severity,
        "ai_confidence": confidence,
        "action_unit": action_unit,
        "penalty_clause": penalty_applicable,
        "urgency_badge": urgency_badge,
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "resolution_deadline": deadline.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "DISPATCHED_TO_WARD_INSPECTOR"
    }


def get_all_wards() -> List[Dict[str, Any]]:
    """Return all configured BBMP wards."""
    return BBMP_WARDS
