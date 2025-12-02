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
          // Aggregate similar events within the same minute
          const aggregatedEvents = aggregateEventsByMinute(dbEvents)
          
          events = aggregatedEvents
          
          console.log(`Found ${dbEvents.length} raw events, aggregated to ${events.length} events`)
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

// Function to aggregate similar events within the same minute
function aggregateEventsByMinute(events: any[]): any[] {
  const eventMap = new Map<string, { count: number, representative: any, firstSeen: Date }>()
  
  // Group events by minute and type
  events.forEach(event => {
    const eventDate = new Date(event.timestamp)
    const minuteKey = `${eventDate.getFullYear()}-${String(eventDate.getMonth() + 1).padStart(2, '0')}-${String(eventDate.getDate()).padStart(2, '0')}-${String(Math.floor(eventDate.getMinutes() / 1) * 1).padStart(2, '0')}`
    
    const agentId = event.agentId || event.agent_id || 'unknown'
    const typeKey = `${event.type}-${agentId}`
    const fullKey = `${minuteKey}-${typeKey}`
    
    if (!eventMap.has(fullKey)) {
      eventMap.set(fullKey, {
        count: 1,  // Start with 1 for the first event
        representative: event,
        firstSeen: eventDate
      })
    } else {
      const existing = eventMap.get(fullKey)!
      existing.count++
      
      // Update representative if this event is more severe or newer
      const severityOrder = { critical: 4, high: 3, medium: 2, low: 1 }
      if ((severityOrder[event.severity as keyof typeof severityOrder] > severityOrder[existing.representative.severity as keyof typeof severityOrder]) ||
          eventDate > existing.firstSeen) {
        existing.representative = event
        existing.firstSeen = eventDate
      }
    }
  })
  
  // Convert aggregated events back to array format
  const aggregatedEvents: any[] = []
  eventMap.forEach((value, key) => {
    const aggregated = { ...value.representative }
    aggregated.count = value.count
    aggregated.aggregatedCount = value.count
    
    // Create unique ID for aggregated event to avoid conflicts
    aggregated.id = `aggregated-${value.representative.id}-${value.count}-${Date.now()}`
    aggregated.originalId = value.representative.id
    
    // Add aggregation metadata
    aggregated.details = {
      ...value.representative.details,
      aggregated: true,
      originalCount: value.count,
      aggregationPeriod: '1-minute',
      aggregatedAt: new Date().toISOString(),
      originalEventIds: [value.representative.id] // Store original IDs for reference
    }
    
    aggregatedEvents.push(aggregated)
  })
  
  // Sort by timestamp (most recent first)
  return aggregatedEvents.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
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