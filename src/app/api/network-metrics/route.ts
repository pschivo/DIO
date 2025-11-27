import { NextRequest, NextResponse } from 'next/server'
import { getEvents } from '@/lib/events-storage'
import { getThreats } from '@/lib/threats-storage'

const NERVE_CENTER_URL = process.env.NERVE_CENTER_URL || 'http://nerve-center:8000'

export async function GET() {
  try {
    // Try to fetch from nerve center first
    try {
      const response = await fetch(`${NERVE_CENTER_URL}/network-metrics`)
      
      if (response.ok) {
        const networkMetrics = await response.json()
        return NextResponse.json({
          success: true,
          data: networkMetrics,
          timestamp: new Date().toISOString()
        })
      }
    } catch (nerveCenterError) {
      console.log('Nerve center not available')
    }
    
    // In production, if nerve center is not available, return empty data
    if (process.env.NODE_ENV === 'production') {
      console.warn('Nerve center not available in production - no network metrics available')
      return NextResponse.json({
        success: true,
        data: {},
        timestamp: new Date().toISOString()
      })
    }
    
    // Only return database results - no mock data
    console.warn('No network metrics available - network components need to be running')
    return NextResponse.json({
      success: true,
      data: {},
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to fetch network metrics:', error)
    
    // In production, return empty data on error
    if (process.env.NODE_ENV === 'production') {
      return NextResponse.json({
        success: true,
        data: {},
        timestamp: new Date().toISOString()
      })
    }
    
    // Fallback to minimal data in development
    return NextResponse.json(
      { 
        success: false, 
        data: {},
        error: 'Failed to fetch network metrics',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}