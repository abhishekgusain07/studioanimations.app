"use client"
import React, { useState } from 'react'
import { PlusCircle, Search, Mic, SendHorizontal, Image } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function ChatInput() {
  const [inputValue, setInputValue] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Handle form submission logic here
    console.log('Submitted:', inputValue)
    setInputValue('')
  }

  return (
    <div className="relative w-full">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center bg-background rounded-xl border shadow-sm transition-all focus-within:shadow-md focus-within:border-primary">
          <div className="flex items-center pl-3">
            <Button type="button" variant="ghost" size="icon" className="rounded-full h-8 w-8 text-muted-foreground">
              <PlusCircle className="h-5 w-5" />
            </Button>
          </div>
          
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask anything..."
            className="flex-1 h-14 px-3 py-4 bg-transparent border-0 focus:outline-none text-base"
          />
          
          <div className="flex items-center gap-2 pr-3">
            <Button type="button" variant="ghost" size="icon" className="rounded-full h-8 w-8 text-muted-foreground">
              <Search className="h-4 w-4" />
            </Button>
            <Button type="button" variant="ghost" size="icon" className="rounded-full h-8 w-8 text-muted-foreground">
              <Image className="h-4 w-4" />
            </Button>
            <Button type="button" variant="ghost" size="icon" className="rounded-full h-8 w-8 text-muted-foreground">
              <Mic className="h-4 w-4" />
            </Button>
            <Button 
              type="submit" 
              variant="ghost" 
              size="icon" 
              className={`rounded-full h-8 w-8 ${inputValue ? 'text-primary' : 'text-muted-foreground'}`}
              disabled={!inputValue}
            >
              <SendHorizontal className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </form>
    </div>
  )
} 