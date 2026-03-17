/**
 * TypeScript types mirroring the FastAPI AnalyzeResponse schema.
 * These must stay in sync with server/app/schemas/prediction_schema.py
 */

export interface InfrastructureFeatures {
  tls_ssl_certificate?: number | null;
  qty_ip_resolved?: number | null;
  qty_nameservers?: number | null;
  qty_mx_servers?: number | null;
  ttl_hostname?: number | null;
  time_response?: number | null;
  domain_spf?: number | null;
  asn_ip?: number | null;
  time_domain_activation?: number | null;
  time_domain_expiration?: number | null;
  qty_redirects?: number | null;
  url_google_index?: number;
  domain_google_index?: number;
}

export interface DomainInfo {
  domain?: string | null;
  registrar?: string | null;
  creation_date?: string | null;
  expiration_date?: string | null;
  updated_date?: string | null;
  domain_age?: string | null;
  is_new_domain: boolean;
  is_expiring_soon: boolean;
  name_servers: string[];
  status: string[];
  country?: string | null;
  org?: string | null;
  whois_available: boolean;
  error?: string | null;
}

export interface EnsembleBreakdown {
  xgb_probability: number;
  nlp_probability: number;
  xgb_weight: number;
  nlp_weight: number;
  final_probability: number;
}

export interface AnalyzeResponse {
  url: string;
  prediction: string;   // "phishing" | "safe" | "invalid" | "unknown"
  label: number;         // 1 = phishing, 0 = safe, -1 = unknown
  confidence: number;    // 0–1
  risk_level: string;    // "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN"
  reason?: string | null;
  infrastructure?: InfrastructureFeatures | null;
  domain_info?: DomainInfo | null;
  ensemble_breakdown?: EnsembleBreakdown | null;
  degraded: boolean;
  latency_ms: number;
  model_version: string;
}

export interface MetricsResponse {
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1?: number;
  f1_score?: number;
  roc_auc?: number;
  model_file?: string;
  model?: string;
  dataset_size?: number;
  feature_count?: number;
  n_features?: number;
  trained_at?: string;
  confusion_matrix?: number[][];
  available_runs?: string[];
}
