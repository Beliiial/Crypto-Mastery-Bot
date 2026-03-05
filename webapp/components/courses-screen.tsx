"use client"

import { Play, Clock, Star, Lock, PlusCircle } from "lucide-react"
import { motion } from "framer-motion"
import { useUser } from "@/lib/user-context"
import { useData } from "@/lib/data-context"
import { LockedOverlay } from "./locked-overlay"

export function CoursesScreen({ onSubscribe }: { onSubscribe?: () => void }) {
  const { user } = useUser()
  const { courses } = useData()

  // Показываем только опубликованные курсы или все, если пользователь админ
  const displayCourses = user?.isAdmin ? courses : courses.filter(c => c.status === "published")

  return (
    <div className="relative flex flex-col px-4 pb-28 pt-4 min-h-[80vh]">
      {!user?.isSubscribed && (
        <LockedOverlay 
          title="Обучение закрыто" 
          description="Получите VIP-доступ, чтобы смотреть все уроки и стратегии от экспертов."
          onSubscribe={onSubscribe}
        />
      )}
      
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-xl font-bold text-white">Курсы</h2>
        <p className="mt-1 text-xs text-[#71717a]">Обучение от лучших экспертов</p>
      </div>

      {/* Progress summary */}
      <motion.div
        initial={{ opacity: 0, y: 15 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card-strong mb-6 rounded-2xl p-4"
      >
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-white">Ваш прогресс</span>
          <span className="text-sm font-bold text-[#8b5cf6]">
            {user?.isSubscribed && displayCourses.length > 0 ? "0/" + displayCourses.length : "0/0"}
          </span>
        </div>
        <div className="h-2 w-full overflow-hidden rounded-full bg-[rgba(255,255,255,0.06)]">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: "0%" }}
            transition={{ duration: 1, delay: 0.3 }}
            className="h-full rounded-full gradient-primary"
          />
        </div>
        <p className="mt-2 text-[11px] text-[#71717a]">
          {displayCourses.length === 0 ? "Курсы пока не добавлены" : "Начните обучение прямо сейчас"}
        </p>
      </motion.div>

      {/* Course list */}
      {displayCourses.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-center">
          <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[rgba(255,255,255,0.04)]">
            <PlusCircle className="h-8 w-8 text-[#71717a] opacity-50" />
          </div>
          <h3 className="text-sm font-bold text-white">Нет доступных курсов</h3>
          <p className="mt-2 text-xs text-[#71717a] max-w-[200px]">
            Администратор скоро добавит новые обучающие материалы.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-3">
          {displayCourses.map((course, i) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className={`glass-card rounded-2xl p-4 transition-all ${
                course.locked && !user?.isSubscribed ? "opacity-60" : "hover:bg-[rgba(255,255,255,0.06)]"
              }`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1 pr-3">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-semibold text-white">{course.title}</h3>
                    {(course.locked || !user?.isSubscribed) && <Lock className="h-3 w-3 text-[#71717a]" />}
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-[#71717a]">
                    <span className="flex items-center gap-1">
                      <Play className="h-3 w-3" /> {course.lessons} уроков
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" /> {course.duration}
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="h-3 w-3 text-[#f59e0b]" fill="#f59e0b" /> {course.rating}
                    </span>
                  </div>
                </div>
                {(!course.locked || user?.isSubscribed) && (
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-[rgba(139,92,246,0.15)]">
                    <Play className="h-4 w-4 text-[#8b5cf6]" fill="#8b5cf6" />
                  </div>
                )}
              </div>
              {(!course.locked || user?.isSubscribed) && (
                <div className="flex items-center gap-2">
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-[rgba(255,255,255,0.06)]">
                    <div
                      className="h-full rounded-full gradient-primary transition-all"
                      style={{ width: `${course.progress}%` }}
                    />
                  </div>
                  <span className="text-[10px] font-semibold text-[#71717a]">{course.progress}%</span>
                </div>
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
