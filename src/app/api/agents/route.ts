import { NextRequest, NextResponse } from 'next/server'
import { getThreats } from '@/lib/threats-storage'

const NERVE_CENTER_URL = process.env.NERVE_CENTER_URL || 'http://nerve-center:8000'

// Mock agents data based on agents.sh script structure
const getMockAgents = () => {
  return [
    {
      id: 'agent-24e8f584',
      name: 'DIO-Agent-ffe647820740',
      hostname: 'dio-agent-001',
      status: 'active' as const,
      rank: 1,
      cpu: 13.5,
      memory: 13.7,
      lastSeen: new Date().toISOString(),
      threats: 0,
      ipAddress: '172.20.0.9',
      osType: 'Linux 6.8.0-87-generic'
    },
    {
      id: 'agent-5b2a9c1f',
      name: 'DIO-Agent-8d3e4a2b1c9f',
      hostname: 'dio-agent-002',
      status: 'active' as const,
      rank: 2,
      cpu: 8.2,
      memory: 16.4,
      lastSeen: new Date().toISOString(),
      threats: 1,
      ipAddress: '172.20.0.10',
      osType: 'Linux 6.8.0-87-generic'
    },
    {
      id: 'agent-9f7e3d2a',
      name: 'DIO-Agent-6c5b8a1e4f9d',
      hostname: 'dio-agent-003',
      status: 'warning' as const,
      rank: 3,
      cpu: 45.8,
      memory: 67.2,
      lastSeen: new Date(Date.now() - 300000).toISOString(), // 5 minutes ago
      threats: 3,
      ipAddress: '172.20.0.11',
      osType: 'Linux 6.8.0-87-generic'
    }
  ]
}

export async function GET() {
  try {
    // Try to fetch from nerve center first
    try {
      const response = await fetch(`${NERVE_CENTER_URL}/agents`)
      
      if (response.ok) {
        const agents = await response.json()
        return NextResponse.json({
          success: true,
          data: agents,
          timestamp: new Date().toISOString()
        })
      }
    } catch (nerveCenterError) {
      console.log('Nerve center not available')
    }
    
    // In production, if nerve center is not available, return empty data
    // Do NOT use mock data in production environment
    if (process.env.NODE_ENV === 'production') {
      console.warn('Nerve center not available in production - no agents data available')
      return NextResponse.json({
        success: true,
        data: [],
        timestamp: new Date().toISOString()
      })
    }
    
    // Only use mock data in development
    console.warn('Nerve center not available, using mock agents data for development only')
    const agents = getMockAgents()
    
    // Get threats and calculate threats per agent
    const threats = getThreats()
    const agentsWithThreats = agents.map(agent => {
      const agentThreats = threats.filter(threat => threat.agent_id === agent.id && threat.status === 'active')
      return {
        ...agent,
        threats: agentThreats.length
      }
    })
    
    return NextResponse.json({
      success: true,
      data: agentsWithThreats,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Failed to fetch agents:', error)
    
    // In production, return empty data on error
    if (process.env.NODE_ENV === 'production') {
      return NextResponse.json({
        success: true,
        data: [],
        timestamp: new Date().toISOString()
      })
    }
    
    return NextResponse.json(
      { 
        success: false, 
        data: [],
        error: 'Failed to fetch agents - no real agents in production',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Forward agent registration to nerve center
    const response = await fetch(`${NERVE_CENTER_URL}/agents/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    })
    
    if (!response.ok) {
      throw new Error(`Nerve center responded with ${response.status}`)
    }
    
    const result = await response.json()
    
    return NextResponse.json({
      success: true,
      data: result,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Failed to create agent:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to create agent',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}