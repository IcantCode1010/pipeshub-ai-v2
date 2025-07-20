"""
API endpoints for confidence-based quality monitoring
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from pydantic import BaseModel

from app.modules.extraction.confidence_utils import (
    get_cache_stats,
    get_quality_metrics, 
    get_review_queue,
    get_confidence_trend,
    quality_monitor
)

router = APIRouter(prefix="/confidence", tags=["confidence"])


class ConfidenceStatsResponse(BaseModel):
    cache_stats: Dict
    quality_metrics: Dict
    confidence_trend: Dict


class ReviewQueueResponse(BaseModel):
    items: List[Dict]
    total_count: int
    pending_urgent: int
    pending_high: int


@router.get("/stats", response_model=ConfidenceStatsResponse)
async def get_confidence_stats():
    """Get overall confidence statistics"""
    try:
        cache_stats = get_cache_stats()
        quality_metrics = get_quality_metrics()
        confidence_trend = get_confidence_trend()
        
        return ConfidenceStatsResponse(
            cache_stats=cache_stats,
            quality_metrics=quality_metrics,
            confidence_trend=confidence_trend
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving stats: {str(e)}")


@router.get("/review-queue", response_model=ReviewQueueResponse)
async def get_review_queue_endpoint(
    limit: int = Query(50, ge=1, le=200),
    priority: Optional[str] = Query(None, regex="^(URGENT|HIGH|MEDIUM|LOW)$")
):
    """Get documents in review queue"""
    try:
        all_items = get_review_queue(limit * 2)  # Get more to filter if needed
        
        # Filter by priority if specified
        if priority:
            filtered_items = [item for item in all_items if item['priority'] == priority]
            items = filtered_items[:limit]
        else:
            items = all_items[:limit]
        
        # Count by priority
        urgent_count = sum(1 for item in all_items if item['priority'] == 'URGENT')
        high_count = sum(1 for item in all_items if item['priority'] == 'HIGH')
        
        return ReviewQueueResponse(
            items=items,
            total_count=len(all_items),
            pending_urgent=urgent_count,
            pending_high=high_count
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving review queue: {str(e)}")


@router.get("/metrics/summary")
async def get_metrics_summary():
    """Get summarized confidence metrics for dashboard"""
    try:
        metrics = get_quality_metrics()
        trend = get_confidence_trend(window=50)
        
        # Calculate percentages
        total = metrics['total_documents']
        if total > 0:
            high_percent = (metrics['high_confidence_count'] / total) * 100
            review_percent = (metrics['documents_requiring_review'] / total) * 100
        else:
            high_percent = 0
            review_percent = 0
            
        summary = {
            'total_documents': total,
            'average_confidence': round(metrics['avg_confidence'], 3),
            'high_confidence_percentage': round(high_percent, 1),
            'documents_requiring_review': metrics['documents_requiring_review'],
            'review_percentage': round(review_percent, 1),
            'safety_critical_low_confidence': metrics['safety_critical_low_confidence'],
            'confidence_trend': trend['trend'],
            'recent_avg_confidence': round(trend['recent_avg'], 3)
        }
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving summary: {str(e)}")


@router.get("/alerts")
async def get_confidence_alerts():
    """Get confidence-based alerts and warnings"""
    try:
        metrics = get_quality_metrics()
        trend = get_confidence_trend()
        review_queue = get_review_queue(10)
        
        alerts = []
        
        # Check for declining confidence trend
        if trend['trend'] == 'declining':
            alerts.append({
                'type': 'warning',
                'message': f"Confidence trend is declining. Recent average: {trend['recent_avg']:.3f}",
                'action': 'Review extraction quality and model performance'
            })
            
        # Check for high volume of safety critical low confidence
        if metrics['safety_critical_low_confidence'] > 5:
            alerts.append({
                'type': 'critical',
                'message': f"{metrics['safety_critical_low_confidence']} safety critical documents with low confidence",
                'action': 'Immediate review of safety critical extractions required'
            })
            
        # Check for urgent review queue items
        urgent_items = [item for item in review_queue if item['priority'] == 'URGENT']
        if urgent_items:
            alerts.append({
                'type': 'urgent',
                'message': f"{len(urgent_items)} urgent items in review queue",
                'action': 'Process urgent review items immediately'
            })
            
        # Check for low overall confidence
        if metrics['avg_confidence'] < 0.7 and metrics['total_documents'] > 10:
            alerts.append({
                'type': 'warning',
                'message': f"Overall confidence is low: {metrics['avg_confidence']:.3f}",
                'action': 'Consider retraining or adjusting extraction parameters'
            })
            
        return {
            'alerts': alerts,
            'alert_count': len(alerts),
            'last_updated': quality_monitor.metrics.total_documents  # Use as simple timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving alerts: {str(e)}")


@router.post("/review-queue/{document_id}/resolve")
async def resolve_review_item(document_id: str, resolution: str):
    """Mark a review queue item as resolved"""
    try:
        # Find and remove item from review queue
        queue_items = quality_monitor.review_queue
        original_length = len(queue_items)
        
        quality_monitor.review_queue = [
            item for item in queue_items 
            if item.document_id != document_id
        ]
        
        removed_count = original_length - len(quality_monitor.review_queue)
        
        if removed_count > 0:
            return {
                'success': True,
                'message': f'Resolved review item for document {document_id}',
                'resolution': resolution
            }
        else:
            raise HTTPException(status_code=404, detail=f"Document {document_id} not found in review queue")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resolving review item: {str(e)}")


# Health check endpoint
@router.get("/health")
async def confidence_health_check():
    """Health check for confidence monitoring system"""
    try:
        cache_stats = get_cache_stats()
        metrics = get_quality_metrics()
        
        # Simple health indicators
        health_status = "healthy"
        issues = []
        
        if metrics['avg_confidence'] < 0.5:
            health_status = "degraded"
            issues.append("Low average confidence")
            
        if cache_stats['expired_items'] > cache_stats['active_items']:
            health_status = "degraded"
            issues.append("High cache expiration rate")
            
        return {
            'status': health_status,
            'issues': issues,
            'last_check': 'now',
            'system_operational': True
        }
    except Exception as e:
        return {
            'status': 'error',
            'issues': [f"Health check failed: {str(e)}"],
            'last_check': 'failed',
            'system_operational': False
        }