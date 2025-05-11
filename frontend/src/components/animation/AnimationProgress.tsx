import React from 'react';
import { useAnimationStatus } from '@/hooks/use-animation-status';
import { AnimationStatus } from '@/types/animation';
import { Progress } from '@/components/ui/progress';
import { Loader2 } from 'lucide-react';

interface AnimationProgressProps {
  animationId: string;
  userId: string;
  onComplete?: (videoUrl: string) => void;
}

export function AnimationProgress({ 
  animationId, 
  userId,
  onComplete 
}: AnimationProgressProps) {
  const { 
    status, 
    progress, 
    statusMessage, 
    videoUrl, 
    error, 
    loading 
  } = useAnimationStatus({
    animationId,
    userId,
    pollingInterval: 2000, // Poll every 2 seconds
  });

  // Call onComplete callback when animation is complete and we have a video URL
  React.useEffect(() => {
    if (status === AnimationStatus.COMPLETED && videoUrl && onComplete) {
      onComplete(videoUrl);
    }
  }, [status, videoUrl, onComplete]);

  // Get appropriate status message for UI
  const displayMessage = (): string => {
    if (error) return `Error: ${error}`;
    if (statusMessage) return statusMessage;
    
    // Default messages based on status
    switch (status) {
      case AnimationStatus.PENDING:
        return "Preparing to generate animation...";
      case AnimationStatus.PROCESSING:
        return "Generating animation...";
      case AnimationStatus.COMPLETED:
        return "Animation complete!";
      case AnimationStatus.FAILED:
        return "Animation generation failed";
      default:
        return "Unknown status";
    }
  };

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">
          {status === AnimationStatus.PROCESSING && 'Generating Animation'}
          {status === AnimationStatus.PENDING && 'Starting...'}
          {status === AnimationStatus.COMPLETED && 'Complete!'}
          {status === AnimationStatus.FAILED && 'Failed'}
        </span>
        <span className="text-sm text-muted-foreground">
          {Math.round(progress)}%
        </span>
      </div>
      
      <Progress value={progress} className="h-2 w-full" />
      
      <div className="flex items-center gap-2 text-sm">
        {(status === AnimationStatus.PENDING || status === AnimationStatus.PROCESSING) && (
          <Loader2 className="h-4 w-4 animate-spin" />
        )}
        <p className="text-sm text-muted-foreground">
          {displayMessage()}
        </p>
      </div>
      
      {error && (
        <p className="text-sm text-destructive">
          {error}
        </p>
      )}
    </div>
  );
} 