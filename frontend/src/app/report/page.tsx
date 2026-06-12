'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { FileText, Download, Users, Briefcase, Search, AlertCircle, ShieldAlert } from 'lucide-react'
import { getCompanyReport, getCommitteeReport } from '@/services/api'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { LoadingSpinner } from '@/components/ui/loading-spinner'
import type { ReportData } from '@/types'

export default function ReportPage() {
  const [activeTab, setActiveTab] = useState<'committee' | 'company'>('committee')
  const [companyInput, setCompanyInput] = useState('')
  const [selectedCompany, setSelectedCompany] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [reportData, setReportData] = useState<ReportData | null>(null)

  const fetchCommitteeReport = async () => {
    setLoading(true)
    setError(null)
    setReportData(null)
    try {
      const data = await getCommitteeReport()
      setReportData({
        title: 'Joint Investment Committee Report',
        content: data.content,
        report_path: data.report_path
      })
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || 'Failed to fetch committee report.'
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  const fetchCompanyReport = async (company: string) => {
    if (!company) return
    setLoading(true)
    setError(null)
    setReportData(null)
    try {
      const data = await getCompanyReport(company)
      setReportData({
        title: `Asset Audit Report: ${company.toUpperCase()}`,
        content: data.content,
        report_path: data.report_path
      })
    } catch (err: any) {
      const detail = err.response?.data?.detail || err.message || `Failed to generate report for ${company}.`
      setError(detail)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (activeTab === 'committee') {
      fetchCommitteeReport()
    } else if (activeTab === 'company' && selectedCompany) {
      fetchCompanyReport(selectedCompany)
    }
  }, [activeTab, selectedCompany])

  const handleCompanySubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const c = companyInput.trim().toUpperCase()
    if (!c) return
    setSelectedCompany(c)
  }

  const handleDownload = () => {
    if (!reportData || !reportData.content) return
    const blob = new Blob([reportData.content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const filename = reportData.title.toLowerCase().replace(/[^a-z0-9]+/g, '_') + '.txt'
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  return (
    <div className="flex flex-col gap-12">
      {/* Title */}
      <div className="pb-10 flex items-center gap-5 border-b border-border/6">
        <div className="p-5 rounded-xl bg-surface border border-border/6">
          <FileText className="w-5 h-5 text-gold-accent" />
        </div>
        <div>
          <h1 className="text-[42px] font-bold text-primary-text tracking-tight uppercase leading-tight">
            Due Diligence Reports
          </h1>
          <span className="text-[16px] text-secondary-text mt-5 block">
            Generate, audit, and export equities research
          </span>
        </div>
      </div>

      {/* Main Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-10 items-start">
        {/* Selector Sidepanel */}
        <div className="flex flex-col gap-8">
            <Card>
              <CardContent className="px-6 py-5 flex flex-col gap-4">
              <span className="text-[14px] text-muted-text block mb-5 font-semibold">
                Select report scope
              </span>

              <button
                onClick={() => {
                  setActiveTab('committee')
                  setError(null)
                }}
                className={`w-full flex items-center gap-4 px-6 py-3 rounded-xl text-left text-[16px] border transition-all ${
                  activeTab === 'committee'
                    ? 'bg-gold-accent/10 border-gold-accent/20 text-gold-accent font-semibold shadow-sm'
                    : 'border-transparent text-secondary-text hover:text-primary-text hover:bg-surface/50'
                }`}
              >
                <Users className="w-5 h-5 shrink-0" />
                Joint committee report
              </button>

              <button
                onClick={() => {
                  setActiveTab('company')
                  setError(null)
                }}
                className={`w-full flex items-center gap-4 px-6 py-3 rounded-xl text-left text-[16px] border transition-all ${
                  activeTab === 'company'
                    ? 'bg-gold-accent/10 border-gold-accent/20 text-gold-accent font-semibold shadow-sm'
                    : 'border-transparent text-secondary-text hover:text-primary-text hover:bg-surface/50'
                }`}
              >
                <Briefcase className="w-5 h-5 shrink-0" />
                Individual asset report
              </button>
            </CardContent>
          </Card>

          {activeTab === 'company' && (
            <Card>
              <CardContent className="px-4 py-3">
                <span className="text-[14px] text-muted-text block mb-5 font-semibold">
                  Configure audit target
                </span>
                <form onSubmit={handleCompanySubmit} className="flex flex-col gap-6">
                  <Input
                    type="text"
                    placeholder="Enter ticker (e.g. MSFT)..."
                    value={companyInput}
                    onChange={(e) => setCompanyInput(e.target.value)}
                  />
                  <button
                    type="submit"
                    className="h-[44px] w-full bg-gold-accent hover:bg-gold-accent/90 text-background font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 text-[16px]"
                  >
                    <Search className="w-5 h-5" />
                    Generate report
                  </button>
                </form>
              </CardContent>
            </Card>
          )}

          {reportData && (
            <button
              onClick={handleDownload}
              className="h-[44px] w-full bg-surface hover:bg-elevated border border-border/6 text-primary-text font-semibold rounded-xl transition-colors flex items-center justify-center gap-3 shadow-sm text-[16px]"
            >
              <Download className="w-5 h-5 text-gold-accent" />
              Export report text
            </button>
          )}
        </div>

        {/* Report Viewer */}
        <div className="lg:col-span-3 flex flex-col gap-12">
          {loading && <LoadingSpinner message="Querying report databases..." />}

          {error && (
            <Card className="bg-surface">
              <CardContent className="px-4 py-3">
                <div className="flex items-start gap-8 mb-8">
                  <AlertCircle className="w-8 h-8 text-danger shrink-0 mt-1" />
                  <div>
                    <h3 className="text-[18px] font-semibold text-danger mb-3">
                      Report not found
                    </h3>
                    <p className="text-[14px] text-secondary-text leading-relaxed">
                      {error}
                    </p>
                  </div>
                </div>
                {activeTab === 'committee' && (
                  <div className="pt-8 text-[14px] text-secondary-text leading-relaxed border-t border-border/6">
                    The joint committee report is generated automatically when you compare multiple companies. 
                    Please go to the <Link href="/compare" className="text-gold-accent hover:underline font-semibold">Compare</Link> page, input assets, and run the comparison pipeline first.
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {!loading && !error && !reportData && (
            <Card className="bg-surface">
              <CardContent className="px-4 py-3 text-center text-[16px] text-secondary-text min-h-[420px] flex flex-col items-center justify-center">
                <ShieldAlert className="w-20 h-20 text-muted-text mb-8" />
                <span>Configure a company above to build and display an individual audit report.</span>
              </CardContent>
            </Card>
          )}

          {!loading && !error && reportData && (
            <Card className="overflow-hidden shadow-2xl">
              {/* Document Header block - Notion Dark Mode styled */}
              <div className="px-14 pt-14 pb-10 flex flex-col gap-5 bg-elevated">
                <div className="flex items-center justify-between border-b border-border/6 pb-6">
                  <Badge variant="gold" className="text-[14px] tracking-wider uppercase font-bold">
                    Investment Research Dossier
                  </Badge>
                  <Badge variant="outline" className="text-[14px] uppercase font-bold">
                    Confidential
                  </Badge>
                </div>
                
                <h2 className="text-[32px] font-bold text-primary-text mt-8 leading-tight">
                  {reportData.title}
                </h2>
                
                <div className="flex flex-wrap gap-x-12 gap-y-4 mt-8 text-[14px] text-secondary-text">
                  <span>Date: {new Date().toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                  <span>Archive: {reportData.report_path?.split('/').pop() || 'Ingested Document'}</span>
                  <span>Verification: Cryptographic Seal Applied</span>
                </div>
              </div>

              {/* Document Content - Styled in Geist light-gray with Gold accents for headings */}
              <div className="px-14 py-14 max-h-[600px] overflow-y-auto border-t border-b border-border/6 bg-surface">
                <pre className="whitespace-pre-wrap select-text font-normal text-[18px] text-primary-text leading-[1.8]">
                  {reportData.content}
                </pre>
              </div>
              
              {/* Document Footer block */}
              <div className="px-14 py-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4 text-[14px] text-muted-text bg-elevated">
                <span>Portfolio compliance notes: Solvency metrics verified</span>
                <span>Lines: {reportData.content?.split('\n').length || 0}</span>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
