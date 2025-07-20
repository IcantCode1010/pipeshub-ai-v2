import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
  Button,
  Tab,
  Tabs,
  CircularProgress
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Assignment,
  Warning,
  CheckCircle,
  Error
} from '@mui/icons-material';

interface ConfidenceStats {
  cache_stats: {
    total_items: number;
    active_items: number;
    expired_items: number;
  };
  quality_metrics: {
    total_documents: number;
    high_confidence_count: number;
    medium_confidence_count: number;
    low_confidence_count: number;
    avg_confidence: number;
    safety_critical_low_confidence: number;
    documents_requiring_review: number;
  };
  confidence_trend: {
    trend: string;
    recent_avg: number;
    sample_size: number;
  };
}

interface ReviewQueueItem {
  document_id: string;
  confidence_score: number;
  confidence_band: string;
  priority: string;
  reason: string;
  timestamp: number;
  metadata: any;
}

interface Alert {
  type: string;
  message: string;
  action: string;
}

const ConfidenceDashboard: React.FC = () => {
  const [stats, setStats] = useState<ConfidenceStats | null>(null);
  const [reviewQueue, setReviewQueue] = useState<ReviewQueueItem[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/confidence/stats');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching confidence stats:', error);
    }
  };

  const fetchReviewQueue = async () => {
    try {
      const response = await fetch('/api/confidence/review-queue?limit=20');
      const data = await response.json();
      setReviewQueue(data.items);
    } catch (error) {
      console.error('Error fetching review queue:', error);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/confidence/alerts');
      const data = await response.json();
      setAlerts(data.alerts);
    } catch (error) {
      console.error('Error fetching alerts:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchStats(), fetchReviewQueue(), fetchAlerts()]);
      setLoading(false);
    };

    loadData();
    
    // Refresh every 30 seconds
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving':
        return <TrendingUp color="success" />;
      case 'declining':
        return <TrendingDown color="error" />;
      case 'stable':
        return <TrendingFlat color="info" />;
      default:
        return <TrendingFlat />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return 'error';
      case 'HIGH':
        return 'warning';
      case 'MEDIUM':
        return 'info';
      default:
        return 'default';
    }
  };

  const resolveReviewItem = async (documentId: string) => {
    try {
      await fetch(`/api/confidence/review-queue/${documentId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution: 'manual_review_completed' })
      });
      
      // Refresh review queue
      await fetchReviewQueue();
    } catch (error) {
      console.error('Error resolving review item:', error);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!stats) {
    return <Alert severity="error">Failed to load confidence statistics</Alert>;
  }

  const { quality_metrics, confidence_trend } = stats;
  const confidencePercentage = quality_metrics.avg_confidence * 100;

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Confidence Monitoring Dashboard
      </Typography>

      {/* Alerts */}
      {alerts.length > 0 && (
        <Box sx={{ mb: 3 }}>
          {alerts.map((alert, index) => (
            <Alert 
              key={index} 
              severity={alert.type as any} 
              sx={{ mb: 1 }}
              action={
                <Button size="small" color="inherit">
                  {alert.action}
                </Button>
              }
            >
              {alert.message}
            </Alert>
          ))}
        </Box>
      )}

      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Overall Confidence
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h4" color="primary">
                  {confidencePercentage.toFixed(1)}%
                </Typography>
                {getTrendIcon(confidence_trend.trend)}
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={confidencePercentage} 
                sx={{ mt: 1 }}
                color={confidencePercentage >= 80 ? 'success' : confidencePercentage >= 60 ? 'warning' : 'error'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Documents Processed
              </Typography>
              <Typography variant="h4" color="primary">
                {quality_metrics.total_documents}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total extractions
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Requiring Review
              </Typography>
              <Typography variant="h4" color="warning.main">
                {quality_metrics.documents_requiring_review}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                {quality_metrics.total_documents > 0 
                  ? ((quality_metrics.documents_requiring_review / quality_metrics.total_documents) * 100).toFixed(1)
                  : 0}% of total
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Safety Critical Issues
              </Typography>
              <Typography variant="h4" color="error.main">
                {quality_metrics.safety_critical_low_confidence}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Low confidence safety docs
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Confidence Distribution */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Confidence Distribution
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CheckCircle color="success" />
                    <Typography>High (≥85%)</Typography>
                  </Box>
                  <Typography fontWeight="bold">
                    {quality_metrics.high_confidence_count}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Warning color="warning" />
                    <Typography>Medium (60-84%)</Typography>
                  </Box>
                  <Typography fontWeight="bold">
                    {quality_metrics.medium_confidence_count}
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Error color="error" />
                    <Typography>Low (&lt;60%)</Typography>
                  </Box>
                  <Typography fontWeight="bold">
                    {quality_metrics.low_confidence_count}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Confidence Trend
              </Typography>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                {getTrendIcon(confidence_trend.trend)}
                <Typography variant="h6" textTransform="capitalize">
                  {confidence_trend.trend.replace('_', ' ')}
                </Typography>
              </Box>
              <Typography variant="body2" color="textSecondary">
                Recent Average: {(confidence_trend.recent_avg * 100).toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Sample Size: {confidence_trend.sample_size} documents
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Review Queue */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Assignment />
            Review Queue ({reviewQueue.length})
          </Typography>
          
          {reviewQueue.length === 0 ? (
            <Typography color="textSecondary">No items in review queue</Typography>
          ) : (
            <List>
              {reviewQueue.slice(0, 10).map((item) => (
                <ListItem 
                  key={item.document_id}
                  sx={{ 
                    border: 1, 
                    borderColor: 'divider', 
                    borderRadius: 1, 
                    mb: 1,
                    bgcolor: item.priority === 'URGENT' ? 'error.light' : 'background.paper'
                  }}
                >
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body1">
                          Document: {item.document_id.slice(-8)}
                        </Typography>
                        <Chip 
                          size="small" 
                          label={item.priority} 
                          color={getPriorityColor(item.priority) as any}
                        />
                        <Chip 
                          size="small" 
                          label={`${(item.confidence_score * 100).toFixed(0)}%`}
                          variant="outlined"
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography variant="body2" color="textSecondary">
                          {item.reason}
                        </Typography>
                        <Typography variant="caption" color="textSecondary">
                          {new Date(item.timestamp * 1000).toLocaleString()}
                        </Typography>
                      </Box>
                    }
                  />
                  <Button 
                    size="small" 
                    onClick={() => resolveReviewItem(item.document_id)}
                    color="primary"
                  >
                    Resolve
                  </Button>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default ConfidenceDashboard;