"use client"

import { useState, useEffect } from "react"
import { TrendingUp, DollarSign, Plus, Trash2, Calendar, Target, LayoutGrid, Calculator, X, AreaChart } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useUser } from "@/lib/user-context"
import { LockedOverlay } from "./locked-overlay"
import { ArbitrageCalculator } from "./arbitrage-calculator"
import { 
  AreaChart as ReAreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer 
} from 'recharts';

interface Trade {
  id: string
  amount: number
  date: string
  note: string
}

export function StatsScreen({ onSubscribe }: { onSubscribe?: () => void }) {
  const { user } = useUser()
  const [trades, setTrades] = useState<Trade[]>([])
  const [isAdding, setIsAdding] = useState(false)
  const [showCalculator, setShowCalculator] = useState(false)
  const [amount, setAmount] = useState("")
  const [note, setNote] = useState("")

  // Load trades from localStorage
  useEffect(() => {
    const savedTrades = localStorage.getItem(`trades_${user?.id}`)
    if (savedTrades) {
      setTrades(JSON.parse(savedTrades))
    }
  }, [user?.id])

  // Save trades to localStorage
  const saveTrades = (newTrades: Trade[]) => {
    setTrades(newTrades)
    localStorage.setItem(`trades_${user?.id}`, JSON.stringify(newTrades))
  }

  const handleAddTrade = () => {
    if (!amount || isNaN(Number(amount))) return

    const newTrade: Trade = {
      id: Date.now().toString(),
      amount: Number(amount),
      date: new Date().toLocaleDateString("ru-RU"),
      note: note || "Сделка"
    }

    saveTrades([newTrade, ...trades])
    setAmount("")
    setNote("")
    setIsAdding(false)
  }

  const deleteTrade = (id: string) => {
    saveTrades(trades.filter(t => t.id !== id))
  }

  // Stats calculations
  const totalProfit = trades.reduce((acc, t) => acc + t.amount, 0)
  const todayProfit = trades
    .filter(t => t.date === new Date().toLocaleDateString("ru-RU"))
    .reduce((acc, t) => acc + t.amount, 0)
  
  const weekAgo = new Date()
  weekAgo.setDate(weekAgo.getDate() - 7)
  const weeklyProfit = trades
    .filter(t => {
      const [day, month, year] = t.date.split(".").map(Number)
      const tradeDate = new Date(year, month - 1, day)
      return tradeDate >= weekAgo
    })
    .reduce((acc, t) => acc + t.amount, 0)

  // Chart data preparation
  const chartData = trades
    .sort((a, b) => new Date(a.date.split('.').reverse().join('-')).getTime() - new Date(b.date.split('.').reverse().join('-')).getTime())
    .reduce((acc, trade) => {
      const date = trade.date;
      const existing = acc.find(d => d.date === date);
      if (existing) {
        existing.profit += trade.amount;
      } else {
        acc.push({ date, profit: trade.amount });
      }
      return acc;
    }, [] as { date: string; profit: number }[]).map(d => ({...d, profit: Math.round(d.profit)}));

  return (
    <div className="relative flex flex-col px-4 pb-28 pt-4 min-h-[80vh]">
      {!user?.isSubscribed && (
        <LockedOverlay 
          title="Дневник закрыт" 
          description="Получите VIP-доступ, чтобы вести личный дневник сделок и отслеживать свою прибыль."
          onSubscribe={onSubscribe}
        />
      )}
      
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Моя статистика</h2>
          <p className="mt-1 text-xs text-[#71717a]">Личный дневник прибыли</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setShowCalculator(true)}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-[rgba(255,255,255,0.04)] text-[#71717a] transition-colors hover:text-[#8b5cf6]"
          >
            <Calculator className="h-5 w-5" />
          </button>
          <button
            onClick={() => setIsAdding(true)}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#8b5cf6] text-white shadow-[0_0_15px_rgba(139,92,246,0.3)]"
          >
            <Plus className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Calculator Modal */}
      <AnimatePresence>
        {showCalculator && (
          <div className="fixed inset-0 z-[70] flex items-end justify-center">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setShowCalculator(false)}
            />
            <motion.div
              initial={{ y: "100%" }}
              animate={{ y: 0 }}
              exit={{ y: "100%" }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="relative w-full max-w-[430px]"
            >
              <div className="absolute right-4 top-4 z-10">
                <button
                  onClick={() => setShowCalculator(false)}
                  className="flex h-8 w-8 items-center justify-center rounded-full bg-[rgba(255,255,255,0.1)] text-white backdrop-blur-md"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <ArbitrageCalculator />
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Summary Cards */}
      <div className="mb-6 grid grid-cols-3 gap-3">
        {[
          { label: "За сегодня", value: `${todayProfit > 0 ? "+" : ""}${todayProfit}$`, icon: Calendar, color: "#8b5cf6" },
          { label: "За неделю", value: `${weeklyProfit > 0 ? "+" : ""}${weeklyProfit}$`, icon: Target, color: "#22c55e" },
          { label: "Всего", value: `${totalProfit > 0 ? "+" : ""}${totalProfit}$`, icon: LayoutGrid, color: "#f59e0b" },
        ].map((card, i) => (
          <motion.div
            key={card.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="glass-card rounded-xl p-3 flex flex-col items-center text-center"
          >
            <div
              className="mb-2 flex h-8 w-8 items-center justify-center rounded-lg"
              style={{ background: `${card.color}20` }}
            >
              <card.icon className="h-4 w-4" style={{ color: card.color }} />
            </div>
            <span className="text-sm font-bold text-white truncate w-full">{card.value}</span>
            <span className="text-[9px] text-[#71717a] leading-tight mt-1">{card.label}</span>
          </motion.div>
        ))}
      </div>

      {/* Add Trade Form */}
      <AnimatePresence>
        {isAdding && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="glass-card mb-6 overflow-hidden rounded-2xl p-4 border border-[#8b5cf6]/30"
          >
            <h3 className="mb-4 text-sm font-bold text-white">Добавить профит</h3>
            <div className="space-y-3">
              <div className="relative">
                <DollarSign className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[#71717a]" />
                <input
                  type="number"
                  placeholder="Сумма (USDT)"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  className="w-full rounded-xl bg-[rgba(255,255,255,0.04)] py-3 pl-10 pr-4 text-sm text-white outline-none ring-1 ring-white/10 focus:ring-[#8b5cf6]/50"
                />
              </div>
              <input
                type="text"
                placeholder="Комментарий (напр. Bybit -> HTX)"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className="w-full rounded-xl bg-[rgba(255,255,255,0.04)] py-3 px-4 text-sm text-white outline-none ring-1 ring-white/10 focus:ring-[#8b5cf6]/50"
              />
              <div className="flex gap-2 pt-2">
                <button
                  onClick={handleAddTrade}
                  className="flex-1 rounded-xl bg-[#8b5cf6] py-3 text-sm font-bold text-white"
                >
                  Сохранить
                </button>
                <button
                  onClick={() => setIsAdding(false)}
                  className="flex-1 rounded-xl bg-[rgba(255,255,255,0.06)] py-3 text-sm font-bold text-[#71717a]"
                >
                  Отмена
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Profit Chart */}
      <div className="mb-6">
        <div className="mb-3 flex items-center gap-2">
          <AreaChart className="h-4 w-4 text-[#71717a]" />
          <h3 className="text-sm font-semibold text-white">График прибыли</h3>
        </div>
        <div className="glass-card h-48 w-full rounded-2xl p-2">
          {trades.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <ReAreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#22c55e" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="date" tick={{ fontSize: 9, fill: '#71717a' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 9, fill: '#71717a' }} axisLine={false} tickLine={false} width={30} />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'rgba(10, 10, 15, 0.8)', 
                    borderColor: 'rgba(255,255,255,0.1)', 
                    borderRadius: '12px',
                    fontSize: '12px'
                  }}
                  labelStyle={{ fontWeight: 'bold' }}
                  formatter={(value: number) => [`${value.toFixed(2)} USDT`, 'Профит']}
                />
                <Area type="monotone" dataKey="profit" stroke="#22c55e" fillOpacity={1} fill="url(#colorProfit)" strokeWidth={2} />
              </ReAreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex h-full items-center justify-center">
              <p className="text-xs text-[#71717a]">Добавьте первую сделку, чтобы увидеть график</p>
            </div>
          )}
        </div>
      </div>

      {/* Trades List */}
      <div>
        <p className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-[#71717a]">
          История сделок
        </p>
        <div className="flex flex-col gap-2">
          {trades.length === 0 ? (
            <div className="py-10 text-center">
              <p className="text-sm text-[#71717a]">Сделок пока нет</p>
            </div>
          ) : (
            trades.map((trade, i) => (
              <motion.div
                key={trade.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
                className="glass-card flex items-center justify-between rounded-xl px-4 py-3"
              >
                <div className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[rgba(34,197,94,0.12)]">
                    <TrendingUp className="h-4 w-4 text-[#22c55e]" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">{trade.note}</p>
                    <p className="text-[10px] text-[#71717a]">{trade.date}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-bold text-[#22c55e]">
                    +{trade.amount}$
                  </span>
                  <button 
                    onClick={() => deleteTrade(trade.id)}
                    className="text-[#71717a] hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
