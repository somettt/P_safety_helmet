"use client"

import { useState, useEffect } from "react"
import { DashboardHeader } from "@/components/dashboard-header"
import { HelmetCard, type RiskLevel } from "@/components/helmet-card"
import { StatsCard } from "@/components/stats-card"
import { RiskSummary } from "@/components/risk-summary"
import { HardHat, AlertTriangle, ThermometerSun } from "lucide-react"

export interface HelmetData {
  id: number
  deviceId: string
  helmetOn: boolean
  riskLevel: RiskLevel
  temperature: number
  noise: number
  score: number
  lastUpdate: string
}

// Demo data for when MQTT is not connected
const generateDemoData = (): HelmetData[] => {
  const now = new Date()

  return Array.from({ length: 8 }, (_, i) => {
    const riskIndex = Math.random()
    let riskLevel: RiskLevel
    if (riskIndex < 0.5) riskLevel = "LOW"
    else if (riskIndex < 0.8) riskLevel = "MID"
    else riskLevel = "HIGH"

    const temperature =
      riskLevel === "HIGH"
        ? 35 + Math.random() * 10
        : riskLevel === "MID"
          ? 28 + Math.random() * 7
          : 20 + Math.random() * 8

    const noise =
      riskLevel === "HIGH"
        ? 90 + Math.random() * 20
        : riskLevel === "MID"
          ? 75 + Math.random() * 15
          : 50 + Math.random() * 25

    return {
      id: i + 1,
      deviceId: `DEV-${String(1000 + i).padStart(4, "0")}`,
      helmetOn: Math.random() > 0.15,
      riskLevel,
      temperature: Math.round(temperature * 10) / 10,
      noise: Math.round(noise),
      score: 0.75 + Math.random() * 0.24,
      lastUpdate: new Date(now.getTime() - Math.random() * 60000).toLocaleTimeString("ko-KR"),
    }
  })
}

export default function DashboardPage() {
  const [helmets, setHelmets] = useState<HelmetData[]>([])
  const [lastRefresh, setLastRefresh] = useState<string>("")
  const [mounted, setMounted] = useState(false)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    setMounted(true)
    setHelmets(generateDemoData())
    setLastRefresh(new Date().toLocaleTimeString("ko-KR"))
  }, [])

  // Connect to Python AI WebSocket server
  useEffect(() => {
    const wsUrl = "ws://localhost:8765"
    let ws: WebSocket

    const connectWebSocket = () => {
      ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        console.log("Connected to AI WebSocket Server")
        setIsConnected(true)
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          // data contains { riskLevel, temperature, noise, reason }
          setHelmets((prevHelmets) => {
            if (prevHelmets.length === 0) return prevHelmets;
            
            // For now, map the real-time stream to the first helmet card (DEV-1000)
            const updatedHelmets = [...prevHelmets]
            const now = new Date()
            
            updatedHelmets[0] = {
              ...updatedHelmets[0],
              riskLevel: data.riskLevel,
              temperature: Math.round(data.temperature * 10) / 10,
              noise: Math.round(data.noise),
              lastUpdate: now.toLocaleTimeString("ko-KR"),
              // Add custom reason field if needed later
            }
            
            return updatedHelmets
          })
          setLastRefresh(new Date().toLocaleTimeString("ko-KR"))
        } catch (error) {
          console.error("Failed to parse WebSocket message", error)
        }
      }

      ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 3 seconds...")
        setIsConnected(false)
        setTimeout(connectWebSocket, 3000)
      }
    }

    connectWebSocket()

    return () => {
      if (ws) {
        ws.onclose = null // prevent auto-reconnect on unmount
        ws.close()
      }
    }
  }, [])

  const refreshData = () => {
    setHelmets(generateDemoData())
    setLastRefresh(new Date().toLocaleTimeString("ko-KR"))
  }

  const highRiskCount = helmets.filter((h) => h.riskLevel === "HIGH").length
  const avgTemperature =
    helmets.length > 0
      ? helmets.reduce((sum, h) => sum + h.temperature, 0) / helmets.length
      : 0

  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <DashboardHeader onRefresh={refreshData} isConnected={isConnected} />

        {/* Stats Overview */}
        <div className="mt-6 grid gap-4 sm:grid-cols-3">
          <StatsCard
            title="전체 헬멧"
            value={helmets.length}
            icon={HardHat}
          />
          <StatsCard
            title="위험 상태"
            value={highRiskCount}
            icon={AlertTriangle}
          />
          <StatsCard
            title="평균 온도"
            value={`${avgTemperature.toFixed(1)}°C`}
            icon={ThermometerSun}
          />
        </div>

        {/* Risk Summary */}
        <div className="mt-6">
          <RiskSummary helmets={helmets} />
        </div>

        {/* Helmets Grid */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">헬멧 현황</h2>
            <span className="text-xs text-muted-foreground">
              마지막 업데이트: {mounted ? lastRefresh : "로딩 중..."}
            </span>
          </div>
          
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {helmets.map((helmet) => (
              <HelmetCard key={helmet.deviceId} {...helmet} />
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
