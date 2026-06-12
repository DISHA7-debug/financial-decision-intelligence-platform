'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { BarChart3, Search, GitCompare, FileText, Activity, Menu, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { useState } from 'react'

const navItems = [
  { href: '/', label: 'Dashboard', icon: BarChart3 },
  { href: '/analyze', label: 'Analyze', icon: Search },
  { href: '/compare', label: 'Compare', icon: GitCompare },
  { href: '/report', label: 'Reports', icon: FileText },
]

export function Navigation() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <nav className="border-b border-border/6 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-12 md:px-16">
        <div className="flex items-center justify-between h-[80px]">
          <Link href="/" className="flex items-center gap-5">
            <motion.div 
              className="w-10 h-10 rounded-lg bg-gradient-to-br from-gold-accent to-gold-accent/60 flex items-center justify-center"
              whileHover={{ scale: 1.05 }}
              transition={{ duration: 0.2 }}
            >
              <Activity className="w-6 h-6 text-background" />
            </motion.div>
            <span className="text-[18px] md:text-[20px] font-semibold text-primary-text">
              Decision Intelligence
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-4">
            {navItems.map((item) => {
              const Icon = item.icon
              const isActive = pathname === item.href
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                >
                  <motion.div
                    className={cn(
                      "flex items-center gap-3 px-7 py-3 rounded-xl text-[16px] font-medium transition-all duration-200",
                      isActive
                        ? "bg-gold-accent/10 text-gold-accent border border-gold-accent/20"
                        : "text-secondary-text hover:text-primary-text hover:bg-surface/50"
                    )}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    transition={{ duration: 0.2 }}
                  >
                    <Icon className="w-5 h-5" />
                    {item.label}
                  </motion.div>
                </Link>
              )
            })}
          </div>

          {/* Desktop Status */}
          <div className="hidden md:flex items-center gap-4">
            <motion.div 
              className="w-3 h-3 rounded-full bg-success"
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span className="text-[16px] text-secondary-text">System Active</span>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-3 rounded-lg hover:bg-surface/50 transition-colors"
          >
            {mobileMenuOpen ? (
              <X className="w-6 h-6 text-primary-text" />
            ) : (
              <Menu className="w-6 h-6 text-primary-text" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="md:hidden border-t border-border/6 bg-card/50"
          >
            <div className="px-4 py-6 space-y-3">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = pathname === item.href
                
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <motion.div
                      className={cn(
                        "flex items-center gap-4 px-5 py-4 rounded-xl text-[18px] font-medium transition-all duration-200",
                        isActive
                          ? "bg-gold-accent/10 text-gold-accent border border-gold-accent/20"
                          : "text-secondary-text hover:text-primary-text hover:bg-surface/50"
                      )}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Icon className="w-6 h-6" />
                      {item.label}
                    </motion.div>
                  </Link>
                )
              })}
              
              <div className="flex items-center gap-3 px-5 py-4 mt-6 border-t border-border/6">
                <motion.div 
                  className="w-3 h-3 rounded-full bg-success"
                  animate={{ opacity: [1, 0.5, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <span className="text-[16px] text-secondary-text">System Active</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}
