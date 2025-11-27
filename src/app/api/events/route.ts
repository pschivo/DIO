import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'
import { addEvent, getEvents } from '@/lib/events-storage'

export async function GET() {
  try {
    // Query events directly from database
    let events: any[] = []
    
    try {
      if (db) {
        const dbEvents = await db.event.findMany({
          orderBy: {
            timestamp: 'desc'
          },
          take: 100
        })
        
        if (dbEvents && dbEvents.length > 0) {
          events = dbEvents.map((event: any) => ({
            id: event.id,
            name: event.name,
            type: event.type,
            severity: event.severity,
            description: event.description,
            timestamp: event.timestamp.toISOString(),
            agent_id: event.agentId,
            details: event.details || {},
            status: event.status || 'active'
          }))
          
          console.log(`Found ${events.length} events in database`)
        } else {
          console.log('No events found in database')
        }
      }
    } catch (dbError) {
      console.error('Database query failed, falling back to memory storage:', dbError)
      
      // Fall back to memory storage
      const memoryEvents = getEvents()
      events = memoryEvents
      console.log(`Found ${events.length} events in memory storage`)
    }
    
    return NextResponse.json({
      success: true,
      data: events,
      count: events.length,
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to fetch events:', error)
    return NextResponse.json(
      { 
        success: false, 
        data: [],
        error: 'Failed to fetch events',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const eventData = await request.json()
    
    console.log('Saving event to database:', eventData.type, eventData.name || eventData.title)
    
    // Save event to database
    let savedEvent = null
    try {
      if (db) {
        savedEvent = await db.event.create({
          data: {
            id: eventData.id || `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            name: eventData.name || eventData.title || 'Unknown Event',
            type: eventData.type || 'system',
            severity: eventData.severity || 'medium',
            description: eventData.description || 'Event occurred',
            timestamp: eventData.timestamp ? new Date(eventData.timestamp) : new Date(),
            agentId: eventData.agent_id || eventData.agentId,
            details: eventData.details || {},
            status: eventData.status || 'active'
          }
        })
        
        if (savedEvent) {
          console.log('Event saved to database with ID:', savedEvent.id)
        } else {
          console.log('Failed to save event to database')
        }
      }
    } catch (dbError) {
      console.error('Failed to save event to database, saving to memory storage:', dbError)
      
      // Fall back to memory storage
      addEvent({
        id: eventData.id || `event-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: eventData.name || eventData.title || 'Unknown Event',
        type: eventData.type || 'system',
        severity: eventData.severity || 'medium',
        description: eventData.description || 'Event occurred',
        timestamp: eventData.timestamp || new Date().toISOString(),
        agent_id: eventData.agent_id || eventData.agentId,
        details: eventData.details || {},
        status: eventData.status || 'active'
      })
      
      console.log('Event saved to memory storage')
    }
    
    return NextResponse.json({
      success: true,
      data: {
        id: savedEvent?.id || eventData.id,
        ...eventData,
        timestamp: eventData.timestamp || new Date().toISOString()
      },
      savedToDb: !!savedEvent,
      message: 'Event saved successfully',
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to receive event:', error)
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