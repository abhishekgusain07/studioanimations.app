"use client"

import React from "react"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

interface DeleteConversationDialogProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  isDeleting: boolean
}

const dialogContentStyle = {
  backgroundColor: "white",
  maxWidth: "500px",
  width: "100%"
}

const titleStyle = {
  fontSize: "1.5rem",
  fontWeight: "600",
  color: "#000"
}

const descriptionStyle = {
  color: "#374151",
  marginTop: "8px"
}

const cancelButtonStyle = {
  backgroundColor: "transparent",
  border: "1px solid #d1d5db",
  color: "#374151"
}

const deleteButtonStyle = {
  backgroundColor: "#ef4444",
  color: "white"
}

const deleteButtonHoverStyle = {
  backgroundColor: "#dc2626"
}

export function DeleteConversationDialog({
  isOpen,
  onClose,
  onConfirm,
  title,
  isDeleting
}: DeleteConversationDialogProps) {
  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent style={dialogContentStyle}>
        <DialogHeader>
          <DialogTitle style={titleStyle}>Delete Thread</DialogTitle>
          <DialogDescription style={descriptionStyle}>
            Are you sure you want to delete "{title}"? This action cannot be undone.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter style={{ marginTop: "16px", display: "flex", justifyContent: "flex-end", gap: "8px" }}>
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isDeleting}
            style={cancelButtonStyle}
          >
            Cancel
          </Button>
          <Button 
            type="button" 
            variant="destructive"
            onClick={onConfirm}
            disabled={isDeleting}
            style={isDeleting ? { ...deleteButtonStyle, opacity: 0.7 } : deleteButtonStyle}
            onMouseOver={(e) => {
              if (!isDeleting) {
                e.currentTarget.style.backgroundColor = deleteButtonHoverStyle.backgroundColor;
              }
            }}
            onMouseOut={(e) => {
              if (!isDeleting) {
                e.currentTarget.style.backgroundColor = deleteButtonStyle.backgroundColor;
              }
            }}
          >
            {isDeleting ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
} 