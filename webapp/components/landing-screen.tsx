"use client"

import { ArrowRight, Play, HelpCircle } from "lucide-react"
import { motion } from "framer-motion"
import { useUser } from "@/lib/user-context"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"

interface LandingScreenProps {
  onJoin: () => void
}

const stats = [
  { value: "10K+", label: "УЧЕНИКОВ" },
  { value: "95%", label: "ДОВОЛЬНЫХ" },
  { value: "50+", label: "УРОКОВ" },
]

const exchanges = ["Binance", "Coinbase", "Kraken", "Bybit", "OKX"]

const faqItems = [
  {
    question: "Как это работает?",
    answer: "Мы предоставляем пошаговое обучение криптоарбитражу, доступ к закрытому чату с экспертами и личное менторство для быстрого старта."
  },
  {
    question: "Нужен ли большой капитал?",
    answer: "Начать можно с небольших сумм. В обучении мы разбираем стратегии для разных уровней депозита."
  },
  {
    question: "Как получить доступ к VIP?",
    answer: "Доступ открывается после оформления подписки. Вы получите все обучающие материалы и доступ в закрытое комьюнити."
  },
  {
    question: "Есть ли поддержка?",
    answer: "Да, наши менторы и опытные участники чата всегда готовы помочь с любыми вопросами 24/7."
  }
]

export function LandingScreen({ onJoin }: LandingScreenProps) {
  const { user } = useUser()

  return (
    <div className="relative flex flex-col items-center px-4 pb-28 pt-4 overflow-hidden">
      {/* Ambient glow */}
      <div className="pointer-events-none absolute -top-20 left-1/2 h-64 w-64 -translate-x-1/2 rounded-full bg-[#8b5cf6] opacity-10 blur-[100px]" />
      <div className="pointer-events-none absolute top-40 -right-20 h-48 w-48 rounded-full bg-[#6366f1] opacity-8 blur-[80px]" />

      {/* Header */}
      <div className="relative z-10 flex w-full items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#8b5cf6] text-sm font-bold text-white">
            {user?.nickname?.[0] || "B"}
          </div>
          <h1 className="text-lg font-bold tracking-wide text-[#f0f0f5]">CRYPTO MASTERY</h1>
        </div>
        <div className="h-11 w-11 rounded-full border-2 border-[#f59e0b] overflow-hidden flex items-center justify-center bg-[#1a1a2e]">
          <div className="flex h-full w-full items-center justify-center text-lg">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="8" r="4" fill="#f59e0b" />
              <path d="M4 20c0-4 4-6 8-6s8 2 8 6" fill="#f59e0b" opacity="0.3" />
              <circle cx="12" cy="8" r="3" fill="#1a1a2e" />
              <rect x="10" y="6" width="4" height="2" rx="1" fill="#f59e0b" />
              <path d="M9 10c0 0 1.5 2 3 2s3-2 3-2" stroke="#f59e0b" strokeWidth="0.5" fill="none" />
            </svg>
          </div>
        </div>
      </div>

      {/* Hero Card */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 glass-card-strong w-full rounded-3xl p-6 mb-8"
      >
        {/* VIP Badge */}
        <div className="mb-5 inline-flex items-center gap-2 rounded-full bg-[rgba(255,255,255,0.08)] px-3.5 py-1.5">
          <span className={`h-2 w-2 rounded-full ${user?.isSubscribed ? "bg-[#f59e0b] glow-gold" : "bg-[#71717a]"}`} />
          <span className="text-xs font-medium text-[#d4d4d8]">
            {user?.isSubscribed ? "VIP Access Active" : "No VIP Access"}
          </span>
        </div>

        {/* Heading */}
        <h2 className="text-[28px] font-extrabold leading-tight text-white mb-2 text-balance">
          {"Стань профи в "}
          <span className="text-[#8b5cf6]">криптоарбитраже</span>
        </h2>
        <p className="text-sm leading-relaxed text-[#a1a1aa] mb-8">
          Изучи проверенные стратегии от экспертов и начни зарабатывать на крипторынке уже сегодня
        </p>

        {/* CTA Buttons */}
        <motion.button
          whileTap={{ scale: 0.97 }}
          onClick={onJoin}
          className="gradient-primary glow-purple mb-3 flex w-full items-center justify-center gap-2 rounded-2xl py-4 text-base font-semibold text-white transition-all hover:opacity-90"
        >
          {"Присоединиться"}
          <ArrowRight className="h-4 w-4" />
        </motion.button>

        <motion.button
          whileTap={{ scale: 0.97 }}
          className="glass-card flex w-full items-center justify-center gap-2 rounded-2xl py-4 text-base font-medium text-[#d4d4d8] transition-all hover:bg-[rgba(255,255,255,0.08)]"
        >
          <Play className="h-4 w-4 text-[#8b5cf6]" fill="#8b5cf6" />
          {"Смотреть демо"}
        </motion.button>
      </motion.div>

      {/* Stats */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.15 }}
        className="relative z-10 mb-8 grid w-full grid-cols-3 gap-4"
      >
        {stats.map((stat) => (
          <div key={stat.label} className="flex flex-col items-center">
            <span className="text-2xl font-bold text-[#8b5cf6]">{stat.value}</span>
            <span className="mt-1 text-[10px] font-semibold tracking-widest text-[#71717a]">
              {stat.label}
            </span>
          </div>
        ))}
      </motion.div>

      {/* Trust Bar */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.25 }}
        className="relative z-10 flex w-full flex-col items-center mb-12"
      >
        <p className="mb-4 text-xs text-[#71717a]">
          {"Нам доверяют "}
          <span className="font-semibold text-[#f59e0b]">{"10 000+"}</span>
          {" трейдеров по всему миру"}
        </p>
        <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-2">
          {exchanges.map((name) => (
            <span
              key={name}
              className="text-sm font-bold tracking-wide text-[#3f3f46]"
            >
              {name}
            </span>
          ))}
        </div>
      </motion.div>

      {/* FAQ Section */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.35 }}
        className="relative z-10 w-full"
      >
        <div className="mb-6 flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(139,92,246,0.1)] text-[#8b5cf6]">
            <HelpCircle className="h-4 w-4" />
          </div>
          <h3 className="text-lg font-bold text-white">Частые вопросы</h3>
        </div>

        <Accordion type="single" collapsible className="w-full space-y-3">
          {faqItems.map((item, index) => (
            <AccordionItem
              key={index}
              value={`item-${index}`}
              className="glass-card overflow-hidden rounded-2xl border-none px-4"
            >
              <AccordionTrigger className="py-4 text-sm font-semibold text-[#e4e4e7] hover:no-underline">
                {item.question}
              </AccordionTrigger>
              <AccordionContent className="pb-4 text-xs leading-relaxed text-[#a1a1aa]">
                {item.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </motion.div>
    </div>
  )
}
