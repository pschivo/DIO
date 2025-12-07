// Simple in-memory storage for development events
let developmentEvents: any[] = []

export const addEvent = (event: any) => {
  developmentEvents.push(event)
  // Keep only the last 100 events
  if (developmentEvents.length > 100) {
    developmentEvents = developmentEvents.slice(-100)
  }
}

export const getEvents = () => {
  return developmentEvents.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}

export const clearEvents = () => {
  developmentEvents = []
}