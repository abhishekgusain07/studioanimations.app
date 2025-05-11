"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/hooks/useUser';
import { AnimationProgress } from '@/components/animation/AnimationProgress';
import { Button } from '@/components/ui/button';
import { ArrowLeft, RefreshCw } from 'lucide-react';

export default function AnimationDetailsPage({ 
  params 
}: { 
  params: { id: string } 
}) {
  const router = useRouter();
  const { user } = useUser();
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  
  // Handler for when animation completes
  const handleAnimationComplete = (url: string) => {
    setVideoUrl(url);
  };
  
  // If no user is available, we can't display anything
  if (!user) {
    return <div className="flex items-center justify-center min-h-screen">
      <p>Loading user information...</p>
    </div>;
  }
  
  return (
    <div className="container max-w-6xl mx-auto py-8">
      <div className="mb-6">
        <Button 
          variant="ghost" 
          onClick={() => router.back()}
          className="flex items-center gap-2"
        >
          <ArrowLeft className="h-4 w-4" />
          Back
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-card rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-4">Animation Status</h2>
            
            {/* Animation Progress Component */}
            <AnimationProgress 
              animationId={params.id} 
              userId={user.id}
              onComplete={handleAnimationComplete}
            />
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-card rounded-lg shadow-md p-6">
            <h2 className="text-2xl font-bold mb-4">Animation Preview</h2>
            
            {videoUrl ? (
              <div className="aspect-video rounded-md overflow-hidden bg-black">
                <video 
                  src={videoUrl} 
                  controls 
                  className="w-full h-full"
                >
                  Your browser does not support the video tag.
                </video>
              </div>
            ) : (
              <div className="aspect-video rounded-md overflow-hidden bg-muted flex items-center justify-center">
                <p className="text-muted-foreground">
                  Video will appear here when animation is complete
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 