"use client"

import React, { createContext, useContext, useState, useEffect } from "react"

declare global {
  interface Window {
    Telegram?: {
      WebApp: any
    }
  }
}

interface User {
  id: string
  nickname: string
  avatar: string
  isAdmin: boolean
  isSubscribed: boolean
  daysLeft?: number
  mentor?: string
  mentorAccess: string[]
}

const ADMIN_IDS = ["1224124665", "8429170216"]

interface UserContextType {
  user: User | null
  loading: boolean
  updateUser: (updates: Partial<User>) => void
  toggleAdmin: () => void
  loginAsAdmin: (password: string) => boolean
  toggleSubscription: () => void
  grantMentorAccess: (mentorId: string) => void
}

const UserContext = createContext<UserContextType | undefined>(undefined)

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const tg = window.Telegram?.WebApp
    if (tg) {
      tg.ready()
      const tgUser = tg.initDataUnsafe?.user

      if (tgUser) {
        const userId = tgUser.id.toString()
        const savedUserData = localStorage.getItem(`crypto_user_${userId}`)
        
        if (savedUserData) {
          setUser(JSON.parse(savedUserData))
        } else {
          const newUser: User = {
            id: userId,
            nickname: tgUser.first_name || tgUser.username || "User",
            avatar: (tgUser.first_name || tgUser.username || "U")[0],
            isAdmin: ADMIN_IDS.includes(userId),
            isSubscribed: false,
            daysLeft: 0,
            mentorAccess: []
          }
          setUser(newUser)
          localStorage.setItem(`crypto_user_${userId}`, JSON.stringify(newUser))
        }
      } else {
        // Fallback for development in browser
        const devUser: User = {
          id: "8472",
          nickname: "Dev User",
          avatar: "D",
          isAdmin: true,
          isSubscribed: true,
          daysLeft: 30,
          mentorAccess: ["gatee"]
        }
        setUser(devUser)
      }
    } else {
      // Fallback for development
      const devUser: User = {
        id: "8472",
        nickname: "Dev User",
        avatar: "D",
        isAdmin: true,
        isSubscribed: true,
        daysLeft: 30,
        mentorAccess: ["gatee"]
      }
      setUser(devUser)
    }
    setLoading(false)
  }, [])

  const updateUser = (updates: Partial<User>) => {
    setUser((prev) => {
      if (!prev) return null
      const newUser = { ...prev, ...updates }
      localStorage.setItem(`crypto_user_${prev.id}`, JSON.stringify(newUser))
      return newUser
    })
  }

  const toggleAdmin = () => {
    setUser((prev: User | null) => (prev ? { ...prev, isAdmin: !prev.isAdmin } : null))
  }

  const loginAsAdmin = (password: string) => {
    if (password === "admin777") { // Mock password
      setUser((prev: User | null) => (prev ? { ...prev, isAdmin: true } : null))
      return true
    }
    return false
  }

  const toggleSubscription = () => {
    setUser((prev: User | null) => (prev ? { ...prev, isSubscribed: !prev.isSubscribed } : null))
  }

  const grantMentorAccess = (mentorId: string) => {
    setUser((prev: User | null) => {
      if (!prev) return null
      const currentAccess = prev.mentorAccess || []
      if (currentAccess.includes(mentorId)) return prev
      return { ...prev, mentorAccess: [...currentAccess, mentorId], mentor: "Gatee" }
    })
  }

  return (
    <UserContext.Provider value={{ 
      user, 
      loading, 
      updateUser, 
      toggleAdmin, 
      loginAsAdmin, 
      toggleSubscription, 
      grantMentorAccess 
    }}>
      {children}
    </UserContext.Provider>
  )
}

export function useUser() {
  const context = useContext(UserContext)
  if (context === undefined) {
    throw new Error("useUser must be used within a UserProvider")
  }
  return context
}
