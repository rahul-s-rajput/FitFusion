/**
 * Online Status Hook for FitFusion AI Workout App
 * Manages offline/online state with intelligent connectivity detection
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useAppStore } from '../store';
import { getSyncAdapter } from '../lib/sync-adapter';

export interface NetworkStatus {
  isOnline: boolean;
  isSlowConnection: boolean;
  connectionType: string;
  effectiveType: string;
  downlink: number;
  rtt: number;
  saveData: boolean;
}

export interface OnlineStatusOptions {
  checkInterval?: number;
  timeout?: number;
  enableNetworkInfo?: boolean;
  enablePing?: boolean;
  pingUrl?: string;
  onStatusChange?: (status: NetworkStatus) => void;
}

const DEFAULT_OPTIONS: Required<OnlineStatusOptions> = {
  checkInterval: 30000, // 30 seconds
  timeout: 5000, // 5 seconds
  enableNetworkInfo: true,
  enablePing: true,
  pingUrl: '/api/profile/health',
  onStatusChange: () => {}
};

export function useOnlineStatus(options?: OnlineStatusOptions) {
  const {
    checkInterval,
    timeout,
    enableNetworkInfo,
    enablePing,
    pingUrl,
    onStatusChange,
  } = (options ?? {}) as OnlineStatusOptions;

  const config = useMemo(
    () => ({
      ...DEFAULT_OPTIONS,
      checkInterval: checkInterval ?? DEFAULT_OPTIONS.checkInterval,
      timeout: timeout ?? DEFAULT_OPTIONS.timeout,
      enableNetworkInfo: enableNetworkInfo ?? DEFAULT_OPTIONS.enableNetworkInfo,
      enablePing: enablePing ?? DEFAULT_OPTIONS.enablePing,
      pingUrl: pingUrl ?? DEFAULT_OPTIONS.pingUrl,
      onStatusChange: onStatusChange ?? DEFAULT_OPTIONS.onStatusChange,
    }),
    [
      checkInterval,
      timeout,
      enableNetworkInfo,
      enablePing,
      pingUrl,
      onStatusChange,
    ]
  );

  const setOnlineStatus = useAppStore((state) => state.setOnlineStatus);
const addNotification = useAppStore((state) => state.addNotification);

  const syncAdapter = getSyncAdapter();
  
  const [networkStatus, setNetworkStatus] = useState<NetworkStatus>({
    isOnline: navigator.onLine,
    isSlowConnection: false,
    connectionType: 'unknown',
    effectiveType: 'unknown',
    downlink: 0,
    rtt: 0,
    saveData: false
  });

  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  const lastPingRef = useRef<number>(0);
  const consecutiveFailuresRef = useRef<number>(0);

  // Get network information if available
  const getNetworkInfo = useCallback((): Partial<NetworkStatus> => {
    if (!config.enableNetworkInfo || !('connection' in navigator)) {
      return {};
    }

    const connection = (navigator as any).connection || 
                      (navigator as any).mozConnection || 
                      (navigator as any).webkitConnection;

    if (!connection) return {};

    return {
      connectionType: connection.type || 'unknown',
      effectiveType: connection.effectiveType || 'unknown',
      downlink: connection.downlink || 0,
      rtt: connection.rtt || 0,
      saveData: connection.saveData || false,
      isSlowConnection: connection.effectiveType === 'slow-2g' || 
                       connection.effectiveType === '2g' ||
                       connection.downlink < 0.5
    };
  }, [config.enableNetworkInfo]);

  // Ping server to verify actual connectivity
  const pingServer = useCallback(async (): Promise<boolean> => {
    if (!config.enablePing) return navigator.onLine;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), config.timeout);

      const response = await fetch(config.pingUrl, {
        method: 'HEAD',
        mode: 'cors',
        cache: 'no-cache',
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      return response.ok;
    } catch (error) {
      console.warn('Server ping failed:', error);
      return false;
    }
  }, [config.enablePing, config.pingUrl, config.timeout]);

  // Update network status
  const updateNetworkStatus = useCallback(async () => {
    const now = Date.now();
    
    // Throttle ping requests
    if (now - lastPingRef.current < config.checkInterval / 2) {
      return;
    }
    
    lastPingRef.current = now;

    const browserOnline = navigator.onLine;
    const serverReachable = await pingServer();
    const networkInfo = getNetworkInfo();
    
    const isActuallyOnline = browserOnline && serverReachable;
    
    const newStatus: NetworkStatus = {
      isOnline: isActuallyOnline,
      isSlowConnection: networkInfo.isSlowConnection || false,
      connectionType: networkInfo.connectionType || 'unknown',
      effectiveType: networkInfo.effectiveType || 'unknown',
      downlink: networkInfo.downlink || 0,
      rtt: networkInfo.rtt || 0,
      saveData: networkInfo.saveData || false
    };

    // Track consecutive failures
    if (!isActuallyOnline) {
      consecutiveFailuresRef.current++;
    } else {
      consecutiveFailuresRef.current = 0;
    }

    // Only update if status changed
    if (newStatus.isOnline !== networkStatus.isOnline || 
        newStatus.isSlowConnection !== networkStatus.isSlowConnection) {
      
      setNetworkStatus(newStatus);
      setOnlineStatus(newStatus.isOnline);
      config.onStatusChange(newStatus);

      // Show notifications for status changes
      if (newStatus.isOnline && !networkStatus.isOnline) {
        addNotification({
          type: 'success',
          title: 'Back Online',
          message: 'Connection restored. Syncing your data...'
        });
        
        // Trigger sync when coming back online
        syncAdapter.processSyncQueue();
      } else if (!newStatus.isOnline && networkStatus.isOnline) {
        addNotification({
          type: 'warning',
          title: 'Connection Lost',
          message: 'Working offline. Changes will sync when connection is restored.'
        });
      }

      // Warn about slow connection
      if (newStatus.isSlowConnection && !networkStatus.isSlowConnection) {
        addNotification({
          type: 'info',
          title: 'Slow Connection',
          message: 'Detected slow connection. Some features may be limited.'
        });
      }
    }
  }, [networkStatus, config, setOnlineStatus, addNotification, syncAdapter, pingServer, getNetworkInfo]);

  // Handle browser online/offline events
  const handleOnline = useCallback(() => {
    console.log('Browser online event detected');
    updateNetworkStatus();
  }, [updateNetworkStatus]);

  const handleOffline = useCallback(() => {
    console.log('Browser offline event detected');
    setNetworkStatus(prev => ({ ...prev, isOnline: false }));
    setOnlineStatus(false);
    addNotification({
      type: 'warning',
      title: 'Connection Lost',
      message: 'Working offline. Changes will sync when connection is restored.'
    });
  }, [setOnlineStatus, addNotification]);

  // Handle visibility change (check connection when app becomes visible)
  const handleVisibilityChange = useCallback(() => {
    if (!document.hidden) {
      console.log('App became visible, checking connection...');
      updateNetworkStatus();
    }
  }, [updateNetworkStatus]);

  // Handle focus (check connection when window gains focus)
  const handleFocus = useCallback(() => {
    console.log('Window focused, checking connection...');
    updateNetworkStatus();
  }, [updateNetworkStatus]);

  // Setup event listeners and intervals
  useEffect(() => {
    // Initial status check
    updateNetworkStatus();

    // Browser online/offline events
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Visibility and focus events
    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('focus', handleFocus);

    // Network information change events
    if (config.enableNetworkInfo && 'connection' in navigator) {
      const connection = (navigator as any).connection;
      if (connection && connection.addEventListener) {
        connection.addEventListener('change', updateNetworkStatus);
      }
    }

    // Periodic connectivity checks
    intervalRef.current = setInterval(updateNetworkStatus, config.checkInterval);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('focus', handleFocus);

      if (config.enableNetworkInfo && 'connection' in navigator) {
        const connection = (navigator as any).connection;
        if (connection && connection.removeEventListener) {
          connection.removeEventListener('change', updateNetworkStatus);
        }
      }

      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [config, handleOnline, handleOffline, handleVisibilityChange, handleFocus, updateNetworkStatus]);

  // Manual refresh function
  const refreshStatus = useCallback(() => {
    updateNetworkStatus();
  }, [updateNetworkStatus]);

  // Get connection quality description
  const getConnectionQuality = useCallback((): 'excellent' | 'good' | 'fair' | 'poor' | 'offline' => {
    if (!networkStatus.isOnline) return 'offline';
    
    if (networkStatus.effectiveType === '4g' && networkStatus.downlink > 10) {
      return 'excellent';
    } else if (networkStatus.effectiveType === '4g' || networkStatus.downlink > 2) {
      return 'good';
    } else if (networkStatus.effectiveType === '3g' || networkStatus.downlink > 0.5) {
      return 'fair';
    } else {
      return 'poor';
    }
  }, [networkStatus]);

  // Check if we should limit data usage
  const shouldLimitData = useCallback((): boolean => {
    return networkStatus.saveData || 
           networkStatus.isSlowConnection || 
           consecutiveFailuresRef.current > 2;
  }, [networkStatus]);

  // Get retry delay based on connection quality
  const getRetryDelay = useCallback((): number => {
    const baseDelay = 1000; // 1 second
    const failures = consecutiveFailuresRef.current;
    
    if (networkStatus.isSlowConnection) {
      return baseDelay * Math.pow(2, Math.min(failures, 6)) * 2; // Longer delays for slow connections
    }
    
    return baseDelay * Math.pow(2, Math.min(failures, 4)); // Exponential backoff
  }, [networkStatus]);

  return {
    // Status information
    isOnline: networkStatus.isOnline,
    isSlowConnection: networkStatus.isSlowConnection,
    connectionType: networkStatus.connectionType,
    effectiveType: networkStatus.effectiveType,
    downlink: networkStatus.downlink,
    rtt: networkStatus.rtt,
    saveData: networkStatus.saveData,
    
    // Computed properties
    connectionQuality: getConnectionQuality(),
    shouldLimitData: shouldLimitData(),
    consecutiveFailures: consecutiveFailuresRef.current,
    retryDelay: getRetryDelay(),
    
    // Actions
    refreshStatus,
    
    // Full status object
    networkStatus
  };
}

// Hook for components that only need basic online/offline status
export function useSimpleOnlineStatus() {
  const { isOnline } = useOnlineStatus();
  return isOnline;
}

// Hook for components that need to react to connection quality changes
export function useConnectionQuality() {
  const { connectionQuality, isSlowConnection, shouldLimitData } = useOnlineStatus();
  
  return {
    quality: connectionQuality,
    isSlowConnection,
    shouldLimitData
  };
}

// Hook for handling network-dependent operations
export function useNetworkAwareOperation() {
  const { isOnline, shouldLimitData, retryDelay, refreshStatus } = useOnlineStatus();
  
  const executeWhenOnline = useCallback(async (
    operation: () => Promise<any>,
    options: {
      maxRetries?: number;
      showOfflineMessage?: boolean;
    } = {}
  ) => {
    const { maxRetries = 3, showOfflineMessage = true } = options;
    
    if (!isOnline) {
      if (showOfflineMessage) {
        useAppStore.getState().addNotification({
          type: 'warning',
          title: 'Offline',
          message: 'This action requires an internet connection.'
        });
      }
      throw new Error('Operation requires internet connection');
    }
    
    let attempts = 0;
    while (attempts < maxRetries) {
      try {
        return await operation();
      } catch (error) {
        attempts++;
        if (attempts >= maxRetries) {
          throw error;
        }
        
        // Wait before retry
        await new Promise(resolve => setTimeout(resolve, retryDelay));
        
        // Refresh status before retry
        refreshStatus();
      }
    }
  }, [isOnline, retryDelay, refreshStatus]);
  
  return {
    isOnline,
    shouldLimitData,
    executeWhenOnline
  };
}






