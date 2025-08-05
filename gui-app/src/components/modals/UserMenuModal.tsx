import { Button } from '@/components/ui/Button'
import { Modal } from '@/components/ui/Modal'
import { useAppStore } from '@/store/appStore'
import { LogOut, Settings, UserCircle } from 'lucide-react'

interface UserMenuModalProps {
  isOpen: boolean
  onClose: () => void
}

export function UserMenuModal({ isOpen, onClose }: UserMenuModalProps) {
  const { user, setUser, setActiveModal } = useAppStore()

  const handleLogout = () => {
    setUser(null)
    onClose()
  }

  const openSettings = () => {
    onClose()
    setActiveModal('settings')
  }

  if (!user) return null

  return (
    <Modal isOpen={isOpen} onClose={onClose} className="max-w-sm">
      <div className="text-center space-y-4">
        {/* User Avatar and Info */}
        <div className="space-y-3">
          {user.avatar ? (
            <img
              src={user.avatar}
              alt={user.name}
              className="w-16 h-16 rounded-full mx-auto object-cover"
            />
          ) : (
            <div className="w-16 h-16 rounded-full bg-primary/20 flex items-center justify-center mx-auto">
              <UserCircle className="w-8 h-8 text-primary" />
            </div>
          )}

          <div>
            <h3 className="font-semibold text-lg">{user.name}</h3>
            <p className="text-sm text-muted-foreground capitalize">{user.role}</p>
            <p className="text-xs text-muted-foreground mt-1">{user.email}</p>
          </div>
        </div>

        {/* Menu Actions */}
        <div className="space-y-2 pt-4 border-t border-border">
          <Button
            variant="ghost"
            onClick={openSettings}
            className="w-full justify-start"
          >
            <Settings className="w-4 h-4 mr-3" />
            Settings
          </Button>

          <Button
            variant="ghost"
            onClick={handleLogout}
            className="w-full justify-start text-red-400 hover:text-red-300 hover:bg-red-500/10"
          >
            <LogOut className="w-4 h-4 mr-3" />
            Sign Out
          </Button>
        </div>
      </div>
    </Modal>
  )
}
