import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card'
import { generateSeismicData } from '@/lib/utils'
import { motion } from 'framer-motion'
import React from 'react'
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00']

interface SeismicWaveformProps {
  className?: string
}

export function SeismicWaveform({ className }: SeismicWaveformProps) {
  const [data, setData] = React.useState(() => generateSeismicData(200))

  React.useEffect(() => {
    const interval = setInterval(() => {
      setData(generateSeismicData(200))
    }, 2000)

    return () => clearInterval(interval)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={className}
    >
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Live Seismic Waveform</span>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-green-400">Live</span>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="time"
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                  stroke="#9CA3AF"
                />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  labelFormatter={(value) => new Date(value).toLocaleTimeString()}
                  contentStyle={{
                    backgroundColor: 'rgba(17, 24, 39, 0.8)',
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="amplitude"
                  stroke="#3B82F6"
                  fill="url(#waveGradient)"
                  strokeWidth={2}
                />
                <defs>
                  <linearGradient id="waveGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
                  </linearGradient>
                </defs>
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

interface MagnitudeDistributionProps {
  className?: string
}

export function MagnitudeDistribution({ className }: MagnitudeDistributionProps) {
  const data = [
    { magnitude: '1.0-2.0', count: 120, color: '#10B981' },
    { magnitude: '2.0-3.0', count: 85, color: '#3B82F6' },
    { magnitude: '3.0-4.0', count: 45, color: '#F59E0B' },
    { magnitude: '4.0-5.0', count: 22, color: '#EF4444' },
    { magnitude: '5.0+', count: 8, color: '#DC2626' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className={className}
    >
      <Card>
        <CardHeader>
          <CardTitle>Magnitude Distribution (24h)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="magnitude" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(17, 24, 39, 0.8)',
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}

interface FrequencyAnalysisProps {
  className?: string
}

export function FrequencyAnalysis({ className }: FrequencyAnalysisProps) {
  const [data, setData] = React.useState(() => {
    return Array.from({ length: 50 }, (_, i) => ({
      frequency: i * 2,
      amplitude: Math.random() * 100 * Math.exp(-i * 0.1),
      phase: Math.random() * 360
    }))
  })

  React.useEffect(() => {
    const interval = setInterval(() => {
      setData(Array.from({ length: 50 }, (_, i) => ({
        frequency: i * 2,
        amplitude: Math.random() * 100 * Math.exp(-i * 0.1),
        phase: Math.random() * 360
      })))
    }, 3000)

    return () => clearInterval(interval)
  }, [])

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className={className}
    >
      <Card>
        <CardHeader>
          <CardTitle>Frequency Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="frequency"
                  label={{ value: 'Frequency (Hz)', position: 'insideBottom', offset: -10, style: { fill: '#9CA3AF' } }}
                  stroke="#9CA3AF"
                />
                <YAxis
                  label={{ value: 'Amplitude', angle: -90, position: 'insideLeft', style: { fill: '#9CA3AF' } }}
                  stroke="#9CA3AF"
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(17, 24, 39, 0.8)',
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="amplitude"
                  stroke="#8B5CF6"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
