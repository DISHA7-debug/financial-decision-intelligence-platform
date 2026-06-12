import axios from 'axios'
import type { AnalysisResult, ComparisonResult, ReportData, HealthStatus } from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export async function checkHealth(): Promise<HealthStatus> {
  const response = await client.get('/health')
  return response.data
}

export async function analyzeCompany(company: string): Promise<AnalysisResult> {
  const response = await client.post('/analyze', { company })
  return response.data
}

export async function compareCompanies(companies: string[]): Promise<ComparisonResult> {
  const response = await client.post('/compare', { companies })
  return response.data
}

export async function getCompanyReport(company: string): Promise<ReportData> {
  const response = await client.get(`/report/${company}`)
  return response.data
}

export async function getCommitteeReport(): Promise<ReportData> {
  const response = await client.get('/committee-report')
  return response.data
}

export default {
  checkHealth,
  analyzeCompany,
  compareCompanies,
  getCompanyReport,
  getCommitteeReport,
}
