import { motion } from 'framer-motion'
import { Activity, CheckCircle, Clock, MapPin, Wifi, WifiOff } from 'lucide-react'
import React from 'react'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { useAppStore } from '../store/appStore'

export function Monitoring() {
  const { seismicEvents, monitoringSettings, addNotification } = useAppStore()
  const [isLiveMonitoring, setIsLiveMonitoring] = React.useState(true)
  const [connectedStations, setConnectedStations] = React.useState(12)
  const [liveData, setLiveData] = React.useState<Array<{ time: number; amplitude: number }>>([])

  // Simulate real-time seismic data
  React.useEffect(() => {
    if (!isLiveMonitoring) return

    const interval = setInterval(() => {
      const now = Date.now()
      const amplitude = (Math.random() - 0.5) * 100 + Math.sin(now / 1000) * 20

      setLiveData(prev => {
        const newData = [...prev, { time: now, amplitude }].slice(-50)
        return newData
      })

      // Simulate random station connectivity changes
      if (Math.random() < 0.1) {
        setConnectedStations(prev => Math.max(8, Math.min(15, prev + (Math.random() > 0.5 ? 1 : -1))))
      }

      // Simulate earthquake detection
      if (Math.abs(amplitude) > 80 && Math.random() < 0.05) {
        addNotification({
          type: 'warning',
          title: 'Seismic Activity Detected',
          message: `High amplitude detected: ${amplitude.toFixed(1)} units`
        })
      }
    }, 100)

    return () => clearInterval(interval)
  }, [isLiveMonitoring, addNotification])

  const recentEvents = seismicEvents
    .filter(event => Date.now() - new Date(event.timestamp).getTime() < 24 * 60 * 60 * 1000)
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 10)

  const stationData = [
    { id: 'ST01', name: 'Mount Wilson', lat: 34.2259, lon: -118.0596, status: 'online', lastUpdate: '2 min ago' },
    { id: 'ST02', name: 'Pasadena', lat: 34.1478, lon: -118.1445, status: 'online', lastUpdate: '1 min ago' },
    { id: 'ST03', name: 'Long Beach', lat: 33.7701, lon: -118.1937, status: 'warning', lastUpdate: '5 min ago' },
    { id: 'ST04', name: 'Santa Monica', lat: 34.0194, lon: -118.4912, status: 'online', lastUpdate: '1 min ago' },
    { id: 'ST05', name: 'Riverside', lat: 33.9533, lon: -117.3962, status: 'offline', lastUpdate: '15 min ago' },
    { id: 'ST06', name: 'San Bernardino', lat: 34.1083, lon: -117.2898, status: 'online', lastUpdate: '3 min ago' },
  ]

  const toggleMonitoring = () => {
    setIsLiveMonitoring(!isLiveMonitoring)
    addNotification({
      type: 'info',
      title: 'Monitoring Status',
      message: `Live monitoring ${!isLiveMonitoring ? 'started' : 'stopped'}`
    })
  }

  const getMagnitudeColor = (magnitude: number) => {
    if (magnitude >= 7) return 'text-red-500'
    if (magnitude >= 5) return 'text-orange-500'
    if (magnitude >= 3) return 'text-yellow-500'
    return 'text-green-500'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return 'text-green-500'
      case 'warning': return 'text-yellow-500'
      case 'offline': return 'text-red-500'
      default: return 'text-gray-500'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Real-time Monitoring</h1>
          <p className="text-muted-foreground">Live seismic activity monitoring and station status</p>
        </div>

        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            {isLiveMonitoring ? (
              <Wifi className="w-4 h-4 text-green-500" />
            ) : (
              <WifiOff className="w-4 h-4 text-red-500" />
            )}
            <span className="text-sm font-medium">
              {isLiveMonitoring ? 'Live' : 'Offline'}
            </span>
          </div>

          <Button
            variant={isLiveMonitoring ? 'outline' : 'default'}
            onClick={toggleMonitoring}
            className="flex items-center space-x-2"
          >
            <Activity className="w-4 h-4" />
            <span>{isLiveMonitoring ? 'Stop' : 'Start'} Monitoring</span>
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Connected Stations</p>
                <p className="text-2xl font-bold">{connectedStations}/15</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Events Today</p>
                <p className="text-2xl font-bold">{recentEvents.length}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-500" />
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Avg Response Time</p>
                <p className="text-2xl font-bold">1.2s</p>
              </div>
              <Clock className="w-8 h-8 text-purple-500" />
            </div>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">System Status</p>
                <p className="text-2xl font-bold text-green-500">Healthy</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-500" />
            </div>
          </Card>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Live Waveform */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Live Seismic Waveform</h3>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-muted-foreground">Live</span>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={liveData}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                <XAxis
                  dataKey="time"
                  type="number"
                  scale="time"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  stroke="currentColor"
                  opacity={0.5}
                />
                <YAxis stroke="currentColor" opacity={0.5} />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                  formatter={(value: number) => [value.toFixed(2), 'Amplitude']}
                  contentStyle={{
                    background: 'rgba(0, 0, 0, 0.8)',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="amplitude"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 4, fill: '#3b82f6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Station Status */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Station Network Status</h3>

          <div className="space-y-3">
            {stationData.map((station, index) => (
              <motion.div
                key={station.id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 rounded-lg bg-secondary/30 border border-border/50"
              >
                <div className="flex items-center space-x-3">
                  <MapPin className="w-4 h-4 text-muted-foreground" />
                  <div>
                    <p className="font-medium">{station.name}</p>
                    <p className="text-xs text-muted-foreground">{station.id}</p>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <span className="text-xs text-muted-foreground">{station.lastUpdate}</span>
                  <div className={`w-2 h-2 rounded-full ${
                    station.status === 'online' ? 'bg-green-500' :
                    station.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                  }`} />
                  <span className={`text-sm font-medium ${getStatusColor(station.status)}`}>
                    {station.status}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </Card>
      </div>

      {/* Recent Events */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Events (Last 24 Hours)</h3>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-3 px-4 font-medium">Time</th>
                <th className="text-left py-3 px-4 font-medium">Location</th>
                <th className="text-left py-3 px-4 font-medium">Magnitude</th>
                <th className="text-left py-3 px-4 font-medium">Depth</th>
                <th className="text-left py-3 px-4 font-medium">Classification</th>
                <th className="text-left py-3 px-4 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {recentEvents.map((event, index) => (
                <motion.tr
                  key={event.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="border-b border-border/50 hover:bg-secondary/20"
                >
                  <td className="py-3 px-4 text-sm">
                    {new Date(event.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-3 px-4 text-sm">{event.location}</td>
                  <td className={`py-3 px-4 text-sm font-medium ${getMagnitudeColor(event.magnitude)}`}>
                    {event.magnitude.toFixed(1)}
                  </td>
                  <td className="py-3 px-4 text-sm">{event.depth.toFixed(1)} km</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      event.classification === 'earthquake' ? 'bg-red-500/20 text-red-500' :
                      event.classification === 'explosion' ? 'bg-orange-500/20 text-orange-500' :
                      'bg-blue-500/20 text-blue-500'
                    }`}>
                      {event.classification}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      event.confidence > 0.8 ? 'bg-green-500/20 text-green-500' :
                      event.confidence > 0.6 ? 'bg-yellow-500/20 text-yellow-500' :
                      'bg-red-500/20 text-red-500'
                    }`}>
                      {(event.confidence * 100).toFixed(0)}% confident
                    </span>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {recentEvents.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No recent seismic events detected</p>
          </div>
        )}
      </Card>
    </div>
  )
}
