import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import { ThemeProvider } from 'next-themes'
import { UserProvider } from '@/lib/user-context'
import { DataProvider } from '@/lib/data-context'
import './globals.css'

const _inter = Inter({ subsets: ['latin', 'cyrillic'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'Crypto Mastery - Telegram Mini App',
  description: 'Стань профи в криптоарбитраже. Обучение, менторство и лайв-чат с экспертами.',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#0a0a0f',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ru" suppressHydrationWarning>
      <body className={`${_inter.variable} font-sans antialiased`}>
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem={false}
        >
          <UserProvider>
            <DataProvider>{children}</DataProvider>
          </UserProvider>
          <Analytics />
        </ThemeProvider>
      </body>
    </html>
  )
}
