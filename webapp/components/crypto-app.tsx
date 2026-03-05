"use client"

import { useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { useUser } from "@/lib/user-context"
import { WebAppAuth } from "./auth-screen"
import { ArbitrageCalculator } from "./arbitrage-calculator"
import { BottomNav } from "./bottom-nav"
import { LandingScreen } from "./landing-screen"
import { PricingModal } from "./pricing-modal"
import { ChatScreen } from "./chat-screen"
import { CoursesScreen } from "./courses-screen"
import { StatsScreen } from "./stats-screen"
import { ProfileScreen } from "./profile-screen"

type Tab = "home" | "courses" | "exchange" | "stats" | "profile"

export function CryptoApp() {
  const { user, loading } = useUser()
  const [activeTab, setActiveTab] = useState<Tab>("home")
  const [pricingOpen, setPricingOpen] = useState(false)

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  // No need for !user check anymore if TG auth is reliable

  const handleTabChange = (tab: Tab) => {
    if (tab === "exchange") {
      setActiveTab("exchange")
    } else {
      setActiveTab(tab)
    }
  }

  return (
    <div className="relative mx-auto min-h-screen max-w-[430px] bg-[#0a0a0f] overflow-x-hidden">
      <AnimatePresence mode="wait">
        {activeTab === "home" && (
          <motion.div
            key="home"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <LandingScreen onJoin={() => setPricingOpen(true)} />
          </motion.div>
        )}
        {activeTab === "courses" && (
          <motion.div
            key="courses"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <CoursesScreen onSubscribe={() => setPricingOpen(true)} />
          </motion.div>
        )}
        {activeTab === "exchange" && (
          <motion.div
            key="exchange"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChatScreen onSubscribe={() => setPricingOpen(true)} />
          </motion.div>
        )}
        {activeTab === "stats" && (
          <motion.div
            key="stats"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <StatsScreen onSubscribe={() => setPricingOpen(true)} />
          </motion.div>
        )}
        {activeTab === "profile" && (
          <motion.div
            key="profile"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <ProfileScreen />
          </motion.div>
        )}
      </AnimatePresence>

      <BottomNav 
        activeTab={activeTab} 
        onTabChange={handleTabChange} 
        isSubscribed={!!user?.isSubscribed}
      />
      <PricingModal open={pricingOpen} onClose={() => setPricingOpen(false)} />
    </div>
  )
}
