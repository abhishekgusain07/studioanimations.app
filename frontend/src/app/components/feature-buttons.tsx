import React from 'react'
import { Search, Code, BookOpen, Sparkles, Globe, Shield } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function FeatureButtons() {
  const features = [
    { icon: <Search className="w-4 h-4 mr-2" />, label: 'Search', action: () => console.log('Search') },
    { icon: <Code className="w-4 h-4 mr-2" />, label: 'Code', action: () => console.log('Code') },
    { icon: <BookOpen className="w-4 h-4 mr-2" />, label: 'Learn', action: () => console.log('Learn') },
    { icon: <Sparkles className="w-4 h-4 mr-2" />, label: 'Create', action: () => console.log('Create') },
    { icon: <Globe className="w-4 h-4 mr-2" />, label: 'Explore', action: () => console.log('Explore') },
  ]

  return (
    <div className="flex flex-wrap justify-center gap-3">
      {features.map((feature, index) => (
        <Button
          key={index}
          variant="outline"
          size="sm"
          className="bg-background hover:bg-muted transition-colors rounded-full text-sm font-medium"
          onClick={feature.action}
        >
          {feature.icon}
          {feature.label}
        </Button>
      ))}
    </div>
  )
} 