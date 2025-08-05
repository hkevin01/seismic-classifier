import { AnimatePresence, motion } from 'framer-motion'
import React from 'react'
import { Toaster } from 'react-hot-toast'
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom'

// Layout Components
import { Header } from './components/layout/Header'
import { Sidebar } from './components/layout/Sidebar'

// Page Components
import { Analysis } from './pages/Analysis'
import { Dashboard } from './pages/Dashboard'
import { Monitoring } from './pages/Monitoring'

// Modal Components
import { FileUploadModal } from './components/modals/FileUploadModal'
import { NotificationsModal } from './components/modals/NotificationsModal'
import { SettingsModal } from './components/modals/SettingsModal'
import { UserMenuModal } from './components/modals/UserMenuModal'

// Store
import { useAppStore } from './store/appStore'

function App() {
  const { activeModal, setActiveModal, addSeismicEvent, addNotification, isMonitoring } = useAppStore()

  // Simulate real-time events
  React.useEffect(() => {
    if (!isMonitoring) return

    const interval = setInterval(() => {
      if (Math.random() > 0.7) { // 30% chance every 10 seconds
        const locations = [
          'Los Angeles, CA',
          'San Francisco, CA',
          'Seattle, WA',
          'Portland, OR',
          'San Diego, CA'
        ]
        const classifications = ['earthquake', 'explosion', 'volcanic', 'noise']

        const newEvent = {
          id: `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          timestamp: new Date().toISOString(),
          location: locations[Math.floor(Math.random() * locations.length)],
          magnitude: parseFloat((1.5 + Math.random() * 4).toFixed(1)),
          depth: parseFloat((5 + Math.random() * 30).toFixed(1)),
          classification: classifications[Math.floor(Math.random() * classifications.length)] as any,
          confidence: parseFloat((0.6 + Math.random() * 0.4).toFixed(2)),
          waveformData: Array.from({ length: 100 }, (_, i) => ({
            time: i,
            amplitude: Math.sin(i * 0.1) * (2 + Math.random() * 3) + (Math.random() - 0.5) * 0.5
          }))
        }

        addSeismicEvent(newEvent)

        if (newEvent.magnitude > 5.0) {
          addNotification({
            type: 'warning',
            title: 'High Magnitude Event Detected',
            message: `Magnitude ${newEvent.magnitude} detected at ${newEvent.location}`
          })
        }
      }
    }, 10000) // Every 10 seconds

    return () => clearInterval(interval)
  }, [isMonitoring, addSeismicEvent, addNotification])

  return (
    <div className="min-h-screen bg-background text-foreground">
      <Router>
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Content */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <Header />

            {/* Page Content */}
            <main className="flex-1 overflow-auto p-6">
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
              >
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/monitoring" element={<Monitoring />} />
                  <Route path="/analysis" element={<Analysis />} />
                </Routes>
              </motion.div>
            </main>
          </div>
        </div>

        {/* Modals */}
        <AnimatePresence>
          {activeModal === 'notifications' && (
            <NotificationsModal
              isOpen={true}
              onClose={() => setActiveModal(null)}
            />
          )}

          {activeModal === 'settings' && (
            <SettingsModal
              isOpen={true}
              onClose={() => setActiveModal(null)}
            />
          )}

          {activeModal === 'userMenu' && (
            <UserMenuModal
              isOpen={true}
              onClose={() => setActiveModal(null)}
            />
          )}

          {activeModal === 'fileUpload' && (
            <FileUploadModal
              isOpen={true}
              onClose={() => setActiveModal(null)}
            />
          )}
        </AnimatePresence>

        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'rgba(17, 24, 39, 0.9)',
              color: '#F9FAFB',
              border: '1px solid #374151',
              borderRadius: '8px',
            },
          }}
        />
      </Router>
    </div>
  )
}

export default App
