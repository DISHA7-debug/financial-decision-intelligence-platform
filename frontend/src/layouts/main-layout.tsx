import { Navigation } from './navigation'

interface MainLayoutProps {
  children: React.ReactNode
}

export function MainLayout({ children }: MainLayoutProps) {
  return (
    <div className="min-h-screen bg-background text-primary-text">
      <Navigation />
      <main 
        className="w-full mx-auto"
        style={{ 
          maxWidth: '1600px',
          paddingLeft: '64px',
          paddingRight: '64px',
          paddingTop: '64px',
          paddingBottom: '64px'
        }}
      >
        {children}
      </main>
    </div>
  )
}
