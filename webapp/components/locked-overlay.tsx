"use client"

import React from "react"
import { motion } from "framer-motion"
import { Lock, Crown, ArrowRight } from "lucide-react"

interface LockedOverlayProps {
  title: string
  description: string
  onSubscribe?: () => void
}

export function LockedOverlay({ title, description, onSubscribe }: LockedOverlayProps) {
  return (
    <div className="absolute inset-0 z-50 flex flex-col items-center justify-center p-6 text-center backdrop-blur-sm bg-[rgba(10,10,15,0.7)]">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass-card-strong flex max-w-[280px] flex-col items-center rounded-3xl p-8 shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
      >
        <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-[rgba(245,158,11,0.15)] text-[#f59e0b] glow-gold">
          <Lock className="h-8 w-8" />
        </div>
        
        <h3 className="mb-2 text-xl font-bold text-white">{title}</h3>
        <p className="mb-8 text-sm leading-relaxed text-[#71717a]">
          {description}
        </p>

        <motion.button
          whileTap={{ scale: 0.95 }}
          onClick={onSubscribe}
          className="gradient-primary glow-purple flex w-full items-center justify-center gap-2 rounded-2xl py-3.5 text-sm font-bold text-white shadow-lg"
        >
          <Crown className="h-4 w-4" />
          {"Получить доступ"}
          <ArrowRight className="h-3.5 w-3.5" />
        </motion.button>
        
        <p className="mt-4 text-[10px] font-medium uppercase tracking-widest text-[#52525b]">
          VIP ACCESS REQUIRED
        </p>
      </motion.div>
    </div>
  )
}
