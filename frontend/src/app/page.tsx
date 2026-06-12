'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Search, History, Database, TrendingUp, Scale, ArrowRight } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import type { RecentCompany } from '@/types'

const INITIAL_RECENTS: RecentCompany[] = [
  { company: 'Microsoft', recommendation: 'BUY', altmanZ: 3.12, piotroskiF: 8, riskClassification: 'Low Risk' },
  { company: 'Apple', recommendation: 'BUY', altmanZ: 3.56, piotroskiF: 7, riskClassification: 'Low Risk' }
]

export default function Dashboard() {
  const [ticker, setTicker] = useState('')
  const [recentCompanies, setRecentCompanies] = useState<RecentCompany[]>([])
  const router = useRouter()

  useEffect(() => {
    const stored = localStorage.getItem('recent_searches')
    if (stored) {
      try {
        setRecentCompanies(JSON.parse(stored))
      } catch (e) {
        setRecentCompanies(INITIAL_RECENTS)
      }
    } else {
      setRecentCompanies(INITIAL_RECENTS)
      localStorage.setItem('recent_searches', JSON.stringify(INITIAL_RECENTS))
    }
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (!ticker.trim()) return
    
    const updated = [
      { company: ticker.trim().toUpperCase(), recommendation: null, altmanZ: null, piotroskiF: null, riskClassification: 'Pending Analysis' },
      ...recentCompanies.filter(c => c.company.toUpperCase() !== ticker.trim().toUpperCase())
    ].slice(0, 4)
    
    setRecentCompanies(updated)
    localStorage.setItem('recent_searches', JSON.stringify(updated))
    
    router.push(`/analyze?company=${encodeURIComponent(ticker.trim())}`)
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Hero Section */}
      <div className="max-w-6xl">
        <h1 className="text-[46px] md:text-[54px] font-bold leading-tight tracking-tight text-primary-text mb-6">
          Decision Intelligence
          <br />
          <span className="text-gold-accent">for Public Markets</span>
        </h1>
        <p className="text-[17px] text-secondary-text leading-relaxed max-w-3xl mb-6">
          Transform SEC filings, financial statements, risk disclosures, and machine learning signals into investment-grade decisions.
        </p>

        {/* Metric Cards */}
        <div className="flex flex-wrap gap-6 mt-6">
          <Badge variant="outline" className="text-[14px] border-border/6 bg-surface">
            43 Companies Indexed
          </Badge>
          <Badge variant="outline" className="text-[14px] border-border/6 bg-surface">
            55 SEC Filings Parsed
          </Badge>
          <Badge variant="gold" className="text-[14px]">
            Multi-Agent Pipeline
          </Badge>
          <Badge variant="gold" className="text-[14px]">
            XGBoost Model Active
          </Badge>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Search Console */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-3 text-[24px]">
                <Search className="w-5 h-5 text-gold-accent" />
                Asset Analysis Console
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-6">
                <Input
                  type="text"
                  placeholder="Search equity ticker or target name (e.g. MSFT, AAPL)..."
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value)}
                  className="flex-1"
                />
                <button
                  type="submit"
                  className="h-[44px] px-6 bg-gold-accent hover:bg-gold-accent/90 text-background font-semibold rounded-xl transition-all duration-200 flex items-center gap-2 text-[16px]"
                >
                  Analyze Asset
                  <ArrowRight className="w-4 h-4" />
                </button>
              </form>
              <p className="text-[14px] text-muted-text mt-8 leading-relaxed">
                SEC disclosure documents are ingested and analyzed dynamically if they are missing from the cache.
              </p>
            </CardContent>
          </Card>

          {/* System Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card>
              <CardContent className="px-4 py-3 flex flex-col items-center justify-center gap-4 min-h-[136px]">
                <div className="p-4 bg-elevated rounded-xl border border-border/6">
                  <Database className="w-5 h-5 text-secondary-text" />
                </div>
                <div className="text-center">
                  <span className="text-[14px] text-muted-text block font-medium mb-2">Data Ingestion</span>
                  <span className="text-[16px] font-semibold text-primary-text">Active</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="px-4 py-3 flex flex-col items-center justify-center gap-6 min-h-[160px]">
                  <div className="p-5 bg-elevated rounded-xl border border-border/6">
                  <TrendingUp className="w-5 h-5 text-gold-accent" />
                </div>
                <div className="text-center">
                  <span className="text-[14px] text-muted-text block font-medium mb-2">Predictive Model</span>
                  <span className="text-[16px] font-semibold text-primary-text">Active</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="px-4 py-3 flex flex-col items-center justify-center gap-6 min-h-[160px]">
                  <div className="p-5 bg-elevated rounded-xl border border-border/6">
                  <Scale className="w-5 h-5 text-secondary-text" />
                </div>
                <div className="text-center">
                  <span className="text-[14px] text-muted-text block font-medium mb-2">Decision Engine</span>
                  <span className="text-[16px] font-semibold text-primary-text">Active</span>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Research Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="text-[24px]">Research Index</CardTitle>
          </CardHeader>
          <CardContent className="px-4 py-3">
            <div className="space-y-3 text-[15px] text-primary-text">
              <div className="flex justify-between py-4 border-b border-border/6">
                <span className="text-secondary-text">Research database</span>
                <span>SEC filings index</span>
              </div>
              <div className="flex justify-between py-4 border-b border-border/6">
                <span className="text-secondary-text">Intelligence layer</span>
                <span>Dense embeddings</span>
              </div>
              <div className="flex justify-between py-4 border-b border-border/6">
                <span className="text-secondary-text">Reasoning model</span>
                <span>Gemini 1.5 Pro</span>
              </div>
              <div className="flex justify-between py-4">
                <span className="text-secondary-text">Last sync</span>
                <span>Just now</span>
              </div>
            </div>

            <div className="mt-8 pt-8 border-t border-border/6">
              <span className="text-[14px] text-secondary-text block mb-4 font-semibold">
                Research Note
              </span>
              <p className="text-[14px] text-muted-text leading-relaxed">
                Verify parameters by adding multiple companies in the comparison panel to view side-by-side rankings.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recently Analyzed */}
      <div>
        <div className="flex items-center gap-3 mb-12">
          <History className="w-5 h-5 text-gold-accent" />
          <h2 className="text-[32px] font-semibold text-primary-text leading-tight">
            Recently Analyzed Securities
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
          {recentCompanies.map((c, idx) => (
            <Card key={idx}>
              <CardContent className="px-4 py-3">
                <h3 className="text-[22px] font-semibold text-primary-text mb-6">{c.company}</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between gap-4">
                    <span className="text-[14px] text-secondary-text">Recommendation</span>
                    <Badge 
                      variant={c.recommendation === 'BUY' ? 'success' : c.recommendation === 'AVOID' ? 'destructive' : 'warning'}
                      className="text-[14px]"
                    >
                      {c.recommendation || 'Pending'}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[14px] text-secondary-text">Altman Z</span>
                    <span className="text-[14px] text-primary-text">{c.altmanZ ?? 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[14px] text-secondary-text">Piotroski F</span>
                    <span className="text-[14px] text-primary-text">{c.piotroskiF ?? 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[14px] text-secondary-text">Risk</span>
                    <span className="text-[14px] text-primary-text">{c.riskClassification}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
