import { NextRequest, NextResponse } from 'next/server'
import { getEvents } from '@/lib/events-storage'

const NERVE_CENTER_URL = process.env.NERVE_CENTER_URL || 'http://nerve-center:8000'

// Mock events data for development when nerve center is not available
const getMockEvents = () => {
  const now = new Date()
  const events = [
    {
      id: 'event-001',
      name: 'CPU usage reached 92.1%, indicating potential crypto-mining malware',
      type: 'evidence',
      severity: 'critical',
      description: 'CPU usage reached 92.1%, indicating potential crypto-mining malware',
      timestamp: new Date(now.getTime() - 3600000).toISOString(), // 1 hour ago
      agent_id: 'agent-167f0fee',
      details: {
        system_info: {
          hostname: '3eb3c821a6b1',
          ip_address: '172.20.0.9',
          os_type: 'Linux 6.8.0-87-generic'
        }
      }
    },
    {
      id: 'event-002',
      name: 'Memory usage reached 85.3%, indicating potential memory leak attack',
      type: 'evidence',
      severity: 'high',
      description: 'Memory usage reached 85.3%, indicating potential memory leak attack',
      timestamp: new Date(now.getTime() - 7200000).toISOString(), // 2 hours ago
      agent_id: 'agent-24e8f584',
      details: {
        system_info: {
          hostname: 'DIO-Agent-ffe647820740',
          ip_address: '172.20.0.10',
          os_type: 'Linux 6.8.0-87-generic'
        }
      }
    },
    {
      id: 'event-003',
      name: 'Network traffic spike detected: 45000 packets per second',
      type: 'evidence',
      severity: 'medium',
      description: 'Network traffic spike detected: 45000 packets per second',
      timestamp: new Date(now.getTime() - 5400000).toISOString(), // 1.5 hours ago
      agent_id: 'agent-5b2a9c1f',
      details: {
        system_info: {
          hostname: 'DIO-Agent-8d3e4a2b1c9f',
          ip_address: '172.20.0.11',
          os_type: 'Linux 6.8.0-87-generic'
        }
      }
    },
    {
      id: 'event-004',
      name: 'Unusual process creation detected: 380 processes',
      type: 'threat',
      severity: 'medium',
      description: 'Unusual process creation detected: 380 processes',
      timestamp: new Date(now.getTime() - 1800000).toISOString(), // 30 minutes ago
      agent_id: 'agent-9f7e3d2a',
      details: {
        system_info: {
          hostname: 'DIO-Agent-6c5b8a1e4f9d',
          ip_address: '172.20.0.12',
          os_type: 'Linux 6.8.0-87-generic'
        }
      }
    },
    {
      id: 'event-005',
      name: 'TLS handshake failed with unknown client',
      type: 'security',
      severity: 'low',
      description: 'TLS handshake failed with unknown client - invalid certificate',
      timestamp: new Date(now.getTime() - 900000).toISOString(), // 15 minutes ago
      agent_id: 'system',
      details: {
        system_info: {
          hostname: 'nerve-center',
          ip_address: '172.20.0.1',
          os_type: 'Ubuntu 22.04 LTS'
        }
      }
    }
  ]
  
  return events.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()).reverse()
}

export async function GET() {
  try {
    // Fetch events from nerve center (production should have real event logs)
    try {
      const response = await fetch(`${NERVE_CENTER_URL}/events`)
      
      if (response.ok) {
        const events = await response.json()
        return NextResponse.json({
          success: true,
          data: events,
          timestamp: new Date().toISOString()
        })
      }
    } catch (nerveCenterError) {
      console.log('Nerve center not available')
    }
    
    // In production, if nerve center is not available, return empty data
    // Do NOT use mock data in production environment
    if (process.env.NODE_ENV === 'production') {
      console.warn('Nerve center not available in production - no events data available')
      return NextResponse.json({
        success: true,
        data: [],
        timestamp: new Date().toISOString()
      })
    }
    
    // Only use mock data in development
    console.warn('Nerve center not available, using mock events data for development only')
    const mockEvents = getMockEvents()
    const developmentEvents = getEvents()
    
    // Combine mock events with development events
    const allEvents = [...mockEvents, ...developmentEvents]
    
    return NextResponse.json({
      success: true,
      data: allEvents,
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to fetch events:', error)
    
    // Always return mock data in development if nerve center fetch fails
    if (process.env.NODE_ENV !== 'production') {
      const mockEvents = getMockEvents()
      const developmentEvents = getEvents()
      
      // Combine mock events with development events
      const allEvents = [...mockEvents, ...developmentEvents]
      
      return NextResponse.json({
        success: true,
        data: allEvents,
        timestamp: new Date().toISOString()
      })
    }
    
    // In production, return empty data on error
    return NextResponse.json(
      { 
        success: false, 
        data: [],
        error: 'Failed to fetch events - no real events in production',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}