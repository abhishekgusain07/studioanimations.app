import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarHeader,
    SidebarTrigger,
  } from "@/components/ui/sidebar"
  
  export function AppSidebar() {
    return (
      <>
        <SidebarTrigger className="fixed top-4 left-4 z-50" />
        <Sidebar>
          <SidebarHeader />
          <SidebarContent>
            <SidebarGroup />
            <SidebarGroup />
          </SidebarContent>
          <SidebarFooter />
        </Sidebar>
      </>
    )
  }
  