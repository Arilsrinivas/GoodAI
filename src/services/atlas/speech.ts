import { AtlasClient, defaultAtlasClient } from "./client";
import { GenerateSpeechOptions, GenerateSpeechResult } from "./types";

export class SpeechService {
  private client: AtlasClient;

  constructor(client?: AtlasClient) {
    this.client = client || defaultAtlasClient;
  }

  public async generateSpeech(
    options: GenerateSpeechOptions
  ): Promise<GenerateSpeechResult> {
    const startTimeStr = new Date().toISOString();
    const startMs = Date.now();

    const model = options.model || "speech-tts-1";
    const sanitizedText = this.client.sanitizePrompt(options.text);

    const payload = {
      model,
      text: sanitizedText,
      voice: options.voice || "en-US-Standard",
      speed: options.speed || 1.0,
    };

    const response = await this.client.request<{
      code?: number;
      data?: {
        audio_url?: string;
        url?: string;
      };
      audio_url?: string;
      url?: string;
    }>("/model/generateSpeech", {
      method: "POST",
      body: payload,
      modelForLogging: model,
    });

    const completionTimeStr = new Date().toISOString();
    const durationMs = Date.now() - startMs;

    const audioUrl =
      response?.data?.audio_url ||
      response?.data?.url ||
      response?.audio_url ||
      response?.url ||
      "";

    if (!audioUrl) {
      throw new Error("Atlas Speech generation response did not contain a valid audio URL");
    }

    return {
      audioUrl,
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

export const defaultSpeechService = new SpeechService();

export async function generateSpeech(
  options: GenerateSpeechOptions
): Promise<GenerateSpeechResult> {
  return defaultSpeechService.generateSpeech(options);
}
