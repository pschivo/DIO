"use client"

import { useEffect, useState, useRef } from 'react'
import { toast } from 'sonner'

interface SocketMessage {
  type: string
  data: any
  timestamp: string
}

export function useSocket() {
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<SocketMessage | null>(null)
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    // WebSocket connection
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:3001'
    const socket = new WebSocket(wsUrl)
    
    socketRef.current = socket

    socket.onopen = () => {
      setIsConnected(true)
      console.log('Connected to DIO WebSocket')
      toast.success('Connected to DIO Platform')
    }

    socket.onmessage = (event) => {
      try {
        const message: SocketMessage = JSON.parse(event.data)
        setLastMessage(message)
        
        // Handle different message types
        switch (message.type) {
          case 'agent_update':
            // Handle agent status updates
            break
          case 'threat_detected':
            toast.error(`Threat detected: ${message.data.name}`)
            break
          case 'system_alert':
            toast.warning(`System alert: ${message.data.message}`)
            break
          default:
            console.log('Unknown message type:', message.type)
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }

    socket.onclose = () => {
      setIsConnected(false)
      console.log('Disconnected from DIO WebSocket')
      toast.warning('Disconnected from DIO Platform')
    }

    socket.onerror = (error) => {
      console.error('WebSocket error:', error)
      toast.error('WebSocket connection error')
    }

    // Cleanup
    return () => {
      if (socketRef.current) {
        socketRef.current.close()
      }
    }
  }, [])

  const sendMessage = (type: string, data: any) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      const message: SocketMessage = {
        type,
        data,
        timestamp: new Date().toISOString()
      }
      socketRef.current.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  const subscribe = (event: string, callback: (data: any) => void) => {
    // Store subscription callbacks
    // This would be expanded in a real implementation
  }

  return {
    isConnected,
    lastMessage,
    sendMessage,
    subscribe
  }
}