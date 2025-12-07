"use client"

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Separator } from '@/components/ui/separator'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { 
  Shield, 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Server, 
  Network, 
  Brain,
  Eye,
  TrendingUp,
  Users,
  Cpu,
  HardDrive,
  Wifi,
  Zap,
  Moon,
  Sun,
  Calendar,
  Clock,
  FileText,
  Bug,
  AlertCircle
} from 'lucide-react'

interface Agent {
  id: string
  name: string
  hostname: string
  status: 'active' | 'warning' | 'offline'
  rank: number
  cpu: number
  memory: number
  lastSeen: string
  threats: number
  ipAddress: string
  osType: string
}

interface SystemHealth {
  component: string
  status: 'healthy' | 'warning' | 'critical'
  cpu: number
  memory: number
  disk: number
  network: number
  uptime: number
}

interface ComponentLogs {
  mTLS: string[]
  NATS: string[]
  SPIFFE: string[]
  System: string[]
}

interface Threat {
  id: string
  name: string
  type: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  description: string
  status: string
  detected_at: string
  agent_id?: string
  agent_info?: {
    hostname: string
    os_type: string
    ip_address: string
  }
  confidence?: number
  signature?: string
}

export default function DIODashboard() {
  const [agents, setAgents] = useState<Agent[]>([])
  const [threats, setThreats] = useState<Threat[]>([])
  const [events, setEvents] = useState<any[]>([])
  const [selectedEvent, setSelectedEvent] = useState<any>(null)
  const [showInvestigationModal, setShowInvestigationModal] = useState(false)
  const [showLogsModal, setShowLogsModal] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h')
  const [isDarkMode, setIsDarkMode] = useState(false)
  const [systemHealth, setSystemHealth] = useState<SystemHealth[]>([])
  const [networkMetrics, setNetworkMetrics] = useState<any>(null)
  const [componentLogs, setComponentLogs] = useState<ComponentLogs | null>(null)

  // Fetch real data from API
  useEffect(() => {
    const fetchRealData = async () => {
      try {
        // Fetch agents from API
        const agentsResponse = await fetch('/api/agents')
        if (agentsResponse.ok) {
          const agentsData = await agentsResponse.json()
          setAgents(agentsData.data || [])
        }

        // Fetch threats from API
        const threatsResponse = await fetch('/api/threats')
        if (threatsResponse.ok) {
          const threatsData = await threatsResponse.json()
          setThreats(threatsData.data || [])
        }

        // Fetch events from API
        const eventsResponse = await fetch('/api/events')
        if (eventsResponse.ok) {
          const eventsData = await eventsResponse.json()
          setEvents(eventsData.data || [])
        }

        // Fetch component logs from API
        const logsResponse = await fetch('/api/logs')
        if (logsResponse.ok) {
          const logsData = await logsResponse.json()
          setComponentLogs(logsData.data)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
        // Set empty arrays if API fails
        setAgents([])
        setEvents([])
      }
      setIsLoading(false)
    }

    fetchRealData()
    const interval = setInterval(fetchRealData, 10000) // Update every 10 seconds
    return () => clearInterval(interval)
  }, [])

  // Fetch system health data
  useEffect(() => {
    const fetchSystemHealth = async () => {
      try {
        const response = await fetch('/api/system-health')
        if (response.ok) {
          const data = await response.json()
          setSystemHealth(data.data || [])
        }
      } catch (error) {
        console.error('Error fetching system health:', error)
      }
    }

    fetchSystemHealth()
    const interval = setInterval(fetchSystemHealth, 3000) // Update every 3 seconds
    return () => clearInterval(interval)
  }, [])

  // Fetch network metrics data
  useEffect(() => {
    const fetchNetworkMetrics = async () => {
      try {
        const response = await fetch('/api/network-metrics')
        if (response.ok) {
          const data = await response.json()
          setNetworkMetrics(data.data || {})
        }
      } catch (error) {
        console.error('Error fetching network metrics:', error)
      }
    }

    fetchNetworkMetrics()
    const interval = setInterval(fetchNetworkMetrics, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'healthy':
        return isDarkMode ? 'bg-green-600' : 'bg-green-500'
      case 'warning':
        return isDarkMode ? 'bg-yellow-600' : 'bg-yellow-500'
      case 'offline':
      case 'critical':
        return isDarkMode ? 'bg-red-600' : 'bg-red-500'
      default:
        return isDarkMode ? 'bg-gray-600' : 'bg-gray-500'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low':
        return isDarkMode ? 'bg-blue-900 text-blue-200' : 'bg-blue-100 text-blue-800'
      case 'medium':
        return isDarkMode ? 'bg-yellow-900 text-yellow-200' : 'bg-yellow-100 text-yellow-800'
      case 'high':
        return isDarkMode ? 'bg-orange-900 text-orange-200' : 'bg-orange-100 text-orange-800'
      case 'critical':
        return isDarkMode ? 'bg-red-900 text-red-200' : 'bg-red-100 text-red-800'
      default:
        return isDarkMode ? 'bg-gray-700 text-gray-300' : 'bg-gray-100 text-gray-800'
    }
  }

  const formatUptime = (uptimeSeconds: number) => {
    if (uptimeSeconds < 60) {
      return `${Math.floor(uptimeSeconds)}m`
    } else if (uptimeSeconds < 3600) {
      const hours = Math.floor(uptimeSeconds / 3600)
      const minutes = Math.floor((uptimeSeconds % 3600) / 60)
      return `${hours}h ${minutes}m`
    } else {
      const hours = Math.floor(uptimeSeconds / 3600)
      const minutes = Math.floor((uptimeSeconds % 3600) / 60)
      return `${hours}h ${minutes}m`
    }
  }

  const acknowledgeEvent = async (eventId: string) => {
    try {
      const response = await fetch(`/api/events/${eventId}`, {
        method: 'POST'
      })
      const result = await response.json()
      if (result.success) {
        // Update the event status in local state
        setEvents(prev => prev.map(event => 
          event.id === eventId ? { ...event, status: 'acknowledged' } : event
        ))
        setThreats(prev => prev.map(threat => {
          // Handle both event-threat- prefixed IDs and raw threat IDs
          const threatId = eventId.replace('event-threat-', '')
          return threat.id === eventId || threat.id === threatId ? { ...threat, status: 'acknowledged' } : threat
        }))
      }
    } catch (error) {
      console.error('Failed to acknowledge event:', error)
    }
  }

  const openInvestigationModal = (event: any) => {
    setSelectedEvent(event)
    setShowInvestigationModal(true)
  }

  const goToEvent = (eventId: string) => {
    // Navigate to Events tab and highlight the specific event
    // Remove any existing hash
    window.history.pushState({}, '')
    // Add the event ID to hash
    window.location.hash = `#events-${eventId}`
  }

  const fetchEvents = async () => {
    try {
      const response = await fetch('/api/events')
      const result = await response.json()
      if (result.success) {
        setEvents(result.data || [])
      }
    } catch (error) {
      console.error('Failed to fetch events:', error)
      setEvents([])
    }
  }

  const activeAgents = agents.filter(a => a.status === 'active').length
  const totalThreats = threats.length
  const criticalThreats = threats.filter(t => t.severity === 'critical').length
  const highThreats = threats.filter(t => t.severity === 'high').length
  const mediumThreats = threats.filter(t => t.severity === 'medium').length
  const lowThreats = threats.filter(t => t.severity === 'low').length
  
  // Get only last 5 threats for Overview tab (sorted by detected_at)
  const recentThreats = threats
    .sort((a, b) => new Date(b.detected_at || 0).getTime() - new Date(a.detected_at || 0).getTime())
    .slice(0, 5)

  if (isLoading) {
    return (
      <div className={`flex items-center justify-center min-h-screen ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-background text-foreground'} transition-colors duration-300`}>
        <div className="text-center">
          <Activity className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p>Initializing DIO Platform...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen ${isDarkMode ? 'bg-gray-900 text-white' : 'bg-background text-foreground'} transition-colors duration-300`}>
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Shield className={`h-8 w-8 ${isDarkMode ? 'text-primary' : 'text-primary'}`} />
            <div>
              <h1 className={`text-3xl font-bold ${isDarkMode ? 'text-white' : 'text-foreground'}`}>DIO Platform</h1>
              <p className={isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}>Digital Immune Organism Security Dashboard</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsDarkMode(!isDarkMode)}
              className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white hover:bg-gray-600' : 'bg-background border-border hover:bg-gray-50'} transition-colors duration-300`}
            >
              {isDarkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
            <Badge variant="outline" className="text-green-600">
              <CheckCircle className="h-3 w-3 mr-1" />
              System Active
            </Badge>
            <Badge variant="outline" className={`${isDarkMode ? 'text-white border-gray-600' : ''}`}>
              {new Date().toLocaleString()}
            </Badge>
          </div>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-white' : ''}`}>Active Agents</CardTitle>
              <Users className={`h-4 w-4 ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{activeAgents}</div>
              <p className={`text-xs ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>
                {agents.length} total deployed
              </p>
            </CardContent>
          </Card>

          <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-white' : ''}`}>Total Threats</CardTitle>
              <AlertTriangle className={`h-4 w-4 ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalThreats}</div>
              <div className="flex flex-wrap gap-1 mt-2">
                {criticalThreats > 0 && (
                  <Badge className="bg-red-600 text-white border-red-700">
                    {criticalThreats} critical
                  </Badge>
                )}
                {highThreats > 0 && (
                  <Badge className="bg-orange-600 text-white border-orange-700">
                    {highThreats} high
                  </Badge>
                )}
                {mediumThreats > 0 && (
                  <Badge className="bg-yellow-600 text-white border-yellow-700">
                    {mediumThreats} medium
                  </Badge>
                )}
                {lowThreats > 0 && (
                  <Badge className="bg-blue-400 text-white border-blue-500">
                    {lowThreats} low
                  </Badge>
                )}
                {totalThreats === 0 && (
                  <span className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-muted-foreground'}`}>
                    No threats detected
                  </span>
                )}
              </div>
            </CardContent>
          </Card>

          <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-white' : ''}`}>Network Health</CardTitle>
              <Network className={`h-4 w-4 ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {networkMetrics?.status === 'healthy' ? '98%' : 
                 networkMetrics?.status === 'degraded' ? '85%' : '65%'}
              </div>
              <p className={`text-xs ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>
                {networkMetrics?.status === 'healthy' ? 'Optimal performance' : 
                 networkMetrics?.status === 'degraded' ? 'Degraded performance' : 'Poor performance'}
              </p>
            </CardContent>
          </Card>

          <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className={`text-sm font-medium ${isDarkMode ? 'text-white' : ''}`}>AI Response Time</CardTitle>
              <Brain className={`h-4 w-4 ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {networkMetrics?.latency ? `${(networkMetrics.latency / 1000).toFixed(1)}s` : '1.2s'}
              </div>
              <p className={`text-xs ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>
                Average detection
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className={`grid w-full grid-cols-6 ${isDarkMode ? 'bg-gray-700 border-gray-600' : 'bg-background'}`}>
            <TabsTrigger value="overview" className={isDarkMode ? 'text-white data-[state=active]:bg-white data-[state=active]:text-black' : ''}>Overview</TabsTrigger>
            <TabsTrigger value="agents" className={isDarkMode ? 'text-white data-[state=active]:bg-white data-[state=active]:text-black' : ''}>Agents</TabsTrigger>
            <TabsTrigger value="threats" className={isDarkMode ? 'text-white data-[state=active]:bg-white data-[state=active]:text-black' : ''}>Threats</TabsTrigger>
            <TabsTrigger value="network" className={isDarkMode ? 'text-white data-[state=active]:bg-white data-[state=active]:text-black' : ''}>Network</TabsTrigger>
            <TabsTrigger value="health" className={isDarkMode ? 'text-white data-[state=active]:bg-white data-[state=active]:text-black' : ''}>System Health</TabsTrigger>
            <TabsTrigger value="events" className={isDarkMode ? 'text-white data-[state=active]:bg-white data-[state=active]:text-black' : ''}>Events</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
                <CardHeader>
                  <CardTitle>Recent Threats</CardTitle>
                  <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Latest security events and anomalies</CardDescription>
                </CardHeader>
                <CardContent className="space-y-3">
                  {recentThreats.length > 0 ? (
                    recentThreats.map((threat) => (
                      <div key={threat.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          <AlertTriangle className="h-4 w-4 text-orange-500" />
                          <div>
                            <p className="font-medium">{threat.name}</p>
                            <p className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>{threat.type}</p>
                            <p className={`text-xs ${isDarkMode ? 'text-gray-400' : 'text-muted-foreground'} mt-1`}>
                              Agent: {threat.agent_id || threat.agentId || 'Unknown'}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge className={getSeverityColor(threat.severity)}>
                            {threat.severity}
                          </Badge>
                          <p className={`text-xs ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'} mt-1`}>
                            {threat.detected_at ? new Date(threat.detected_at).toLocaleTimeString() : 'Unknown'}
                          </p>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className={`text-center py-8 ${isDarkMode ? 'text-gray-400' : 'text-muted-foreground'}`}>
                      <AlertTriangle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                      <p>No recent threats detected</p>
                      <p className="text-sm">System is operating normally</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
                <CardHeader>
                  <CardTitle>System Components</CardTitle>
                  <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Real-time component status</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {systemHealth.length > 0 ? (
                    systemHealth.map((component) => (
                      <div key={component.component} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <div className={`w-2 h-2 rounded-full ${getStatusColor(component.status)}`} />
                            <span className={`font-medium ${isDarkMode ? 'text-white' : ''}`}>{component.component}</span>
                          </div>
                          <Badge className="bg-green-100 text-green-800">{component.status}</Badge>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-sm">
                          <div className="flex items-center space-x-1">
                            <Cpu className="h-3 w-3" />
                            <span className={isDarkMode ? 'text-white' : ''}>CPU: {component.cpu.toFixed(1)}%</span>
                          </div>
                          <div className="flex items-center space-x-1">
                            <HardDrive className="h-3 w-3" />
                            <span className={isDarkMode ? 'text-white' : ''}>Memory: {component.memory.toFixed(1)}%</span>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="text-center py-8">
                      <Activity className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
                      <p className={`text-muted-foreground ${isDarkMode ? 'text-gray-300' : ''}`}>
                        System health data will appear here once components are active.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="agents" className="space-y-4">
            <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
              <CardHeader>
                <CardTitle>Deployed Agents</CardTitle>
                <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Monitor all active endpoint agents</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {agents.map((agent) => (
                    <Card key={agent.id} className={`relative ${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg">{agent.id}</CardTitle>
                          <div className={`w-3 h-3 rounded-full ${getStatusColor(agent.status)}`} />
                        </div>
                        <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>{agent.name}</CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex items-center justify-between text-sm">
                          <span className={isDarkMode ? 'text-white' : ''}>Rank</span>
                          <Badge className="bg-green-100 text-green-800">R{agent.rank}</Badge>
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className={isDarkMode ? 'text-white' : ''}>CPU</span>
                            <span>{agent.cpu.toFixed(1)}%</span>
                          </div>
                          <Progress value={agent.cpu} className="h-2" />
                        </div>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-sm">
                            <span className={isDarkMode ? 'text-white' : ''}>Memory</span>
                            <span>{agent.memory.toFixed(1)}%</span>
                          </div>
                          <Progress value={agent.memory} className="h-2" />
                        <div className="flex items-center justify-between text-sm pt-2 border-t">
                          <span>Threats</span>
                          <Badge variant={agent.threats > 0 ? "destructive" : "secondary"}>
                            {agent.threats}
                          </Badge>
                        </div>
                        </div>
                        <div className={`text-xs ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>
                          <p>{agent.ipAddress} • {agent.osType}</p>
                          <p>Last seen: {agent.lastSeen ? new Date(agent.lastSeen).toLocaleTimeString() : 'Unknown'}</p>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="threats" className="space-y-4">
            <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
              <CardHeader>
                <CardTitle>Security Threats</CardTitle>
                <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Detected threats and security events</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {threats.map((threat) => (
                    <Card key={threat.id} className={`border-l-4 border-l-orange-500 ${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg">{threat.name}</CardTitle>
                          <div className="flex items-center space-x-2">
                            <Badge className={getSeverityColor(threat.severity)}>
                              {threat.severity}
                            </Badge>
                            <Badge className="bg-green-100 text-green-800">{threat.status}</Badge>
                          </div>
                        </div>
                        <CardDescription>{threat.description}</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className={`flex items-center justify-between text-sm ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>
                            <span>Type: {threat.type}</span>
                            <div className="space-y-1">
                              <span>Detected: {threat.detected_at ? new Date(threat.detected_at).toLocaleString() : 'Unknown'}</span>
                              {threat.agent_info && (
                                <div className={`text-xs ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>
                                  <p>Agent: {threat.agent_id} ({threat.agent_info.os_type})</p>
                                  <p>IP: {threat.agent_info.ip_address}</p>
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <span className={`text-xs ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>
                              Confidence: {Math.round((threat.confidence || 0.8) * 100)}%
                            </span>
                            <div className="flex space-x-2">
                              {threat.status !== 'acknowledged' && (
                                <Button 
                                  size="sm" 
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    // Check if threat ID already has event-threat- prefix
                                    const eventId = threat.id.startsWith('event-threat-') ? threat.id : `event-threat-${threat.id}`
                                    acknowledgeEvent(eventId)
                                  }}
                                >
                                  Acknowledge
                                </Button>
                              )}
                              <Button 
                                size="sm" 
                                variant="outline"
                                className={isDarkMode ? 'text-black hover:text-gray-700' : ''}
                                onClick={(e) => {
                                  e.stopPropagation()
                                  openInvestigationModal({
                                    ...threat,
                                    id: `threat-${threat.id}`,
                                    type: 'threat',
                                    details: {
                                      threat_type: threat.type,
                                      signature: threat.signature
                                    }
                                  })
                                }}
                              >
                                Investigate
                              </Button>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="network" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
                <CardHeader>
                  <CardTitle>Mesh Network Status</CardTitle>
                  <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Network communication backbone</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className={isDarkMode ? 'text-white' : ''}>Network Status</span>
                    <Badge className={networkMetrics?.status === 'healthy' ? 'bg-green-100 text-green-800' : 
                                   networkMetrics?.status === 'degraded' ? 'bg-yellow-100 text-yellow-800' : 
                                   'bg-red-100 text-red-800'}>
                      {networkMetrics?.status || 'Unknown'}
                    </Badge>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Active Connections</span>
                      <span>{networkMetrics?.activeConnections || activeAgents}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className={isDarkMode ? 'text-white' : ''}>Message Rate</span>
                      <span>{networkMetrics?.messageRate ? `${networkMetrics.messageRate.toLocaleString()} msg/s` : 'Loading...'}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className={isDarkMode ? 'text-white' : ''}>Latency</span>
                      <span>{networkMetrics?.latency ? `${networkMetrics.latency}ms` : 'Loading...'}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
                <CardHeader>
                  <CardTitle>Communication Protocols</CardTitle>
                  <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Active communication channels</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    {networkMetrics?.protocols?.map((protocol: any, index: number) => (
                      <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-2">
                          {protocol.name === 'mTLS Transport' && <Wifi className="h-4 w-4" />}
                          {protocol.name === 'NATS Messaging' && <Zap className="h-4 w-4" />}
                          {protocol.name === 'SPIFFE Identity' && <Eye className="h-4 w-4" />}
                          <span>{protocol.name}</span>
                        </div>
                        <Badge className={protocol.status === 'Active' ? 'bg-green-100 text-green-800' : 
                                       protocol.status === 'Warning' ? 'bg-yellow-100 text-yellow-800' : 
                                       'bg-red-100 text-red-800'}>
                          {protocol.status}
                        </Badge>
                      </div>
                    )) || (
                      <>
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-2">
                            <Wifi className="h-4 w-4" />
                            <span>mTLS Transport</span>
                          </div>
                          <Badge className="bg-green-100 text-green-800">Active</Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-2">
                            <Zap className="h-4 w-4" />
                            <span>NATS Messaging</span>
                          </div>
                          <Badge className="bg-green-100 text-green-800">Active</Badge>
                        </div>
                        <div className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-2">
                            <Eye className="h-4 w-4" />
                            <span>SPIFFE Identity</span>
                          </div>
                          <Badge className="bg-green-100 text-green-800">Active</Badge>
                        </div>
                      </>
                    )}
                  </div>
                  <Button variant="outline" className={`w-full mt-4 ${isDarkMode ? 'text-black hover:text-gray-300' : 'text-gray-700 hover:text-gray-900'}`} onClick={() => setShowLogsModal(true)}>
                    <FileText className="h-4 w-4 mr-2" />
                    See More - Component Logs
                  </Button>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="health" className="space-y-4">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {systemHealth.map((component) => (
                <Card key={component.component} className={isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Server className="h-5 w-5" />
                      <span>{component.component}</span>
                    </CardTitle>
                    <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Component health metrics</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className={isDarkMode ? 'text-white' : 'text-foreground'}>Status</span>
                      <Badge className={getStatusColor(component.status) === 'bg-green-600' ? 'bg-green-100 text-green-800' : 
                                     getStatusColor(component.status) === 'bg-yellow-600' ? 'bg-yellow-100 text-yellow-800' : 
                                     'bg-red-100 text-red-800'}>
                        {component.status}
                      </Badge>
                    </div>
                    <div className="space-y-3">
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span>CPU Usage</span>
                          <span>{component.cpu.toFixed(1)}%</span>
                        </div>
                        <Progress value={component.cpu} className="h-2" />
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span>Memory</span>
                          <span>{component.memory.toFixed(1)}%</span>
                        </div>
                        <Progress value={component.memory} className="h-2" />
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span>Disk</span>
                          <span>{component.disk.toFixed(1)}%</span>
                        </div>
                        <Progress value={component.disk} className="h-2" />
                      </div>
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-sm">
                          <span>Network</span>
                          <span>{component.network.toFixed(1)}%</span>
                        </div>
                        <Progress value={component.network} className="h-2" />
                      </div>
                    </div>
                    <Separator />
                    <div className={`text-sm ${isDarkMode ? 'text-gray-300' : 'text-muted-foreground'}`}>
                      <p>Uptime: {formatUptime(component.uptime)}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="events" className="space-y-4">
            <Card className={`${isDarkMode ? 'bg-gray-700 border-gray-600 text-white' : 'bg-card border-border'}`}>
              <CardHeader>
                <CardTitle>System Events</CardTitle>
                <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Recent security events and activities</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                {/* Expand container to full height */}
                <div className="min-h-[600px] max-h-[800px]">
                  <div className="overflow-x-auto overflow-y-auto h-full">
                    <Table className="w-full min-w-[1200px]">
                      <TableHeader className="sticky top-0 bg-inherit z-10">
                        <TableRow>
                          <TableHead className="w-[180px] min-w-[150px] text-left">Datetime</TableHead>
                          <TableHead className="w-[300px] min-w-[250px] text-left">Description</TableHead>
                          <TableHead className="w-[100px] min-w-[80px] text-left">Severity</TableHead>
                          <TableHead className="w-[80px] min-w-[60px] text-left">Count</TableHead>
                          <TableHead className="w-[120px] min-w-[100px] text-left">Agent</TableHead>
                          <TableHead className="w-[140px] min-w-[120px] text-left">Hostname</TableHead>
                          <TableHead className="w-[120px] min-w-[100px] text-left">IP</TableHead>
                          <TableHead className="w-[100px] min-w-[80px] text-left">Type</TableHead>
                          <TableHead className="w-[80px] min-w-[60px] text-left">O.S.</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {events.length === 0 ? (
                          <TableRow>
                            <TableCell colSpan={9} className={`text-center py-8 ${isDarkMode ? 'text-gray-400' : 'text-muted-foreground'}`}>
                              <div className="flex flex-col items-center space-y-2">
                                <Calendar className="h-8 w-8 opacity-50" />
                                <p>No events found</p>
                                <p className="text-sm">Events will appear here when threats, anomalies, or system activities are detected.</p>
                              </div>
                            </TableCell>
                          </TableRow>
                        ) : (
                          events.map((event, index) => (
                            <TableRow key={event.id} id={`event-${event.id}`} className="border-b hover:bg-inherit">
                              <TableCell className="w-[180px] align-top">
                                <div className="text-xs">
                                  {event.timestamp ? new Date(event.timestamp).toLocaleString() : 'Unknown'}
                                </div>
                              </TableCell>
                              <TableCell className="w-[300px] align-top">
                                <div className="text-sm">
                                  <div className="font-semibold mb-1">{event.name}</div>
                                  {event.aggregated && (
                                    <div className="text-xs text-gray-500">
                                      Since: {event.firstSeen ? new Date(event.firstSeen).toLocaleString() : 'Unknown'}
                                    </div>
                                  )}
                                </div>
                              </TableCell>
                              <TableCell className="w-[100px] align-top">
                                <Badge className={getSeverityColor(event.severity)}>
                                  {event.severity}
                                </Badge>
                              </TableCell>
                              <TableCell className="w-[80px] align-top">
                                {event.aggregated ? (
                                  <div className="flex items-center space-x-2">
                                    <Badge variant="outline" className="bg-blue-100 text-blue-800 border-blue-300">
                                      {event.originalCount || event.count || 1}
                                    </Badge>
                                    <span className="text-xs text-gray-500">aggregated</span>
                                  </div>
                                ) : (
                                  <Badge variant="outline" className="bg-gray-100 text-gray-800 border-gray-300">
                                    1
                                  </Badge>
                                )}
                              </TableCell>
                              <TableCell className="w-[120px] align-top">
                                <div className="text-sm">
                                  {event.agentId || event.agent_id || 'Unknown'}
                                </div>
                              </TableCell>
                              <TableCell className="w-[140px] align-top">
                                <div className="text-sm">
                                  {event.details?.system_info?.hostname || 'Unknown'}
                                </div>
                              </TableCell>
                              <TableCell className="w-[120px] align-top">
                                <div className="text-sm">
                                  {event.details?.system_info?.ip_address || 'Unknown'}
                                </div>
                              </TableCell>
                              <TableCell className="w-[100px] align-top">
                                <div className="text-sm">
                                  {event.type}
                                </div>
                              </TableCell>
                              <TableCell className="w-[80px] align-top">
                                <div className="text-sm">
                                  {event.details?.system_info?.os_type || 'Unknown'}
                                </div>
                              </TableCell>
                            </TableRow>
                          ))
                        )}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Investigation Modal */}
      {showInvestigationModal && selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
             onClick={() => setShowInvestigationModal(false)}>
          <div className={`${isDarkMode ? 'bg-gray-700 text-white' : 'bg-white'} rounded-lg p-6 max-w-2xl max-h-[80vh] overflow-y-auto`}
               onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Event Investigation</h3>
              <Button variant="ghost" size="sm" onClick={() => setShowInvestigationModal(false)}>
                ×
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h4 className="font-medium">Event Information</h4>
                <div className="mt-2 space-y-2 text-sm">
                  <p><strong>ID:</strong> {selectedEvent.id}</p>
                  <p><strong>Type:</strong> {selectedEvent.type}</p>
                  <p><strong>Severity:</strong> {selectedEvent.severity}</p>
                  <p><strong>Status:</strong> {selectedEvent.status}</p>
                  <p><strong>Agent:</strong> {selectedEvent.agent_id}</p>
                  <p><strong>Detected:</strong> {selectedEvent.timestamp ? new Date(selectedEvent.timestamp).toLocaleString() : 'Unknown'}</p>
                </div>
              </div>
              
              <div>
                <h4 className="font-medium">Description</h4>
                <p className="mt-1 text-sm">{selectedEvent.description}</p>
              </div>
              
              {selectedEvent.details && (
                <div>
                  <h4 className="font-medium">Detailed Information</h4>
                  <div className={`mt-2 p-3 ${isDarkMode ? 'bg-gray-900 text-gray-200' : 'bg-gray-50'} rounded text-sm`}>
                    <pre className="whitespace-pre-wrap">{JSON.stringify(selectedEvent.details, null, 2)}</pre>
                  </div>
                </div>
              )}
              
              {selectedEvent.details && selectedEvent.details.processes && selectedEvent.details.processes.length > 0 && (
                <div>
                  <h4 className="font-medium">Suspicious Processes</h4>
                  <div className={`mt-2 p-2 ${isDarkMode ? 'bg-red-900 text-red-200' : 'bg-red-50'} rounded text-sm`}>
                    <ul className="list-disc list-inside ml-4">
                      {selectedEvent.details.processes.map((process: string, idx: number) => (
                        <li key={idx} className="text-red-600">{process}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
              
              {selectedEvent.details && selectedEvent.details.trigger && (
                <div>
                  <h4 className="font-medium">Attack Trigger</h4>
                  <div className={`mt-2 p-2 ${isDarkMode ? 'bg-orange-900 text-orange-200' : 'bg-orange-50'} rounded text-sm`}>
                    <p className="text-orange-600">{selectedEvent.details.trigger}</p>
                  </div>
                </div>
              )}
              
              {selectedEvent.details && selectedEvent.details.attack_type && (
                <div>
                  <h4 className="font-medium">Attack Type</h4>
                  <div className={`mt-2 p-2 ${isDarkMode ? 'bg-blue-900 text-blue-200' : 'bg-blue-50'} rounded text-sm`}>
                    <p className="text-blue-600">{selectedEvent.details.attack_type}</p>
                  </div>
                </div>
              )}
              
              {selectedEvent.details && selectedEvent.details.metrics && (
                <div>
                  <h4 className="font-medium">System Metrics</h4>
                  <div className={`mt-2 p-2 ${isDarkMode ? 'bg-gray-900 text-gray-200' : 'bg-gray-50'} rounded text-sm`}>
                    <div className="grid grid-cols-2 gap-2">
                      {Object.entries(selectedEvent.details.metrics || {}).map(([key, value]) => (
                        <div key={key}>
                          <span className="font-medium">{key}:</span> {String(value)}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
              
              <div className="flex space-x-2">
                {selectedEvent.status !== 'acknowledged' && (
                  <Button onClick={() => acknowledgeEvent(selectedEvent.id)}>
                    Acknowledge Event
                  </Button>
                )}
                <Button variant="outline" className={isDarkMode ? 'text-black hover:text-gray-300' : 'text-gray-700 hover:text-gray-900'} onClick={() => {
                  
                  // Find and click the events tab using multiple selectors
                  const eventsTab = document.querySelector('[value="events"]') || 
                                   document.querySelector('[data-state="active"][value="events"]') ||
                                   Array.from(document.querySelectorAll('[role="tab"]')).find((tab: any) => tab.textContent === 'Events')
                  if (eventsTab) {
                    (eventsTab as HTMLElement).click()
                  }
                  
                  // Add hash to URL and wait for tab to be active
                  window.location.hash = `event-${selectedEvent.id}`
                  
                  // Wait for tab content to be visible before scrolling
                  setTimeout(() => {
                    const eventElement = document.getElementById(`event-${selectedEvent.id}`)
                    if (eventElement) {
                      eventElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
                      eventElement.classList.add('ring-2', 'ring-blue-500', 'ring-offset-2')
                      setTimeout(() => {
                        eventElement.classList.remove('ring-2', 'ring-blue-500', 'ring-offset-2')
                      }, 3000)
                    } else {
                      console.warn('Event element not found:', `event-${selectedEvent.id}`)
                    }
                  }, 500) // Wait longer for tab to switch
                }}>
                  Go to Event
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Component Logs Modal */}
      <Dialog open={showLogsModal} onOpenChange={setShowLogsModal}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>DIO Component Logs</DialogTitle>
            <DialogDescription>
              Real-time logs from DIO platform components for troubleshooting and monitoring
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-6">
            {/* mTLS Transport Logs */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Wifi className="h-5 w-5" />
                  <span>mTLS Transport Logs</span>
                </CardTitle>
                <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Secure transport layer logs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm space-y-1 max-h-40 overflow-y-auto">
                  {componentLogs?.mTLS.map((log, index) => (
                    <div key={index}>{log}</div>
                  )) || <div>No logs available</div>}
                </div>
              </CardContent>
            </Card>

            {/* NATS Messaging Logs */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span>NATS Messaging Logs</span>
                </CardTitle>
                <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Message bus communication logs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm space-y-1 max-h-40 overflow-y-auto">
                  {componentLogs?.NATS.map((log, index) => (
                    <div key={index}>{log}</div>
                  )) || <div>No logs available</div>}
                </div>
              </CardContent>
            </Card>

            {/* SPIFFE Identity Logs */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Eye className="h-5 w-5" />
                  <span>SPIFFE Identity Logs</span>
                </CardTitle>
                <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Identity management and authentication logs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm space-y-1 max-h-40 overflow-y-auto">
                  {componentLogs?.SPIFFE.map((log, index) => (
                    <div key={index}>{log}</div>
                  )) || <div>No logs available</div>}
                </div>
              </CardContent>
            </Card>

            {/* System Logs */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Server className="h-5 w-5" />
                  <span>System Component Logs</span>
                </CardTitle>
                <CardDescription className={isDarkMode ? 'text-gray-300' : ''}>Overall system health and error logs</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="bg-black text-green-400 p-4 rounded-lg font-mono text-sm space-y-1 max-h-40 overflow-y-auto">
                  {componentLogs?.System.map((log, index) => (
                    <div key={index}>{log}</div>
                  )) || <div>No logs available</div>}
                </div>
              </CardContent>
            </Card>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}