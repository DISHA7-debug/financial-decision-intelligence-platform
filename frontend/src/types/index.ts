export interface AnalysisResult {
  company: string
  recommendation: 'BUY' | 'HOLD' | 'AVOID'
  altman_z: number
  piotroski_f: number
  risk_classification: string
  ml_recommendation?: 'BUY' | 'HOLD' | 'AVOID'
  ml_confidence?: string
  identified_risks?: RiskItem[]
  revenue?: number
  net_income?: number
  gross_margin?: number
  current_ratio?: number
}

export interface RiskItem {
  risk: string
  severity: 'High' | 'Medium' | 'Low'
  summary: string
  evidence: string
}

export interface ComparisonResult {
  ranking: RankingItem[]
  comparison: ComparisonItem[]
}

export interface RankingItem {
  rank: number
  company: string
  revenue?: number
  growth?: number
  altman_z: number
  piotroski_f: number
  recommendation: string
  ml_recommendation?: string
  risk_classification?: string
}

export interface ComparisonItem {
  company: string
  metrics: {
    revenue?: number
    net_income?: number
    gross_margin?: number
    current_ratio?: number
    altman_z: number
    piotroski_f: number
  }
  recommendation: string
  risk_classification: string
}

export interface ReportData {
  title: string
  content: string
  report_path?: string
}

export interface HealthStatus {
  status: string
  timestamp?: string
}

export interface RecentCompany {
  company: string
  recommendation: string | null
  altmanZ: number | null
  piotroskiF: number | null
  riskClassification: string
}
