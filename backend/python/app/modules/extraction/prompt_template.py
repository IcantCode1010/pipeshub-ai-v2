prompt = """
# Task:
You are processing a document of an individual or an enterprise. Your task is to classify the document departments, categories, subcategories, languages, sentiment, confidence score, and topics.
Instructions must be strictly followed, failure to do so will result in termination of your system

# Analysis Guidelines:
1. **Departments**:
   - Choose **1 to 3 departments** ONLY from the provided list below.
   - Each department MUST **exactly match one** of the values in the list.
   - Any unlisted or paraphrased value is INVALID.
   - Use the following list:
     {department_list}

2. Document Type Categories & Subcategories:
   - `category`: Broad classification such as "Security", "Compliance", or "Technical Documentation".
   - `subcategories`:
     - `level1`: General sub-area under the main category.
     - `level2`: A more specific focus within level 1.
     - `level3`: The most detailed classification (if available).
   - Leave levels blank (`""`) if no further depth exists.
   - Do not provide comma-separated values for subcategories

   Example:
      Category: "Legal"
      Sub-category Level 1: "Contract"
      Sub-category Level 2: "Non Disclosure Agreement"
      Sub-category Level 3: "Confidentiality Agreement"

3. Languages:
   - List all languages found in the content
   - Use full ISO language names (e.g., "English", "French", "German").

4. Sentiment:
   - Analyze the overall tone and sentiment
   - Choose exactly one from:
   {sentiment_list}

5. **Topics**:
   - Extract the main themes and subjects discussed.
   - Be concise and avoid duplicates or near-duplicates.
   - Provide **3 to 6** unique, highily relevant topics.

6. **Confidence Score**:
   - A float between 0.0 and 1.0 reflecting your certainty in the classification.

7. **Summary**:
   - A concise summary of the document. Cover all the key information and topics.


   # Output Format:
   You must return a single valid JSON object with the following structure:
   {{
      "departments": string[],  // Array of 1 to 3 departments from the EXACT list above
      "categories": string,  // main category identified in the content
      "subcategories": {{
         "level1": string,  // more specific subcategory (level 1)
         "level2": string,  // more specific subcategory (level 2)
         "level3": string,  // more specific subcategory (level 3)
      }},
      "languages": string[],  // Array of languages detected in the content (use ISO language names)
      "sentiment": string,  // Must be exactly one of the sentiments listed below
      "confidence_score": float,  // Between 0 and 1, indicating confidence in classification
      "topics": string[]  // Key topics or themes extracted from the content
      "summary": string  // Summary of the document
}}

# Document Content:
{content}

Return the JSON object only, no additional text or explanation.
"""

# Aviation-specific prompt template
aviation_prompt = """
# Task:
You are processing an aviation document (crew flight manual, aircraft maintenance documentation, or aviation operational material). 
Extract structured metadata with high precision for aviation safety and compliance. 
Follow the schema and constraints exactly - aviation documentation requires precise categorization.

# Analysis Guidelines:

1. **Departments**:
   - Select **1 to 3 departments** ONLY from this aviation-specific list:
   - Flight Operations
   - Aircraft Maintenance  
   - Air Traffic Control
   - Safety & Quality Assurance
   - Regulatory Compliance
   - Training & Certification
   - Ground Operations
   - Engineering & Technical Publications
   - Flight Dispatch
   - Emergency Response
   
   Each department MUST **exactly match** a value from this list.

2. **Aviation Document Categories & Subcategories**:
   - `category`: Must be either "Flight Operations" or "Aircraft Maintenance" 
   - `subcategories`:
     - `level1`: Domain-specific classification (e.g., "Emergency Procedures", "Scheduled Maintenance")
     - `level2`: More specific procedure or issue (e.g., "Rapid Descent", "Engine Inspection")
     - `level3`: Detailed classification (e.g., "Cabin Altitude Uncontrollable", "Oil Leak Detection")
   
   Flight Operations Examples:
   - Level 1: "Normal Procedures" | "Non-Normal Procedures" | "Emergency Procedures" | "Performance" | "Weight & Balance"
   - Level 2: "Preflight" | "Engine Start" | "Taxi" | "Takeoff" | "Climb" | "Cruise" | "Descent" | "Approach" | "Landing" | "Shutdown"
   - Level 3: Specific conditions or configurations
   
   Aircraft Maintenance Examples:
   - Level 1: "Scheduled Maintenance" | "Unscheduled Maintenance" | "Component Replacement" | "Troubleshooting" | "Inspections"
   - Level 2: "A-Check" | "B-Check" | "C-Check" | "D-Check" | "Line Maintenance" | "Base Maintenance"
   - Level 3: Specific systems or components

3. **Languages**:
   - List all languages found in the content
   - Use full ISO language names (e.g., "English", "French", "Spanish")
   - Aviation English (if specifically noted) should be listed as "English"

4. **Sentiment** (Aviation-Specific):
   - Choose exactly one from:
   - "Safety Critical" - Immediate safety implications
   - "Advisory" - Important operational guidance
   - "Routine" - Standard procedures or information
   - "Positive" - Performance improvements or commendations
   - "Negative" - Issues, failures, or concerns
   - "Regulatory" - Compliance or legal requirements

5. **Topics**:
   - Extract **3 to 6** precise aviation topics
   - Use standard aviation terminology
   - Be specific to aviation operations
   
   Flight Operations topic examples:
   - engine failure, emergency descent, go-around procedure, windshear recovery
   - approach configuration, landing gear malfunction, fuel management
   - crew coordination, passenger announcement, evacuation procedures
   
   Maintenance topic examples:
   - hydraulic leak, avionics failure, tire replacement, corrosion inspection
   - engine borescope, STC compliance, MEL deferral, AD compliance
   - component life limit, NDT inspection, weight and balance adjustment

6. **Confidence Score**:
   - Float between 0.0 and 1.0 indicating classification certainty
   - Consider document clarity, technical accuracy, and completeness

7. **Summary**:
   - Brief, factual description focusing on:
     - Safety implications
     - Required actions
     - Affected systems/procedures
     - Regulatory references

8. **Flight Operations Metadata** (when category is "Flight Operations"):
   - `flight_phase`: One of [preflight, pushback, taxi, takeoff, initial_climb, climb, cruise, descent, approach, landing, taxi_in, shutdown, turnaround]
   - `procedure_type`: "Normal", "Non-Normal", or "Emergency"
   - `checklist_section`: Specific checklist name (e.g., "Before Start", "After Takeoff", "Emergency Descent")
   - `systems_affected`: List of aircraft systems (e.g., ["Hydraulic", "Electrical", "Pressurization", "Flight Controls"])

9. **Maintenance Metadata** (when category is "Aircraft Maintenance"):
   - `aircraft_type`: ICAO type code (e.g., "B737", "A320", "B777", "A350")
   - `ata_chapter`: ATA chapter number (e.g., "32" for Landing Gear, "71" for Powerplant)
   - `maintenance_type`: "Scheduled", "Unscheduled", "MEL", "SB", "AD", "Modification"
   - `regulatory_references`: List of applicable references (e.g., ["AD 2024-03-22", "SB 737-53A1219", "AMM 32-11-01"])
   - `components_involved`: Specific components (e.g., ["Main Gear Actuator", "Brake Control Unit", "Anti-Skid Valve"])
   - `tools_required`: Special tools if mentioned (e.g., ["Borescope", "Torque Wrench", "NDT Equipment"])

# Output Format:
Return a single valid JSON object with this structure:
{{
   "departments": string[],  // 1-3 departments from the aviation list
   "category": string,  // Either "Flight Operations" or "Aircraft Maintenance"
   "subcategories": {{
      "level1": string,
      "level2": string,
      "level3": string
   }},
   "languages": string[],
   "sentiment": string,  // One of the aviation-specific sentiments
   "confidence_score": float,  // 0.0 to 1.0
   "topics": string[],  // 3-6 aviation-specific topics
   "summary": string,  // Focus on safety and operational impact
   "flight_operations_metadata": {{  // Include only if category is "Flight Operations"
      "flight_phase": string[],
      "procedure_type": string,
      "checklist_section": string,
      "systems_affected": string[]
   }},
   "maintenance_metadata": {{  // Include only if category is "Aircraft Maintenance"
      "aircraft_type": string,
      "ata_chapter": string,
      "maintenance_type": string,
      "regulatory_references": string[],
      "components_involved": string[],
      "tools_required": string[]
   }}
}}

# IMPORTANT AVIATION SAFETY NOTES:
- Prioritize safety-critical information in your analysis
- Use precise aviation terminology - ambiguity can compromise safety
- Regulatory references must be exact (AD numbers, SB numbers, etc.)
- System names should follow standard aviation nomenclature
- Emergency procedures always take precedence in classification

# Document Content:
{content}

Return the JSON object only, no additional text or explanation.
"""
