"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Calculator, X, TrendingUp, Percent } from "lucide-react"

export function ArbitrageCalculator() {
  const [amount, setAmount] = useState("1000")
  const [buyPrice, setBuyPrice] = useState("")
  const [sellPrice, setSellPrice] = useState("")
  const [networkFee, setNetworkFee] = useState("1")

  const parse = (value: string) => parseFloat(value) || 0

  const amountNum = parse(amount)
  const buyPriceNum = parse(buyPrice)
  const sellPriceNum = parse(sellPrice)
  const feeNum = parse(networkFee)

  const buyAmount = amountNum / buyPriceNum
  const sellValue = buyAmount * sellPriceNum
  const netProfit = sellValue - amountNum - feeNum
  const roi = (netProfit / amountNum) * 100

  const isValid = amountNum > 0 && buyPriceNum > 0 && sellPriceNum > 0

  return (
    <div className="glass-card-strong w-full max-w-md rounded-t-3xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[rgba(34,197,94,0.15)] text-[#22c55e]">
            <Calculator className="h-5 w-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-white">Калькулятор</h3>
            <p className="text-xs text-[#71717a]">Расчет профита P2P-сделки</p>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <InputField label="Сумма сделки (USDT)" value={amount} setValue={setAmount} />
        <div className="grid grid-cols-2 gap-3">
          <InputField label="Цена покупки" value={buyPrice} setValue={setBuyPrice} />
          <InputField label="Цена продажи" value={sellPrice} setValue={setSellPrice} />
        </div>
        <InputField label="Комиссия сети (USDT)" value={networkFee} setValue={setNetworkFee} />
      </div>

      <div className="mt-6 space-y-4">
        <h4 className="text-sm font-semibold text-white">Результат:</h4>
        <div className="grid grid-cols-2 gap-3">
          <ResultCard 
            label="Чистый профит" 
            value={`${isValid ? netProfit.toFixed(2) : "0.00"} USDT`} 
            isPositive={netProfit > 0}
            icon={TrendingUp}
          />
          <ResultCard 
            label="ROI" 
            value={`${isValid ? roi.toFixed(2) : "0.00"}%`}
            isPositive={roi > 0}
            icon={Percent}
          />
        </div>
      </div>
    </div>
  )
}

const InputField = ({ label, value, setValue }: { label: string, value: string, setValue: (val: string) => void }) => (
  <div>
    <label className="mb-1.5 block text-xs font-medium text-[#a1a1aa]">{label}</label>
    <input
      type="number"
      value={value}
      onChange={(e) => setValue(e.target.value)}
      placeholder="0.00"
      className="w-full rounded-xl bg-[rgba(255,255,255,0.04)] py-3 px-4 text-sm text-white outline-none ring-1 ring-white/10 focus:ring-[#8b5cf6]/50"
    />
  </div>
)

const ResultCard = ({ label, value, isPositive, icon: Icon }: { label: string, value: string, isPositive: boolean, icon: any }) => (
  <div className="glass-card rounded-xl p-4">
    <div className="flex items-center gap-2 mb-1">
      <Icon className={`h-3.5 w-3.5 ${isPositive ? "text-green-500" : "text-red-500"}`} />
      <p className="text-xs text-[#a1a1aa]">{label}</p>
    </div>
    <p className={`text-xl font-bold ${isPositive ? "text-green-400" : "text-red-400"}`}>{value}</p>
  </div>
)
