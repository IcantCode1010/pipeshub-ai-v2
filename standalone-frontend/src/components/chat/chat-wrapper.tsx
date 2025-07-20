import { useEffect, useState } from 'react';
import { Box, Alert, Button } from '@mui/material';
import { Icon } from '@iconify/react';
import refreshIcon from '@iconify-icons/mdi/refresh';

import { useHealthMonitor } from '../../services/health-monitor';
import { FallbackChat } from '../fallback/fallback-chat';

interface ChatWrapperProps {
  children: React.ReactNode;
  requiresServices?: Array<'backend' | 'queryService' | 'indexingService' | 'connectorService'>;
}

export function ChatWrapper({ 
  children, 
  requiresServices = ['backend', 'queryService'] 
}: ChatWrapperProps) {
  const { systemHealth, refreshHealth } = useHealthMonitor();
  const [isRetrying, setIsRetrying] = useState(false);
  const [showFallback, setShowFallback] = useState(false);

  // Check if required services are available
  const servicesAvailable = requiresServices.every(
    (serviceName) => systemHealth[serviceName]?.status === 'healthy'
  );

  const handleRetry = async () => {
    setIsRetrying(true);
    await refreshHealth();
    setIsRetrying(false);
  };

  useEffect(() => {
    // Show fallback after a short delay if services are not available
    if (!servicesAvailable) {
      const timer = setTimeout(() => {
        setShowFallback(true);
      }, 3000); // Wait 3 seconds before showing fallback

      return () => clearTimeout(timer);
    }
    
    setShowFallback(false);
    return undefined;
  }, [servicesAvailable]);

  // If services are checking, show loading state
  const isChecking = requiresServices.some(
    (serviceName) => systemHealth[serviceName]?.status === 'checking'
  );

  if (isChecking && !showFallback) {
    return (
      <Box
        sx={{
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          p: 3,
        }}
      >
        <Alert severity="info" sx={{ width: '100%', maxWidth: 600 }}>
          Connecting to Aerointel Solutions services...
        </Alert>
      </Box>
    );
  }

  // If services are not available, show fallback
  if (!servicesAvailable && showFallback) {
    return <FallbackChat onRetry={handleRetry} isRetrying={isRetrying} />;
  }

  // If some services are degraded but core ones work, show warning
  if (servicesAvailable && systemHealth.overallStatus === 'degraded') {
    return (
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Alert
          severity="warning"
          sx={{ mb: 1 }}
          action={
            <Button
              size="small"
              startIcon={<Icon icon={refreshIcon} />}
              onClick={handleRetry}
            >
              Retry
            </Button>
          }
        >
          Some services are experiencing issues. Functionality may be limited.
        </Alert>
        <Box sx={{ flexGrow: 1 }}>{children}</Box>
      </Box>
    );
  }

  // Services are available, render normally
  return <>{children}</>;
}

export default ChatWrapper;