"use client"

import React, { createContext, useContext, useState, useEffect } from "react"

export interface Lesson {
  id: string
  title: string
  type: "video" | "text"
  content: string // URL for video, markdown for text
  duration: number // in minutes
}

export interface Course {
  id: string
  title: string
  lessons: Lesson[]
  duration: string
  rating: number
  progress: number
  locked: boolean
  status: "draft" | "published"
}

export interface Mentor {
  id: string
  name: string
  role: string
  online: boolean
  avatar: string
  specialization: string
  students: number
}

export interface ChatMessage {
  id: string
  sender: "user" | "mentor"
  text: string
  time: string
  read: boolean
}

export interface Message {
  id: string
  text: string
  time: string
  sender: "user" | string // user or mentorId
}

export interface Chat {
  mentorId: string
  messages: Message[]
  unread: number
}

interface DataContextType {
  courses: Course[]
  mentors: Mentor[]
  chats: Chat[]
  addCourse: (course: Course) => void
  deleteCourse: (id: string) => void
  updateCourse: (id: string, updates: Partial<Course>) => void
  addMentor: (mentor: Mentor) => void
  addMessage: (mentorId: string, message: Message) => void
  sendMessage: (mentorId: string, text: string) => void
  markChatRead: (mentorId: string) => void
}

const DataContext = createContext<DataContextType | undefined>(undefined)

const initialMentors: Mentor[] = [
  {
    id: "gatee",
    name: "Gatee",
    role: "Старший ментор",
    online: true,
    avatar: "G",
    specialization: "P2P & Inter-exchange",
    students: 142
  },
  {
    id: "agwwee",
    name: "Agwwee",
    role: "Арбитраж-эксперт",
    online: true,
    avatar: "A",
    specialization: "Technical Analysis",
    students: 89
  },
  {
    id: "support",
    name: "Support",
    role: "Техническая поддержка",
    online: true,
    avatar: "S",
    specialization: "General Support",
    students: 0
  },
]

export function DataProvider({ children }: { children: React.ReactNode }) {
  // Courses start empty as requested
  const [courses, setCourses] = useState<Course[]>([])
  const [mentors, setMentors] = useState<Mentor[]>(initialMentors)
  // Chats start empty
  const [chats, setChats] = useState<Chat[]>([])

  // Initialize chats for mentors
  useEffect(() => {
    setChats(mentors.map(m => ({ mentorId: m.id, messages: [], unread: 0 })))
  }, [mentors])

  const addCourse = (course: Course) => {
    setCourses(prev => [...prev, course])
  }

  const updateCourse = (courseId: string, updates: Partial<Course>) => {
    setCourses(prev => prev.map(c => c.id === courseId ? { ...c, ...updates } : c))
  }

  const deleteCourse = (id: string) => {
    setCourses(prev => prev.filter(c => c.id !== id))
  }

  const addMentor = (mentor: Mentor) => {
    setMentors(prev => [...prev, mentor])
    setChats(prev => [...prev, { mentorId: mentor.id, messages: [], unread: 0 }])
  }

  const addMessage = (mentorId: string, message: Message) => {
    setChats(prev => prev.map(c => 
      c.mentorId === mentorId 
        ? { ...c, messages: [...c.messages, message], unread: c.unread + 1 } 
        : c
    ))
  }

  const sendMessage = (mentorId: string, text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }

    setChats(prev => prev.map(chat => {
      if (chat.mentorId === mentorId) {
        return { ...chat, messages: [...chat.messages, newMessage] }
      }
      return chat
    }))

    // Simulate auto-reply for demo purposes (optional)
    if (mentorId === 'support') {
      setTimeout(() => {
        const reply: Message = {
          id: (Date.now() + 1).toString(),
          sender: "support",
          text: "Спасибо за обращение! Оператор скоро ответит.",
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        }
        setChats(prev => prev.map(chat => {
            if (chat.mentorId === mentorId) {
              return { ...chat, messages: [...chat.messages, reply], unread: chat.unread + 1 }
            }
            return chat
          }))
      }, 1000)
    }
  }

  const markChatRead = (mentorId: string) => {
    setChats(prev => prev.map(chat => {
      if (chat.mentorId === mentorId) {
        return { ...chat, unread: 0 }
      }
      return chat
    }))
  }

  return (
    <DataContext.Provider value={{ 
      courses, 
      mentors, 
      chats, 
      addCourse, 
      updateCourse, 
      deleteCourse,
      addMentor,
      addMessage,
      sendMessage,
      markChatRead
    }}>
      {children}
    </DataContext.Provider>
  )
}

export function useData() {
  const context = useContext(DataContext)
  if (context === undefined) {
    throw new Error("useData must be used within a DataProvider")
  }
  return context
}
