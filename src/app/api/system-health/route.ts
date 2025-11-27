import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET() {
  try {
    // Try to get system health from database first
    try {
      if (db) {
        const systemHealthRecords = await db.systemHealth.findMany({
          orderBy: {
            lastCheck: 'desc'
          },
          take: 10
        })
        
        if (systemHealthRecords && systemHealthRecords.length > 0) {
          // Group by component and get only the latest record for each component
          const latestByComponent = new Map()
          
          systemHealthRecords.forEach(record => {
            const component = record.component
            const existing = latestByComponent.get(component)
            
            if (!existing || record.lastCheck > existing.lastCheck) {
              latestByComponent.set(component, record)
            }
          })
          
          // Convert to array format
          const systemHealth = Array.from(latestByComponent.values()).map(record => ({
            component: record.component,
            status: record.status,
            cpu: record.cpu,
            memory: record.memory,
            disk: record.disk,
            network: record.network,
            uptime: record.uptime,
            lastCheck: record.lastCheck.toISOString(),
            errorMessage: record.errorMessage
          }))
          
          console.log(`Found ${systemHealth.length} unique system health components in database`)
          
          // Check for any critical components and create events if needed (with deduplication)
          for (const component of systemHealth) {
            if (component.status === 'critical' || component.status === 'warning') {
              try {
                // Check if we already have a recent active event for this component and status
                const existingEvent = await db.event.findFirst({
                  where: {
                    name: `System Health Alert: ${component.component}`,
                    type: 'system',
                    status: 'active',
                    timestamp: {
                      gte: new Date(Date.now() - 5 * 60 * 1000) // Last 5 minutes
                    }
                  }
                })
                
                // Only create event if we don't already have a recent one
                if (!existingEvent) {
                  await db.event.create({
                    data: {
                      name: `System Health Alert: ${component.component}`,
                      type: 'system',
                      severity: component.status === 'critical' ? 'critical' : 'medium',
                      description: `${component.component} status: ${component.status}${component.errorMessage ? ' - ' + component.errorMessage : ''}`,
                      timestamp: new Date(),
                      agentId: null,
                      details: {
                        component: component.component,
                        status: component.status,
                        cpu: component.cpu || 0,
                        memory: component.memory || 0,
                        disk: component.disk || 0,
                        network: component.network || 0,
                        uptime: component.uptime || 0
                      },
                      status: 'active'
                    }
                  })
                  console.log(`Created new system health event for ${component.component} (${component.status})`)
                } else {
                  console.log(`Skipping duplicate system health event for ${component.component} - already exists`)
                }
              } catch (eventError) {
                console.error('Failed to create system health event:', eventError)
              }
            }
          }
          
          return NextResponse.json({
            success: true,
            data: systemHealth,
            timestamp: new Date().toISOString()
          })
        }
      }
    } catch (dbError) {
      console.error('Database query failed, using fallback:', dbError)
    }
    
    // Only return database results - no mock data
    console.warn('No system health available - system health components need to be running')
    return NextResponse.json({
      success: true,
      data: [],
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to fetch system health:', error)
    return NextResponse.json(
      { 
        success: false, 
        data: [],
        error: 'Failed to fetch system health',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}