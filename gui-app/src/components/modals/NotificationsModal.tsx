import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { formatTimestamp } from '@/lib/utils'
import { useAppStore } from '@/store/appStore'
import { motion } from 'framer-motion'
import { AlertCircle, AlertTriangle, Bell, CheckCircle, Info, X } from 'lucide-react'

interface NotificationsModalProps {
  isOpen: boolean
  onClose: () => void
}

export function NotificationsModal({ isOpen, onClose }: NotificationsModalProps) {
  const { notifications, removeNotification } = useAppStore()

  const getIcon = (type: string) => {
    switch (type) {
      case 'error': return <AlertCircle className="w-5 h-5 text-red-500" />
      case 'warning': return <AlertTriangle className="w-5 h-5 text-yellow-500" />
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />
      default: return <Info className="w-5 h-5 text-blue-500" />
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Notifications" className="max-w-lg">
      <div className="space-y-4">
        {notifications.length === 0 ? (
          <div className="text-center py-8">
            <Bell className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No notifications</p>
          </div>
        ) : (
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {notifications.map((notification, index) => (
              <motion.div
                key={notification.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-start space-x-3 p-3 rounded-lg bg-secondary/30 border border-border/50"
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getIcon(notification.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">{notification.title}</p>
                  <p className="text-sm text-muted-foreground mt-1">{notification.message}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    {formatTimestamp(notification.timestamp)}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeNotification(notification.id)}
                  className="flex-shrink-0"
                >
                  <X className="w-4 h-4" />
                </Button>
              </motion.div>
            ))}
          </div>
        )}

        {notifications.length > 0 && (
          <div className="pt-3 border-t border-border">
            <Button
              variant="outline"
              onClick={() => {
                notifications.forEach(n => removeNotification(n.id))
              }}
              className="w-full"
            >
              Clear All
            </Button>
          </div>
        )}
      </div>
    </Modal>
  )
}
