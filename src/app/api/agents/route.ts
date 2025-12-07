import { NextRequest, NextResponse } from 'next/server'
import { getThreats } from '@/lib/threats-storage'
import { db } from '@/lib/db'

const NERVE_CENTER_URL = process.env.NERVE_CENTER_URL || 'http://nerve-center:8000'

export async function GET() {
  try {
    // Try to get agents from database first
    try {
      if (db) {
        const agents = await db.agent.findMany({
          orderBy: {
            lastSeen: 'desc'
          }
        })
        
        if (agents && agents.length > 0) {
          const agentsData = agents.map(agent => ({
            id: agent.id,
            name: agent.name,
            hostname: agent.hostname,
            status: agent.status,
            rank: agent.rank,
            cpu: agent.cpu,
            memory: agent.memory,
            lastSeen: agent.lastSeen.toISOString(),
            threats: agent.threats,
            ipAddress: agent.ipAddress,
            osType: agent.osType,
            version: agent.version
          }))
          
          console.log(`Found ${agentsData.length} agents in database`)
          return NextResponse.json({
            success: true,
            data: agentsData,
            timestamp: new Date().toISOString()
          })
        } else {
          console.log('No agents found in database')
        }
      }
    } catch (dbError) {
      console.error('Database query failed:', dbError)
    }
    
    // Try to fetch from nerve center as fallback
    try {
      const response = await fetch(`${NERVE_CENTER_URL}/agents`)
      
      if (response.ok) {
        const agents = await response.json()
        return NextResponse.json({
          success: true,
          data: agents,
          timestamp: new Date().toISOString()
        })
      }
    } catch (nerveCenterError) {
      console.log('Nerve center not available')
    }
    
    // In production, if no agents available, return empty data
    if (process.env.NODE_ENV === 'production') {
      console.warn('No agents available in production')
      return NextResponse.json({
        success: true,
        data: [],
        timestamp: new Date().toISOString()
      })
    }
    
    // Only return database results - no mock data
    console.warn('No agents available - agents need to register via the agent components')
    return NextResponse.json({
      success: true,
      data: [],
      timestamp: new Date().toISOString()
    })
  } catch (error) {
    console.error('Failed to fetch agents:', error)
    
    // In production, return empty data on error
    if (process.env.NODE_ENV === 'production') {
      return NextResponse.json({
        success: true,
        data: [],
        timestamp: new Date().toISOString()
      })
    }
    
    return NextResponse.json(
      { 
        success: false, 
        data: [],
        error: 'Failed to fetch agents',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Save agent to database first
    let savedAgent = null
    try {
      if (db) {
        // Check if agent already exists
        const existingAgent = await db.agent.findUnique({
          where: { id: body.id }
        })
        
        if (existingAgent) {
          // Update existing agent
          const updatedAgent = await db.agent.update({
            where: { id: body.id },
            data: {
              name: body.name || existingAgent.name,
              hostname: body.hostname || existingAgent.hostname,
              status: body.status || existingAgent.status,
              rank: body.rank !== undefined ? body.rank : existingAgent.rank,
              cpu: body.cpu !== undefined ? body.cpu : existingAgent.cpu,
              memory: body.memory !== undefined ? body.memory : existingAgent.memory,
              lastSeen: new Date(),
              ipAddress: body.ipAddress || existingAgent.ipAddress,
              osType: body.osType || existingAgent.osType,
              version: body.version || existingAgent.version
            }
          })
          
          console.log('Agent updated in database with ID:', updatedAgent.id)
          savedAgent = updatedAgent
        } else {
          // Create new agent
          savedAgent = await db.agent.create({
            data: {
              id: body.id || `agent-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
              name: body.name || 'DIO Agent',
              hostname: body.hostname || 'unknown',
              status: body.status || 'offline',
              rank: body.rank || 0,
              cpu: body.cpu || 0,
              memory: body.memory || 0,
              lastSeen: new Date(),
              threats: 0,
              ipAddress: body.ipAddress || 'unknown',
              osType: body.osType || 'unknown',
              version: body.version || '1.0.0'
            }
          })
          
          console.log('New agent created in database with ID:', savedAgent.id)
        }
      }
    } catch (dbError) {
      console.error('Failed to save agent to database:', dbError)
    }
    
    // Also try to forward to nerve center if available
    try {
      const response = await fetch(`${NERVE_CENTER_URL}/agents/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body)
      })
      
      if (response.ok) {
        const result = await response.json()
        return NextResponse.json({
          success: true,
          data: result,
          savedToDb: !!savedAgent,
          timestamp: new Date().toISOString()
        })
      }
    } catch (nerveCenterError) {
      console.log('Nerve center not available, agent saved to database only')
    }
    
    // Return success even if nerve center is not available
    return NextResponse.json({
      success: true,
      data: {
        id: savedAgent?.id || body.id,
        ...body,
        registered: true
      },
      savedToDb: !!savedAgent,
      message: 'Agent registered successfully',
      timestamp: new Date().toISOString()
    })
    
  } catch (error) {
    console.error('Failed to create agent:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to create agent',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}