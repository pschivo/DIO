import { NextRequest, NextResponse } from 'next/server'
import { getEvents } from '@/lib/events-storage'
import { getThreats, updateThreatStatus } from '@/lib/threats-storage'

const NERVE_CENTER_URL = process.env.NERVE_CENTER_URL || 'http://nerve-center:8000'

export async function POST(
  request: NextRequest,
  { params }: { params: { eventId: string } }
) {
  try {
    const eventId = params.eventId
    
    // In production, forward acknowledgment to nerve center
    if (process.env.NODE_ENV === 'production') {
      try {
        const response = await fetch(`${NERVE_CENTER_URL}/events/${eventId}/acknowledge`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
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
        console.error('Failed to forward acknowledgment to nerve center:', error)
      }
    }
    
    // For development or if nerve center fails, update local storage
    console.log('Acknowledging event:', eventId)
    
    // Update event status in development storage
    const events = getEvents()
    const event = events.find(e => e.id === eventId)
    if (event) {
      event.status = 'acknowledged'
    }
    
    // If this is a threat event, also update threat status
    if (eventId.startsWith('threat-')) {
      updateThreatStatus(eventId, 'acknowledged')
    }
    
    return NextResponse.json({
      success: true,
      data: {
        event_id: eventId,
        status: 'acknowledged',
        message: 'Event acknowledged successfully'
      },
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Failed to acknowledge event:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to acknowledge event',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}

export async function GET(
  request: NextRequest,
  { params }: { params: { eventId: string } }
) {
  try {
    const eventId = params.eventId
    
    // Fetch event details from nerve center
    const response = await fetch(`${NERVE_CENTER_URL}/events/${eventId}`)
    
    if (!response.ok) {
      throw new Error(`Nerve center responded with ${response.status}`)
    }
    
    const event = await response.json()
    
    return NextResponse.json({
      success: true,
      data: event,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Failed to fetch event details:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch event details',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}