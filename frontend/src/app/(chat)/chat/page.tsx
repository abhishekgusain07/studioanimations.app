"use client"
import { ChatInput } from '@/app/components/chat-input'
import { FeatureButtons } from '@/app/components/feature-buttons'
import { SuggestedPrompts } from '@/app/components/suggested-prompts'
import { WelcomeHeader } from '@/app/components/welcome-header'
import React from 'react'

const ChatPage = () => {
  return (
    <div className="flex flex-col items-center justify-between w-full h-full px-4 py-10 overflow-auto bg-muted/20">
      <div />
      <div className="flex-1 flex flex-col items-center justify-center w-full max-w-3xl mx-auto gap-8">
        <WelcomeHeader />
        
        <div className="w-full">
          <ChatInput />
        </div>

        <FeatureButtons />
        
        <SuggestedPrompts />
      </div>
      
      <div className="text-xs text-muted-foreground mt-8">
        <span>Make sure you agree to our </span>
        <a href="#" className="underline hover:text-foreground">Terms</a>
        <span> and our </span>
        <a href="#" className="underline hover:text-foreground">Privacy Policy</a>
      </div>
    </div>
  )
}

export default ChatPage
