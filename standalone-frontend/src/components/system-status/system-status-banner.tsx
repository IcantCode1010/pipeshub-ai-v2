import { useState } from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Chip,
  Collapse,
  Dialog,
  DialogContent,
  DialogTitle,
  Grid,
  IconButton,
  Typography,
  useTheme,
} from '@mui/material';
import { Icon } from '@iconify/react';
import refreshIcon from '@iconify-icons/mdi/refresh';
import chevronDownIcon from '@iconify-icons/mdi/chevron-down';
import chevronUpIcon from '@iconify-icons/mdi/chevron-up';
import closeIcon from '@iconify-icons/mdi/close';

import { useHealthMonitor, type SystemHealth, type ServiceStatus } from '../../services/health-monitor';

export function SystemStatusBanner() {
  const theme = useTheme();
  const { systemHealth, isSystemHealthy, isSystemDegraded, isSystemDown, refreshHealth } = useHealthMonitor();
  const [showDetails, setShowDetails] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);

  if (isSystemHealthy) {
    return null; // Don't show banner when everything is healthy
  }

  const getSeverity = () => {
    if (isSystemDown) return 'error';
    if (isSystemDegraded) return 'warning';
    return 'info';
  };

  const getStatusMessage = () => {
    if (isSystemDown) {
      return 'System services are currently unavailable. Some features may not work properly.';
    }
    if (isSystemDegraded) {
      return 'Some system services are experiencing issues. Limited functionality may be available.';
    }
    return 'System status is being checked...';
  };

  const getStatusColor = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'unhealthy':
        return 'error';
      case 'checking':
        return 'warning';
      default:
        return 'default';
    }
  };

  return (
    <>
      <Alert
        severity={getSeverity()}
        sx={{
          mb: 2,
          '& .MuiAlert-message': {
            width: '100%',
          },
        }}
        action={
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              size="small"
              onClick={refreshHealth}
              sx={{ color: 'inherit' }}
              title="Refresh status"
            >
              <Icon icon={refreshIcon} />
            </IconButton>
            <IconButton
              size="small"
              onClick={() => setShowDetails(!showDetails)}
              sx={{ color: 'inherit' }}
              title={showDetails ? 'Hide details' : 'Show details'}
            >
              <Icon icon={showDetails ? chevronUpIcon : chevronDownIcon} />
            </IconButton>
          </Box>
        }
      >
        <AlertTitle>System Status Alert</AlertTitle>
        {getStatusMessage()}
        
        <Collapse in={showDetails} sx={{ mt: 1 }}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
            {Object.entries(systemHealth).map(([key, service]) => {
              if (key === 'overallStatus') return null;
              
              return (
                <Chip
                  key={key}
                  label={service.name}
                  size="small"
                  color={getStatusColor(service.status)}
                  variant="outlined"
                />
              );
            })}
            <Button
              size="small"
              variant="outlined"
              onClick={() => setDetailsDialogOpen(true)}
              sx={{ ml: 1 }}
            >
              View Details
            </Button>
          </Box>
        </Collapse>
      </Alert>

      <SystemStatusDialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        systemHealth={systemHealth}
        refreshHealth={refreshHealth}
      />
    </>
  );
}

interface SystemStatusDialogProps {
  open: boolean;
  onClose: () => void;
  systemHealth: SystemHealth;
  refreshHealth: () => Promise<void>;
}

function SystemStatusDialog({ open, onClose, systemHealth, refreshHealth }: SystemStatusDialogProps) {
  const theme = useTheme();

  const getStatusIcon = (status: ServiceStatus['status']) => {
    switch (status) {
      case 'healthy':
        return { icon: 'mdi:check-circle', color: theme.palette.success.main };
      case 'unhealthy':
        return { icon: 'mdi:alert-circle', color: theme.palette.error.main };
      case 'checking':
        return { icon: 'mdi:loading', color: theme.palette.warning.main };
      default:
        return { icon: 'mdi:help-circle', color: theme.palette.grey[500] };
    }
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        System Health Status
        <IconButton onClick={onClose} size="small">
          <Icon icon={closeIcon} />
        </IconButton>
      </DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            Overall Status: {systemHealth.overallStatus.toUpperCase()}
          </Typography>
          <Button
            variant="outlined"
            startIcon={<Icon icon={refreshIcon} />}
            onClick={refreshHealth}
          >
            Refresh All
          </Button>
        </Box>
        
        <Grid container spacing={2}>
          {Object.entries(systemHealth).map(([key, service]) => {
            if (key === 'overallStatus') return null;
            
            const statusInfo = getStatusIcon(service.status);
            
            return (
              <Grid item xs={12} sm={6} md={4} key={key}>
                <Box
                  sx={{
                    p: 2,
                    border: 1,
                    borderColor: 'divider',
                    borderRadius: 1,
                    height: '100%',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Icon
                      icon={statusInfo.icon}
                      style={{ color: statusInfo.color, marginRight: 8 }}
                    />
                    <Typography variant="subtitle2">{service.name}</Typography>
                  </Box>
                  
                  <Typography variant="body2" color="textSecondary" sx={{ mb: 1 }}>
                    {service.url}
                  </Typography>
                  
                  <Typography variant="caption" color="textSecondary">
                    Last checked: {service.lastChecked.toLocaleTimeString()}
                  </Typography>
                  
                  {service.error && (
                    <Typography variant="caption" color="error" sx={{ display: 'block', mt: 1 }}>
                      Error: {service.error}
                    </Typography>
                  )}
                </Box>
              </Grid>
            );
          })}
        </Grid>
      </DialogContent>
    </Dialog>
  );
}

export default SystemStatusBanner;