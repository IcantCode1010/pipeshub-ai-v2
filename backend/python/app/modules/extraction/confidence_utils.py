"""
Confidence-based utilities for caching, storage, and quality monitoring
"""

import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
from collections import defaultdict


class ReviewPriority(Enum):
    URGENT = "URGENT"      # Safety critical with low confidence
    HIGH = "HIGH"          # Low confidence general
    MEDIUM = "MEDIUM"      # Medium confidence requiring review
    LOW = "LOW"            # High confidence spot checks


@dataclass
class ConfidenceMetrics:
    """Metrics for confidence-based quality monitoring"""
    total_documents: int = 0
    high_confidence_count: int = 0
    medium_confidence_count: int = 0
    low_confidence_count: int = 0
    avg_confidence: float = 0.0
    safety_critical_low_confidence: int = 0
    documents_requiring_review: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ReviewQueueItem:
    """Item for human review queue"""
    document_id: str
    org_id: str
    confidence_score: float
    confidence_band: str
    priority: ReviewPriority
    reason: str
    timestamp: float
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ConfidenceCache:
    """Simple in-memory cache with confidence-based TTL"""
    
    def __init__(self):
        self._cache: Dict[str, Dict] = {}
        self._timestamps: Dict[str, float] = {}
        
    def set(self, key: str, value: Any, ttl: int):
        """Set cache item with TTL"""
        current_time = time.time()
        self._cache[key] = {
            'value': value,
            'expires_at': current_time + ttl
        }
        self._timestamps[key] = current_time
        
    def get(self, key: str) -> Optional[Any]:
        """Get cache item if not expired"""
        if key not in self._cache:
            return None
            
        item = self._cache[key]
        if time.time() > item['expires_at']:
            # Expired
            del self._cache[key]
            del self._timestamps[key]
            return None
            
        return item['value']
        
    def delete(self, key: str):
        """Delete cache item"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        
    def clear_expired(self):
        """Clear all expired items"""
        current_time = time.time()
        expired_keys = [
            key for key, item in self._cache.items()
            if current_time > item['expires_at']
        ]
        for key in expired_keys:
            self.delete(key)
            
    def stats(self) -> Dict:
        """Get cache statistics"""
        current_time = time.time()
        total_items = len(self._cache)
        expired_items = sum(
            1 for item in self._cache.values()
            if current_time > item['expires_at']
        )
        return {
            'total_items': total_items,
            'active_items': total_items - expired_items,
            'expired_items': expired_items
        }


class ConfidenceQualityMonitor:
    """Monitor extraction quality based on confidence scores"""
    
    def __init__(self):
        self.metrics = ConfidenceMetrics()
        self.review_queue: List[ReviewQueueItem] = []
        self.confidence_history: List[float] = []
        
    def record_extraction(self, confidence_score: float, metadata: Dict, 
                         requires_review: bool = False, 
                         is_safety_critical_low: bool = False):
        """Record extraction result for quality monitoring"""
        self.metrics.total_documents += 1
        self.confidence_history.append(confidence_score)
        
        # Update confidence band counts
        if confidence_score >= 0.85:
            self.metrics.high_confidence_count += 1
        elif confidence_score >= 0.6:
            self.metrics.medium_confidence_count += 1
        else:
            self.metrics.low_confidence_count += 1
            
        # Update safety critical tracking
        if is_safety_critical_low:
            self.metrics.safety_critical_low_confidence += 1
            
        # Update review tracking
        if requires_review:
            self.metrics.documents_requiring_review += 1
            
        # Calculate running average
        self.metrics.avg_confidence = sum(self.confidence_history) / len(self.confidence_history)
        
        # Add to review queue if needed
        if requires_review or is_safety_critical_low:
            self._add_to_review_queue(confidence_score, metadata, is_safety_critical_low)
            
    def _add_to_review_queue(self, confidence_score: float, metadata: Dict, 
                           is_safety_critical_low: bool):
        """Add item to review queue with appropriate priority"""
        if is_safety_critical_low:
            priority = ReviewPriority.URGENT
            reason = "Safety critical document with low confidence"
        elif confidence_score < 0.3:
            priority = ReviewPriority.HIGH
            reason = "Very low confidence extraction"
        elif confidence_score < 0.6:
            priority = ReviewPriority.HIGH  
            reason = "Low confidence extraction"
        else:
            priority = ReviewPriority.MEDIUM
            reason = "Medium confidence requiring review"
            
        review_item = ReviewQueueItem(
            document_id=metadata.get('document_id', 'unknown'),
            org_id=metadata.get('org_id', 'unknown'),
            confidence_score=confidence_score,
            confidence_band=metadata.get('confidence_band', 'UNKNOWN'),
            priority=priority,
            reason=reason,
            timestamp=time.time(),
            metadata=metadata
        )
        
        self.review_queue.append(review_item)
        
        # Sort queue by priority (URGENT first)
        priority_order = {
            ReviewPriority.URGENT: 0,
            ReviewPriority.HIGH: 1,
            ReviewPriority.MEDIUM: 2,
            ReviewPriority.LOW: 3
        }
        self.review_queue.sort(key=lambda x: priority_order[x.priority])
        
    def get_review_queue(self, limit: int = 50) -> List[Dict]:
        """Get items from review queue"""
        return [item.to_dict() for item in self.review_queue[:limit]]
        
    def get_metrics(self) -> Dict:
        """Get current quality metrics"""
        return self.metrics.to_dict()
        
    def get_confidence_trend(self, window: int = 100) -> Dict:
        """Get confidence trend over recent extractions"""
        recent_scores = self.confidence_history[-window:] if self.confidence_history else []
        if not recent_scores:
            return {'trend': 'no_data', 'recent_avg': 0.0, 'sample_size': 0}
            
        recent_avg = sum(recent_scores) / len(recent_scores)
        
        # Simple trend calculation
        if len(recent_scores) >= 10:
            first_half = recent_scores[:len(recent_scores)//2]
            second_half = recent_scores[len(recent_scores)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg + 0.05:
                trend = 'improving'
            elif second_avg < first_avg - 0.05:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
            
        return {
            'trend': trend,
            'recent_avg': recent_avg,
            'sample_size': len(recent_scores)
        }


class ConfidenceBasedRouter:
    """Route documents based on confidence scores"""
    
    def __init__(self, cache: ConfidenceCache, monitor: ConfidenceQualityMonitor):
        self.cache = cache
        self.monitor = monitor
        
    async def route_document(self, document_id: str, metadata: Dict) -> Dict[str, Any]:
        """Route document based on confidence score and return routing decision"""
        confidence_score = metadata.get('confidence_score', 0.0)
        confidence_band = metadata.get('confidence_band', 'LOW')
        requires_review = metadata.get('requires_review', False)
        is_safety_critical_low = metadata.get('safety_critical_low_confidence', False)
        cache_ttl = metadata.get('cache_ttl', 3600)
        
        # Record for quality monitoring
        self.monitor.record_extraction(
            confidence_score, metadata, requires_review, is_safety_critical_low
        )
        
        # Determine processing path
        if confidence_score >= 0.85:
            processing_path = "auto_approve"
            next_action = "index_immediately"
        elif confidence_score >= 0.6:
            processing_path = "standard_review"
            next_action = "queue_for_review"
        elif confidence_score >= 0.3:
            processing_path = "enhanced_review"
            next_action = "queue_for_detailed_review"
        else:
            processing_path = "manual_validation"
            next_action = "queue_for_manual_processing"
            
        # Safety critical override
        if is_safety_critical_low:
            processing_path = "urgent_safety_review"
            next_action = "immediate_safety_review"
            
        # Cache the document with confidence-based TTL
        cache_key = f"document:{document_id}"
        self.cache.set(cache_key, metadata, cache_ttl)
        
        routing_decision = {
            'document_id': document_id,
            'confidence_score': confidence_score,
            'confidence_band': confidence_band,
            'processing_path': processing_path,
            'next_action': next_action,
            'cache_ttl': cache_ttl,
            'requires_review': requires_review,
            'is_safety_critical_low': is_safety_critical_low,
            'timestamp': time.time()
        }
        
        return routing_decision


# Global instances (would be properly injected in production)
confidence_cache = ConfidenceCache()
quality_monitor = ConfidenceQualityMonitor()
document_router = ConfidenceBasedRouter(confidence_cache, quality_monitor)


# Utility functions for easy access
def get_cache_stats() -> Dict:
    """Get cache statistics"""
    return confidence_cache.stats()


def get_quality_metrics() -> Dict:
    """Get quality monitoring metrics"""
    return quality_monitor.get_metrics()


def get_review_queue(limit: int = 50) -> List[Dict]:
    """Get review queue items"""
    return quality_monitor.get_review_queue(limit)


def get_confidence_trend(window: int = 100) -> Dict:
    """Get confidence trend"""
    return quality_monitor.get_confidence_trend(window)


async def route_document_by_confidence(document_id: str, metadata: Dict) -> Dict:
    """Route document based on confidence"""
    return await document_router.route_document(document_id, metadata)