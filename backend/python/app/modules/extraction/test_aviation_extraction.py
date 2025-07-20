"""
Test script for aviation metadata extraction
"""

# Sample aviation content for testing
flight_ops_sample = """
EMERGENCY DESCENT PROCEDURE - B737-800

When cabin altitude cannot be controlled or excessive cabin differential pressure:

1. Don oxygen masks and set regulators to 100%
2. Establish crew communications
3. Immediately initiate emergency descent to 10,000 ft or MEA
4. Set transponder to 7700
5. PA announcement: "This is the Captain. Put on your oxygen masks"

Flight Phase: Cruise
System Affected: Pressurization System
Reference: QRH Section 2.4, AD 2023-19-02

This procedure is SAFETY CRITICAL and must be executed immediately upon recognition of uncontrollable cabin altitude.
"""

maintenance_sample = """
SERVICE BULLETIN 737-53A1219
Aircraft Type: B737-700/800/900
ATA Chapter: 53 - Fuselage

Subject: Fuselage Skin Inspection for Cracks

Compliance: Mandatory within 90 days per AD 2024-03-22

Required Tools:
- Borescope inspection equipment
- NDT ultrasonic testing equipment
- Torque wrench (50-75 in-lbs)

Components Involved:
- Fuselage skin panels (STA 360-540)
- Lap joint fasteners
- Doubler plates

Maintenance Type: Unscheduled inspection following AD release

Regulatory References:
- AD 2024-03-22
- SB 737-53A1219 Rev 2
- AMM 53-00-00

Safety Note: Any cracks found must be reported to engineering before flight.
"""

# Expected output structure for flight ops
expected_flight_ops = {
    "departments": ["Flight Operations", "Safety & Quality Assurance", "Emergency Response"],
    "category": "Flight Operations",
    "subcategories": {
        "level1": "Emergency Procedures",
        "level2": "Rapid Descent", 
        "level3": "Cabin Altitude Uncontrollable"
    },
    "sentiment": "Safety Critical",
    "topics": [
        "emergency descent",
        "cabin pressurization",
        "oxygen masks",
        "crew communication",
        "passenger announcement"
    ],
    "flight_operations_metadata": {
        "flight_phase": ["cruise"],
        "procedure_type": "Emergency",
        "checklist_section": "Emergency Descent",
        "systems_affected": ["Pressurization"]
    }
}

# Expected output structure for maintenance
expected_maintenance = {
    "departments": ["Aircraft Maintenance", "Regulatory Compliance", "Engineering & Technical Publications"],
    "category": "Aircraft Maintenance",
    "subcategories": {
        "level1": "Unscheduled Maintenance",
        "level2": "Fuselage Inspection",
        "level3": "Crack Detection"
    },
    "sentiment": "Regulatory",
    "topics": [
        "fuselage inspection",
        "AD compliance", 
        "NDT inspection",
        "crack detection",
        "lap joint inspection"
    ],
    "maintenance_metadata": {
        "aircraft_type": "B737",
        "ata_chapter": "53",
        "maintenance_type": "AD",
        "regulatory_references": ["AD 2024-03-22", "SB 737-53A1219 Rev 2", "AMM 53-00-00"],
        "components_involved": ["Fuselage skin panels", "Lap joint fasteners", "Doubler plates"],
        "tools_required": ["Borescope inspection equipment", "NDT ultrasonic testing equipment", "Torque wrench"]
    }
}

print("Aviation extraction test samples created successfully!")
print("\nFlight Operations Sample:")
print(flight_ops_sample)
print("\nExpected extraction includes:")
print(f"- Departments: {expected_flight_ops['departments']}")
print(f"- Category: {expected_flight_ops['category']}")
print(f"- Sentiment: {expected_flight_ops['sentiment']}")
print(f"- Flight Phase: {expected_flight_ops['flight_operations_metadata']['flight_phase']}")

print("\n" + "="*50 + "\n")

print("Maintenance Sample:")
print(maintenance_sample)
print("\nExpected extraction includes:")
print(f"- Departments: {expected_maintenance['departments']}")
print(f"- Category: {expected_maintenance['category']}")
print(f"- Aircraft Type: {expected_maintenance['maintenance_metadata']['aircraft_type']}")
print(f"- Regulatory Refs: {expected_maintenance['maintenance_metadata']['regulatory_references']}")