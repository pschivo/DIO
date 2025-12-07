import { NextRequest, NextResponse } from 'next/server'
import { addEvent } from '@/lib/events-storage'
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
    const evidenceData = await request.json()
    
    // Get agent information to populate system_info
    const agentInfo = await getAgentInfo(evidenceData.agent_id)
    
    // Create event with system information
    const eventData = {
      id: `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: evidenceData.title || evidenceData.name || evidenceData.type || 'Security Event',
      type: evidenceData.type || 'evidence',
      severity: evidenceData.severity || 'medium',
      description: evidenceData.description || 'Security event detected',
      timestamp: new Date().toISOString(),
      agent_id: evidenceData.agent_id,
      details: {
        ...evidenceData.raw_data,
        system_info: agentInfo,
        confidence: evidenceData.confidence || 0.8
      }
    }
    
    // In production, try to send to nerve center
    if (process.env.NODE_ENV === 'production') {
      try {
        const response = await fetch(`${NERVE_CENTER_URL}/evidence`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(eventData)
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
        console.error('Failed to send evidence to nerve center:', error)
      }
    }
    
    // For development or if nerve center fails, just return success
    // The event will be picked up by the events API
    console.log('Evidence created:', eventData)
    
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
        console.log('Evidence event saved via events API:', eventsResult.savedToDb)
      } else {
        console.log('Failed to save evidence event via events API')
      }
    } catch (eventsError) {
      console.error('Error saving evidence event via events API:', eventsError)
    }
    
    return NextResponse.json({
      success: true,
      data: {
        event_id: eventData.id,
        message: 'Evidence created successfully'
      },
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to create evidence:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to create evidence',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}