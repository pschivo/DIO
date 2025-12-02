import { NextRequest, NextResponse } from 'next/server'
import { addEvent, getEvents } from '@/lib/events-storage'
import { addThreat, getThreats } from '@/lib/threats-storage'
import { db } from '@/lib/db'

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
        system_info: threatData.system_info || agentInfo, // Use agent-provided system_info first, fallback to fetched info
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
    
    // Store the event in development storage AND database
    addEvent(eventData)
    
    // Save to database via events API to ensure consistent fallback behavior
    try {
      const eventsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'}/api/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData)
      })
      
      if (eventsResponse.ok) {
        const eventsResult = await eventsResponse.json()
        console.log('Threat event saved via events API:', eventsResult.savedToDb)
      } else {
        console.log('Failed to save threat event via events API')
      }
    } catch (eventsError) {
      console.error('Error saving threat event via events API:', eventsError)
    }
    
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
    // In production, query threats from database events
    try {
      if (db) {
        const threatEvents = await db.event.findMany({
          where: {
            type: 'threat'
          },
          orderBy: {
            timestamp: 'desc'
          },
          take: 50
        })
        
        if (threatEvents && threatEvents.length > 0) {
          const threats = threatEvents.map(event => ({
            id: event.id,
            name: event.name,
            type: event.details?.threat_type || 'unknown',
            severity: event.severity,
            description: event.description,
            agent_id: event.agentId,
            agent_info: event.details?.system_info,
            detected_at: event.timestamp.toISOString(),
            status: event.status || 'active'
          }))
          
          console.log(`Found ${threats.length} threat events in database`)
          return NextResponse.json({
            success: true,
            data: threats,
            timestamp: new Date().toISOString()
          })
        } else {
          console.log('No threat events found in database')
        }
      }
    } catch (dbError) {
      console.error('Database query failed:', dbError)
    }
    
    // In production, if no database threats, return empty array
    if (process.env.NODE_ENV === 'production') {
      console.warn('No threat events available in production')
      return NextResponse.json({
        success: true,
        data: [],
        timestamp: new Date().toISOString()
      })
    }
    
    // Only return database results - no mock data
    console.warn('No threat events available - threats need to be generated by agents or attack simulator')
    return NextResponse.json({
      success: true,
      data: [],
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to fetch threats:', error)
    return NextResponse.json(
      { 
        success: false, 
        data: [],
        error: 'Failed to fetch threats',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}