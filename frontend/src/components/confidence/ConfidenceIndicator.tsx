import React from 'react';
import { Box, Chip, Tooltip, Typography } from '@mui/material';
import { 
  CheckCircle, 
  Warning, 
  Error, 
  FlightTakeoff,
  Build,
  Security 
} from '@mui/icons-material';

interface ConfidenceIndicatorProps {
  confidenceScore: number;
  confidenceBand: 'HIGH' | 'MEDIUM' | 'LOW';
  requiresReview?: boolean;
  isSafetyCritical?: boolean;
  isAviation?: boolean;
  category?: string;
  compact?: boolean;
}

interface ConfidenceMetadata {
  score: number;
  band: string;
  color: 'success' | 'warning' | 'error';
  icon: React.ReactElement;
  label: string;
  description: string;
}

const getConfidenceMetadata = (
  score: number, 
  band: string, 
  isSafetyCritical: boolean = false
): ConfidenceMetadata => {
  if (score >= 0.85) {
    return {
      score,
      band,
      color: 'success',
      icon: <CheckCircle />,
      label: 'High Confidence',
      description: 'Extraction is highly reliable'
    };
  } else if (score >= 0.6) {
    return {
      score,
      band,
      color: 'warning',
      icon: <Warning />,
      label: 'Medium Confidence',
      description: isSafetyCritical 
        ? 'Safety critical document requires review'
        : 'May require review'
    };
  } else {
    return {
      score,
      band,
      color: 'error',
      icon: <Error />,
      label: 'Low Confidence',
      description: isSafetyCritical 
        ? 'URGENT: Safety critical document needs immediate review'
        : 'Requires human review'
    };
  }
};

const getCategoryIcon = (category: string = '') => {
  if (category.toLowerCase().includes('flight')) {
    return <FlightTakeoff sx={{ fontSize: 16 }} />;
  }
  if (category.toLowerCase().includes('maintenance')) {
    return <Build sx={{ fontSize: 16 }} />;
  }
  return null;
};

export const ConfidenceIndicator: React.FC<ConfidenceIndicatorProps> = ({
  confidenceScore,
  confidenceBand,
  requiresReview = false,
  isSafetyCritical = false,
  isAviation = false,
  category = '',
  compact = false
}) => {
  const metadata = getConfidenceMetadata(confidenceScore, confidenceBand, isSafetyCritical);
  const categoryIcon = getCategoryIcon(category);

  if (compact) {
    return (
      <Tooltip title={`${metadata.label}: ${(confidenceScore * 100).toFixed(0)}% - ${metadata.description}`}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          {isAviation && categoryIcon}
          <Chip
            size="small"
            color={metadata.color}
            label={`${(confidenceScore * 100).toFixed(0)}%`}
            icon={metadata.icon}
            variant={requiresReview ? 'outlined' : 'filled'}
          />
          {isSafetyCritical && (
            <Security sx={{ fontSize: 16, color: 'error.main' }} />
          )}
        </Box>
      </Tooltip>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, minWidth: 200 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        {isAviation && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            {categoryIcon}
            <Typography variant="caption" color="text.secondary">
              Aviation
            </Typography>
          </Box>
        )}
        <Chip
          color={metadata.color}
          label={metadata.label}
          icon={metadata.icon}
          variant={requiresReview ? 'outlined' : 'filled'}
          size="small"
        />
        {isSafetyCritical && (
          <Tooltip title="Safety Critical Document">
            <Security sx={{ fontSize: 18, color: 'error.main' }} />
          </Tooltip>
        )}
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="body2" fontWeight="medium">
          Score: {(confidenceScore * 100).toFixed(1)}%
        </Typography>
        <Typography variant="caption" color="text.secondary">
          ({confidenceBand})
        </Typography>
      </Box>
      
      <Typography variant="caption" color="text.secondary">
        {metadata.description}
      </Typography>
      
      {requiresReview && (
        <Typography variant="caption" color="warning.main" fontWeight="medium">
          ⚠️ Review Required
        </Typography>
      )}
      
      {isSafetyCritical && confidenceScore < 0.8 && (
        <Typography variant="caption" color="error.main" fontWeight="bold">
          🚨 URGENT SAFETY REVIEW NEEDED
        </Typography>
      )}
    </Box>
  );
};

export default ConfidenceIndicator;