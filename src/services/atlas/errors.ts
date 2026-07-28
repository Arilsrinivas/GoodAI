export class AtlasAPIError extends Error {
  public readonly statusCode?: number;
  public readonly endpoint?: string;
  public readonly details?: unknown;

  constructor(message: string, statusCode?: number, endpoint?: string, details?: unknown) {
    super(message);
    this.name = "AtlasAPIError";
    this.statusCode = statusCode;
    this.endpoint = endpoint;
    this.details = details;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class AtlasAuthError extends AtlasAPIError {
  constructor(message = "Unauthorized Atlas Cloud API key", endpoint?: string, details?: unknown) {
    super(message, 401, endpoint, details);
    this.name = "AtlasAuthError";
  }
}

export class AtlasForbiddenError extends AtlasAPIError {
  constructor(message = "Access forbidden for Atlas Cloud resource", endpoint?: string, details?: unknown) {
    super(message, 403, endpoint, details);
    this.name = "AtlasForbiddenError";
  }
}

export class AtlasNotFoundError extends AtlasAPIError {
  constructor(message = "Requested Atlas Cloud model or endpoint not found", endpoint?: string, details?: unknown) {
    super(message, 404, endpoint, details);
    this.name = "AtlasNotFoundError";
  }
}

export class AtlasRateLimitError extends AtlasAPIError {
  constructor(message = "Atlas Cloud API rate limit exceeded (429)", endpoint?: string, details?: unknown) {
    super(message, 429, endpoint, details);
    this.name = "AtlasRateLimitError";
  }
}

export class AtlasServerError extends AtlasAPIError {
  constructor(message = "Atlas Cloud internal server error (500)", statusCode = 500, endpoint?: string, details?: unknown) {
    super(message, statusCode, endpoint, details);
    this.name = "AtlasServerError";
  }
}

export class AtlasTimeoutError extends AtlasAPIError {
  constructor(message = "Atlas Cloud API request timed out", endpoint?: string) {
    super(message, 408, endpoint);
    this.name = "AtlasTimeoutError";
  }
}

export class AtlasValidationError extends AtlasAPIError {
  constructor(message: string, endpoint?: string, details?: unknown) {
    super(message, 422, endpoint, details);
    this.name = "AtlasValidationError";
  }
}

export function parseAtlasError(error: unknown, endpoint?: string): AtlasAPIError {
  if (error instanceof AtlasAPIError) {
    return error;
  }
  if (error && typeof error === "object" && "status" in error) {
    const status = Number((error as { status?: number }).status);
    const msg = (error as { message?: string }).message || "Atlas API Error";
    if (status === 401) return new AtlasAuthError(msg, endpoint, error);
    if (status === 403) return new AtlasForbiddenError(msg, endpoint, error);
    if (status === 404) return new AtlasNotFoundError(msg, endpoint, error);
    if (status === 429) return new AtlasRateLimitError(msg, endpoint, error);
    if (status >= 500) return new AtlasServerError(msg, status, endpoint, error);
    return new AtlasAPIError(msg, status, endpoint, error);
  }
  if (error instanceof Error) {
    if (error.name === "AbortError" || error.message.includes("timeout")) {
      return new AtlasTimeoutError(error.message, endpoint);
    }
    return new AtlasAPIError(error.message, 0, endpoint, error);
  }
  return new AtlasAPIError("Unknown Atlas Cloud error occurred", 0, endpoint, error);
}
