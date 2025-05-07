import { NextResponse } from 'next/server'
import { auth } from '@/lib/auth'
import { conversation } from '@/db/schema'
import { eq, and } from 'drizzle-orm'
import { headers } from 'next/headers'
import { db } from '@/db/drizzle'

// PATCH handler to update a conversation
export async function PATCH(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth.api.getSession({
        headers: await headers()
    })
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    
    const userId = session.user.id
    const conversationId = params.id
    
    // Check if conversation exists and belongs to user
    const existingConversation = await db
      .select()
      .from(conversation)
      .where(
        and(
          eq(conversation.id, conversationId),
          eq(conversation.userId, userId)
        )
      )
      .then(rows => rows[0])
    
    if (!existingConversation) {
      return NextResponse.json({ error: 'Conversation not found' }, { status: 404 })
    }
    
    const { title } = await request.json()
    
    if (!title) {
      return NextResponse.json({ error: 'Title is required' }, { status: 400 })
    }
    
    const now = new Date()
    
    // Update the conversation
    await db
      .update(conversation)
      .set({ 
        title,
        updatedAt: now
      })
      .where(eq(conversation.id, conversationId))
    
    return NextResponse.json({
      id: conversationId,
      title,
      updatedAt: now
    })
  } catch (error) {
    console.error('Error updating conversation:', error)
    return NextResponse.json({ error: 'Failed to update conversation' }, { status: 500 })
  }
}

// DELETE handler to delete a conversation
export async function DELETE(
  request: Request,
  { params }: { params: { id: string } }
) {
  try {
    const session = await auth.api.getSession({
        headers: await headers()
    })
    
    if (!session?.user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
    }
    
    const userId = session.user.id
    const conversationId = params.id
    
    // Check if conversation exists and belongs to user
    const existingConversation = await db
      .select()
      .from(conversation)
      .where(
        and(
          eq(conversation.id, conversationId),
          eq(conversation.userId, userId)
        )
      )
      .then(rows => rows[0])
    
    if (!existingConversation) {
      return NextResponse.json({ error: 'Conversation not found' }, { status: 404 })
    }
    
    // Delete the conversation
    await db
      .delete(conversation)
      .where(eq(conversation.id, conversationId))
    
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Error deleting conversation:', error)
    return NextResponse.json({ error: 'Failed to delete conversation' }, { status: 500 })
  }
} 