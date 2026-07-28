import {
  AtlasAPIError,
  AtlasAuthError,
  AtlasForbiddenError,
  AtlasNotFoundError,
  AtlasRateLimitError,
  AtlasServerError,
  AtlasTimeoutError,
  parseAtlasError,
} from "./errors";
import { AtlasConfig, RequestLogEntry } from "./types";

export class AtlasClient {
  private readonly baseUrl: string;
  private readonly apiKey: string;
  private readonly timeoutMs: number;
  private readonly maxRetries: number;

  constructor(config?: Partial<AtlasConfig>) {
    this.baseUrl = (
      config?.baseUrl ||
      process.env.ATLAS_BASE_URL ||
      process.env.ATLASCLOUD_MEDIA_BASE_URL ||
      "https://api.atlascloud.ai/api/v1"
    ).replace(/\/+$/, "");

    this.apiKey =
      config?.apiKey ||
      process.env.ATLAS_API_KEY ||
      process.env.ATLASCLOUD_API_KEY ||
      "";

    this.timeoutMs = config?.timeoutMs ?? 60000;
    this.maxRetries = config?.maxRetries ?? 3;
  }

  public getApiKey(): string {
    return this.apiKey;
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }

  public sanitizePrompt(prompt: string): string {
    if (!prompt) return "";
    return prompt
      .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, "")
      .trim();
  }

  private logRequest(entry: RequestLogEntry): void {
    const safeLog = { ...entry };
    if (safeLog.endpoint.includes("key=") || safeLog.endpoint.includes("token=")) {
      safeLog.endpoint = safeLog.endpoint.replace(/(key|token)=[^&]+/gi, "$1=REDACTED");
    }
    const logLine = `[AtlasClient ${safeLog.timestamp}] ${safeLog.endpoint} | Status: ${safeLog.statusCode || "N/A"} | Duration: ${safeLog.durationMs}ms | Model: ${safeLog.model || "N/A"}`;
    if (safeLog.status === "error") {
      console.error(`${logLine} | Error: ${safeLog.error}`);
    } else {
      console.log(logLine);
    }
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  public async request<T>(
    endpoint: string,
    options: {
      method?: string;
      body?: unknown;
      formData?: FormData;
      modelForLogging?: string;
      customTimeoutMs?: number;
    } = {}
  ): Promise<T> {
    if (!this.apiKey) {
      throw new AtlasAuthError("Atlas Cloud API key is not configured", endpoint);
    }

    const url = endpoint.startsWith("http") ? endpoint : `${this.baseUrl}${endpoint.startsWith("/") ? "" : "/"}${endpoint}`;
    const method = options.method || (options.body || options.formData ? "POST" : "GET");
    const timeout = options.customTimeoutMs ?? this.timeoutMs;

    let attempt = 0;
    let delay = 1000;

    while (attempt <= this.maxRetries) {
      attempt++;
      const startTime = Date.now();
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      try {
        const headers: Record<string, string> = {
          Authorization: `Bearer ${this.apiKey}`,
        };

        let reqBody: BodyInit | undefined = undefined;

        if (options.formData) {
          reqBody = options.formData;
        } else if (options.body) {
          headers["Content-Type"] = "application/json";
          reqBody = JSON.stringify(options.body);
        }

        const response = await fetch(url, {
          method,
          headers,
          body: reqBody,
          signal: controller.signal,
        });

        clearTimeout(timeoutId);
        const durationMs = Date.now() - startTime;

        if (!response.ok) {
          const status = response.status;
          let errText = "";
          try {
            errText = await response.text();
          } catch {}

          let parsedMessage = errText;
          try {
            const jsonErr = JSON.parse(errText);
            parsedMessage = jsonErr.message || jsonErr.detail || jsonErr.error || errText;
          } catch {}

          const errorObj = this.mapStatusToError(status, parsedMessage, endpoint);

          this.logRequest({
            timestamp: new Date().toISOString(),
            endpoint,
            model: options.modelForLogging,
            durationMs,
            statusCode: status,
            status: "error",
            error: errorObj.message,
          });

          // Check if retryable (429 rate limit or 5xx server error)
          const isRetryable = status === 429 || status >= 500;
          if (isRetryable && attempt <= this.maxRetries) {
            this.logRequest({
              timestamp: new Date().toISOString(),
              endpoint,
              model: options.modelForLogging,
              durationMs,
              statusCode: status,
              status: "retried",
              error: `Attempt ${attempt} failed with ${status}. Retrying in ${delay}ms...`,
            });
            await this.sleep(delay);
            delay *= 2;
            continue;
          }

          throw errorObj;
        }

        const data = (await response.json()) as T;
        this.logRequest({
          timestamp: new Date().toISOString(),
          endpoint,
          model: options.modelForLogging,
          durationMs,
          statusCode: response.status,
          status: "success",
        });

        return data;
      } catch (err) {
        clearTimeout(timeoutId);
        const durationMs = Date.now() - startTime;

        if (err instanceof AtlasAPIError) {
          throw err;
        }

        const atlasErr = parseAtlasError(err, endpoint);
        this.logRequest({
          timestamp: new Date().toISOString(),
          endpoint,
          model: options.modelForLogging,
          durationMs,
          status: "error",
          error: atlasErr.message,
        });

        const isNetworkOrTimeout = atlasErr instanceof AtlasTimeoutError || atlasErr.statusCode === 0;
        if (isNetworkOrTimeout && attempt <= this.maxRetries) {
          await this.sleep(delay);
          delay *= 2;
          continue;
        }

        throw atlasErr;
      }
    }

    throw new AtlasAPIError(`Failed request after ${this.maxRetries} attempts`, 0, endpoint);
  }

  private mapStatusToError(status: number, message: string, endpoint: string): AtlasAPIError {
    switch (status) {
      case 401:
        return new AtlasAuthError(message || "Unauthorized Atlas Cloud API Key", endpoint);
      case 403:
        return new AtlasForbiddenError(message || "Forbidden Atlas Cloud Resource", endpoint);
      case 404:
        return new AtlasNotFoundError(message || "Atlas Endpoint or Model Not Found", endpoint);
      case 429:
        return new AtlasRateLimitError(message || "Atlas Rate Limit Exceeded", endpoint);
      case 500:
      case 502:
      case 503:
      case 504:
        return new AtlasServerError(message || "Atlas Server Error", status, endpoint);
      default:
        return new AtlasAPIError(message || "Atlas API Request Failed", status, endpoint);
    }
  }
}

export const defaultAtlasClient = new AtlasClient();
