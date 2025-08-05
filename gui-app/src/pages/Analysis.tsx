import { motion } from 'framer-motion'
import { Activity, BarChart, Calendar, Download, Filter, LineChart, TrendingUp } from 'lucide-react'
import React from 'react'
import {
    Bar,
    CartesianGrid,
    Cell,
    Line,
    Pie,
    PieChart,
    BarChart as RechartsBarChart,
    LineChart as RechartsLineChart,
    ResponsiveContainer,
    Scatter,
    ScatterChart,
    Tooltip,
    XAxis,
    YAxis
} from 'recharts'
import { Button } from '../components/ui/Button'
import { Card } from '../components/ui/Card'
import { useAppStore } from '../store/appStore'

export function Analysis() {
  const { seismicEvents } = useAppStore()
  const [timeRange, setTimeRange] = React.useState('30d')
  const [filterType, setFilterType] = React.useState('all')

  // Process data for charts
  const processedData = React.useMemo(() => {
    const filtered = seismicEvents.filter(event => {
      const eventDate = new Date(event.timestamp)
      const now = new Date()
      const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 365
      const cutoff = new Date(now.getTime() - days * 24 * 60 * 60 * 1000)

      return eventDate >= cutoff && (filterType === 'all' || event.classification === filterType)
    })

    // Magnitude distribution
    const magnitudeDistribution = Array.from({ length: 8 }, (_, i) => {
      const min = i
      const max = i + 1
      const count = filtered.filter(e => e.magnitude >= min && e.magnitude < max).length
      return { magnitude: `${min}-${max}`, count, fill: getMagnitudeColor(min + 0.5) }
    })

    // Events over time
    const timelineData = Array.from({ length: 30 }, (_, i) => {
      const date = new Date()
      date.setDate(date.getDate() - (29 - i))
      const dayEvents = filtered.filter(e => {
        const eventDate = new Date(e.timestamp)
        return eventDate.toDateString() === date.toDateString()
      })
      return {
        date: date.toISOString().split('T')[0],
        events: dayEvents.length,
        avgMagnitude: dayEvents.length > 0 ? dayEvents.reduce((sum, e) => sum + e.magnitude, 0) / dayEvents.length : 0
      }
    })

    // Classification distribution
    const classificationData = [
      { name: 'Earthquake', value: filtered.filter(e => e.classification === 'earthquake').length, fill: '#ef4444' },
      { name: 'Explosion', value: filtered.filter(e => e.classification === 'explosion').length, fill: '#f97316' },
      { name: 'Volcanic', value: filtered.filter(e => e.classification === 'volcanic').length, fill: '#8b5cf6' },
      { name: 'Noise', value: filtered.filter(e => e.classification === 'noise').length, fill: '#6b7280' }
    ]

    // Depth vs Magnitude scatter
    const depthMagnitudeData = filtered.map(event => ({
      depth: event.depth,
      magnitude: event.magnitude,
      classification: event.classification
    }))

    return {
      magnitudeDistribution,
      timelineData,
      classificationData,
      depthMagnitudeData,
      totalEvents: filtered.length,
      avgMagnitude: filtered.length > 0 ? filtered.reduce((sum, e) => sum + e.magnitude, 0) / filtered.length : 0,
      maxMagnitude: filtered.length > 0 ? Math.max(...filtered.map(e => e.magnitude)) : 0
    }
  }, [seismicEvents, timeRange, filterType])

  function getMagnitudeColor(magnitude: number): string {
    if (magnitude >= 7) return '#dc2626'
    if (magnitude >= 5) return '#ea580c'
    if (magnitude >= 3) return '#ca8a04'
    return '#16a34a'
  }

  const exportData = () => {
    const csvContent = [
      ['Timestamp', 'Location', 'Magnitude', 'Depth', 'Classification', 'Confidence'],
      ...seismicEvents.map(event => [
        event.timestamp,
        event.location,
        event.magnitude,
        event.depth,
        event.classification,
        event.confidence
      ])
    ].map(row => row.join(',')).join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `seismic-analysis-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Data Analysis</h1>
          <p className="text-muted-foreground">Comprehensive seismic event analysis and trends</p>
        </div>

        <div className="flex items-center space-x-4">
          <Button
            variant="outline"
            onClick={exportData}
            className="flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export CSV</span>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card className="p-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Filter className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Filters:</span>
          </div>

          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-muted-foreground" />
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="px-3 py-1 rounded border border-border bg-background text-sm"
            >
              <option value="7d">Last 7 days</option>
              <option value="30d">Last 30 days</option>
              <option value="365d">Last year</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-muted-foreground" />
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3 py-1 rounded border border-border bg-background text-sm"
            >
              <option value="all">All Types</option>
              <option value="earthquake">Earthquakes</option>
              <option value="explosion">Explosions</option>
              <option value="volcanic">Volcanic</option>
              <option value="noise">Noise</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Events</p>
                <p className="text-2xl font-bold">{processedData.totalEvents}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-500" />
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
                <p className="text-sm text-muted-foreground">Avg Magnitude</p>
                <p className="text-2xl font-bold">{processedData.avgMagnitude.toFixed(1)}</p>
              </div>
              <BarChart className="w-8 h-8 text-green-500" />
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
                <p className="text-sm text-muted-foreground">Max Magnitude</p>
                <p className="text-2xl font-bold">{processedData.maxMagnitude.toFixed(1)}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-red-500" />
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
                <p className="text-sm text-muted-foreground">Events/Day</p>
                <p className="text-2xl font-bold">
                  {(processedData.totalEvents / (timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 365)).toFixed(1)}
                </p>
              </div>
              <LineChart className="w-8 h-8 text-purple-500" />
            </div>
          </Card>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Events Timeline */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Events Over Time</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsLineChart data={processedData.timelineData}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                <XAxis
                  dataKey="date"
                  tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  stroke="currentColor"
                  opacity={0.5}
                />
                <YAxis stroke="currentColor" opacity={0.5} />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  contentStyle={{
                    background: 'rgba(0, 0, 0, 0.8)',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="events"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', r: 4 }}
                  activeDot={{ r: 6, fill: '#3b82f6' }}
                />
              </RechartsLineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Magnitude Distribution */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Magnitude Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsBarChart data={processedData.magnitudeDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                <XAxis dataKey="magnitude" stroke="currentColor" opacity={0.5} />
                <YAxis stroke="currentColor" opacity={0.5} />
                <Tooltip
                  contentStyle={{
                    background: 'rgba(0, 0, 0, 0.8)',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} />
              </RechartsBarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Classification Distribution */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Event Classification</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={processedData.classificationData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {processedData.classificationData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: 'rgba(0, 0, 0, 0.8)',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-4">
            {processedData.classificationData.map((item) => (
              <div key={item.name} className="flex items-center space-x-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.fill }}
                />
                <span className="text-sm">{item.name}: {item.value}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* Depth vs Magnitude Scatter */}
        <Card className="p-6">
          <h3 className="text-lg font-semibold mb-4">Depth vs Magnitude</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart data={processedData.depthMagnitudeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.1} />
                <XAxis
                  dataKey="depth"
                  name="Depth (km)"
                  stroke="currentColor"
                  opacity={0.5}
                />
                <YAxis
                  dataKey="magnitude"
                  name="Magnitude"
                  stroke="currentColor"
                  opacity={0.5}
                />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value, name) => [value, name === 'magnitude' ? 'Magnitude' : 'Depth (km)']}
                  contentStyle={{
                    background: 'rgba(0, 0, 0, 0.8)',
                    border: 'none',
                    borderRadius: '8px',
                    color: '#fff'
                  }}
                />
                <Scatter
                  dataKey="magnitude"
                  fill="#3b82f6"
                  opacity={0.7}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Additional Insights */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Analysis Insights</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
            <h4 className="font-medium text-blue-600 dark:text-blue-400">Activity Trend</h4>
            <p className="text-sm text-muted-foreground mt-2">
              {processedData.timelineData.slice(-7).reduce((sum, d) => sum + d.events, 0) >
               processedData.timelineData.slice(-14, -7).reduce((sum, d) => sum + d.events, 0)
                ? "Seismic activity has increased"
                : "Seismic activity has decreased"} in the last week compared to the previous week.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-green-500/10 border border-green-500/20">
            <h4 className="font-medium text-green-600 dark:text-green-400">Magnitude Patterns</h4>
            <p className="text-sm text-muted-foreground mt-2">
              Most events ({processedData.magnitudeDistribution.find(d => d.count === Math.max(...processedData.magnitudeDistribution.map(x => x.count)))?.magnitude || 'N/A'})
              fall within the lower magnitude range, indicating normal seismic background activity.
            </p>
          </div>

          <div className="p-4 rounded-lg bg-purple-500/10 border border-purple-500/20">
            <h4 className="font-medium text-purple-600 dark:text-purple-400">Classification Accuracy</h4>
            <p className="text-sm text-muted-foreground mt-2">
              The detection system shows high confidence ({((seismicEvents.reduce((sum, e) => sum + e.confidence, 0) / seismicEvents.length) * 100).toFixed(0)}% average)
              across all event classifications.
            </p>
          </div>
        </div>
      </Card>
    </div>
  )
}
