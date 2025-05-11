import { AnimationStatus } from '@/types/animation';
import { useState, useEffect } from 'react'

interface UseAnimationStatusProps {
  animationId: string;
  userId: string;
  pollingInterval?: number; // in milliseconds
  autoStart?: boolean;
}

interface AnimationStatusResponse {
  id: string;
  status: AnimationStatus
  progress: number;
  status_message: string | null;
  video_url: string | null;
  created_at: string;
}

export function useAnimationStatus({
  animationId,
  userId,
  pollingInterval = 3000, // default 3 seconds
  autoStart = true,
}: UseAnimationStatusProps) {
  const [status, setStatus] = useState<AnimationStatus>(AnimationStatus.PENDING);
  const [progress, setProgress] = useState<number>(0);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [isPolling, setIsPolling] = useState<boolean>(autoStart);

  const fetchStatus = async () => {
    if (!animationId || !userId) return;
    
    setLoading(true);
    try {
      const response = await fetch(`/api/animation/${animationId}/status?user_id=${userId}`);
      
      if (!response.ok) {
        throw new Error(`Error fetching animation status: ${response.statusText}`);
      }
      
      const data: AnimationStatusResponse = await response.json();
      
      // Update state with new status information
      setStatus(data.status);
      setProgress(data.progress);
      setStatusMessage(data.status_message);
      
      // Set video URL if available
      if (data.video_url) {
        setVideoUrl(data.video_url);
      }
      
      // Clear any previous errors
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Start/stop polling
  const startPolling = () => setIsPolling(true);
  const stopPolling = () => setIsPolling(false);

  // Poll for status updates
  useEffect(() => {
    if (!isPolling) return;
    
    // Fetch immediately on start
    fetchStatus();
    
    // Set up polling interval
    const intervalId = setInterval(fetchStatus, pollingInterval);
    
    // Stop polling when status is completed or failed
    if (status === AnimationStatus.COMPLETED || status === AnimationStatus.FAILED) {
      stopPolling();
    }
    
    // Clean up on unmount or when polling stops
    return () => clearInterval(intervalId);
  }, [animationId, userId, isPolling, pollingInterval, status]);

  return {
    status,
    progress,
    statusMessage,
    videoUrl,
    error,
    loading,
    isPolling,
    startPolling,
    stopPolling,
    refetch: fetchStatus,
  };
} 