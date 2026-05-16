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
export default function DashboardPage() {
  const [helmets, setHelmets] = useState<HelmetData[]>([])
  const [lastRefresh, setLastRefresh] = useState<string>("")
  const [mounted, setMounted] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  useEffect(() => {
    setMounted(true)
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
          const now = new Date()
          setHelmets([
            {
              id: 1,
              deviceId: data.deviceId || "DEV-1000",
              helmetOn: data.riskLevel !== "HIGH",
              riskLevel: data.riskLevel,
              temperature: Math.round(data.temperature * 10) / 10,
              noise: Math.round(data.noise),
              score: 0.9,
              lastUpdate: now.toLocaleTimeString("ko-KR"),
            }
          ])
          setLastRefresh(now.toLocaleTimeString("ko-KR"))
        } catch (error) {
          console.error(
            "Failed to parse WebSocket message",
            error
          )
        }
      }
      ws.onclose = () => {
        console.log(
          "WebSocket disconnected. Reconnecting in 3 seconds..."
        )
        setIsConnected(false)
        setTimeout(connectWebSocket, 3000)
      }
    }
    connectWebSocket()
    return () => {
      if (ws) {
        ws.onclose = null
        ws.close()
      }
    }
  }, [])
  const highRiskCount =
    helmets.filter(
      (h) => h.riskLevel === "HIGH"
    ).length
  const avgTemperature =
    helmets.length > 0
      ? helmets.reduce(
          (sum, h) => sum + h.temperature,
          0
        ) / helmets.length
      : 0
  return (
    <div className="min-h-screen bg-background">
      <main className="container mx-auto p-4 sm:p-6 lg:p-8">
        <DashboardHeader
          onRefresh={() => {}}
          isConnected={isConnected}
        />
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
        {/* Helmet Grid */}
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">
              헬멧 현황
            </h2>
            <span className="text-xs text-muted-foreground">
              마지막 업데이트:
              {" "}
              {mounted
                ? lastRefresh
                : "로딩 중..."}
            </span>
          </div>
          {helmets.length === 0 ? (
            <div className="w-full text-center py-20 text-muted-foreground border rounded-xl">
              연결된 장비 없음
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {helmets.map((helmet) => (
                <HelmetCard
                  key={helmet.deviceId}
                  {...helmet}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}