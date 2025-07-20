import { useEffect, useState, useCallback } from 'react';

export interface ServiceStatus {
  name: string;
  url: string;
  status: 'healthy' | 'unhealthy' | 'checking';
  lastChecked: Date;
  error?: string;
}

export interface SystemHealth {
  backend: ServiceStatus;
  queryService: ServiceStatus;
  indexingService: ServiceStatus;
  connectorService: ServiceStatus;
  arango: ServiceStatus;
  qdrant: ServiceStatus;
  mongodb: ServiceStatus;
  redis: ServiceStatus;
  overallStatus: 'healthy' | 'degraded' | 'down';
}

const HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
const HEALTH_CHECK_TIMEOUT = 5000; // 5 seconds

// Health check endpoints for each service
const SERVICE_HEALTH_ENDPOINTS = {
  backend: '/api/health',
  queryService: '/health',
  indexingService: '/health',
  connectorService: '/health',
  arango: '/_api/version',
  qdrant: '/health',
  mongodb: '/admin/ping',
  redis: '/ping',
};

async function checkServiceHealth(url: string, endpoint: string, timeout: number = HEALTH_CHECK_TIMEOUT): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    const response = await fetch(`${url}${endpoint}`, {
      method: 'GET',
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    clearTimeout(timeoutId);
    return response.ok;
  } catch (error) {
    console.warn(`Health check failed for ${url}${endpoint}:`, error);
    return false;
  }
}

export function useHealthMonitor(): {
  systemHealth: SystemHealth;
  isSystemHealthy: boolean;
  isSystemDegraded: boolean;
  isSystemDown: boolean;
  refreshHealth: () => Promise<void>;
} {
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({
    backend: {
      name: 'Backend API',
      url: import.meta.env.VITE_BACKEND_URL || 'http://localhost:3000',
      status: 'checking',
      lastChecked: new Date(),
    },
    queryService: {
      name: 'Query Service',
      url: import.meta.env.VITE_QUERY_SERVICE_URL || 'http://localhost:8001',
      status: 'checking',
      lastChecked: new Date(),
    },
    indexingService: {
      name: 'Indexing Service',
      url: import.meta.env.VITE_INDEXING_SERVICE_URL || 'http://localhost:8091',
      status: 'checking',
      lastChecked: new Date(),
    },
    connectorService: {
      name: 'Connector Service',
      url: import.meta.env.VITE_CONNECTOR_SERVICE_URL || 'http://localhost:8088',
      status: 'checking',
      lastChecked: new Date(),
    },
    arango: {
      name: 'ArangoDB',
      url: import.meta.env.VITE_ARANGO_URL || 'http://localhost:8529',
      status: 'checking',
      lastChecked: new Date(),
    },
    qdrant: {
      name: 'Qdrant Vector DB',
      url: import.meta.env.VITE_QDRANT_URL || 'http://localhost:6333',
      status: 'checking',
      lastChecked: new Date(),
    },
    mongodb: {
      name: 'MongoDB',
      url: import.meta.env.VITE_MONGODB_URL || 'http://localhost:27017',
      status: 'checking',
      lastChecked: new Date(),
    },
    redis: {
      name: 'Redis Cache',
      url: import.meta.env.VITE_REDIS_URL || 'http://localhost:6379',
      status: 'checking',
      lastChecked: new Date(),
    },
    overallStatus: 'down' as const,
  });

  const checkAllServices = useCallback(async () => {
    const services = Object.keys(systemHealth) as Array<keyof Omit<SystemHealth, 'overallStatus'>>;
    const healthPromises = services.map(async (serviceName) => {
      const service = systemHealth[serviceName];
      const endpoint = SERVICE_HEALTH_ENDPOINTS[serviceName];
      
      try {
        const isHealthy = await checkServiceHealth(service.url, endpoint);
        return {
          serviceName,
          status: (isHealthy ? 'healthy' : 'unhealthy') as 'healthy' | 'unhealthy',
          error: isHealthy ? undefined : 'Service unreachable',
        };
      } catch (error) {
        return {
          serviceName,
          status: 'unhealthy' as const,
          error: error instanceof Error ? error.message : 'Unknown error',
        };
      }
    });

    const results = await Promise.all(healthPromises);
    
    setSystemHealth((prev) => {
      const updated = { ...prev };
      let healthyCount = 0;
      
      results.forEach(({ serviceName, status, error }) => {
        updated[serviceName] = {
          ...prev[serviceName],
          status: status as 'healthy' | 'unhealthy' | 'checking',
          error,
          lastChecked: new Date(),
        };
        
        if (status === 'healthy') {
          healthyCount += 1;
        }
      });

      // Determine overall status
      if (healthyCount === services.length) {
        updated.overallStatus = 'healthy';
      } else if (healthyCount >= Math.ceil(services.length * 0.6)) {
        updated.overallStatus = 'degraded';
      } else {
        updated.overallStatus = 'down';
      }

      return updated;
    });
  }, [systemHealth]);

  const refreshHealth = useCallback(async () => {
    await checkAllServices();
  }, [checkAllServices]);

  useEffect(() => {
    // Initial health check
    checkAllServices();

    // Set up periodic health checks
    const interval = setInterval(checkAllServices, HEALTH_CHECK_INTERVAL);

    return () => clearInterval(interval);
  }, [checkAllServices]);

  const isSystemHealthy = systemHealth.overallStatus === 'healthy';
  const isSystemDegraded = systemHealth.overallStatus === 'degraded';
  const isSystemDown = systemHealth.overallStatus === 'down';

  return {
    systemHealth,
    isSystemHealthy,
    isSystemDegraded,
    isSystemDown,
    refreshHealth,
  };
}

export default useHealthMonitor;