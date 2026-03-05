"use client"

import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Users, 
  BookOpen, 
  CreditCard, 
  UserPlus, 
  ChevronLeft, 
  Plus, 
  Trash2, 
  Edit2,
  CheckCircle2,
  XCircle,
  Clock as ClockIcon,
  Crown,
  UserCheck
} from "lucide-react"
import { useData, Course } from "@/lib/data-context"
import { useUser } from "@/lib/user-context"

type AdminTab = "users" | "courses" | "payments" | "mentors"

interface Mentor {
  id: number
  name: string
  specialization: string
  students: number
}

interface User {
  id: number
  name: string
  role: string
  status: string
}

interface Payment {
  id: string
  user: string
  amount: string
  date: string
  status: string
}

export function AdminPanel({ onBack }: { onBack: () => void }) {
  const [activeTab, setActiveTab] = useState<AdminTab>("courses")

  return (
    <div className="flex flex-col px-4 pb-28 pt-4">
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button 
            onClick={onBack}
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-[rgba(255,255,255,0.06)] text-white"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <h2 className="text-xl font-bold text-white">Админ-панель</h2>
        </div>
      </div>

      {/* Admin Tabs */}
      <div className="mb-6 flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {[
          { id: "courses", label: "Курсы", icon: BookOpen },
          { id: "mentors", label: "Менторы", icon: UserPlus },
          { id: "users", label: "Юзеры", icon: Users },
          { id: "payments", label: "Платежи", icon: CreditCard },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as AdminTab)}
            className={`flex items-center gap-2 whitespace-nowrap rounded-xl px-4 py-2.5 text-sm font-medium transition-all ${
              activeTab === tab.id
                ? "bg-[#8b5cf6] text-white shadow-[0_0_15px_rgba(139,92,246,0.3)]"
                : "bg-[rgba(255,255,255,0.04)] text-[#71717a] hover:bg-[rgba(255,255,255,0.08)]"
            }`}
          >
            <tab.icon className="h-4 w-4" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {activeTab === "courses" && <CoursesManager />}
          {activeTab === "mentors" && <MentorsManager />}
          {activeTab === "users" && <UsersManager />}
          {activeTab === "payments" && <PaymentsManager />}
        </motion.div>
      </AnimatePresence>
    </div>
  )
}

function CoursesManager() {
  const { courses, addCourse, deleteCourse, updateCourse } = useData()
  const [isAdding, setIsAdding] = useState(false)
  const [newCourseTitle, setNewCourseTitle] = useState("")
  const [editingCourse, setEditingCourse] = useState<Course | null>(null)

  const handleAddCourse = () => {
    if (!newCourseTitle.trim()) return
    
    const newCourse: Course = {
      id: Date.now().toString(),
      title: newCourseTitle,
      lessons: [],
      duration: "0ч 0мин",
      rating: 5.0,
      progress: 0,
      locked: true,
      status: "draft"
    }
    
    addCourse(newCourse)
    setNewCourseTitle("")
    setIsAdding(false)
  }

  if (editingCourse) {
    return <CourseEditor course={editingCourse} onBack={() => setEditingCourse(null)} updateCourse={(updates) => updateCourse(editingCourse.id, updates)} />
  }

  return (
    <div className="space-y-4">
      {isAdding ? (
        <div className="glass-card rounded-2xl p-4">
          <input
            type="text"
            value={newCourseTitle}
            onChange={(e) => setNewCourseTitle(e.target.value)}
            placeholder="Название курса"
            className="w-full mb-3 rounded-xl bg-[rgba(255,255,255,0.06)] px-4 py-2 text-sm text-white outline-none"
            autoFocus
          />
          <div className="flex gap-2">
            <button 
              onClick={handleAddCourse}
              className="flex-1 rounded-xl bg-[#8b5cf6] py-2 text-sm font-bold text-white"
            >
              Добавить
            </button>
            <button 
              onClick={() => setIsAdding(false)}
              className="flex-1 rounded-xl bg-[rgba(255,255,255,0.1)] py-2 text-sm font-bold text-white"
            >
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <button 
          onClick={() => setIsAdding(true)}
          className="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-[rgba(139,92,246,0.3)] py-4 text-sm font-medium text-[#8b5cf6] hover:bg-[rgba(139,92,246,0.05)] transition-colors"
        >
          <Plus className="h-4 w-4" /> Добавить курс
        </button>
      )}
      
      <div className="grid gap-3">
        {courses.length === 0 ? (
          <p className="text-center text-sm text-[#71717a] py-4">Список курсов пуст</p>
        ) : (
          courses.map((course) => (
            <div key={course.id} className="glass-card flex items-center justify-between rounded-2xl p-4">
              <div>
                <h4 className="text-sm font-bold text-white">{course.title}</h4>
                <p className="text-[11px] text-[#71717a]">{course.lessons.length} уроков • {course.status === 'published' ? 'Опубликован' : 'Черновик'}</p>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => setEditingCourse(course)}
                  className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(255,255,255,0.06)] text-[#71717a]"
                >
                  <Edit2 className="h-3.5 w-3.5" />
                </button>
                <button 
                  onClick={() => deleteCourse(course.id)}
                  className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(248,113,113,0.1)] text-[#f87171]"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}

function CourseEditor({ course, onBack, updateCourse }: { course: Course, onBack: () => void, updateCourse: (updates: Partial<Course>) => void }) {
  const [lessons, setLessons] = useState(course.lessons)
  const [isAdding, setIsAdding] = useState(false)
  const [newLessonTitle, setNewLessonTitle] = useState("")
  const [newLessonType, setNewLessonType] = useState<"video" | "text">("video")
  const [newLessonContent, setNewLessonContent] = useState("")

  const addLesson = () => {
    if (!newLessonTitle.trim() || !newLessonContent.trim()) return
    const newLesson: any = {
      id: Date.now().toString(),
      title: newLessonTitle,
      type: newLessonType,
      content: newLessonContent,
      duration: 5 // Mock duration
    }
    const updatedLessons = [...lessons, newLesson]
    setLessons(updatedLessons)
    updateCourse({ lessons: updatedLessons })
    setNewLessonTitle("")
    setNewLessonContent("")
    setIsAdding(false)
  }

  const deleteLesson = (id: string) => {
    const updatedLessons = lessons.filter(l => l.id !== id)
    setLessons(updatedLessons)
    updateCourse({ lessons: updatedLessons })
  }

  return (
    <div>
      <div className="mb-6 flex items-center gap-3">
        <button onClick={onBack} className="flex h-9 w-9 items-center justify-center rounded-xl bg-[rgba(255,255,255,0.06)] text-white">
          <ChevronLeft className="h-5 w-5" />
        </button>
        <div>
          <h3 className="text-lg font-bold text-white">{course.title}</h3>
          <p className="text-xs text-[#71717a]">Редактор уроков</p>
        </div>
      </div>

      {isAdding ? (
        <div className="glass-card rounded-2xl p-4 mb-4 space-y-3">
          <input type="text" value={newLessonTitle} onChange={e => setNewLessonTitle(e.target.value)} placeholder="Название урока" className="w-full rounded-xl bg-[rgba(255,255,255,0.06)] px-4 py-2 text-sm text-white outline-none" />
          <select value={newLessonType} onChange={e => setNewLessonType(e.target.value as any)} className="w-full rounded-xl bg-[rgba(255,255,255,0.06)] px-4 py-2 text-sm text-white outline-none">
            <option value="video">Видео</option>
            <option value="text">Текст</option>
          </select>
          <textarea value={newLessonContent} onChange={e => setNewLessonContent(e.target.value)} placeholder={newLessonType === 'video' ? "Ссылка на YouTube/Vimeo" : "Содержимое урока (Markdown)"} className="w-full rounded-xl bg-[rgba(255,255,255,0.06)] px-4 py-2 text-sm text-white outline-none h-24" />
          <div className="flex gap-2">
            <button onClick={addLesson} className="flex-1 rounded-xl bg-[#8b5cf6] py-2 text-sm font-bold text-white">Добавить</button>
            <button onClick={() => setIsAdding(false)} className="flex-1 rounded-xl bg-[rgba(255,255,255,0.1)] py-2 text-sm font-bold text-white">Отмена</button>
          </div>
        </div>
      ) : (
        <button onClick={() => setIsAdding(true)} className="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-[rgba(139,92,246,0.3)] py-4 text-sm font-medium text-[#8b5cf6] hover:bg-[rgba(139,92,246,0.05)] transition-colors mb-4">
          <Plus className="h-4 w-4" /> Добавить урок
        </button>
      )}

      <div className="space-y-3">
        {lessons.map(lesson => (
          <div key={lesson.id} className="glass-card flex items-center justify-between rounded-2xl p-4">
            <h4 className="text-sm font-bold text-white">{lesson.title}</h4>
            <button onClick={() => deleteLesson(lesson.id)} className="flex h-8 w-8 items-center justify-center rounded-lg bg-[rgba(248,113,113,0.1)] text-[#f87171]">
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function MentorsManager() {
  const { mentors, addMentor } = useData()
  const [isAdding, setIsAdding] = useState(false)
  const [newMentorName, setNewMentorName] = useState("")

  const handleAddMentor = () => {
    if (!newMentorName.trim()) return
    
    // В реальном приложении нужно больше полей, здесь для демо упростим
    const newMentor = {
      id: Date.now().toString(),
      name: newMentorName,
      role: "Ментор",
      specialization: "General",
      students: 0,
      online: false,
      avatar: newMentorName[0].toUpperCase()
    }
    
    addMentor(newMentor)
    setNewMentorName("")
    setIsAdding(false)
  }

  return (    
    <div className="space-y-4">
      {isAdding ? (
        <div className="glass-card rounded-2xl p-4">
          <input
            type="text"
            value={newMentorName}
            onChange={(e) => setNewMentorName(e.target.value)}
            placeholder="Имя ментора"
            className="w-full mb-3 rounded-xl bg-[rgba(255,255,255,0.06)] px-4 py-2 text-sm text-white outline-none"
            autoFocus
          />
          <div className="flex gap-2">
            <button 
              onClick={handleAddMentor}
              className="flex-1 rounded-xl bg-[#8b5cf6] py-2 text-sm font-bold text-white"
            >
              Добавить
            </button>
            <button 
              onClick={() => setIsAdding(false)}
              className="flex-1 rounded-xl bg-[rgba(255,255,255,0.1)] py-2 text-sm font-bold text-white"
            >
              Отмена
            </button>
          </div>
        </div>
      ) : (
        <button 
          onClick={() => setIsAdding(true)}
          className="flex w-full items-center justify-center gap-2 rounded-xl border-2 border-dashed border-[rgba(139,92,246,0.3)] py-4 text-sm font-medium text-[#8b5cf6] hover:bg-[rgba(139,92,246,0.05)] transition-colors"
        >
          <Plus className="h-4 w-4" /> Добавить ментора
        </button>
      )}

      <div className="grid gap-3">
        {mentors.map((mentor) => (
          <div key={mentor.id} className="glass-card flex items-center justify-between rounded-2xl p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[rgba(139,92,246,0.1)] text-xs font-bold text-[#8b5cf6]">
                {mentor.name[0]}
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{mentor.name}</h4>
                <p className="text-[11px] text-[#71717a]">{mentor.specialization}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-[10px] text-[#71717a]">Учеников</p>
              <p className="text-xs font-bold text-white">{mentor.students}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function UsersManager() {
  const { user, toggleSubscription, grantMentorAccess } = useUser()
  
  // Для демо используем текущего пользователя и пару моковых
  const users = [
    { id: user?.id || 1, name: user?.nickname || "Вы", role: user?.isAdmin ? "Admin" : "User", status: "Active", isSubscribed: user?.isSubscribed },
    { id: 2, name: "Elena M.", role: "User", status: "Inactive", isSubscribed: false },
    { id: 3, name: "Alex R.", role: "User", status: "Active", isSubscribed: true },
  ]

  return (
    <div className="grid gap-3">
      {users.map((u) => (
        <div key={u.id} className="glass-card flex flex-col rounded-2xl p-4 gap-4">
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-[rgba(255,255,255,0.06)] flex items-center justify-center text-xs font-bold text-white">
                {u.name[0]}
              </div>
              <div>
                <h4 className="text-sm font-bold text-white">{u.name}</h4>
                <p className="text-[10px] text-[#71717a]">{u.role} • ID: {u.id}</p>
              </div>
            </div>
            <div className={`rounded-full px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${
              u.status === 'Active' ? 'bg-[rgba(34,197,94,0.1)] text-[#22c55e]' : 'bg-[rgba(248,113,113,0.1)] text-[#f87171]'
            }`}>
              {u.status}
            </div>
          </div>

          {/* Admin Actions */}
          <div className="flex gap-2 border-t border-white/5 pt-4">
            <button 
              onClick={() => u.id === user?.id && toggleSubscription()}
              className={`flex-1 flex items-center justify-center gap-2 rounded-xl py-2.5 text-[11px] font-bold transition-all ${
                u.isSubscribed 
                  ? "bg-[rgba(248,113,113,0.1)] text-[#f87171] hover:bg-[rgba(248,113,113,0.2)]" 
                  : "bg-[rgba(34,197,94,0.1)] text-[#22c55e] hover:bg-[rgba(34,197,94,0.2)]"
              }`}
            >
              <Crown className="h-3.5 w-3.5" />
              {u.isSubscribed ? "Забрать VIP" : "Выдать VIP"}
            </button>
            <button 
              onClick={() => u.id === user?.id && grantMentorAccess("gatee")}
              className="flex-1 flex items-center justify-center gap-2 rounded-xl bg-[rgba(139,92,246,0.1)] py-2.5 text-[11px] font-bold text-[#a78bfa] hover:bg-[rgba(139,92,246,0.2)]"
            >
              <UserCheck className="h-3.5 w-3.5" />
              Доступ к ментору
            </button>
          </div>
          {u.id !== user?.id && (
            <p className="text-[9px] text-center text-[#71717a] italic">Управление доступно только для вашего аккаунта в демо</p>
          )}
        </div>
      ))}
    </div>
  )
}

function PaymentsManager() {
  const payments: Payment[] = [
    { id: "TX-9012", user: "Dmitry K.", amount: "69 USDT", date: "Сегодня, 14:20", status: "completed" },
    { id: "TX-9011", user: "Elena M.", amount: "69 USDT", date: "Сегодня, 11:05", status: "pending" },
    { id: "TX-9010", user: "Alex R.", amount: "99 USDT", date: "Вчера, 22:45", status: "completed" },
  ]

  return (
    <div className="space-y-3">
      {payments.map((pay: Payment) => (
        <div key={pay.id} className="glass-card flex items-center justify-between rounded-2xl p-4">
          <div className="flex items-center gap-3">
            <div className={`flex h-9 w-9 items-center justify-center rounded-lg ${
              pay.status === 'completed' ? 'bg-[rgba(34,197,94,0.1)]' : 'bg-[rgba(245,158,11,0.1)]'
            }`}>
              {pay.status === 'completed' ? <CheckCircle2 className="h-4 w-4 text-[#22c55e]" /> : <ClockIcon className="h-4 w-4 text-[#f59e0b]" />}
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">{pay.user}</h4>
              <p className="text-[10px] text-[#71717a]">{pay.date}</p>
            </div>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold text-white">{pay.amount}</p>
            <p className="text-[9px] text-[#71717a]">{pay.id}</p>
          </div>
        </div>
      ))}
    </div>
  )
}
