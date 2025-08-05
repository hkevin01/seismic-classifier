import { Button } from '@/components/ui/Button'
import { Input, Label } from '@/components/ui/Input'
import { Modal } from '@/components/ui/Modal'
import { useAppStore } from '@/store/appStore'
import { Bell, Globe, Moon, RefreshCw, Sun, Zap } from 'lucide-react'
import React from 'react'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function SettingsModal({ isOpen, onClose }: SettingsModalProps) {
  const { settings, updateSettings } = useAppStore()
  const [localSettings, setLocalSettings] = React.useState(settings)

  React.useEffect(() => {
    setLocalSettings(settings)
  }, [settings])

  const handleSave = () => {
    updateSettings(localSettings)
    onClose()
  }

  const handleReset = () => {
    setLocalSettings({
      theme: 'dark',
      notifications: true,
      autoRefresh: true,
      refreshInterval: 30,
      alertThreshold: 5.0,
      mapStyle: 'satellite'
    })
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Settings" className="max-w-md">
      <div className="space-y-6">
        {/* Theme Settings */}
        <div className="space-y-3">
          <Label className="text-sm font-medium flex items-center">
            <Moon className="w-4 h-4 mr-2" />
            Appearance
          </Label>
          <div className="flex space-x-2">
            <Button
              variant={localSettings.theme === 'dark' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setLocalSettings(prev => ({ ...prev, theme: 'dark' }))}
              className="flex-1"
            >
              <Moon className="w-4 h-4 mr-2" />
              Dark
            </Button>
            <Button
              variant={localSettings.theme === 'light' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setLocalSettings(prev => ({ ...prev, theme: 'light' }))}
              className="flex-1"
            >
              <Sun className="w-4 h-4 mr-2" />
              Light
            </Button>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="space-y-3">
          <Label className="text-sm font-medium flex items-center">
            <Bell className="w-4 h-4 mr-2" />
            Notifications
          </Label>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Enable notifications</span>
            <Button
              variant={localSettings.notifications ? 'default' : 'outline'}
              size="sm"
              onClick={() => setLocalSettings(prev => ({ ...prev, notifications: !prev.notifications }))}
            >
              {localSettings.notifications ? 'On' : 'Off'}
            </Button>
          </div>
        </div>

        {/* Monitoring Settings */}
        <div className="space-y-3">
          <Label className="text-sm font-medium flex items-center">
            <RefreshCw className="w-4 h-4 mr-2" />
            Monitoring
          </Label>
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Auto-refresh data</span>
            <Button
              variant={localSettings.autoRefresh ? 'default' : 'outline'}
              size="sm"
              onClick={() => setLocalSettings(prev => ({ ...prev, autoRefresh: !prev.autoRefresh }))}
            >
              {localSettings.autoRefresh ? 'On' : 'Off'}
            </Button>
          </div>

          {localSettings.autoRefresh && (
            <div className="space-y-2">
              <Label className="text-sm text-muted-foreground">
                Refresh interval (seconds)
              </Label>
              <Input
                type="number"
                value={localSettings.refreshInterval}
                onChange={(e) => setLocalSettings(prev => ({
                  ...prev,
                  refreshInterval: parseInt(e.target.value) || 30
                }))}
                min="5"
                max="300"
              />
            </div>
          )}
        </div>

        {/* Alert Settings */}
        <div className="space-y-3">
          <Label className="text-sm font-medium flex items-center">
            <Zap className="w-4 h-4 mr-2" />
            Alerts
          </Label>
          <div className="space-y-2">
            <Label className="text-sm text-muted-foreground">
              Alert threshold (magnitude)
            </Label>
            <Input
              type="number"
              value={localSettings.alertThreshold}
              onChange={(e) => setLocalSettings(prev => ({
                ...prev,
                alertThreshold: parseFloat(e.target.value) || 5.0
              }))}
              min="1.0"
              max="10.0"
              step="0.1"
            />
          </div>
        </div>

        {/* Map Settings */}
        <div className="space-y-3">
          <Label className="text-sm font-medium flex items-center">
            <Globe className="w-4 h-4 mr-2" />
            Map Style
          </Label>
          <div className="grid grid-cols-3 gap-2">
            {(['satellite', 'terrain', 'street'] as const).map(style => (
              <Button
                key={style}
                variant={localSettings.mapStyle === style ? 'default' : 'outline'}
                size="sm"
                onClick={() => setLocalSettings(prev => ({ ...prev, mapStyle: style }))}
                className="capitalize"
              >
                {style}
              </Button>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-3 pt-4 border-t border-border">
          <Button
            variant="outline"
            onClick={handleReset}
            className="flex-1"
          >
            Reset
          </Button>
          <Button
            onClick={handleSave}
            className="flex-1"
          >
            Save Changes
          </Button>
        </div>
      </div>
    </Modal>
  )
}
