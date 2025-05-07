import React from 'react'

export function SuggestedPrompts() {
  const prompts = [
    "How does AI work?",
    "Are black holes real?",
    "How many Rs are in the word \"strawberry\"?",
    "What is the meaning of life?"
  ]

  return (
    <div className="w-full max-w-xl space-y-3">
      {prompts.map((prompt, index) => (
        <button
          key={index}
          className="w-full text-left p-3 rounded-lg bg-background hover:bg-muted text-muted-foreground hover:text-foreground border border-transparent hover:border-border transition-all"
          onClick={() => console.log('Selected prompt:', prompt)}
        >
          {prompt}
        </button>
      ))}
    </div>
  )
} 