import { NextRequest, NextResponse } from 'next/server'
import { addEvent, getEvents } from '@/lib/events-storage'
import { addThreat, getThreats } from '@/lib/threats-storage'

const NERVE_CENTER_URL = process.env.NERVE_CENTER_URL || 'http://nerve-center:8000'

// Helper function to get agent information
const getAgentInfo = async (agentId: string) => {
  try {
    // Try to get agent info from the agents API
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'}/api/agents`)
    if (response.ok) {
      const agentsData = await response.json()
      const agents = agentsData.data || []
      const agent = agents.find((a: any) => a.id === agentId)
      
      if (agent) {
        return {
          hostname: agent.hostname || `DIO-Agent-${agentId.slice(-12)}`,
          ip_address: agent.ipAddress || '172.20.0.9',
          os_type: agent.osType || 'Linux 6.8.0-87-generic'
        }
      }
    }
  } catch (error) {
    console.error('Failed to get agent info:', error)
  }
  
  // Fallback to generated values
  return {
    hostname: `DIO-Agent-${agentId.slice(-12)}`,
    ip_address: '172.20.0.9',
    os_type: 'Linux 6.8.0-87-generic'
  }
}

export async function POST(request: NextRequest) {
  try {
    const threatData = await request.json()
    
    // Get agent information to populate system_info
    const agentInfo = await getAgentInfo(threatData.agent_id)
    
    // Create event with system information
    const eventData = {
      id: `threat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: threatData.name || threatData.title || 'Threat Detected',
      type: 'threat',
      severity: threatData.severity || 'medium',
      description: threatData.description || 'Threat detected by agent',
      timestamp: new Date().toISOString(),
      agent_id: threatData.agent_id,
      details: {
        threat_type: threatData.type,
        system_info: agentInfo,
        confidence: 0.8
      }
    }
    
    // Create threat object for storage
    const threatObject = {
      id: eventData.id,
      name: threatData.name || 'Threat Detected',
      type: threatData.type || 'unknown',
      severity: threatData.severity || 'medium',
      description: threatData.description || 'Threat detected by agent',
      agent_id: threatData.agent_id,
      agent_info: agentInfo,
      detected_at: new Date().toISOString(),
      status: 'active'
    }
    
    // In production, try to send to nerve center
    if (process.env.NODE_ENV === 'production') {
      try {
        const response = await fetch(`${NERVE_CENTER_URL}/threats`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(threatData)
        })
        
        if (response.ok) {
          const result = await response.json()
          return NextResponse.json({
            success: true,
            data: result,
            timestamp: new Date().toISOString()
          })
        }
      } catch (error) {
        console.error('Failed to send threat to nerve center:', error)
      }
    }
    
    // For development or if nerve center fails, just return success
    // The event will be picked up by the events API
    console.log('Threat created:', eventData)
    
    // Store the event in development storage
    addEvent(eventData)
    
    // Store the threat in development storage
    addThreat(threatObject)
    
    return NextResponse.json({
      success: true,
      data: {
        threat_id: eventData.id,
        message: 'Threat created successfully'
      },
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to create threat:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to create threat',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  try {
    // Fetch threats from nerve center (production should have real threat logs)
    try {
      const response = await fetch(`${NERVE_CENTER_URL}/threats`)
      
      if (response.ok) {
        const threats = await response.json()
        return NextResponse.json({
          success: true,
          data: threats,
          timestamp: new Date().toISOString()
        })
      }
    } catch (nerveCenterError) {
      console.log('Nerve center not available')
    }
    
    // In production, if nerve center is not available, return empty data
    // Do NOT use mock data in production environment
    if (process.env.NODE_ENV === 'production') {
      console.warn('Nerve center not available in production - no threats data available')
      return NextResponse.json({
        success: true,
        data: [],
        timestamp: new Date().toISOString()
      })
    }
    
    // Only use mock data in development
    console.warn('Nerve center not available, using mock threats data for development only')
    const mockThreats = [
      {
        id: 'threat-001',
        name: 'CPU Exhaustion Attack - agent-6710fe5a',
        type: 'crypto_mining',
        severity: 'high',
        description: 'Cryptocurrency mining malware detected',
        agent_id: 'agent-6710fe5a',
        agent_info: {
          hostname: 'DIO-Agent-6710fe5a',
          ip_address: '172.20.0.9',
          os_type: 'Linux 6.8.0-87-generic'
        },
        detected_at: new Date().toISOString(),
        status: 'active'
      },
      {
        id: 'threat-002',
        name: 'Memory Leak Attack - agent-24e8f584',
        type: 'memory_corruption',
        severity: 'high',
        description: 'Process with memory leak consuming system resources',
        agent_id: 'agent-24e8f584',
        agent_info: {
          hostname: 'DIO-Agent-24e8f584',
          ip_address: '172.20.0.10',
          os_type: 'Linux 6.8.0-87-generic'
        },
        detected_at: new Date().toISOString(),
        status: 'active'
      }
    ]
    
    // Get development events that are threats
    const developmentEvents = getEvents()
    const developmentThreats = getThreats()
    
    // Convert development events to threat format
    const eventThreats = developmentEvents
      .filter(event => event.type === 'threat')
      .map(event => ({
        id: event.id,
        name: event.name,
        type: event.details?.threat_type || 'unknown',
        severity: event.severity,
        description: event.description,
        agent_id: event.agent_id,
        agent_info: event.details?.system_info,
        detected_at: event.timestamp,
        status: 'active'
      }))
    
    // Combine mock threats with development threats
    const allThreats = [...mockThreats, ...developmentThreats, ...eventThreats]
    
    return NextResponse.json({
      success: true,
      data: allThreats,
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to fetch threats:', error)
    
    // In production, return empty data on error
    return NextResponse.json(
      { 
        success: false, 
        data: [],
        error: 'Failed to fetch threats - no real threats in production',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}