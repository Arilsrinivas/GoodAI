export type JobQueueStatus =
  | "pending"
  | "uploading"
  | "generating"
  | "completed"
  | "failed"
  | "retrying"
  | "cancelled";

export type ModelCategory = "image" | "video" | "speech" | "llm";

export interface AtlasModelInfo {
  id: string;
  name: string;
  category: ModelCategory;
  provider: string;
  description?: string;
  defaultDuration?: number;
  supportedAspectRatios?: string[];
  maxPromptLength?: number;
}

export interface AtlasConfig {
  baseUrl: string;
  apiKey: string;
  timeoutMs: number;
  maxRetries: number;
}

export interface GenerateImageOptions {
  model?: string;
  prompt: string;
  negativePrompt?: string;
  aspectRatio?: string;
  width?: number;
  height?: number;
  numOutputs?: number;
  seed?: number;
}

export interface GenerateImageResult {
  imageUrl: string;
  modelUsed: string;
  metadata: CostTrackingMetadata;
}

export interface GenerateVideoOptions {
  model?: string;
  prompt: string;
  duration?: number;
  aspectRatio?: string;
  referenceImageUrl?: string;
  negativePrompt?: string;
  seed?: number;
}

export interface GenerateVideoResult {
  videoUrl: string;
  predictionId?: string;
  modelUsed: string;
  status: JobQueueStatus;
  metadata: CostTrackingMetadata;
}

export interface GenerateSpeechOptions {
  model?: string;
  text: string;
  voice?: string;
  speed?: number;
}

export interface GenerateSpeechResult {
  audioUrl: string;
  modelUsed: string;
  metadata: CostTrackingMetadata;
}

export interface UploadMediaOptions {
  file: File | Blob | Uint8Array | ArrayBuffer | unknown;
  filename?: string;
  mimeType?: string;
}

export interface UploadMediaResult {
  url: string;
  filename?: string;
  sizeBytes?: number;
}

export interface PredictionStatusResponse {
  id: string;
  status: "pending" | "processing" | "completed" | "failed" | "cancelled";
  outputs?: string[];
  output?: string;
  url?: string;
  error?: string;
  progress?: number;
  creditsConsumed?: number;
}

export interface CostTrackingMetadata {
  modelUsed: string;
  startTime: string;
  completionTime: string;
  durationMs: number;
  creditsConsumed?: number;
  generationDurationSeconds?: number;
}

export interface RequestLogEntry {
  timestamp: string;
  endpoint: string;
  model?: string;
  durationMs: number;
  statusCode?: number;
  status: "success" | "error" | "retried";
  error?: string;
}
