"use client"

import { useState, useEffect } from "react"
import { conversation } from "@/db/schema"

// Typescript interface for conversations based on our schema
export interface Conversation {
  id: string
  userId: string
  title: string
  createdAt: Date
  updatedAt: Date
}

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Function to fetch conversations
  const fetchConversations = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Replace with your actual API endpoint
      const response = await fetch('/api/conversations')
      
      if (!response.ok) {
        throw new Error('Failed to fetch conversations')
      }
      
      const data = await response.json()
      
      // Transform dates to Date objects
      const conversationsWithDates = data.map((conv: any) => ({
        ...conv,
        createdAt: new Date(conv.createdAt),
        updatedAt: new Date(conv.updatedAt)
      }))
      
      setConversations(conversationsWithDates)
    } catch (err) {
      console.error('Error fetching conversations:', err)
      setError(err instanceof Error ? err.message : 'Failed to fetch conversations')
      
      // Fallback to mock data for development
      setConversations([
        { id: "1", userId: "user1", title: "Greeting", createdAt: new Date(), updatedAt: new Date() },
        { id: "2", userId: "user1", title: "New Thread", createdAt: new Date(), updatedAt: new Date() },
        { id: "3", userId: "user1", title: "ServiceNow career path advice", createdAt: new Date(Date.now() - 86400000), updatedAt: new Date(Date.now() - 86400000) },
        { id: "4", userId: "user1", title: "First Principles Learning App", createdAt: new Date(Date.now() - 86400000 * 2), updatedAt: new Date(Date.now() - 86400000 * 2) },
        { id: "5", userId: "user1", title: "React Native Docs Explanation", createdAt: new Date(Date.now() - 86400000 * 3), updatedAt: new Date(Date.now() - 86400000 * 3) },
        { id: "6", userId: "user1", title: "Welcome to T3 Chat", createdAt: new Date(Date.now() - 86400000 * 5), updatedAt: new Date(Date.now() - 86400000 * 5) },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  // Function to create a new conversation
  const createConversation = async (title: string = "New conversation") => {
    try {
      // Replace with your actual API endpoint
      const response = await fetch('/api/conversations', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to create conversation')
      }
      
      const newConversation = await response.json()
      
      // Add the new conversation to state
      setConversations((prev) => [
        {
          ...newConversation,
          createdAt: new Date(newConversation.createdAt),
          updatedAt: new Date(newConversation.updatedAt),
        },
        ...prev,
      ])
      
      return newConversation
    } catch (err) {
      console.error('Error creating conversation:', err)
      throw err
    }
  }

  // Function to delete a conversation
  const deleteConversation = async (id: string) => {
    try {
      // Replace with your actual API endpoint
      const response = await fetch(`/api/conversations/${id}`, {
        method: 'DELETE',
      })
      
      if (!response.ok) {
        throw new Error('Failed to delete conversation')
      }
      
      // Remove the conversation from state
      setConversations((prev) => prev.filter((conv) => conv.id !== id))
    } catch (err) {
      console.error('Error deleting conversation:', err)
      throw err
    }
  }

  // Function to rename a conversation
  const renameConversation = async (id: string, title: string) => {
    try {
      // Replace with your actual API endpoint
      const response = await fetch(`/api/conversations/${id}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title }),
      })
      
      if (!response.ok) {
        throw new Error('Failed to rename conversation')
      }
      
      const updatedConversation = await response.json()
      
      // Update the conversation in state
      setConversations((prev) => 
        prev.map((conv) => 
          conv.id === id 
            ? {
                ...conv,
                title,
                updatedAt: new Date(updatedConversation.updatedAt),
              }
            : conv
        )
      )
    } catch (err) {
      console.error('Error renaming conversation:', err)
      throw err
    }
  }

  // Fetch conversations on component mount
  useEffect(() => {
    fetchConversations()
  }, [])

  return {
    conversations,
    isLoading,
    error,
    fetchConversations,
    createConversation,
    deleteConversation,
    renameConversation,
  }
} 