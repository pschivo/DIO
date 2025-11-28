import { NextRequest, NextResponse } from 'next/server'
import { addEvent, getEvents } from '@/lib/events-storage'

// This endpoint receives events from nerve center and stores them
export async function POST(request: NextRequest) {
  try {
    const eventData = await request.json()
    
    // Validate event data
    if (!eventData.id || !eventData.type || !eventData.name) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Missing required event fields: id, type, name',
          timestamp: new Date().toISOString()
        },
        { status: 400 }
      )
    }
    
    // Create a new event with proper structure
    const newEvent = {
      id: eventData.id || `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      name: eventData.name || 'Unknown Event',
      type: eventData.type || 'system',
      severity: eventData.severity || 'medium',
      description: eventData.description || 'Event received from nerve center',
      timestamp: eventData.timestamp || new Date().toISOString(),
      agent_id: eventData.agent_id,
      details: eventData.details || {},
      status: eventData.status || 'active'
    }
    
    // Store the event
    addEvent(newEvent)
    
    console.log('Event received from nerve center:', newEvent)
    
    return NextResponse.json({
      success: true,
      data: newEvent,
      message: 'Event received and stored successfully',
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to receive event from nerve center:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to receive event',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}

export async function GET() {
  try {
    const events = getEvents()
    
    return NextResponse.json({
      success: true,
      data: events,
      count: events.length,
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to get events:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to get events',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}