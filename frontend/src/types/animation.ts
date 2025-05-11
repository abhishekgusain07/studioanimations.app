/**
 * Animation-related types
 */

/**
 * Enum for animation processing status.
 * Must match the backend enum in `app/models/db_models.py`
 */
export enum AnimationStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed"
}

/**
 * Base animation type
 */
export interface Animation {
  id: string;
  conversationId: string;
  userId: string;
  query: string;
  generatedCode: string;
  videoUrl: string;
  version: number;
  quality: string;
  success: boolean;
  errorMessage?: string;
  createdAt: string;
  status: AnimationStatus;
  progress: number;
  statusMessage?: string;
}

/**
 * Animation status response 
 */
export interface AnimationStatusData {
  id: string;
  status: AnimationStatus;
  progress: number;
  statusMessage?: string;
  videoUrl?: string;
  createdAt: string;
} 