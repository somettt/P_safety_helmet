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

interface DashboardPayload {
  deviceId: string
  riskLevel: RiskLevel
  temperature: number
  noise: number
  helmet?: 0 | 1 | null
}

const DUMMY_DEVICE_IDS = new Set([
  "DEV-1001",
  "DEV-1002",
  "DEV-1003",
])

const isRiskLevel = (value: unknown): value is RiskLevel => {
  return value === "LOW" || value === "MID" || value === "HIGH"
}

const toNumber = (value: unknown): number | null => {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value
  }

  if (typeof value === "string") {
    const parsed = Number(value)
    return Number.isFinite(parsed) ? parsed : null
  }

  return null
}

const normalizeNoise = (noise: number): number => {
  return noise < 0 ? noise + 100 : noise
}

const getRiskLevel = (
  riskLevel: unknown,
  temperature: number,
  noise: number
): RiskLevel => {
  if (isRiskLevel(riskLevel)) {
    return riskLevel
  }

  if (riskLevel === "위험") {
    return "HIGH"
  }

  if (riskLevel === "경고" || riskLevel === "주의") {
    return "MID"
  }

  if (temperature > 60 || noise > 85) {
    return "HIGH"
  }

  if (temperature > 40 || noise > 70) {
    return "MID"
  }

  return "LOW"
}

const parseDashboardPayload = (value: unknown): DashboardPayload | null => {
  if (typeof value !== "object" || value === null) {
    return null
  }

  const payload = value as Record<string, unknown>
  const sensor = (
    typeof payload.sensor === "object" && payload.sensor !== null
      ? payload.sensor
      : {}
  ) as Record<string, unknown>
  const rawTemperature =
    payload.temperature ?? payload.temp ?? sensor.temperature ?? sensor.temp
  const rawNoise = payload.noise ?? sensor.noise
  const temperature = toNumber(rawTemperature)
  const noise = toNumber(rawNoise)

  if (temperature === null || noise === null) {
    return null
  }

  const deviceId =
    typeof payload.device_id === "string"
      ? payload.device_id
      : typeof payload.deviceId === "string"
      ? payload.deviceId
      : typeof sensor.device_id === "string"
      ? sensor.device_id
      : "helmet_001"
  const normalizedNoise = normalizeNoise(noise)
  const rawHelmet = payload.helmet
  const helmet = rawHelmet === 0 || rawHelmet === 1 || rawHelmet === null
    ? rawHelmet
    : undefined

  return {
    deviceId,
    riskLevel: getRiskLevel(
      payload.riskLevel ?? payload.risk,
      temperature,
      normalizedNoise
    ),
    temperature,
    noise: normalizedNoise,
    helmet,
  }
}

// 더미 헬멧 생성 함수
const generateDummyHelmet = (
  id: number,
  deviceId: string
): HelmetData => {

  const riskRand = Math.random()

  let riskLevel: RiskLevel

  if (riskRand < 0.6) riskLevel = "LOW"
  else if (riskRand < 0.85) riskLevel = "MID"
  else riskLevel = "HIGH"

  const temperature =
    riskLevel === "HIGH"
      ? 35 + Math.random() * 5
      : riskLevel === "MID"
      ? 28 + Math.random() * 5
      : 20 + Math.random() * 5

  const noise =
    riskLevel === "HIGH"
      ? 90 + Math.random() * 10
      : riskLevel === "MID"
      ? 75 + Math.random() * 10
      : 50 + Math.random() * 15

  return {
    id,
    deviceId,
    helmetOn: riskLevel !== "HIGH",
    riskLevel,
    temperature: Math.round(temperature * 10) / 10,
    noise: Math.round(noise),
    score: 0.8,
    lastUpdate: new Date().toLocaleTimeString("ko-KR"),
  }
}

export default function DashboardPage() {

  const [helmets, setHelmets] = useState<HelmetData[]>([])
  const [lastRefresh, setLastRefresh] = useState<string>("")
  const [mounted, setMounted] = useState(false)
  const [isConnected, setIsConnected] = useState(false)

  // 초기 더미 데이터 생성
  useEffect(() => {

    setMounted(true)

    const dummy1 = generateDummyHelmet(
      2,
      "DEV-1001"
    )

    const dummy2 = generateDummyHelmet(
      3,
      "DEV-1002"
    )

    const dummy3 = generateDummyHelmet(
      4,
      "DEV-1003"
    )

    setHelmets([
      dummy1,
      dummy2,
      dummy3
    ])

    setLastRefresh(
      new Date().toLocaleTimeString("ko-KR")
    )

  }, [])

  // 5초마다 더미 데이터 갱신
  useEffect(() => {

    const interval = setInterval(() => {

      setHelmets((prev) => {

        const realHelmets = prev.filter(
          (h) => !DUMMY_DEVICE_IDS.has(h.deviceId)
        )

        const dummy1 = generateDummyHelmet(
          2,
          "DEV-1001"
        )

        const dummy2 = generateDummyHelmet(
          3,
          "DEV-1002"
        )

        const dummy3 = generateDummyHelmet(
          4,
          "DEV-1003"
        )

        if (realHelmets.length > 0) {

          return [
            ...realHelmets,
            dummy1,
            dummy2,
            dummy3
          ]
        }

        return [
          dummy1,
          dummy2,
          dummy3
        ]
      })

      setLastRefresh(
        new Date().toLocaleTimeString("ko-KR")
      )

    }, 1000)

    return () => clearInterval(interval)

  }, [])

  // Python WebSocket 연결
  useEffect(() => {

    const wsUrl = `ws://${window.location.hostname || "localhost"}:8765`

    let ws: WebSocket

    const connectWebSocket = () => {

      ws = new WebSocket(wsUrl)

      ws.onopen = () => {

        console.log(
          "Connected to AI WebSocket Server"
        )

        setIsConnected(true)
      }

      ws.onmessage = (event) => {

        try {

          const payload = parseDashboardPayload(
            JSON.parse(event.data)
          )

          if (payload === null) {
            throw new Error("Invalid dashboard payload")
          }

          const now = new Date()

          const realHelmet: HelmetData = {
            id: 1,
            deviceId: payload.deviceId,
            helmetOn: payload.helmet === undefined
              ? payload.riskLevel !== "HIGH"
              : payload.helmet !== 0,
            riskLevel: payload.riskLevel,
            temperature: Math.round(payload.temperature * 10) / 10,
            noise: Math.round(payload.noise),
            score: 0.95,
            lastUpdate: now.toLocaleTimeString("ko-KR"),
          }

          setHelmets((prev) => {

            const others = prev.filter(
              (h) => h.deviceId !== payload.deviceId
            )

            return [
              realHelmet,
              ...others
            ]
          })

          setLastRefresh(
            now.toLocaleTimeString("ko-KR")
          )

        } catch (error) {

          console.error(
            "Failed to parse WebSocket message",
            error
          )
        }
      }

      ws.onclose = () => {

        console.log(
          "WebSocket disconnected. Reconnecting..."
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

        {/* Stats */}
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
