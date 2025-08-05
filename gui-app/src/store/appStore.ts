import { create } from 'zustand'

// Types for our application state
export interface SeismicEvent {
  id: string
  timestamp: Date
  magnitude: number
  depth: number
  location: {
    latitude: number
    longitude: number
    place: string
  }
  type: 'earthquake' | 'explosion' | 'noise'
  confidence: number
  status: 'detected' | 'analyzing' | 'classified' | 'alert'
}

export interface User {
  name: string
  role: 'analyst' | 'admin' | 'viewer'
  email: string
  avatar?: string
}

export interface AppSettings {
  theme: 'dark' | 'light'
  notifications: boolean
  autoRefresh: boolean
  refreshInterval: number
  alertThreshold: number
  mapStyle: 'satellite' | 'terrain' | 'street'
}

interface AppStore {
  // User data
  user: User
  setUser: (user: User) => void

  // Seismic events
  seismicEvents: SeismicEvent[]
  addSeismicEvent: (event: SeismicEvent) => void
  removeSeismicEvent: (id: string) => void
  clearSeismicEvents: () => void

  // Notifications
  notifications: Notification[]
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void
  removeNotification: (id: string) => void
  markNotificationAsRead: (id: string) => void
  clearNotifications: () => void

  // Settings
  settings: Settings
  updateSettings: (settings: Partial<Settings>) => void
  monitoringSettings: MonitoringSettings
  updateMonitoringSettings: (settings: Partial<MonitoringSettings>) => void

  // UI State
  isMonitoring: boolean
  setIsMonitoring: (monitoring: boolean) => void
  sidebarCollapsed: boolean
  setSidebarCollapsed: (collapsed: boolean) => void
  currentPage: string
  setCurrentPage: (page: string) => void

    // Modal states
  activeModal: null,
  setActiveModal: (modal) => set({ activeModal: modal }),
  showNotifications: false,
  setShowNotifications: (show) => set({ showNotifications: show }),
  showSettings: false,
  setShowSettings: (show) => set({ showSettings: show }),
  showUserMenu: false,
  setShowUserMenu: (show) => set({ showUserMenu: show }),
  showFileUpload: false,
  setShowFileUpload: (show) => set({ showFileUpload: show }),
  showNotifications: boolean
  setShowNotifications: (show: boolean) => void
  showSettings: boolean
  setShowSettings: (show: boolean) => void
  showUserMenu: boolean
  setShowUserMenu: (show: boolean) => void
  showFileUpload: boolean
  setShowFileUpload: (show: boolean) => void
}

export const useAppStore = create<AppStore>((set, get) => ({
  // Initial user state
  user: {
    name: 'Dr. Sarah Chen',
    role: 'analyst',
    email: 'sarah.chen@seismic-monitor.org',
    avatar: 'https://images.unsplash.com/photo-1494790108755-2616c99fe38c?w=150&h=150&fit=crop&crop=face'
  },
  setUser: (user) => set({ user }),

  // Initial events (sample data)
  events: [
    {
      id: '1',
      timestamp: new Date(Date.now() - 3600000), // 1 hour ago
      magnitude: 6.2,
      depth: 15.4,
      location: {
        latitude: 37.7749,
        longitude: -122.4194,
        place: '12km NW of San Francisco, CA'
      },
      type: 'earthquake',
      confidence: 0.94,
      status: 'classified'
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 1800000), // 30 minutes ago
      magnitude: 4.1,
      depth: 8.2,
      location: {
        latitude: 34.0522,
        longitude: -118.2437,
        place: '5km E of Los Angeles, CA'
      },
      type: 'earthquake',
      confidence: 0.87,
      status: 'classified'
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 300000), // 5 minutes ago
      magnitude: 2.8,
      depth: 2.1,
      location: {
        latitude: 40.7128,
        longitude: -74.0060,
        place: 'Manhattan, NY (Suspected Construction)'
      },
      type: 'explosion',
      confidence: 0.76,
      status: 'analyzing'
    },
    {
      id: '4',
      timestamp: new Date(),
      magnitude: 7.1,
      depth: 22.5,
      location: {
        latitude: 36.7783,
        longitude: -119.4179,
        place: '15km SW of Fresno, CA'
      },
      type: 'earthquake',
      confidence: 0.98,
      status: 'alert'
    }
  ],
  setEvents: (events) => set({ events }),
  addEvent: (event) => set((state) => ({ events: [event, ...state.events] })),
  updateEvent: (id, updates) => set((state) => ({
    events: state.events.map(event =>
      event.id === id ? { ...event, ...updates } : event
    )
  })),

  // UI state
  isLoading: false,
  setIsLoading: (isLoading) => set({ isLoading }),

  // Modals
  activeModal: null,
  setActiveModal: (activeModal) => set({ activeModal }),

  // Settings
  settings: {
    theme: 'dark',
    notifications: true,
    autoRefresh: true,
    refreshInterval: 30,
    alertThreshold: 5.0,
    mapStyle: 'satellite'
  },
  updateSettings: (updates) => set((state) => ({
    settings: { ...state.settings, ...updates }
  })),

  // Monitoring
  isMonitoring: true,
  setIsMonitoring: (isMonitoring) => set({ isMonitoring }),

  // Notifications
  notifications: [],
  addNotification: (notification) => {
    const id = Date.now().toString()
    set((state) => ({
      notifications: [{
        ...notification,
        id,
        timestamp: new Date()
      }, ...state.notifications]
    }))

    // Auto-remove after 5 seconds
    setTimeout(() => {
      get().removeNotification(id)
    }, 5000)
  },
  removeNotification: (id) => set((state) => ({
    notifications: state.notifications.filter(n => n.id !== id)
  })),

  // Modal states
  showNotifications: false,
  setShowNotifications: (show) => set({ showNotifications: show }),
  showSettings: false,
  setShowSettings: (show) => set({ showSettings: show }),
  showUserMenu: false,
  setShowUserMenu: (show) => set({ showUserMenu: show }),
  showFileUpload: false,
  setShowFileUpload: (show) => set({ showFileUpload: show })
}))
