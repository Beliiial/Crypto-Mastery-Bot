"use client"

import { Crown, Clock, UserCheck, Copy, ExternalLink, ChevronRight, Shield, Settings, Edit2, LogOut, X, Sun, Moon } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useState } from "react"
import { useTheme } from "next-themes"
import { useUser } from "@/lib/user-context"
import { AdminPanel } from "./admin-panel"
import { AdminAuthModal } from "./admin-auth-modal"

export function ProfileScreen() {
  const { user, updateUser, toggleAdmin } = useUser()
  const { theme, setTheme } = useTheme()
  const [copied, setCopied] = useState(false)
  const [showAdmin, setShowAdmin] = useState(false)
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [tempNickname, setTempNickname] = useState(user?.nickname || "")
  
  // Real transactions would be loaded here. For now, empty list for new users.
  const [transactions, setTransactions] = useState<any[]>([])
  const [showAllTransactions, setShowAllTransactions] = useState(false)

  const referralLink = `t.me/CryptoMastery_bot?ref=user_${user?.id || "8472"}`

  if (showAdmin) {
    return <AdminPanel onBack={() => setShowAdmin(false)} />
  }

  const copyLink = () => {
    navigator.clipboard.writeText(referralLink)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleSaveProfile = () => {
    updateUser({ nickname: tempNickname })
    setIsEditing(false)
  }

  const handleAdminAccess = () => {
    if (user?.isAdmin) {
      // Если уже админ (например, по ID), сразу открываем панель
      setShowAdmin(true)
    } else {
      // Иначе требуем пароль
      setShowAuthModal(true)
    }
  }

  if (!user) return null

  return (
    <div className="flex flex-col px-4 pb-28 pt-4">
      <AdminAuthModal 
        open={showAuthModal} 
        onClose={() => setShowAuthModal(false)}
        onSuccess={() => setShowAdmin(true)}
      />

      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <h2 className="text-xl font-bold text-white">Профиль</h2>
        <div className="flex gap-2">
          {/* Theme Toggle */}
          <button 
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-[rgba(255,255,255,0.04)] text-[#71717a] transition-colors hover:text-white"
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          {/* Admin Settings Button */}
          <button 
            onClick={() => setShowAuthModal(true)}
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-[rgba(255,255,255,0.04)] text-[#71717a] transition-colors hover:text-white"
          >
            <Settings className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* User Card */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card-strong mb-4 flex items-center gap-4 rounded-2xl p-4"
      >
        <div className="relative">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[rgba(139,92,246,0.15)] text-xl font-bold text-[#8b5cf6]">
            {user.avatar || user.nickname[0]}
          </div>
          {user.isSubscribed && (
            <div className="absolute -bottom-0.5 -right-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-[#f59e0b] glow-gold">
              <Crown className="h-3 w-3 text-[#0a0a0f]" />
            </div>
          )}
        </div>
        <div className="flex-1">
          {isEditing ? (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={tempNickname}
                onChange={(e) => setTempNickname(e.target.value)}
                className="w-full rounded-lg bg-[rgba(255,255,255,0.06)] px-2 py-1 text-sm font-bold text-white outline-none ring-1 ring-[#8b5cf6]"
                autoFocus
              />
              <button 
                onClick={handleSaveProfile}
                className="rounded-lg bg-[#8b5cf6] px-2 py-1 text-[10px] font-bold text-white"
              >
                ОК
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <p className="text-base font-bold text-white">{user.nickname}</p>
              <button onClick={() => setIsEditing(true)}>
                <Edit2 className="h-3 w-3 text-[#71717a]" />
              </button>
            </div>
          )}
          <p className="text-xs text-[#71717a]">ID: #{user.id}</p>
          <div className={`mt-1.5 inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 ${
            user.isSubscribed ? "bg-[rgba(34,197,94,0.12)]" : "bg-[rgba(255,255,255,0.06)]"
          }`}>
            <span className={`h-1.5 w-1.5 rounded-full ${user.isSubscribed ? "bg-[#22c55e]" : "bg-[#71717a]"}`} />
            <span className={`text-[10px] font-semibold ${user.isSubscribed ? "text-[#22c55e]" : "text-[#71717a]"}`}>
              {user.isSubscribed ? "VIP Активна" : "Без подписки"}
            </span>
          </div>
        </div>
      </motion.div>

      {/* Admin Button (Visible only to admins) */}
      <motion.button
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        whileTap={{ scale: 0.98 }}
        onClick={handleAdminAccess}
        className="mb-4 flex w-full items-center justify-between rounded-2xl bg-gradient-to-r from-[rgba(139,92,246,0.2)] to-[rgba(99,102,241,0.2)] p-4 border border-[rgba(139,92,246,0.3)] shadow-[0_0_20px_rgba(139,92,246,0.15)]"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#8b5cf6] text-white">
            <Shield className="h-5 w-5" />
          </div>
          <div className="text-left">
            <p className="text-sm font-bold text-white">Админ-панель</p>
            <p className="text-[10px] text-[#a1a1aa]">Управление курсами и юзерами</p>
          </div>
        </div>
        <ChevronRight className="h-5 w-5 text-[#8b5cf6]" />
      </motion.button>

      {/* Subscription Info */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="mb-4 grid grid-cols-2 gap-3"
      >
        <div className="glass-card rounded-xl p-4">
          <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-lg bg-[rgba(139,92,246,0.15)]">
            <Clock className="h-4 w-4 text-[#8b5cf6]" />
          </div>
          <p className="text-[11px] text-[#71717a]">Осталось дней</p>
          <p className="text-xl font-bold text-white">{user.daysLeft || 0}</p>
        </div>
        <div className="glass-card rounded-xl p-4">
          <div className="mb-2 flex h-9 w-9 items-center justify-center rounded-lg bg-[rgba(245,158,11,0.15)]">
            <UserCheck className="h-4 w-4 text-[#f59e0b]" />
          </div>
          <p className="text-[11px] text-[#71717a]">Ментор</p>
          <p className="text-sm font-bold text-white">{user.mentor || "Нет"}</p>
        </div>
      </motion.div>

      {/* Referral */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card mb-4 rounded-2xl p-4"
      >
        <div className="mb-3 flex items-center gap-2">
          <Shield className="h-4 w-4 text-[#8b5cf6]" />
          <span className="text-sm font-semibold text-white">Реферальная программа</span>
        </div>
        <p className="mb-3 text-xs text-[#71717a] leading-relaxed">
          Приглашай друзей и получай 15% от их подписок
        </p>
        <div className="flex items-center gap-2">
          <div className="flex-1 truncate rounded-xl bg-[rgba(255,255,255,0.04)] px-3 py-2.5 text-xs text-[#71717a] border border-[rgba(255,255,255,0.06)]">
            {referralLink}
          </div>
          <motion.button
            whileTap={{ scale: 0.9 }}
            onClick={copyLink}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[rgba(139,92,246,0.15)] text-[#8b5cf6] transition-colors hover:bg-[rgba(139,92,246,0.25)]"
            aria-label="Copy referral link"
          >
            <Copy className="h-4 w-4" />
          </motion.button>
        </div>
        {copied && (
          <motion.p
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2 text-[11px] text-[#22c55e]"
          >
            Ссылка скопирована!
          </motion.p>
        )}
      </motion.div>

      {/* Transactions */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="mb-4"
      >
        <div className="mb-3 flex items-center justify-between px-1">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[#71717a]">
            История транзакций
          </h3>
          <button 
            onClick={() => setShowAllTransactions(true)}
            className="text-[10px] font-bold text-[#8b5cf6] hover:underline"
          >
            Все
          </button>
        </div>

        <div className="flex flex-col gap-2">
          {transactions.length === 0 ? (
            <div className="glass-card flex flex-col items-center justify-center rounded-2xl py-8 text-center">
              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-[rgba(255,255,255,0.04)] text-[#3f3f46]">
                <Clock className="h-5 w-5" />
              </div>
              <p className="text-xs font-medium text-[#52525b]">Транзакций пока нет</p>
            </div>
          ) : (
            transactions.slice(0, 3).map((tx) => (
              <div key={tx.id} className="glass-card flex items-center justify-between rounded-2xl p-4">
                <div className="flex items-center gap-3">
                  <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${
                    tx.amount.startsWith("+") ? "bg-[rgba(34,197,94,0.12)]" : "bg-[rgba(255,255,255,0.06)]"
                  }`}>
                    <ExternalLink className={`h-4 w-4 ${
                      tx.amount.startsWith("+") ? "text-[#22c55e]" : "text-[#71717a]"
                    }`} />
                  </div>
                  <div className="text-left">
                    <p className="text-sm font-bold text-white">{tx.type}</p>
                    <p className="text-[10px] text-[#71717a]">{tx.date}</p>
                  </div>
                </div>
                <p className={`text-sm font-bold ${
                  tx.amount.startsWith("+") ? "text-[#22c55e]" : "text-white"
                }`}>
                  {tx.amount}
                </p>
              </div>
            ))
          )}
        </div>
      </motion.div>

      {/* All Transactions Modal */}
      <AnimatePresence>
        {showAllTransactions && (
          <div className="fixed inset-0 z-[60] flex items-end justify-center">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setShowAllTransactions(false)}
            />
            <motion.div
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="glass-card-strong relative w-full max-w-[430px] rounded-t-3xl p-6 pb-12"
            >
              <div className="mb-6 flex items-center justify-between">
                <h3 className="text-lg font-bold text-white">Все транзакции</h3>
                <button onClick={() => setShowAllTransactions(false)} className="text-[#71717a]">
                  <X className="h-5 w-5" />
                </button>
              </div>
              
              <div className="max-h-[60vh] overflow-y-auto space-y-3 pr-1 scrollbar-hide">
                {transactions.length === 0 ? (
                  <p className="text-center text-sm text-[#71717a] py-10">Транзакций не найдено</p>
                ) : (
                  transactions.map((tx) => (
                    <div key={tx.id} className="glass-card flex items-center justify-between rounded-2xl p-4">
                      <div className="flex items-center gap-3">
                        <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${
                          tx.amount.startsWith("+") ? "bg-[rgba(34,197,94,0.12)]" : "bg-[rgba(255,255,255,0.06)]"
                        }`}>
                          <ExternalLink className={`h-4 w-4 ${
                            tx.amount.startsWith("+") ? "text-[#22c55e]" : "text-[#71717a]"
                          }`} />
                        </div>
                        <div className="text-left">
                          <p className="text-sm font-bold text-white">{tx.type}</p>
                          <p className="text-[10px] text-[#71717a]">{tx.date}</p>
                        </div>
                      </div>
                      <p className={`text-sm font-bold ${
                        tx.amount.startsWith("+") ? "text-[#22c55e]" : "text-white"
                      }`}>
                        {tx.amount}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  )
}
