import { AtlasClient, defaultAtlasClient } from "./client";
import { AtlasValidationError } from "./errors";
import { UploadMediaOptions, UploadMediaResult } from "./types";

export class UploadService {
  private client: AtlasClient;
  private maxSizeBytes: number;

  constructor(client?: AtlasClient, maxSizeBytes = 52428800) { // Default 50MB
    this.client = client || defaultAtlasClient;
    this.maxSizeBytes = maxSizeBytes;
  }

  public async uploadMedia(
    options: UploadMediaOptions
  ): Promise<UploadMediaResult> {
    const formData = new FormData();
    const filename = options.filename || "upload.png";

    if (typeof Buffer !== "undefined" && Buffer.isBuffer(options.file)) {
      const uint8 = new Uint8Array(options.file);
      const blob = new Blob([uint8], { type: options.mimeType || "application/octet-stream" });
      if (blob.size > this.maxSizeBytes) {
        throw new AtlasValidationError(`File size exceeds max limit of ${this.maxSizeBytes / (1024 * 1024)}MB`);
      }
      formData.append("file", blob, filename);
    } else if (options.file instanceof Blob || (typeof File !== "undefined" && options.file instanceof File)) {
      if (options.file.size > this.maxSizeBytes) {
        throw new AtlasValidationError(`File size exceeds max limit of ${this.maxSizeBytes / (1024 * 1024)}MB`);
      }
      formData.append("file", options.file, filename);
    } else {
      throw new AtlasValidationError("Invalid file payload provided to uploadMedia");
    }

    const response = await this.client.request<{
      code?: number;
      data?: {
        url?: string;
        download_url?: string;
        filename?: string;
      };
      url?: string;
      download_url?: string;
    }>("/model/uploadMedia", {
      method: "POST",
      formData,
      modelForLogging: "uploadMedia",
    });

    const url =
      response?.data?.url ||
      response?.data?.download_url ||
      response?.url ||
      response?.download_url ||
      "";

    if (!url) {
      throw new Error("Atlas uploadMedia response did not contain a valid URL");
    }

    return {
      url,
      filename,
    };
  }
}

export const defaultUploadService = new UploadService();

export async function uploadMedia(
  options: UploadMediaOptions
): Promise<UploadMediaResult> {
  return defaultUploadService.uploadMedia(options);
}
