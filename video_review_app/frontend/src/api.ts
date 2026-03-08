import type { AnalysisMode, MetricKey, VideoItem } from "./types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export function getVideoUrl(videoId: string): string {
  return `${API_BASE_URL}/video/${encodeURIComponent(videoId)}`;
}

export async function fetchVideos(): Promise<VideoItem[]> {
  const response = await fetch(`${API_BASE_URL}/videos`);
  if (!response.ok) {
    throw new Error(`Failed to load videos (${response.status})`);
  }
  return response.json() as Promise<VideoItem[]>;
}

interface StatsRequest {
  videoId: string;
  videoLabel: string;
  processedFilename: string;
  selectedMetrics: MetricKey[];
}

interface StatsPreviewResponse {
  text: string;
  row_count: number;
  metric_labels: string[];
}

export async function fetchStatsPreview(request: StatsRequest): Promise<StatsPreviewResponse> {
  const response = await fetch(`${API_BASE_URL}/stats-preview`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      video_id: request.videoId,
      video_label: request.videoLabel,
      processed_filename: request.processedFilename,
      selected_metrics: request.selectedMetrics,
    }),
  });

  if (!response.ok) {
    throw new Error(`Stats preview failed (${response.status})`);
  }

  return response.json() as Promise<StatsPreviewResponse>;
}

interface StreamRequest {
  videoId: string;
  videoLabel: string;
  processedFilename: string;
  mode: AnalysisMode;
  selectedMetrics: MetricKey[];
}

export async function streamAnalysis(
  request: StreamRequest,
  onChunk: (chunk: string) => void,
  signal?: AbortSignal,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      video_id: request.videoId,
      video_label: request.videoLabel,
      processed_filename: request.processedFilename,
      mode: request.mode,
      selected_metrics: request.selectedMetrics,
    }),
    signal,
  });

  if (!response.ok || !response.body) {
    throw new Error(`Analysis stream failed (${response.status})`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }

    if (value) {
      onChunk(decoder.decode(value, { stream: true }));
    }
  }

  const finalChunk = decoder.decode();
  if (finalChunk) {
    onChunk(finalChunk);
  }
}
