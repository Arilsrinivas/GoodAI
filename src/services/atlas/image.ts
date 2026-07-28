import { AtlasClient, defaultAtlasClient } from "./client";
import { GenerateImageOptions, GenerateImageResult } from "./types";

export class ImageService {
  private client: AtlasClient;

  constructor(client?: AtlasClient) {
    this.client = client || defaultAtlasClient;
  }

  public async generateImage(
    options: GenerateImageOptions
  ): Promise<GenerateImageResult> {
    const startTimeStr = new Date().toISOString();
    const startMs = Date.now();

    const model = options.model || "seedream-3.0";
    const sanitizedPrompt = this.client.sanitizePrompt(options.prompt);

    const payload = {
      model,
      prompt: sanitizedPrompt,
      negative_prompt: options.negativePrompt ? this.client.sanitizePrompt(options.negativePrompt) : undefined,
      aspect_ratio: options.aspectRatio || "16:9",
      width: options.width,
      height: options.height,
      num_outputs: options.numOutputs || 1,
      seed: options.seed,
    };

    const response = await this.client.request<{
      code?: number;
      data?: {
        url?: string;
        urls?: string[];
        image_url?: string;
        images?: string[];
        id?: string;
      };
      url?: string;
      image_url?: string;
      outputs?: string[];
    }>("/model/generateImage", {
      method: "POST",
      body: payload,
      modelForLogging: model,
    });

    const completionTimeStr = new Date().toISOString();
    const durationMs = Date.now() - startMs;

    const imageUrl =
      response?.data?.url ||
      response?.data?.image_url ||
      response?.data?.urls?.[0] ||
      response?.data?.images?.[0] ||
      response?.url ||
      response?.image_url ||
      response?.outputs?.[0] ||
      "";

    if (!imageUrl) {
      throw new Error("Atlas Image generation did not return a valid image URL");
    }

    return {
      imageUrl,
      modelUsed: model,
      metadata: {
        modelUsed: model,
        startTime: startTimeStr,
        completionTime: completionTimeStr,
        durationMs,
        generationDurationSeconds: Math.round(durationMs / 1000),
      },
    };
  }
}

export const defaultImageService = new ImageService();

export async function generateImage(
  options: GenerateImageOptions
): Promise<GenerateImageResult> {
  return defaultImageService.generateImage(options);
}
