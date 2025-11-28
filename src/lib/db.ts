import { PrismaClient } from '@prisma/client'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

// Create a prisma client that doesn't auto-connect on initialization
const createPrismaClient = () => {
  return new PrismaClient({
    log: process.env.NODE_ENV === 'development' ? ['info', 'warn', 'error'] : ['warn', 'error'],
  })
}

export const db = createPrismaClient()

// Only assign to global in non-production environments
if (process.env.NODE_ENV !== 'production') {
  globalForPrisma.prisma = db
}

// Test database connection (called when needed, not on initialization)
export async function testConnection() {
  try {
    await db.$connect()
    console.log('Database connected successfully')
    return true
  } catch (error) {
    console.error('Database connection failed:', error)
    return false
  }
}