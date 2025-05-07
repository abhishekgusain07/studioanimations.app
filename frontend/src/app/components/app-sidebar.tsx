"use client"

import { useState } from "react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarSeparator,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { PlusCircle, Search, MessageSquare, User, Trash2, Edit, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { useConversations } from "@/hooks/use-conversations" 
import { useRouter } from "next/navigation"
import { format } from "date-fns"
import { Skeleton } from "@/components/ui/skeleton"
import { RenameConversationDialog } from "./rename-conversation-dialog"

export function AppSidebar() {
  const router = useRouter()
  const { state } = useSidebar()
  const [searchQuery, setSearchQuery] = useState("")
  const [renameDialog, setRenameDialog] = useState<{
    isOpen: boolean;
    conversationId: string;
    title: string;
  }>({
    isOpen: false,
    conversationId: "",
    title: "",
  })
  
  const { 
    conversations, 
    isLoading, 
    error, 
    createConversation,
    deleteConversation
  } = useConversations()
  
  const handleNewChat = async () => {
    try {
      const newConversation = await createConversation()
      router.push(`/chat/${newConversation.id}`)
    } catch (error) {
      console.error("Failed to create new conversation", error)
    }
  }
  
  const openRenameDialog = (id: string, title: string) => {
    setRenameDialog({
      isOpen: true,
      conversationId: id,
      title: title || "New conversation"
    })
  }
  
  const closeRenameDialog = () => {
    setRenameDialog({
      isOpen: false,
      conversationId: "",
      title: ""
    })
  }
  
  // Group conversations by date
  const todayConversations = conversations.filter(
    conv => new Date(conv.createdAt).toDateString() === new Date().toDateString()
  )
  
  const olderConversations = conversations.filter(
    conv => new Date(conv.createdAt).toDateString() !== new Date().toDateString()
  )

  // Filter conversations based on search query
  const filteredToday = searchQuery 
    ? todayConversations.filter(conv => 
        conv.title.toLowerCase().includes(searchQuery.toLowerCase()))
    : todayConversations
    
  const filteredOlder = searchQuery 
    ? olderConversations.filter(conv => 
        conv.title.toLowerCase().includes(searchQuery.toLowerCase()))
    : olderConversations

  return (
    <>
      {/* Show trigger outside sidebar only when sidebar is collapsed on mobile */}
      {state === "collapsed" && (
        <SidebarTrigger className="fixed top-4 left-4 z-50" />
      )}
      
      <Sidebar>
        <SidebarHeader className="p-3">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-lg font-semibold">Studio.animation</h2>
            <SidebarTrigger />
          </div>
          <Button 
            variant="default" 
            className="w-full mb-2 bg-primary/90 hover:bg-primary transition-colors"
            onClick={handleNewChat}
            disabled={isLoading}
          >
            {isLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <PlusCircle className="w-4 h-4 mr-2" />} 
            New Chat
          </Button>
          <div className="relative flex items-center">
            <Search className="absolute left-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search your threads..."
              className="w-full pl-9 h-9 bg-background"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </SidebarHeader>
        
        <SidebarContent className="px-1">
          {isLoading ? (
            <div className="space-y-2 p-3">
              <Skeleton className="h-5 w-full" />
              <Skeleton className="h-9 w-full" />
              <Skeleton className="h-9 w-full" />
              <Skeleton className="h-9 w-full" />
            </div>
          ) : (
            <>
              {filteredToday.length > 0 && (
                <SidebarGroup>
                  <SidebarGroupLabel className="px-3 py-2 text-xs font-medium text-muted-foreground">
                    Today
                  </SidebarGroupLabel>
                  <SidebarGroupContent>
                    <SidebarMenu>
                      {filteredToday.map((conv) => (
                        <SidebarMenuItem key={conv.id}>
                          <SidebarMenuButton 
                            className="w-full justify-start group"
                            onClick={() => router.push(`/chat/${conv.id}`)}
                          >
                            <MessageSquare className="h-4 w-4 mr-2 text-muted-foreground" />
                            <span className="truncate">{conv.title || "New conversation"}</span>
                            <div className="hidden ml-auto group-hover:flex gap-0.5">
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-6 w-6 opacity-70 hover:opacity-100"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  openRenameDialog(conv.id, conv.title)
                                }}
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-6 w-6 text-destructive opacity-70 hover:opacity-100"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  deleteConversation(conv.id)
                                }}
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </SidebarMenuButton>
                        </SidebarMenuItem>
                      ))}
                    </SidebarMenu>
                  </SidebarGroupContent>
                </SidebarGroup>
              )}
              
              {filteredOlder.length > 0 && (
                <SidebarGroup>
                  <SidebarGroupLabel className="px-3 py-2 text-xs font-medium text-muted-foreground">
                    Older
                  </SidebarGroupLabel>
                  <SidebarGroupContent>
                    <SidebarMenu>
                      {filteredOlder.map((conv) => (
                        <SidebarMenuItem key={conv.id}>
                          <SidebarMenuButton 
                            className="w-full justify-start group"
                            onClick={() => router.push(`/chat/${conv.id}`)}
                          >
                            <MessageSquare className="h-4 w-4 mr-2 text-muted-foreground" />
                            <span className="truncate">{conv.title || "New conversation"}</span>
                            <div className="hidden ml-auto group-hover:flex gap-0.5">
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-6 w-6 opacity-70 hover:opacity-100"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  openRenameDialog(conv.id, conv.title)
                                }}
                              >
                                <Edit className="h-3 w-3" />
                              </Button>
                              <Button 
                                variant="ghost" 
                                size="icon" 
                                className="h-6 w-6 text-destructive opacity-70 hover:opacity-100"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  deleteConversation(conv.id)
                                }}
                              >
                                <Trash2 className="h-3 w-3" />
                              </Button>
                            </div>
                          </SidebarMenuButton>
                        </SidebarMenuItem>
                      ))}
                    </SidebarMenu>
                  </SidebarGroupContent>
                </SidebarGroup>
              )}
              
              {filteredToday.length === 0 && filteredOlder.length === 0 && (
                <div className="px-3 py-10 text-center text-muted-foreground">
                  <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No conversations found</p>
                  {searchQuery && (
                    <p className="text-xs mt-1">Try a different search term</p>
                  )}
                </div>
              )}
            </>
          )}
        </SidebarContent>
        
        <SidebarFooter className="p-3 mt-auto">
          <SidebarSeparator />
          <div className="mt-2">
            <SidebarMenuItem>
              <SidebarMenuButton className="w-full justify-start">
                <User className="h-4 w-4 mr-2 text-muted-foreground" />
                <span>Abhishek Gusain</span>
                <span className="ml-auto text-xs text-muted-foreground">Free</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </div>
        </SidebarFooter>
      </Sidebar>
      
      {/* Rename dialog */}
      <RenameConversationDialog
        isOpen={renameDialog.isOpen}
        onClose={closeRenameDialog}
        conversationId={renameDialog.conversationId}
        currentTitle={renameDialog.title}
      />
    </>
  )
}
  