import { motion } from 'framer-motion'
import {
    Activity,
    AlertTriangle,
    BarChart3,
    MapPin,
    Signal,
    Timer,
    TrendingUp,
    Zap
} from 'lucide-react'
import React from 'react'

// Components
import { FrequencyAnalysis, MagnitudeDistribution, SeismicWaveform } from '@/components/charts/SeismicCharts'
import { Button } from '@/components/ui/Button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'

// Store
import { formatMagnitude, formatTimestamp, getEventTypeIcon, getMagnitudeColor } from '@/lib/utils'
import { useAppStore } from '@/store/appStore'

const statsVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.1,
      duration: 0.5,
    },
  }),
}

interface StatCardProps {
  title: string
  value: string | number
  icon: React.ComponentType<any>
  change?: string
  changeType?: 'positive' | 'negative' | 'neutral'
  index: number
  color?: string
}

function StatCard({ title, value, icon: Icon, change, changeType = 'neutral', index, color = 'blue' }: StatCardProps) {
  const getChangeColor = () => {
    switch (changeType) {
      case 'positive': return 'text-green-400'
      case 'negative': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const getColorClasses = () => {
    switch (color) {
      case 'red': return 'from-red-500 to-red-600'
      case 'yellow': return 'from-yellow-500 to-orange-600'
      case 'green': return 'from-green-500 to-green-600'
      case 'purple': return 'from-purple-500 to-purple-600'
      default: return 'from-blue-500 to-blue-600'
    }
  }

  return (
    <motion.div
      custom={index}
      initial="hidden"
      animate="visible"
      variants={statsVariants}
    >
      <Card className="relative overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground mb-1">{title}</p>
              <p className="text-2xl font-bold">{value}</p>
              {change && (
                <p className={`text-sm ${getChangeColor()} flex items-center mt-1`}>
                  <TrendingUp className="w-3 h-3 mr-1" />
                  {change}
                </p>
              )}
            </div>
            <div className={`w-12 h-12 rounded-lg bg-gradient-to-br ${getColorClasses()} flex items-center justify-center`}>
              <Icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </CardContent>

        {/* Animated background element */}
        <motion.div
          className="absolute bottom-0 left-0 h-1 bg-gradient-to-r from-transparent via-primary to-transparent"
          initial={{ width: '0%' }}
          animate={{ width: '100%' }}
          transition={{ duration: 1, delay: index * 0.1 }}
        />
      </Card>
    </motion.div>
  )
}

export function Dashboard() {
  const { events, isMonitoring, setActiveModal } = useAppStore()

  // Calculate stats
  const last24Hours = events.filter(event =>
    new Date().getTime() - event.timestamp.getTime() < 24 * 60 * 60 * 1000
  )

  const highMagnitudeEvents = last24Hours.filter(event => event.magnitude >= 5.0)
  const averageMagnitude = last24Hours.length > 0
    ? last24Hours.reduce((sum, event) => sum + event.magnitude, 0) / last24Hours.length
    : 0
  const alertEvents = events.filter(event => event.status === 'alert').length

  const stats = [
    {
      title: 'Total Events (24h)',
      value: last24Hours.length,
      icon: Activity,
      change: '+12%',
      changeType: 'positive' as const,
      color: 'blue'
    },
    {
      title: 'High Magnitude Events',
      value: highMagnitudeEvents.length,
      icon: AlertTriangle,
      change: '+3',
      changeType: 'negative' as const,
      color: 'red'
    },
    {
      title: 'Average Magnitude',
      value: formatMagnitude(averageMagnitude),
      icon: BarChart3,
      change: '-0.2',
      changeType: 'positive' as const,
      color: 'yellow'
    },
    {
      title: 'Active Alerts',
      value: alertEvents,
      icon: Zap,
      change: alertEvents > 0 ? 'Urgent' : 'Clear',
      changeType: alertEvents > 0 ? 'negative' : 'positive' as const,
      color: alertEvents > 0 ? 'red' : 'green'
    }
  ]

  const recentEvents = events.slice(0, 5)

  return (
    <div className="space-y-6">
      {/* Header Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="flex items-center justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold gradient-text">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Real-time seismic event monitoring and analysis
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${isMonitoring ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
            <span className="text-sm text-muted-foreground">
              {isMonitoring ? 'Monitoring Active' : 'Monitoring Paused'}
            </span>
          </div>
          <Button onClick={() => setActiveModal('fileUpload')}>
            Upload Data
          </Button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <StatCard key={stat.title} {...stat} index={index} />
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SeismicWaveform className="lg:col-span-2" />
        <MagnitudeDistribution />
        <FrequencyAnalysis />
      </div>

      {/* Recent Events Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Recent Events</span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setActiveModal('events')}
              >
                View All
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {recentEvents.map((event, index) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 rounded-lg bg-secondary/30 hover:bg-secondary/50 transition-colors cursor-pointer"
                >
                  <div className="flex items-center space-x-3">
                    <div className="text-xl">
                      {getEventTypeIcon(event.type)}
                    </div>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className={`font-medium ${getMagnitudeColor(event.magnitude)}`}>
                          M{formatMagnitude(event.magnitude)}
                        </span>
                        <span className="text-sm text-muted-foreground">
                          {event.location.place}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-muted-foreground mt-1">
                        <span className="flex items-center">
                          <Timer className="w-3 h-3 mr-1" />
                          {formatTimestamp(event.timestamp)}
                        </span>
                        <span className="flex items-center">
                          <MapPin className="w-3 h-3 mr-1" />
                          {event.depth.toFixed(1)}km deep
                        </span>
                        <span className="flex items-center">
                          <Signal className="w-3 h-3 mr-1" />
                          {(event.confidence * 100).toFixed(0)}% confidence
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className={`px-2 py-1 rounded-md text-xs font-medium ${
                    event.status === 'alert' ? 'bg-red-500/20 text-red-400' :
                    event.status === 'classified' ? 'bg-green-500/20 text-green-400' :
                    event.status === 'analyzing' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>
                    {event.status}
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
