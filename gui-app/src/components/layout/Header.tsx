import { Button } from '@/components/ui/Button'
import { Input } from '@/components/ui/Input'
import { cn } from '@/lib/utils'
import { useAppStore } from '@/store/appStore'
import { motion } from 'framer-motion'
import { Bell, Moon, Search, Settings, Sun } from 'lucide-react'
import React from 'react'

interface HeaderProps {
  className?: string
}

export function Header({ className }: HeaderProps) {
  const { user, notifications, settings, updateSettings, setActiveModal } = useAppStore()
  const [searchQuery, setSearchQuery] = React.useState('')

  const toggleTheme = () => {
    updateSettings({
      theme: settings.theme === 'dark' ? 'light' : 'dark'
    })
  }

  return (
    <motion.header
      initial={{ y: -50, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.3 }}
      className={cn(
        'h-16 bg-card border-b border-border glass-effect px-6 flex items-center justify-between',
        className
      )}
    >
      {/* Left Section - Search */}
      <div className="flex items-center space-x-4 flex-1 max-w-md">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            type="text"
            placeholder="Search events, locations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-background/50"
          />
        </div>
      </div>

      {/* Center Section - Title */}
      <div className="hidden md:block">
        <h1 className="text-xl font-semibold gradient-text">
          Seismic Event Dashboard
        </h1>
      </div>

      {/* Right Section - Actions */}
      <div className="flex items-center space-x-3">
        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          className="relative"
        >
          {settings.theme === 'dark' ? (
            <Sun className="w-4 h-4" />
          ) : (
            <Moon className="w-4 h-4" />
          )}
        </Button>

        {/* Notifications */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setActiveModal('notifications')}
          className="relative"
        >
          <Bell className="w-4 h-4" />
          {notifications.length > 0 && (
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center"
            >
              <span className="text-xs text-white font-medium">
                {notifications.length > 9 ? '9+' : notifications.length}
              </span>
            </motion.div>
          )}
        </Button>

        {/* Settings */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setActiveModal('settings')}
        >
          <Settings className="w-4 h-4" />
        </Button>

        {/* User Menu */}
        {user && (
          <Button
            variant="ghost"
            onClick={() => setActiveModal('userMenu')}
            className="flex items-center space-x-2 pl-2 pr-3"
          >
            {user.avatar && (
              <img
                src={user.avatar}
                alt={user.name}
                className="w-6 h-6 rounded-full object-cover"
              />
            )}
            <div className="hidden md:block text-left">
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-xs text-muted-foreground capitalize">{user.role}</p>
            </div>
          </Button>
        )}
      </div>
    </motion.header>
  )
}
