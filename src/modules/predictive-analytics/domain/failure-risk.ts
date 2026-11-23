export interface PredictFeatures {
  airTemp: number;
  processTemp: number;
  rpm: number;
  torque: number;
  toolWear: number;
  productType: "L" | "M" | "H" | string;
}

export interface PredictResult {
  probability: number;
}

export interface FailureRiskPort {
  predict(features: PredictFeatures): Promise<PredictResult>;
  health(): Promise<boolean>;
}
