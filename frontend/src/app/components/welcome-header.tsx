import React from 'react'

export function WelcomeHeader() {
  // Get time of day greeting
  const getGreeting = () => {
    const hour = new Date().getHours()
    if (hour < 12) return 'Good morning'
    if (hour < 18) return 'Good afternoon'
    return 'Good evening'
  }

  return (
    <div className="text-center space-y-2">
      <div className="flex items-center justify-center mb-2">
        <span className="text-primary text-xl mr-2">✨</span>
      </div>
      <h1 className="text-4xl font-bold tracking-tight text-foreground">{getGreeting()}</h1>
      <p className="text-xl text-muted-foreground mt-2">How can I help you?</p>
    </div>
  )
} 