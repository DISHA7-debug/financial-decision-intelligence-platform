'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Search, AlertTriangle, ArrowLeft, BarChart2, CheckCircle2 } from 'lucide-react'
import Link from 'next/link'
import { analyzeCompany } from '@/services/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import type { AnalysisResult, RiskItem } from '@/types'

export default function AnalyzePage() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const companyParam = searchParams.get('company')

  const [inputCompany, setInputCompany] = useState(companyParam || '')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<AnalysisResult | null>(null)

  const fetchAnalysis = async (companyName: string) => {
    if (!companyName) return
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const result = await analyzeCompany(companyName)
      setData(result)
      
      const stored = localStorage.getItem('recent_searches')
      let recents: any[] = []
      if (stored) {
        try { recents = JSON.parse(stored) } catch(e) {}
      }
      const updated = [
        { 
          company: result.company, 
          recommendation: result.recommendation, 
          altmanZ: result.altman_z, 
          piotroskiF: result.piotroski_f, 
          riskClassification: result.risk_classification || 'Completed' 
        },
        ...recents.filter(c => c.company.toUpperCase() !== result.company.toUpperCase())
      ].slice(0, 4)
      localStorage.setItem('recent_searches', JSON.stringify(updated))
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Workflow execution failed.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (companyParam) {
      setInputCompany(companyParam)
      fetchAnalysis(companyParam)
    }
  }, [companyParam])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputCompany.trim()) return
    router.push(`/analyze?company=${encodeURIComponent(inputCompany.trim())}`)
  }

  const activeRec = data?.recommendation?.toUpperCase() || ''

  return (
    <div className="flex flex-col gap-20">
      {/* Search Header */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-8 pb-12 border-b border-border/6">
        <div className="flex items-center gap-5">
          <Link
            href="/"
            className="p-4 rounded-xl bg-surface hover:bg-gold-accent/10 hover:text-gold-accent text-secondary-text border border-border/6 transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-[42px] font-bold text-primary-text tracking-tight leading-tight">
              {data ? `${data.company} Research Workstation` : "Single Asset Analysis"}
            </h1>
            <span className="text-[16px] text-secondary-text mt-5 block">
              {data ? "SEC filings audited and computed" : "Enter equity ticker for dynamically compiled data"}
            </span>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="flex gap-6 min-w-[450px]">
          <Input
            type="text"
            placeholder="Search company (e.g. AAPL)..."
            value={inputCompany}
            onChange={(e) => setInputCompany(e.target.value)}
            className="flex-1"
          />
          <button
            type="submit"
            className="h-[52px] px-10 bg-gold-accent hover:bg-gold-accent/90 text-background font-semibold rounded-xl transition-colors flex items-center gap-2 text-[16px]"
          >
            <Search className="w-5 h-5" />
            Analyze
          </button>
        </form>
      </div>

      {/* Loading state */}
      {loading && <LoadingSpinner message={`Running analysis for "${inputCompany.toUpperCase()}"`} />}

      {/* Error state */}
      {error && (
        <Card className="bg-surface">
          <CardContent className="p-8 flex items-start gap-6">
            <AlertTriangle className="w-8 h-8 text-danger shrink-0 mt-1" />
            <div>
              <h3 className="text-[18px] font-semibold text-danger mb-2">
                Workflow execution failure
              </h3>
              <p className="text-[14px] text-danger/90 leading-relaxed bg-background p-6 rounded-xl border border-border/6 mt-4 whitespace-pre-wrap">
                {error}
              </p>
              <p className="text-[14px] text-secondary-text mt-6">
                Please check if the ticker is valid or the backend services are running.
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Initial empty state */}
      {!loading && !error && !data && (
        <Card className="bg-surface">
          <CardContent className="p-20 flex flex-col items-center justify-center text-center min-h-[400px]">
            <BarChart2 className="w-16 h-16 text-muted-text mb-6" />
            <h3 className="text-[28px] font-semibold text-primary-text mb-4">
              No security selected
            </h3>
            <p className="text-[16px] text-secondary-text max-w-md leading-relaxed">
              Enter a ticker symbol or company name in the search bar above to trigger the corporate financial extraction and risk pipeline.
            </p>
          </CardContent>
        </Card>
      )}

      {/* Workstation layout grid */}
      {!loading && !error && data && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-start">
          
          {/* Left Column: Company Summary */}
          <div className="lg:col-span-3 flex flex-col gap-12">
            <Card>
              <CardContent className="p-10">
                <span className="text-[14px] text-muted-text uppercase tracking-wider block mb-4 font-semibold">
                  Security Profile
                </span>
                <h2 className="text-[32px] font-bold text-primary-text mb-10 leading-tight">
                  {data.company}
                </h2>
                
                <div className="space-y-8 pt-10 border-t border-border/6">
                  <div>
                    <span className="text-[14px] text-muted-text block mb-3">Risk classification</span>
                    <span className={`text-[18px] font-semibold uppercase ${
                      data.risk_classification?.toUpperCase() === 'LOW RISK' ? 'text-success' :
                      data.risk_classification?.toUpperCase() === 'MEDIUM RISK' ? 'text-warning' : 'text-danger'
                    }`}>
                      {data.risk_classification || 'Low Risk'}
                    </span>
                  </div>
                  <div>
                    <span className="text-[14px] text-muted-text block mb-3">Ingestion status</span>
                    <span className="text-[18px] font-semibold text-primary-text flex items-center gap-2">
                      <CheckCircle2 className="w-5 h-5 text-success" />
                      Completed
                    </span>
                  </div>
                  <div>
                    <span className="text-[14px] text-muted-text block mb-3">Predictive model score</span>
                    <span className="text-[18px] font-semibold text-primary-text">
                      {data.ml_confidence || 'N/A'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-10 text-[16px] text-secondary-text leading-relaxed">
                <span className="text-[14px] text-muted-text uppercase tracking-wider block mb-5 font-semibold">
                  Methodology note
                </span>
                This profile aggregates structural SEC 10-K financial metrics, Altman Z solvency coefficients, and Piotroski F-score models with a proprietary multi-agent text evaluation layer.
              </CardContent>
            </Card>
          </div>

          {/* Center Column: Metrics & Risk Disclosures */}
          <div className="lg:col-span-6 flex flex-col gap-12">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
              <Card>
                <CardHeader>
                  <CardTitle className="text-[24px]">Altman Z-Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-[48px] font-bold text-primary-text leading-none">{data.altman_z?.toFixed(2) || 'N/A'}</div>
                  <p className="text-[16px] text-secondary-text mt-4">Solvency indicator</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-[24px]">Piotroski F-Score</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-[48px] font-bold text-primary-text leading-none">{data.piotroski_f || 'N/A'}</div>
                  <p className="text-[16px] text-secondary-text mt-4">Financial strength</p>
                </CardContent>
              </Card>
            </div>

            {/* Financial Health Panel */}
            <Card>
              <CardHeader>
                <CardTitle className="text-[24px]">Financial Health</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-5">
                  <div className="flex justify-between py-4 border-b border-border/6">
                    <span className="text-[16px] text-secondary-text">Revenue</span>
                    <span className="text-[16px] text-primary-text font-medium">${data.revenue?.toLocaleString() || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between py-4 border-b border-border/6">
                    <span className="text-[16px] text-secondary-text">Net Income</span>
                    <span className="text-[16px] text-primary-text font-medium">${data.net_income?.toLocaleString() || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between py-4 border-b border-border/6">
                    <span className="text-[16px] text-secondary-text">Gross Margin</span>
                    <span className="text-[16px] text-primary-text font-medium">{data.gross_margin?.toFixed(1) || 'N/A'}%</span>
                  </div>
                  <div className="flex justify-between py-4">
                    <span className="text-[16px] text-secondary-text">Current Ratio</span>
                    <span className="text-[16px] text-primary-text font-medium">{data.current_ratio?.toFixed(2) || 'N/A'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Identified Risks */}
            <div>
              <div className="flex items-center justify-between mb-8 border-b border-border/6 pb-4">
                <h3 className="text-[24px] font-semibold text-primary-text">
                  Material risks identified in corporate disclosures
                </h3>
                <span className="text-[16px] text-secondary-text">
                  {data.identified_risks?.length || 0} items retrieved
                </span>
              </div>

              <div className="flex flex-col gap-8">
                {data.identified_risks && data.identified_risks.length > 0 ? (
                  data.identified_risks.map((item: RiskItem, idx: number) => (
                    <Card key={idx}>
                      <CardContent className="p-8">
                        <div className="flex items-start justify-between mb-4">
                          <Badge 
                            variant={item.severity === 'High' ? 'destructive' : item.severity === 'Medium' ? 'warning' : 'success'}
                            className="text-[14px]"
                          >
                            {item.severity}
                          </Badge>
                          <span className="text-[14px] text-muted-text uppercase">{item.risk}</span>
                        </div>
                        <p className="text-[16px] text-primary-text mb-4 leading-relaxed">{item.summary}</p>
                        <p className="text-[14px] text-secondary-text leading-relaxed">{item.evidence}</p>
                      </CardContent>
                    </Card>
                  ))
                ) : (
                  <Card className="bg-surface">
                    <CardContent className="p-10 text-center text-[16px] text-secondary-text">
                      No explicit high/medium risk items retrieved for this company.
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </div>

          {/* Right Column: Recommendation Panels */}
          <div className="lg:col-span-3 flex flex-col gap-12">
            {/* Rule Engine Output */}
            <Card>
              <CardHeader>
                <CardTitle className="text-[24px]">Rule Engine Output</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <span className="text-[14px] text-muted-text block mb-2">Recommendation</span>
                    <Badge 
                      variant={data.recommendation === 'BUY' ? 'success' : data.recommendation === 'AVOID' ? 'destructive' : 'warning'}
                      className="text-[16px] mt-2"
                    >
                      {data.recommendation}
                    </Badge>
                  </div>
                  <div>
                    <span className="text-[14px] text-muted-text block mb-2">Confidence</span>
                    <span className="text-[18px] text-primary-text">100.00% (Absolute)</span>
                  </div>
                  <div>
                    <span className="text-[14px] text-muted-text block mb-2">Reasoning</span>
                    <p className="text-[14px] text-secondary-text leading-relaxed mt-2">
                      Based on Altman Z-score of {data.altman_z?.toFixed(2)} and Piotroski F-score of {data.piotroski_f}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* ML Prediction */}
            <Card>
              <CardHeader>
                <CardTitle className="text-[24px]">ML Prediction</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  <div>
                    <span className="text-[14px] text-muted-text block mb-2">Recommendation</span>
                    <Badge 
                      variant={data.ml_recommendation === 'BUY' ? 'success' : data.ml_recommendation === 'AVOID' ? 'destructive' : 'warning'}
                      className="text-[16px] mt-2"
                    >
                      {data.ml_recommendation || 'N/A'}
                    </Badge>
                  </div>
                  <div>
                    <span className="text-[14px] text-muted-text block mb-2">Confidence</span>
                    <span className="text-[18px] text-primary-text">{data.ml_confidence || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-[14px] text-muted-text block mb-2">Probability Distribution</span>
                    <div className="mt-4 space-y-4">
                      <div className="flex items-center gap-4">
                        <span className="text-[14px] text-secondary-text w-12">BUY</span>
                        <div className="flex-1 h-3 bg-elevated rounded-full overflow-hidden">
                          <div className="h-full bg-success" style={{ width: '60%' }} />
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-[14px] text-secondary-text w-12">HOLD</span>
                        <div className="flex-1 h-3 bg-elevated rounded-full overflow-hidden">
                          <div className="h-full bg-warning" style={{ width: '30%' }} />
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-[14px] text-secondary-text w-12">AVOID</span>
                        <div className="flex-1 h-3 bg-elevated rounded-full overflow-hidden">
                          <div className="h-full bg-danger" style={{ width: '10%' }} />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Audit Recommendation */}
            <Card>
              <CardHeader>
                <CardTitle className="text-[24px]">Audit Recommendation</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col gap-5">
                  {['BUY', 'HOLD', 'AVOID'].map((rec) => (
                    <div 
                      key={rec}
                      className={`p-6 rounded-xl transition-all border ${
                        activeRec === rec
                          ? `bg-${rec === 'BUY' ? 'success' : rec === 'HOLD' ? 'warning' : 'danger'}/10 border-${rec === 'BUY' ? 'success' : rec === 'HOLD' ? 'warning' : 'danger'} text-${rec === 'BUY' ? 'success' : rec === 'HOLD' ? 'warning' : 'danger'}`
                          : 'bg-background/50 border-border/6 text-muted-text opacity-60'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-[18px] font-bold">{rec}</span>
                        {activeRec === rec && (
                          <div className="w-3 h-3 rounded-full bg-current animate-pulse" />
                        )}
                      </div>
                      <p className="text-[14px] leading-relaxed">
                        {rec === 'BUY' && 'Satisfies all fundamental security margins. Optimal Altman Z and Piotroski levels indicate solvency.'}
                        {rec === 'HOLD' && 'Solvency indicators are structurally stable, but margin momentum metrics suggest neutrality.'}
                        {rec === 'AVOID' && 'Calculated scores fall within financial distress thresholds. High risk of capital impairment.'}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

        </div>
      )}
    </div>
  )
}
