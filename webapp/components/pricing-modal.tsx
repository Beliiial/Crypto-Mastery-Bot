"use client"

import { useState } from "react"
import { X, Wallet, Bot, Check, Crown, Users, ArrowLeft, Copy, CheckCircle2, Target } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useUser } from "@/lib/user-context"

interface PricingModalProps {
  open: boolean
  onClose: () => void
}

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        sendData: (data: string) => void
        close: () => void
      }
    }
  }
}

type PayMethod = null | "usdt_ton" | "ton_ton"

const channelPlans = [
  { id: "buy_1_month", label: "1 месяц", price: "150 USDT", popular: false },
  { id: "buy_3_months", label: "3 месяца", price: "299 USDT", popular: true },
  { id: "buy_forever", label: "Навсегда", price: "599 USDT", popular: false },
]

const mentorPlans = [
  { id: "mentorship_gatee_full", label: "Gatee (Полная)", desc: "Личное обучение", price: "1950 USDT" },
  { id: "mentorship_gatee_half", label: "Gatee (50%)", desc: "Рассрочка", price: "975 USDT" },
  { id: "mentorship_agwwee_full", label: "Agwwee (Полная)", desc: "Личное обучение", price: "3900 USDT" },
]

export function PricingModal({ open, onClose }: PricingModalProps) {
  const { toggleSubscription, grantMentorAccess } = useUser()
  const [step, setStep] = useState<"plan" | "payment" | "confirm">("plan")
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [selectedPayMethod, setSelectedPayMethod] = useState<PayMethod>(null)
  const [copied, setCopied] = useState(false)

  // Wallet address for both USDT (TON) and TON
  const walletAddress = "UQBZd9VWbTypz4dy7D5-7Ve7nPTS9eKZ-k9AH3H2hf8rewE5" 

  const handleBack = () => {
    if (step === "confirm") {
      setStep("payment")
    } else if (step === "payment") {
      setStep("plan")
      setSelectedPayMethod(null)
    } else {
      onClose()
      setTimeout(() => {
        setStep("plan")
        setSelectedPlan(null)
        setSelectedPayMethod(null)
      }, 300)
    }
  }

  const handleSelectPlan = (planId: string) => {
    setSelectedPlan(planId)
    setStep("payment")
  }

  const handleProceedToPayment = () => {
    setStep("confirm")
  }

  const handleConfirmPayment = () => {
    // Notify bot about manual payment
    if (selectedPayMethod && selectedPlan) {
      if (window.Telegram?.WebApp) {
        window.Telegram.WebApp.sendData(JSON.stringify({
          action: 'manual_payment',
          plan_id: selectedPlan,
          method: selectedPayMethod
        }))
        window.Telegram.WebApp.close()
      }
    }
    
    onClose()
    setTimeout(() => {
      setStep("plan")
      setSelectedPlan(null)
      setSelectedPayMethod(null)
    }, 300)
  }

  const copyAddress = () => {
    navigator.clipboard.writeText(walletAddress)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <AnimatePresence>
      {open && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.95 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed inset-x-0 bottom-0 z-50 flex justify-center"
          >
            <div className="glass-card-strong w-full max-w-[430px] rounded-t-3xl px-5 pb-10 pt-4">
              {/* Handle */}
              <div className="mb-3 flex justify-center">
                <div className="h-1 w-10 rounded-full bg-[rgba(255,255,255,0.2)]" />
              </div>

              {/* Header */}
              <div className="mb-6 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {step !== "plan" && (
                    <button 
                      onClick={handleBack}
                      className="flex h-8 w-8 items-center justify-center rounded-full bg-[rgba(255,255,255,0.08)] text-[#71717a]"
                    >
                      <ArrowLeft className="h-4 w-4" />
                    </button>
                  )}
                  <h3 className="text-lg font-bold text-white">
                    {step === "plan" ? "Выберите тариф" : step === "payment" ? "Способ оплаты" : "Подтверждение"}
                  </h3>
                </div>
                <button
                  onClick={onClose}
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-[rgba(255,255,255,0.08)] text-[#71717a] transition-colors hover:text-white"
                  aria-label="Close"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <AnimatePresence mode="wait">
                {step === "plan" ? (
                  <motion.div
                    key="plan"
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ duration: 0.2 }}
                  >
                    {/* Channel subscription */}
                    <div className="mb-6">
                      <div className="mb-3 flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(139,92,246,0.15)]">
                          <Crown className="h-4 w-4 text-[#8b5cf6]" />
                        </div>
                        <span className="text-sm font-semibold text-[#d4d4d8]">
                          Подписка на канал
                        </span>
                      </div>
                      <div className="flex flex-col gap-2">
                        {channelPlans.map((plan) => (
                          <button
                            key={plan.id}
                            onClick={() => handleSelectPlan(plan.id)}
                            className="glass-card group flex items-center justify-between rounded-xl px-4 py-3.5 transition-all hover:bg-[rgba(139,92,246,0.1)] hover:border-[rgba(139,92,246,0.3)]"
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-sm font-medium text-[#e4e4e7]">{plan.label}</span>
                              {plan.popular && (
                                <span className="rounded-full bg-[rgba(139,92,246,0.2)] px-2 py-0.5 text-[10px] font-semibold text-[#a78bfa]">
                                  Popular
                                </span>
                              )}
                            </div>
                            <span className="text-sm font-bold text-[#8b5cf6]">{plan.price}</span>
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Personal mentorship */}
                    <div>
                      <div className="mb-3 flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(245,158,11,0.15)]">
                          <Users className="h-4 w-4 text-[#f59e0b]" />
                        </div>
                        <span className="text-sm font-semibold text-[#d4d4d8]">
                          Личное менторство
                        </span>
                      </div>
                      <div className="flex flex-col gap-2">
                        {mentorPlans.map((plan) => (
                          <button
                            key={plan.id}
                            onClick={() => handleSelectPlan(plan.id)}
                            className="glass-card group flex items-center justify-between rounded-xl px-4 py-3.5 transition-all hover:bg-[rgba(245,158,11,0.08)] hover:border-[rgba(245,158,11,0.3)]"
                          >
                            <div className="flex flex-col items-start">
                              <span className="text-sm font-medium text-[#e4e4e7]">{plan.label}</span>
                              <span className="text-[11px] text-[#71717a]">{plan.desc}</span>
                            </div>
                            <span className="text-sm font-bold text-[#f59e0b]">{plan.price}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  </motion.div>
                ) : step === "payment" ? (
                  <motion.div
                    key="payment"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="flex flex-col gap-3"
                  >
                    {/* USDT (TON) */}
                    <button
                      onClick={() => setSelectedPayMethod("usdt_ton")}
                      className={`glass-card flex items-center gap-4 rounded-xl px-4 py-4 transition-all ${
                        selectedPayMethod === "usdt_ton"
                          ? "border-[rgba(139,92,246,0.5)] bg-[rgba(139,92,246,0.1)]"
                          : "hover:bg-[rgba(255,255,255,0.06)]"
                      }`}
                    >
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[rgba(139,92,246,0.15)]">
                        <Wallet className="h-5 w-5 text-[#8b5cf6]" />
                      </div>
                      <div className="flex flex-col items-start text-left">
                        <span className="text-sm font-semibold text-white">USDT (Network: TON)</span>
                        <span className="text-[11px] text-[#71717a]">Оплата в USDT через сеть TON</span>
                      </div>
                      {selectedPayMethod === "usdt_ton" && (
                        <Check className="ml-auto h-5 w-5 text-[#8b5cf6]" />
                      )}
                    </button>

                    {/* TON (TON) */}
                    <button
                      onClick={() => setSelectedPayMethod("ton_ton")}
                      className={`glass-card flex items-center gap-4 rounded-xl px-4 py-4 transition-all ${
                        selectedPayMethod === "ton_ton"
                          ? "border-[rgba(139,92,246,0.5)] bg-[rgba(139,92,246,0.1)]"
                          : "hover:bg-[rgba(255,255,255,0.06)]"
                      }`}
                    >
                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[rgba(0,136,204,0.15)]">
                        <Target className="h-5 w-5 text-[#0088cc]" />
                      </div>
                      <div className="flex flex-col items-start text-left">
                        <span className="text-sm font-semibold text-white">TON (Network: TON)</span>
                        <span className="text-[11px] text-[#71717a]">Оплата в монетах TON</span>
                      </div>
                      {selectedPayMethod === "ton_ton" && (
                        <Check className="ml-auto h-5 w-5 text-[#0088cc]" />
                      )}
                    </button>

                    {/* Proceed */}
                    <motion.button
                      whileTap={{ scale: 0.97 }}
                      disabled={!selectedPayMethod}
                      onClick={handleProceedToPayment}
                      className="gradient-primary glow-purple mt-3 flex w-full items-center justify-center rounded-2xl py-4 text-base font-semibold text-white transition-all disabled:opacity-40 disabled:shadow-none"
                    >
                      Далее
                    </motion.button>
                  </motion.div>
                ) : (
                  <motion.div
                    key="confirm"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.2 }}
                    className="flex flex-col gap-4"
                  >
                    <div className="rounded-xl bg-[rgba(255,255,255,0.04)] p-4 text-center">
                      <p className="text-xs text-[#71717a] mb-2">К оплате</p>
                      <p className="text-2xl font-bold text-white">
                         {[...channelPlans, ...mentorPlans].find(p => p.id === selectedPlan)?.price || '0 USDT'} 
                         <span className="text-sm font-normal text-[#71717a] ml-2">({selectedPayMethod === 'usdt_ton' ? 'USDT' : 'TON'})</span>
                      </p>
                    </div>

                    <div className="space-y-3">
                      <p className="text-xs text-[#71717a] px-1">Реквизиты для оплаты:</p>
                      <div className="glass-card flex items-center justify-between rounded-xl px-4 py-3">
                        <span className="text-xs font-mono text-white truncate mr-2">{walletAddress}</span>
                        <button onClick={copyAddress} className="text-[#8b5cf6]">
                          {copied ? <CheckCircle2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                        </button>
                      </div>
                      <p className="text-[10px] text-[#52525b] px-1 leading-relaxed">
                        После оплаты нажмите кнопку ниже. Администратор проверит платеж и выдаст доступ в течение 15 минут.
                      </p>
                    </div>

                    <motion.button
                      whileTap={{ scale: 0.97 }}
                      onClick={handleConfirmPayment}
                      className="gradient-primary glow-purple mt-2 flex w-full items-center justify-center rounded-2xl py-4 text-base font-semibold text-white transition-all"
                    >
                      Я оплатил
                    </motion.button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
