export type AnalysisMode = "Explosiveness" | "Power" | "Velocity" | "Technique";

export type MetricKey =
  | "rep_speed"
  | "power"
  | "time_to_peak_velocity"
  | "back_rounding"
  | "rep_duration";

export interface MetricOption {
  key: MetricKey;
  label: string;
}

export interface VideoItem {
  id: string;
  label: string;
  source_filename: string;
  processed_filename: string;
}
