'use client'

import { useState, useEffect } from 'react'
import { GitCompare, Plus, X, AlertTriangle, Award, Scale, ShieldCheck } from 'lucide-react'
import { compareCompanies } from '@/services/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import type { ComparisonResult } from '@/types'

export default function ComparePage() {
  const [tickerInput, setTickerInput] = useState('')
  const [companies, setCompanies] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [data, setData] = useState<ComparisonResult | null>(null)

  useEffect(() => {
    const stored = localStorage.getItem('comparison_tickers')
    if (stored) {
      try {
        setCompanies(JSON.parse(stored))
      } catch (e) {}
    }
  }, [])

  const handleAddCompany = (e: React.FormEvent) => {
    e.preventDefault()
    const ticker = tickerInput.trim().toUpperCase()
    if (!ticker) return
    if (companies.includes(ticker)) {
      setTickerInput('')
      return
    }

    const updated = [...companies, ticker]
    setCompanies(updated)
    localStorage.setItem('comparison_tickers', JSON.stringify(updated))
    setTickerInput('')
  }

  const handleRemoveCompany = (ticker: string) => {
    const updated = companies.filter((c) => c !== ticker)
    setCompanies(updated)
    localStorage.setItem('comparison_tickers', JSON.stringify(updated))
  }

  const handleCompare = async () => {
    if (companies.length === 0) return
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const result = await compareCompanies(companies)
      setData(result)
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Comparison execution failed.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Title */}
      <div className="pb-10 flex items-center gap-5 border-b border-border/6">
        <div className="p-5 rounded-xl bg-surface border border-border/6">
          <GitCompare className="w-5 h-5 text-gold-accent" />
        </div>
        <div>
          <h1 className="text-[42px] font-bold text-primary-text tracking-tight uppercase leading-tight">
            Asset Portfolio Comparison
          </h1>
          <span className="text-[16px] text-secondary-text mt-5 block">
            Compare multiple tickers side-by-side
          </span>
        </div>
      </div>

      {/* Selector Console */}
        <Card>
        <CardHeader>
          <CardTitle className="text-[24px]">Configure assets to rank</CardTitle>
        </CardHeader>
        <CardContent className="px-4 py-3">
          <div className="flex flex-col md:flex-row gap-8 md:items-center">
            <form onSubmit={handleAddCompany} className="flex items-center gap-6 shrink-0 w-full md:w-96">
              <Input
                type="text"
                placeholder="Enter ticker (e.g. TSLA)..."
                value={tickerInput}
                onChange={(e) => setTickerInput(e.target.value)}
                className="flex-1"
              />
              <button
                type="submit"
                className="h-[48px] px-5 bg-elevated border border-border/6 hover:bg-surface text-primary-text font-semibold rounded-xl transition-colors flex items-center gap-2 text-[16px]"
              >
                <Plus className="w-4 h-4" />
                Add
              </button>
            </form>

            {/* Active Chips */}
            <div className="flex flex-wrap items-center gap-4 flex-1 bg-background p-5 rounded-xl border border-border/6 min-h-[72px]">
              {companies.length === 0 ? (
                <span className="text-[14px] text-muted-text italic px-4">
                  No companies configured. Enter ticker and click add.
                </span>
              ) : (
                companies.map((c) => (
                  <span 
                    key={c}
                    className="inline-flex items-center gap-3 px-[18px] py-[10px] rounded-lg bg-surface border border-border/6 text-primary-text text-[14px] font-semibold uppercase tracking-wide"
                  >
                    {c}
                    <button 
                      onClick={() => handleRemoveCompany(c)}
                      className="p-2.5 hover:bg-elevated rounded text-secondary-text hover:text-danger transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </span>
                ))
              )}
            </div>
          </div>

          <div className="mt-10 flex items-center justify-between gap-4 pt-8 border-t border-border/6">
            <span className="text-[14px] text-muted-text">
              Evaluating financial portfolio strategies
            </span>
            <button
              onClick={handleCompare}
              disabled={companies.length === 0 || loading}
              className="h-[44px] px-6 bg-gold-accent hover:bg-gold-accent/90 disabled:bg-elevated disabled:text-muted-text text-background font-bold uppercase tracking-wider rounded-xl transition-all text-[16px]"
            >
              Execute comparison
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Loading state */}
      {loading && <LoadingSpinner message="Initiating comparative financial analysis..." />}

      {/* Error state */}
      {error && (
          <Card className="bg-surface">
          <CardContent className="p-6 flex items-start gap-8">
            <AlertTriangle className="w-8 h-8 text-danger shrink-0 mt-1" />
            <div>
              <h3 className="text-[18px] font-semibold text-danger mb-3">
                Comparison workflow failure
              </h3>
              <p className="text-[14px] text-danger bg-background p-6 rounded-xl border border-border/6 mt-5 whitespace-pre-wrap">
                {error}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Comparative Display */}
      {!loading && !error && data && (
        <div className="flex flex-col gap-8">
          {/* Ranking Table */}
          <Card>
              <CardHeader>
                <CardTitle className="text-[24px]">Portfolio Ranking</CardTitle>
              </CardHeader>
              <CardContent className="px-4 py-3">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border/6">
                      <th className="text-left align-middle text-[14px] font-semibold text-secondary-text py-6 px-8">Rank</th>
                      <th className="text-left align-middle text-[14px] font-semibold text-secondary-text py-6 px-8">Company</th>
                      <th className="text-left align-middle text-[14px] font-semibold text-secondary-text py-6 px-8">Revenue</th>
                      <th className="text-left align-middle text-[14px] font-semibold text-secondary-text py-6 px-8">Growth</th>
                      <th className="text-left align-middle text-[14px] font-semibold text-secondary-text py-6 px-8">Altman Z</th>
                      <th className="text-left align-middle text-[14px] font-semibold text-secondary-text py-6 px-8">Piotroski</th>
                      <th className="text-left align-middle text-[14px] font-semibold text-secondary-text py-6 px-8">Recommendation</th>
                      <th className="text-left align-middle text-[14px] font-semibold text-secondary-text py-6 px-8">ML Rec</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.ranking.map((item, idx) => (
                      <tr 
                        key={idx}
                        className={`border-b border-border/6 hover:bg-surface/50 transition-colors ${
                          idx === 0 ? 'bg-gold-accent/5' : ''
                        }`}
                      >
                        <td className="py-6 px-8 align-middle">
                          {idx === 0 ? (
                            <Badge variant="gold" className="text-[14px]">#{item.rank}</Badge>
                          ) : (
                            <span className="text-[14px] text-primary-text">#{item.rank}</span>
                          )}
                        </td>
                        <td className="py-6 px-8 align-middle">
                          <span className={`text-[16px] font-semibold ${idx === 0 ? 'text-gold-accent' : 'text-primary-text'}`}>
                            {item.company}
                          </span>
                        </td>
                        <td className="py-6 px-8 align-middle text-[16px] text-primary-text">
                          ${item.revenue?.toLocaleString() || 'N/A'}
                        </td>
                        <td className="py-6 px-8 align-middle text-[16px] text-primary-text">
                          {item.growth?.toFixed(1) || 'N/A'}%
                        </td>
                        <td className="py-6 px-8 text-[16px] text-primary-text">
                          {item.altman_z?.toFixed(2)}
                        </td>
                        <td className="py-6 px-8 text-[16px] text-primary-text">
                          {item.piotroski_f}
                        </td>
                        <td className="py-6 px-8 align-middle">
                          <Badge 
                            variant={item.recommendation === 'BUY' ? 'success' : item.recommendation === 'AVOID' ? 'destructive' : 'warning'}
                            className="text-[14px]"
                          >
                            {item.recommendation}
                          </Badge>
                        </td>
                        <td className="py-6 px-8 align-middle">
                          <Badge 
                            variant={item.ml_recommendation === 'BUY' ? 'success' : item.ml_recommendation === 'AVOID' ? 'destructive' : 'warning'}
                            className="text-[14px]"
                          >
                            {item.ml_recommendation || 'N/A'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>

          {/* Quick analysis insights */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            {/* Top Recommended Asset Card */}
            <Card>
              <CardContent className="px-4 py-3 flex flex-col justify-between min-h-[200px]">
                <div>
                  <span className="text-[14px] text-muted-text block mb-5 flex items-center gap-3 font-semibold">
                    <Award className="w-5 h-5 text-gold-accent" />
                    Portfolio asset recommendation
                  </span>
                  {data.ranking && data.ranking.length > 0 ? (
                    <div className="mt-4">
                      <h4 className="text-[20px] font-bold text-primary-text uppercase flex items-center gap-3">
                        {data.ranking[0].company}
                        <Badge variant="gold" className="text-[14px]">
                          Top ranked
                        </Badge>
                      </h4>
                      <p className="text-[16px] text-secondary-text mt-5 leading-relaxed">
                        {data.ranking[0].company} is selected as the top asset based on a combined score of solvency and strength metrics. Its Altman Z score is {data.ranking[0].altman_z?.toFixed(2) || 'N/A'} (Classification: {data.ranking[0].risk_classification || 'N/A'}) with a Piotroski F-score of {data.ranking[0].piotroski_f || 'N/A'}.
                      </p>
                    </div>
                  ) : (
                    <p className="text-[16px] text-secondary-text mt-4">
                      No ranks calculated.
                    </p>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* General Advice Summary */}
            <Card>
              <CardContent className="px-4 py-3 flex flex-col justify-between min-h-[200px]">
                <div>
                  <span className="text-[14px] text-muted-text block mb-5 flex items-center gap-3 font-semibold">
                    <Scale className="w-5 h-5 text-gold-accent" />
                    Compliance solvency parameters
                  </span>
                  <p className="text-[16px] text-secondary-text mt-4 leading-relaxed">
                    Deterministic rules establish buy triggers for equities displaying strong Piotroski F-scores (&ge; 7) and Altman Z-scores in the Safe zone (&gt; 3.0). Standard hold statuses are assigned for stable solvency profiles, and avoids are flagged immediately upon distress thresholds.
                  </p>
                </div>
                <div className="mt-10 pt-8 flex items-center gap-3 text-muted-text text-[14px] border-t border-border/6">
                  <ShieldCheck className="w-5 h-5 text-success shrink-0" />
                  <span>All compared assets synced with corporate disclosures</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      )}
    </div>
  )
}
