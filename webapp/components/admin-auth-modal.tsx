"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Shield, X, KeyRound, ArrowRight } from "lucide-react"
import { useUser } from "@/lib/user-context"

interface AdminAuthModalProps {
  open: boolean
  onClose: () => void
  onSuccess: () => void
}

export function AdminAuthModal({ open, onClose, onSuccess }: AdminAuthModalProps) {
  const { loginAsAdmin } = useUser()
  const [password, setPassword] = useState("")
  const [error, setError] = useState(false)

  const handleLogin = () => {
    if (loginAsAdmin(password)) {
      onSuccess()
      onClose()
      setPassword("")
      setError(false)
    } else {
      setError(true)
      setTimeout(() => setError(false), 2000)
    }
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
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed inset-x-4 top-[20%] z-50 mx-auto max-w-sm rounded-3xl border border-[rgba(255,255,255,0.08)] bg-[#0a0a0f] p-6 shadow-2xl"
          >
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[rgba(139,92,246,0.15)] text-[#8b5cf6]">
                  <Shield className="h-5 w-5" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Вход для админа</h3>
                  <p className="text-xs text-[#71717a]">Введите код доступа</p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="flex h-8 w-8 items-center justify-center rounded-full bg-[rgba(255,255,255,0.08)] text-[#71717a] transition-colors hover:text-white"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="relative mb-6">
              <KeyRound className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#71717a]" />
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value)
                  setError(false)
                }}
                onKeyDown={(e) => e.key === "Enter" && handleLogin()}
                placeholder="Введите пароль..."
                className={`w-full rounded-xl bg-[rgba(255,255,255,0.06)] py-3 pl-10 pr-4 text-sm text-white placeholder:text-[#52525b] outline-none transition-all ${
                  error 
                    ? "border border-red-500/50 focus:border-red-500" 
                    : "border border-transparent focus:border-[#8b5cf6]/50"
                }`}
                autoFocus
              />
              {error && (
                <motion.p
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="absolute -bottom-5 left-1 text-[10px] text-red-500 font-medium"
                >
                  Неверный пароль
                </motion.p>
              )}
            </div>

            <motion.button
              whileTap={{ scale: 0.97 }}
              onClick={handleLogin}
              disabled={!password}
              className="gradient-primary glow-purple flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-bold text-white shadow-lg disabled:opacity-50"
            >
              Войти
              <ArrowRight className="h-4 w-4" />
            </motion.button>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
