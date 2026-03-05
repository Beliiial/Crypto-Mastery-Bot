"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ChatRoom } from "./chat-room"
import { useUser } from "@/lib/user-context"
import { useData, Mentor } from "@/lib/data-context"
import { LockedOverlay } from "./locked-overlay"

export function ChatScreen({ onSubscribe }: { onSubscribe?: () => void }) {
  const { user } = useUser()
  const { mentors, chats } = useData()
  const [selectedChat, setSelectedChat] = useState<Mentor | null>(null)

  // Получаем последнее сообщение и кол-во непрочитанных для каждого ментора
  const getChatInfo = (mentorId: string) => {
    const chat = chats.find(c => c.mentorId === mentorId)
    const lastMsg = chat?.messages[chat.messages.length - 1]
    return {
      lastMessage: lastMsg?.text || "Нет сообщений",
      time: lastMsg?.time || "",
      unread: chat?.unread || 0
    }
  }

  if (selectedChat) {
    return <ChatRoom mentor={selectedChat} onBack={() => setSelectedChat(null)} />
  }

  return (
    <div className="relative flex flex-col px-4 pb-28 pt-4 min-h-[80vh]">
      {!user?.isSubscribed && (
        <LockedOverlay 
          title="Чат закрыт" 
          description="Личный чат с менторами доступен только VIP-пользователям."
          onSubscribe={onSubscribe}
        />
      )}
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white">Сообщения</h2>
        <p className="mt-1 text-xs text-[#71717a]">Лайв-чат с менторами</p>
      </div>

      {/* Online mentors */}
      <div className="mb-6">
        <p className="mb-3 text-[11px] font-semibold uppercase tracking-widest text-[#71717a]">
          Менторы онлайн
        </p>
        <div className="flex gap-4">
          {mentors
            .filter((m) => m.online)
            .map((m) => (
              <button
                key={m.id}
                onClick={() => setSelectedChat(m)}
                className="flex flex-col items-center gap-1.5"
              >
                <div className="relative">
                  <div className="flex h-14 w-14 items-center justify-center rounded-full bg-[rgba(139,92,246,0.15)] text-lg font-bold text-[#8b5cf6]">
                    {m.avatar}
                  </div>
                  <div className="absolute bottom-0 right-0 h-3.5 w-3.5 rounded-full border-2 border-[#0a0a0f] bg-[#22c55e]" />
                </div>
                <span className="text-[11px] font-medium text-[#a1a1aa]">{m.name}</span>
              </button>
            ))}
        </div>
      </div>

      {/* Chat list */}
      <div className="flex flex-col gap-2">
        <p className="mb-1 text-[11px] font-semibold uppercase tracking-widest text-[#71717a]">
          Все чаты
        </p>
        {mentors.map((mentor, i) => {
          const info = getChatInfo(mentor.id)
          return (
            <motion.button
              key={mentor.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => setSelectedChat(mentor)}
              className="glass-card flex items-center gap-3 rounded-xl px-4 py-3 transition-all hover:bg-[rgba(255,255,255,0.06)]"
            >
              {/* Avatar */}
              <div className="relative shrink-0">
                <div className="flex h-11 w-11 items-center justify-center rounded-full bg-[rgba(139,92,246,0.15)] text-sm font-bold text-[#8b5cf6]">
                  {mentor.avatar}
                </div>
                {mentor.online && (
                  <div className="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-[#0a0a0f] bg-[#22c55e]" />
                )}
              </div>

              {/* Info */}
              <div className="flex flex-1 flex-col items-start overflow-hidden">
                <div className="flex w-full items-center justify-between">
                  <span className="text-sm font-semibold text-white">{mentor.name}</span>
                  <span className="text-[10px] text-[#71717a]">{info.time}</span>
                </div>
                <div className="flex w-full items-center justify-between">
                  <p className="truncate text-xs text-[#71717a] pr-2">{info.lastMessage}</p>
                  {info.unread > 0 && (
                    <span className="flex h-5 min-w-5 items-center justify-center rounded-full bg-[#8b5cf6] px-1.5 text-[10px] font-bold text-white">
                      {info.unread}
                    </span>
                  )}
                </div>
              </div>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}
