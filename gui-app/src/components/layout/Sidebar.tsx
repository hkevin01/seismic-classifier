import { cn } from '@/lib/utils'
import { useAppStore } from '@/store/appStore'
import { motion } from 'framer-motion'
import { Activity, AlertTriangle, BarChart3, FileUp, Globe, Settings } from 'lucide-react'
import React from 'react'

interface SidebarProps {
  className?: string
}

const navigationItems = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart3, href: '/' },
  { id: 'monitoring', label: 'Real-time Monitoring', icon: Activity, href: '/monitoring' },
  { id: 'events', label: 'Event History', icon: AlertTriangle, href: '/events' },
  { id: 'analysis', label: 'Analysis Tools', icon: FileUp, href: '/analysis' },
  { id: 'globe', label: 'Global Map', icon: Globe, href: '/globe' },
  { id: 'settings', label: 'Settings', icon: Settings, href: '/settings' },
]

export function Sidebar({ className }: SidebarProps) {
  const { user, isMonitoring } = useAppStore()
  const [activeItem, setActiveItem] = React.useState('dashboard')

  return (
    <motion.div
      initial={{ x: -300 }}
      animate={{ x: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'w-64 h-screen bg-card border-r border-border glass-effect p-6 flex flex-col',
        className
      )}
    >
      {/* Logo and Title */}
      <div className="mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold gradient-text">SeismicWatch</h1>
            <p className="text-xs text-muted-foreground">Real-time Monitor</p>
          </div>
        </div>
      </div>

      {/* User Info */}
      {user && (
        <div className="mb-6 p-3 rounded-lg bg-secondary/50 border border-border/50">
          <div className="flex items-center space-x-3">
            {user.avatar && (
              <img
                src={user.avatar}
                alt={user.name}
                className="w-10 h-10 rounded-full object-cover"
              />
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user.name}</p>
              <p className="text-xs text-muted-foreground truncate">{user.role}</p>
            </div>
          </div>
          {isMonitoring && (
            <div className="mt-2 flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-xs text-green-400">Monitoring Active</span>
            </div>
          )}
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 space-y-1">
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isActive = activeItem === item.id

          return (
            <motion.button
              key={item.id}
              whileHover={{ x: 4 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setActiveItem(item.id)}
              className={cn(
                'w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-all duration-200',
                isActive
                  ? 'bg-primary/20 text-primary border border-primary/30'
                  : 'hover:bg-secondary/50 text-muted-foreground hover:text-foreground'
              )}
            >
              <Icon size={18} />
              <span className="text-sm font-medium">{item.label}</span>
              {isActive && (
                <motion.div
                  layoutId="activeIndicator"
                  className="ml-auto w-2 h-2 bg-primary rounded-full"
                />
              )}
            </motion.button>
          )
        })}
      </nav>

      {/* Status Indicator */}
      <div className="mt-6 p-3 rounded-lg bg-muted/30 border border-border/50">
        <div className="flex items-center justify-between">
          <span className="text-xs text-muted-foreground">System Status</span>
          <div className="flex items-center space-x-1">
            <div className="w-2 h-2 bg-green-500 rounded-full" />
            <span className="text-xs text-green-400">Online</span>
          </div>
        </div>
        <div className="mt-2 h-1 bg-muted rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-green-500 to-blue-500"
            style={{ width: '85%' }}
            initial={{ width: 0 }}
            animate={{ width: '85%' }}
            transition={{ duration: 1, delay: 0.5 }}
          />
        </div>
        <p className="text-xs text-muted-foreground mt-1">85% Operational</p>
      </div>
    </motion.div>
  )
}
