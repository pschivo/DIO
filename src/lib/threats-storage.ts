// Simple in-memory storage for development threats
let developmentThreats: any[] = []

export const addThreat = (threat: any) => {
  developmentThreats.push(threat)
  // Keep only the last 50 threats
  if (developmentThreats.length > 50) {
    developmentThreats = developmentThreats.slice(-50)
  }
}

export const getThreats = () => {
  if (developmentThreats.length === 0) {
    return []
  }
  return developmentThreats.sort((a, b) => new Date(b.timestamp || b.detected_at).getTime() - new Date(a.timestamp || a.detected_at).getTime())
}

export const getThreatsByAgent = (agentId: string) => {
  return developmentThreats.filter(threat => threat.agent_id === agentId)
}

export const updateThreatStatus = (threatId: string, status: string) => {
  const threat = developmentThreats.find(t => t.id === threatId)
  if (threat) {
    threat.status = status
  }
}

export const clearThreats = () => {
  developmentThreats = []
}