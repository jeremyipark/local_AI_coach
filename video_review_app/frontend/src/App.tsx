import { useEffect, useMemo, useRef, useState } from "react";

import { fetchStatsPreview, fetchVideos, getVideoUrl, streamAnalysis } from "./api";
import type { MetricKey, MetricOption, VideoItem } from "./types";

const ANALYSIS_MODE = "Technique" as const;
const MODEL_LABEL = import.meta.env.VITE_MODEL_LABEL ?? "Qwen 2.5 3B";

const METRICS: MetricOption[] = [
  { key: "rep_speed", label: "Rep speed (m/s)" },
  { key: "power", label: "Power" },
  { key: "time_to_peak_velocity", label: "Time to peak velocity" },
  { key: "back_rounding", label: "Rounded back" },
  { key: "rep_duration", label: "Rep duration" },
];

const DEFAULT_SELECTED_METRICS: MetricKey[] = [
  "rep_speed",
  "power",
  "time_to_peak_velocity",
  "back_rounding",
];

function stripMarkdown(text: string): string {
  return text
    .replace(/\\n/g, "\n")
    .replace(/```[a-zA-Z]*\n?/g, "")
    .replace(/```/g, "")
    .replace(/^#{1,6}\s+/gm, "")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\*(.*?)\*/g, "$1")
    .replace(/`([^`]+)`/g, "$1")
    .replace(/\[(.*?)\]\((.*?)\)/g, "$1")
    .replace(/^>\s?/gm, "")
    .replace(/^\s*[-*+]\s+/gm, "- ");
}

function App() {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [loadingVideos, setLoadingVideos] = useState(true);
  const [videosError, setVideosError] = useState<string | null>(null);

  const [selectedVideoId, setSelectedVideoId] = useState<string | null>(null);
  const [selectedMetrics, setSelectedMetrics] = useState<MetricKey[]>(DEFAULT_SELECTED_METRICS);

  const [analysisText, setAnalysisText] = useState<string>("");
  const [analysisError, setAnalysisError] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [videoError, setVideoError] = useState<string | null>(null);
  const [rawStatsText, setRawStatsText] = useState<string>("");
  const [rawStatsError, setRawStatsError] = useState<string | null>(null);
  const [isLoadingRawStats, setIsLoadingRawStats] = useState(false);

  const streamAbortRef = useRef<AbortController | null>(null);
  const analysisScrollRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function loadVideos() {
      try {
        const data = await fetchVideos();
        if (!isMounted) {
          return;
        }

        setVideos(data);
        setSelectedVideoId((current) => current ?? data[0]?.id ?? null);
      } catch (error) {
        if (!isMounted) {
          return;
        }
        setVideosError(error instanceof Error ? error.message : "Unable to load videos.");
      } finally {
        if (isMounted) {
          setLoadingVideos(false);
        }
      }
    }

    void loadVideos();

    return () => {
      isMounted = false;
      streamAbortRef.current?.abort();
    };
  }, []);

  useEffect(() => {
    const box = analysisScrollRef.current;
    if (box) {
      box.scrollTop = box.scrollHeight;
    }
  }, [analysisText, isStreaming]);

  useEffect(() => {
    setVideoError(null);
  }, [selectedVideoId]);

  const selectedVideo = useMemo(
    () => videos.find((video) => video.id === selectedVideoId) ?? null,
    [videos, selectedVideoId],
  );
  const displayAnalysisText = useMemo(() => stripMarkdown(analysisText), [analysisText]);
  const combinedText = useMemo(() => {
    const blocks: string[] = [];
    if (rawStatsText) {
      blocks.push(rawStatsText);
    }
    if (displayAnalysisText) {
      blocks.push(`Coach interpretation\n${displayAnalysisText}`);
    }
    return blocks.join("\n\n");
  }, [rawStatsText, displayAnalysisText]);

  useEffect(() => {
    let active = true;

    async function loadRawStats() {
      if (!selectedVideo || selectedMetrics.length === 0) {
        setRawStatsText("");
        setRawStatsError(null);
        return;
      }

      setIsLoadingRawStats(true);
      setRawStatsError(null);
      try {
        const response = await fetchStatsPreview({
          videoId: selectedVideo.id,
          videoLabel: selectedVideo.label,
          processedFilename: selectedVideo.processed_filename,
          selectedMetrics,
        });
        if (!active) {
          return;
        }
        setRawStatsText(response.text);
      } catch (error) {
        if (!active) {
          return;
        }
        setRawStatsText("");
        setRawStatsError(error instanceof Error ? error.message : "Failed to load raw stats.");
      } finally {
        if (active) {
          setIsLoadingRawStats(false);
        }
      }
    }

    void loadRawStats();
    return () => {
      active = false;
    };
  }, [selectedVideo, selectedMetrics]);

  useEffect(() => {
    setAnalysisText("");
    setAnalysisError(null);
  }, [selectedVideoId, selectedMetrics]);

  function toggleMetric(metric: MetricKey) {
    setSelectedMetrics((current) => {
      if (current.includes(metric)) {
        return current.filter((item) => item !== metric);
      }
      return [...current, metric];
    });
  }

  async function handleAnalyze() {
    if (!selectedVideo || isStreaming) {
      return;
    }

    streamAbortRef.current?.abort();
    const controller = new AbortController();
    streamAbortRef.current = controller;

    setAnalysisText("");
    setAnalysisError(null);
    setIsStreaming(true);

    try {
      await streamAnalysis(
        {
          videoId: selectedVideo.id,
          videoLabel: selectedVideo.label,
          processedFilename: selectedVideo.processed_filename,
          mode: ANALYSIS_MODE,
          selectedMetrics,
        },
        (chunk) => {
          setAnalysisText((previous) => previous + chunk);
        },
        controller.signal,
      );
    } catch (error) {
      if ((error as DOMException).name === "AbortError") {
        return;
      }
      setAnalysisError(error instanceof Error ? error.message : "Analysis stream failed.");
    } finally {
      setIsStreaming(false);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <h1>Local AI Coach</h1>
      </header>

      <main className="panel-grid">
        <section className="card left-panel">
          <div className="section-header">
            <h2>Session Videos</h2>
            <span className="meta">{videos.length} matched</span>
          </div>

          <div className="video-list" role="listbox" aria-label="Matched deadlift videos">
            {loadingVideos && <p className="hint">Loading videos...</p>}
            {!loadingVideos && videos.length === 0 && (
              <p className="hint">No matched `_stitched` processed videos were found.</p>
            )}
            {videosError && <p className="error">{videosError}</p>}

            {videos.map((video) => (
              <button
                key={video.id}
                type="button"
                className={`video-item ${selectedVideo?.id === video.id ? "active" : ""}`}
                onClick={() => setSelectedVideoId(video.id)}
              >
                <div>
                  <strong>{video.label}</strong>
                  <span>{video.processed_filename}</span>
                </div>
              </button>
            ))}
          </div>

          <div className="player-wrap">
            {selectedVideo ? (
              <video
                key={selectedVideo.id}
                className="player"
                controls
                preload="metadata"
                src={getVideoUrl(selectedVideo.id)}
                onLoadedData={() => setVideoError(null)}
                onError={() =>
                  setVideoError(
                    "Video failed to load. Backend may still be transcoding, or the source file is corrupted.",
                  )
                }
              />
            ) : (
              <div className="player-empty">Select a video to preview.</div>
            )}
          </div>
          {videoError && <p className="error">{videoError}</p>}
        </section>

        <aside className="card right-panel">
          <div className="section-header">
            <h2>AI Coach</h2>
            <span className="meta">Running {MODEL_LABEL}</span>
          </div>

          <div className="metric-wrap">
            <p className="metric-title">Prompt metrics</p>
            <div className="metric-row" role="group" aria-label="Prompt metric filters">
              {METRICS.map((metric) => (
                <button
                  key={metric.key}
                  type="button"
                  className={`metric-chip ${selectedMetrics.includes(metric.key) ? "active" : ""}`}
                  onClick={() => toggleMetric(metric.key)}
                  disabled={isStreaming}
                >
                  {metric.label}
                </button>
              ))}
            </div>
          </div>

          <div ref={analysisScrollRef} className="analysis-box" aria-live="polite">
            {!combinedText && !isStreaming && !isLoadingRawStats && (
              <p className="hint">
                Choose a video and metrics to load ground truth stats, then click Analyze.
              </p>
            )}
            {isLoadingRawStats && <p className="hint">Loading ground truth stats...</p>}
            {combinedText && <p className="analysis-text">{combinedText}</p>}
            {isStreaming && <span className="typing-cursor" aria-hidden="true" />}
            {rawStatsError && <p className="error">{rawStatsError}</p>}
            {analysisError && <p className="error">{analysisError}</p>}
          </div>

          <button
            type="button"
            className="analyze-button"
            onClick={() => void handleAnalyze()}
            disabled={!selectedVideo || isStreaming || selectedMetrics.length === 0}
          >
            {isStreaming ? "Analyzing..." : "Analyze"}
          </button>
        </aside>
      </main>
    </div>
  );
}

export default App;
