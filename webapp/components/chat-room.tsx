"use client"

import { useState, useRef, useEffect } from "react"
import { ArrowLeft, Send, Paperclip, MoreVertical, Lock } from "lucide-react"
import { motion } from "framer-motion"
import { useUser } from "@/lib/user-context"
import { useData, Mentor, Message } from "@/lib/data-context"

interface ChatRoomProps {
  mentor: Mentor
  onBack: () => void
}

export function ChatRoom({ mentor, onBack }: ChatRoomProps) {
  const { user } = useUser()
  const { chats, addMessage } = useData()
  const [input, setInput] = useState("")
  
  // Получаем сообщения из контекста
  const currentChat = chats.find(c => c.mentorId === mentor.id)
  const messages = currentChat?.messages || []

  // Проверка доступа к чату
  // Support доступен всегда
  // Менторы доступны только если есть активная подписка на конкретного ментора
  const canWrite = mentor.id === "support" || (user?.mentorAccess && user.mentorAccess.includes(mentor.id))

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = () => {
    if (!input.trim() || !canWrite) return

    const newMessage: Message = {
      id: Date.now().toString(),
      text: input,
      time: new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }),
      sender: "user",
    }

    addMessage(mentor.id, newMessage)
    setInput("")

    // Simulate mentor's reply
    setTimeout(() => {
      const reply: Message = {
        id: (Date.now() + 1).toString(),
        text: "Сообщение получено. Скоро отвечу!",
        time: new Date().toLocaleTimeString("ru-RU", { hour: "2-digit", minute: "2-digit" }),
        sender: mentor.id,
      }
      addMessage(mentor.id, reply)
    }, 1500)
  }

  return (
    <div className="fixed inset-0 z-50 flex flex-col bg-[#0a0a0f]">
      {/* Header */}
      <div className="glass-card-strong flex items-center gap-3 px-4 py-4 pt-6 pb-4 shrink-0 z-10">
        <button
          onClick={onBack}
          className="flex h-9 w-9 items-center justify-center rounded-xl bg-[rgba(255,255,255,0.06)] text-[#d4d4d8] active:scale-95 transition-transform"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div className="relative">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[rgba(139,92,246,0.15)] text-sm font-bold text-[#8b5cf6]">
            {mentor.avatar}
          </div>
          {mentor.online && (
            <div className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-[#0a0a0f] bg-[#22c55e]" />
          )}
        </div>
        <div className="flex-1">
          <p className="text-sm font-bold text-white">{mentor.name}</p>
          <p className="text-[10px] text-[#71717a]">
            {mentor.online ? "В сети" : "Не в сети"}
          </p>
        </div>
        <button className="flex h-9 w-9 items-center justify-center rounded-xl bg-[rgba(255,255,255,0.06)] text-[#71717a]">
          <MoreVertical className="h-4 w-4" />
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 scrollbar-hide bg-[#0a0a0f]">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center opacity-50">
            <div className="h-16 w-16 mb-4 rounded-full bg-[rgba(255,255,255,0.04)] flex items-center justify-center">
              <Lock className="h-6 w-6 text-[#71717a]" />
            </div>
            <p className="text-sm text-[#71717a] font-medium">История сообщений пуста</p>
            <p className="text-[10px] text-[#52525b] mt-1 max-w-[200px] text-center">
              {canWrite ? "Начните диалог первым" : "Доступ к переписке ограничен"}
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex w-full ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    msg.sender === "user"
                      ? "gradient-primary text-white rounded-tr-sm"
                      : "glass-card text-[#e4e4e7] rounded-tl-sm"
                  }`}
                >
                  <p className="text-sm leading-relaxed">{msg.text}</p>
                  <div className={`mt-1 flex items-center justify-end gap-1 text-[9px] ${
                    msg.sender === "user" ? "text-white/60" : "text-[#52525b]"
                  }`}>
                    <span>{msg.time}</span>
                  </div>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="glass-card-strong px-4 py-3 pb-8 shrink-0">
        {canWrite ? (
          <div className="flex items-center gap-2">
            <button className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[rgba(255,255,255,0.06)] text-[#71717a] hover:bg-[rgba(255,255,255,0.1)] transition-colors">
              <Paperclip className="h-4 w-4" />
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
              placeholder="Написать сообщение..."
              className="flex-1 rounded-full bg-[rgba(255,255,255,0.06)] px-4 py-2.5 text-sm text-white placeholder:text-[#52525b] outline-none border border-transparent focus:border-[rgba(139,92,246,0.4)] transition-colors"
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim()}
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full gradient-primary text-white disabled:opacity-30 disabled:cursor-not-allowed transition-all active:scale-95"
            >
              <Send className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <div className="flex items-center justify-center gap-3 rounded-xl bg-[rgba(245,158,11,0.1)] p-4 text-center border border-[rgba(245,158,11,0.2)]">
            <Lock className="h-5 w-5 text-[#f59e0b] shrink-0" />
            <div className="text-left">
              <p className="text-sm font-bold text-[#e4e4e7]">Чат недоступен</p>
              <p className="text-[10px] text-[#a1a1aa]">
                Требуется подписка на ментора {mentor.name}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
