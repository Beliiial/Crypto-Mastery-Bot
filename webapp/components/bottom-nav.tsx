"use client"

import { Home, BookOpen, BarChart3, User, ArrowLeftRight } from "lucide-react"
import { motion } from "framer-motion"

type Tab = "home" | "courses" | "exchange" | "stats" | "profile"

interface BottomNavProps {
  activeTab: Tab
  onTabChange: (tab: Tab) => void
}

const tabs: { id: Tab; icon: typeof Home; label: string }[] = [
  { id: "home", icon: Home, label: "Главная" },
  { id: "courses", icon: BookOpen, label: "Курсы" },
  { id: "exchange", icon: ArrowLeftRight, label: "" },
  { id: "stats", icon: BarChart3, label: "Статистика" },
  { id: "profile", icon: User, label: "Профиль" },
]

export function BottomNav({ activeTab, onTabChange, isSubscribed }: BottomNavProps & { isSubscribed: boolean }) {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex justify-center">
      <div className="w-full max-w-[430px] px-4 pb-2 safe-bottom">
        <div className="glass-card-strong rounded-2xl flex items-center justify-around px-2 py-2">
          {tabs.map((tab) => {
            const isCenter = tab.id === "exchange"
            const isActive = activeTab === tab.id

            if (isCenter) {
              return (
                <button
                  key={tab.id}
                  onClick={() => onTabChange(tab.id)}
                  className="relative -mt-6 flex items-center justify-center"
                  aria-label="Exchange"
                >
                  <div className="gradient-primary glow-purple rounded-full p-3.5">
                    <ArrowLeftRight className="h-5 w-5 text-white" />
                  </div>
                  {isActive && (
                    <motion.div
                      layoutId="nav-dot"
                      className="absolute -bottom-1.5 h-1 w-1 rounded-full bg-[#8b5cf6]"
                    />
                  )}
                </button>
              )
            }

            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className="relative flex flex-col items-center gap-0.5 px-3 py-1.5"
                aria-label={tab.label}
              >
                <tab.icon
                  className={`h-5 w-5 transition-colors ${
                    isActive ? "text-[#8b5cf6]" : "text-[#71717a]"
                  }`}
                />
                <span
                  className={`text-[10px] font-medium transition-colors ${
                    isActive ? "text-[#8b5cf6]" : "text-[#71717a]"
                  }`}
                >
                  {tab.label}
                </span>
                {isActive && (
                  <motion.div
                    layoutId="nav-indicator"
                    className="absolute -bottom-0.5 h-0.5 w-5 rounded-full bg-[#8b5cf6]"
                    transition={{ type: "spring", stiffness: 400, damping: 30 }}
                  />
                )}
              </button>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
