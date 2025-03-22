import { useState, useEffect } from 'react';
import { getImportStatus } from '../services/importApi';
import { ImportStatus } from '../types';

interface UseImportStatusResult {
  status: string | null;
  progress: number;
  refreshStatus: () => Promise<void>;
}

/**
 * Hook to monitor import status and provide real-time updates
 */
export const useImportStatus = (importLogId: string | null): UseImportStatusResult => {
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState<number>(0);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);

  // Function to fetch the current status
  const fetchStatus = async () => {
    if (!importLogId) return;

    try {
      const statusData = await getImportStatus(importLogId);
      setStatus(statusData.status);

      // Calculate progress based on status
      if (statusData.status === ImportStatus.COMPLETED || statusData.status === ImportStatus.PARTIALLY_COMPLETED) {
        setProgress(100);
      } else if (statusData.status === ImportStatus.FAILED) {
        setProgress(100); // Still show 100% for failed
      } else if (statusData.status === ImportStatus.PROCESSING) {
        // If processing, calculate percentage from processed vs total
        if (statusData.processed_count && statusData.processed_count > 0) {
          const total = Math.max(statusData.processed_count, 1);
          const percentage = (statusData.success_count + statusData.error_count) / total * 100;
          setProgress(Math.min(percentage, 99)); // Cap at 99% until completed
        } else {
          setProgress(50); // Default to 50% if we don't have counts
        }
      } else {
        setProgress(10); // Show minimal progress for pending
      }

      // Stop polling if import is complete or failed
      if (statusData.status === ImportStatus.COMPLETED ||
          statusData.status === ImportStatus.FAILED ||
          statusData.status === ImportStatus.PARTIALLY_COMPLETED) {
        if (pollingInterval) {
          clearInterval(pollingInterval);
          setPollingInterval(null);
        }
      }
    } catch (error) {
      console.error('Error fetching import status:', error);
    }
  };

  // Manual refresh function
  const refreshStatus = async () => {
    await fetchStatus();
  };

  // Start/stop polling when importLogId changes
  useEffect(() => {
    if (importLogId) {
      // Fetch immediately
      fetchStatus();

      // Start polling - Check every 3 seconds
      const interval = setInterval(fetchStatus, 3000);
      setPollingInterval(interval);

      // Clean up on unmount or when importLogId changes
      return () => {
        clearInterval(interval);
        setPollingInterval(null);
      };
    } else {
      // Reset state when importLogId is cleared
      setStatus(null);
      setProgress(0);

      // Clean up any existing interval
      if (pollingInterval) {
        clearInterval(pollingInterval);
        setPollingInterval(null);
      }
    }
  }, [importLogId]);

  return { status, progress, refreshStatus };
};