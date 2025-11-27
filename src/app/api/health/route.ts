import { NextRequest, NextResponse } from 'next/server'
import { db } from '@/lib/db'

export async function GET() {
  try {
    const systemHealth = await db.systemHealth.findMany({
      orderBy: { lastCheck: 'desc' },
      take: 10
    })

    // Get agent counts
    const agentCounts = await db.agent.groupBy({
      by: ['status'],
      _count: true
    })

    const healthSummary = {
      components: systemHealth,
      agentStats: agentCounts,
      overallStatus: systemHealth.every(h => h.status === 'healthy') ? 'healthy' : 'warning'
    }

    return NextResponse.json({
      success: true,
      data: healthSummary,
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Failed to fetch health data:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch health data',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}