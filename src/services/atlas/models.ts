import { AtlasClient, defaultAtlasClient } from "./client";
import { AtlasModelInfo } from "./types";

const DEFAULT_ATLAS_MODELS: AtlasModelInfo[] = [
  {
    id: "bytedance/seedance-2.0-mini/text-to-video",
    name: "Seedance 2.0 Mini Text-to-Video",
    category: "video",
    provider: "ByteDance / Atlas Cloud",
    description: "Lowest-cost AtlasCloud video tier for short draft and batch generation",
    defaultDuration: 4,
    supportedAspectRatios: ["16:9", "9:16", "1:1"],
    maxPromptLength: 2000,
  },
  {
    id: "kling-v2.0",
    name: "Kling v2.0 AI Video Generator",
    category: "video",
    provider: "KwaiVGI / Atlas Cloud",
    description: "High motion fidelity, 4K realistic physics and temporal continuity",
    defaultDuration: 5,
    supportedAspectRatios: ["16:9", "9:16", "1:1"],
    maxPromptLength: 2000,
  },
  {
    id: "google-veo",
    name: "Google Veo 4K Cinema",
    category: "video",
    provider: "Google DeepMind / Atlas Cloud",
    description: "Ultra-high 4K realism and visual consistency",
    defaultDuration: 5,
    supportedAspectRatios: ["16:9", "9:16"],
    maxPromptLength: 2500,
  },
  {
    id: "runway-gen3",
    name: "Runway Gen-3 Alpha",
    category: "video",
    provider: "RunwayML / Atlas Cloud",
    description: "Artistic control and cinematic dynamic motion",
    defaultDuration: 5,
    supportedAspectRatios: ["16:9", "9:16"],
    maxPromptLength: 2000,
  },
  {
    id: "luma-dream-machine",
    name: "Luma Dream Machine",
    category: "video",
    provider: "Luma AI / Atlas Cloud",
    description: "Smooth camera motion and photorealistic lighting",
    defaultDuration: 5,
    supportedAspectRatios: ["16:9", "9:16", "1:1"],
    maxPromptLength: 2000,
  },
  {
    id: "seedream-3.0",
    name: "SeeDream 3.0 Image Generator",
    category: "image",
    provider: "Atlas Cloud",
    description: "High quality text-to-image concept render engine",
    supportedAspectRatios: ["16:9", "1:1", "4:3", "9:16"],
    maxPromptLength: 2000,
  },
  {
    id: "speech-tts-1",
    name: "Atlas Speech Synthesis",
    category: "speech",
    provider: "Atlas Cloud",
    description: "Multi-voice neural text-to-speech audio synthesis",
    maxPromptLength: 5000,
  },
];

export class ModelService {
  private client: AtlasClient;
  private cachedModels: AtlasModelInfo[] | null = null;
  private cacheTimestamp = 0;
  private readonly ttlMs: number;

  constructor(client?: AtlasClient, ttlMs = 300000) { // 5-minute cache TTL
    this.client = client || defaultAtlasClient;
    this.ttlMs = ttlMs;
  }

  public async getAvailableModels(forceRefresh = false): Promise<AtlasModelInfo[]> {
    const now = Date.now();
    if (!forceRefresh && this.cachedModels && now - this.cacheTimestamp < this.ttlMs) {
      return this.cachedModels;
    }

    try {
      const response = await this.client.request<{
        data?: AtlasModelInfo[];
        models?: AtlasModelInfo[];
      }>("/model/list", { method: "GET", modelForLogging: "modelsList" });

      const fetched = response?.data || response?.models;
      if (fetched && Array.isArray(fetched) && fetched.length > 0) {
        this.cachedModels = fetched;
        this.cacheTimestamp = now;
        return fetched;
      }
    } catch {
      // Fallback to default model manifest on network error
    }

    this.cachedModels = DEFAULT_ATLAS_MODELS;
    this.cacheTimestamp = now;
    return DEFAULT_ATLAS_MODELS;
  }
}

export const defaultModelService = new ModelService();

export async function getAvailableModels(forceRefresh = false): Promise<AtlasModelInfo[]> {
  return defaultModelService.getAvailableModels(forceRefresh);
}
