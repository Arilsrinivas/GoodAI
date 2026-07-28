import { AtlasClient, defaultAtlasClient } from "./client";
import {
  GenerateVideoOptions,
  GenerateVideoResult,
  PredictionStatusResponse,
} from "./types";

export class VideoService {
  private client: AtlasClient;

  constructor(client?: AtlasClient) {
    this.client = client || defaultAtlasClient;
  }

  public async generateVideo(
    options: GenerateVideoOptions
  ): Promise<GenerateVideoResult> {
    const startTimeStr = new Date().toISOString();
    const startMs = Date.now();

    const requestedModel = options.model || "bytedance/seedance-2.0-mini/text-to-video";
    const model = options.referenceImageUrl && requestedModel === "bytedance/seedance-2.0-mini/text-to-video"
      ? "bytedance/seedance-2.0-mini/reference-to-video"
      : requestedModel;
    const sanitizedPrompt = this.client.sanitizePrompt(options.prompt);

    const payload: Record<string, unknown> = {
      model,
      prompt: sanitizedPrompt,
      duration: options.duration || 4,
      resolution: "480p",
      ratio: options.aspectRatio || "16:9",
      bitrate_mode: "standard",
      generate_audio: false,
      watermark: false,
    };

    if (options.referenceImageUrl) {
      payload.reference_images = [options.referenceImageUrl];
    }

    if (options.negativePrompt) {
      payload.negative_prompt = this.client.sanitizePrompt(options.negativePrompt);
    }

    if (options.seed !== undefined) {
      payload.seed = options.seed;
    }

    const response = await this.client.request<{
      code?: number;
      data?: {
        id?: string;
        prediction_id?: string;
        url?: string;
        video_url?: string;
        outputs?: string[];
      };
      id?: string;
      prediction_id?: string;
      url?: string;
      video_url?: string;
      outputs?: string[];
    }>("/model/generateVideo", {
      method: "POST",
      body: payload,
      modelForLogging: model,
    });

    const predictionId =
      response?.data?.id ||
      response?.data?.prediction_id ||
      response?.id ||
      response?.prediction_id;

    const directVideoUrl =
      response?.data?.url ||
      response?.data?.video_url ||
      response?.data?.outputs?.[0] ||
      response?.url ||
      response?.video_url ||
      response?.outputs?.[0];

    if (directVideoUrl) {
      const completionTimeStr = new Date().toISOString();
      const durationMs = Date.now() - startMs;

      return {
        videoUrl: directVideoUrl,
        predictionId,
        modelUsed: model,
        status: "completed",
        metadata: {
          modelUsed: model,
          startTime: startTimeStr,
          completionTime: completionTimeStr,
          durationMs,
          generationDurationSeconds: Math.round(durationMs / 1000),
        },
      };
    }

    if (!predictionId) {
      throw new Error("Atlas Video generation returned neither a video URL nor a prediction ID");
    }

    // Auto-polling for task prediction ID
    const polledResult = await this.pollPrediction(predictionId, model, startMs, startTimeStr);
    return polledResult;
  }

  public async pollPrediction(
    predictionId: string,
    modelUsed: string,
    startMs: number,
    startTimeStr: string,
    pollIntervalMs = 5000,
    maxAttempts = 60
  ): Promise<GenerateVideoResult> {
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      await new Promise((resolve) => setTimeout(resolve, pollIntervalMs));

      try {
        const response = await this.client.request<PredictionStatusResponse>(
          `/model/prediction/${predictionId}`,
          {
            method: "GET",
            modelForLogging: modelUsed,
          }
        );

        const result = (response as PredictionStatusResponse & { data?: PredictionStatusResponse }).data || response;
        const status = result.status;
        const videoUrl =
          result.outputs?.[0] ||
          result.output ||
          result.url;

        if (status === "completed" && videoUrl) {
          const completionTimeStr = new Date().toISOString();
          const durationMs = Date.now() - startMs;

          return {
            videoUrl,
            predictionId,
            modelUsed,
            status: "completed",
            metadata: {
              modelUsed,
              startTime: startTimeStr,
              completionTime: completionTimeStr,
              durationMs,
              creditsConsumed: result.creditsConsumed,
              generationDurationSeconds: Math.round(durationMs / 1000),
            },
          };
        }

        if (status === "failed" || status === "cancelled") {
          throw new Error(`Atlas Video generation task ${status}: ${result.error || "Unknown error"}`);
        }
      } catch (err) {
        if (attempt === maxAttempts) {
          throw err;
        }
      }
    }

    throw new Error(`Timed out waiting for Atlas video task ${predictionId} after ${maxAttempts * (pollIntervalMs / 1000)}s`);
  }
}

export const defaultVideoService = new VideoService();

export async function generateVideo(
  options: GenerateVideoOptions
): Promise<GenerateVideoResult> {
  return defaultVideoService.generateVideo(options);
}
