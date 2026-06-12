import { Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  message?: string
  className?: string
}

export function LoadingSpinner({ message, className }: LoadingSpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-16", className)}>
      <Loader2 className="w-12 h-12 text-gold-accent animate-spin mb-4" />
      {message && (
        <p className="text-[15px] text-secondary-text">{message}</p>
      )}
    </div>
  )
}
