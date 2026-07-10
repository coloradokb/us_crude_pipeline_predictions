export type PredictionRow = {
  series: string;
  target_period: string;
  prediction: number;
  actual: number | null;
  value_error: number | null;
  error_rate: number | null;
  model_name: string;
  model_version: string;
  created_at: string;
  source_data_through_period: string;
};
