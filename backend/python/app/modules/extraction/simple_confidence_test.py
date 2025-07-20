"""
Simple test to demonstrate confidence score utilization
"""

# Test confidence band calculation
def test_confidence_bands():
    print("Testing Confidence Band Classification")
    print("=" * 40)
    
    test_scores = [0.95, 0.85, 0.75, 0.60, 0.45, 0.25]
    
    for score in test_scores:
        if score >= 0.85:
            band = "HIGH"
            cache_ttl = 86400  # 24 hours
            processing = "auto_approve"
        elif score >= 0.6:
            band = "MEDIUM" 
            cache_ttl = 43200  # 12 hours
            processing = "standard_review"
        else:
            band = "LOW"
            cache_ttl = 3600   # 1 hour
            processing = "enhanced_review"
            
        print(f"Score: {score:.2f} -> Band: {band}, Cache: {cache_ttl/3600:.0f}h, Processing: {processing}")

def test_aviation_safety_override():
    print("\nTesting Aviation Safety Critical Override")
    print("=" * 40)
    
    safety_critical_docs = [
        {"score": 0.92, "safety": True, "expected": "auto_approve"},
        {"score": 0.75, "safety": True, "expected": "urgent_safety_review"}, 
        {"score": 0.45, "safety": True, "expected": "urgent_safety_review"},
        {"score": 0.75, "safety": False, "expected": "standard_review"}
    ]
    
    for doc in safety_critical_docs:
        score = doc["score"]
        is_safety = doc["safety"]
        
        # Normal confidence routing
        if score >= 0.85:
            processing = "auto_approve"
        elif score >= 0.6:
            processing = "standard_review"
        else:
            processing = "enhanced_review"
            
        # Safety critical override
        if is_safety and score < 0.8:
            processing = "urgent_safety_review"
            
        status = "CORRECT" if processing == doc["expected"] else "MISMATCH"
        print(f"Score: {score:.2f}, Safety: {is_safety}, Result: {processing} ({status})")

def test_review_requirements():
    print("\nTesting Review Requirements")
    print("=" * 40)
    
    documents = [
        {"score": 0.92, "safety": False},
        {"score": 0.75, "safety": False}, 
        {"score": 0.45, "safety": False},
        {"score": 0.75, "safety": True},
        {"score": 0.45, "safety": True}
    ]
    
    for doc in documents:
        score = doc["score"]
        is_safety = doc["safety"]
        
        # Determine review requirement
        if is_safety:
            requires_review = score < 0.8  # Higher threshold for safety
        else:
            requires_review = 0.6 <= score < 0.85  # Standard review range
            
        if score < 0.6:
            requires_review = True  # Always review low confidence
            
        auto_approve = score >= 0.85 and not (is_safety and score < 0.8)
        
        print(f"Score: {score:.2f}, Safety: {is_safety}")
        print(f"  -> Requires Review: {requires_review}")
        print(f"  -> Auto Approve: {auto_approve}")

def demonstrate_cache_strategy():
    print("\nDemonstrating Cache Strategy")
    print("=" * 40)
    
    # Simulate document processing with different confidence levels
    documents = [
        {"id": "high_conf_manual", "score": 0.92, "type": "Flight Manual"},
        {"id": "medium_maint", "score": 0.68, "type": "Maintenance Guide"},
        {"id": "low_emergency", "score": 0.42, "type": "Emergency Procedure"},
        {"id": "very_low_doc", "score": 0.18, "type": "Technical Doc"}
    ]
    
    total_cache_time = 0
    
    for doc in documents:
        score = doc["score"]
        
        # Calculate cache TTL based on confidence
        if score >= 0.85:
            cache_ttl = 86400  # 24 hours
        elif score >= 0.6:
            cache_ttl = 43200  # 12 hours
        else:
            cache_ttl = 3600   # 1 hour
            
        total_cache_time += cache_ttl
        
        print(f"{doc['id']}: {doc['type']}")
        print(f"  Confidence: {score:.2f}")
        print(f"  Cache TTL: {cache_ttl/3600:.0f} hours")
        print(f"  Cache until: +{cache_ttl} seconds")
        
    avg_cache_time = total_cache_time / len(documents) / 3600
    print(f"\nAverage cache time: {avg_cache_time:.1f} hours")
    print("High confidence documents cached 24x longer than low confidence!")

def main():
    print("Confidence Score Utilization Demonstration")
    print("=" * 50)
    
    test_confidence_bands()
    test_aviation_safety_override()
    test_review_requirements()
    demonstrate_cache_strategy()
    
    print("\nKey Benefits:")
    print("- Automatic routing based on confidence scores")
    print("- Safety-critical document special handling")
    print("- Performance optimization through confidence-based caching")
    print("- Quality monitoring without performance impact")
    print("- Smart review queue prioritization")

if __name__ == "__main__":
    main()