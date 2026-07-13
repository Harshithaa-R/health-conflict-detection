
"use client";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarRail,
  useSidebar,
} from "@/components/ui/sidebar";
import { 
  LayoutDashboard, 
  AlertCircle, 
  BarChart3, 
  Settings, 
  Database,
  History,
  ShieldCheck,
  LogOut,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { ThemeToggle } from "./ThemeToggle";
import { cn } from "@/lib/utils";

const menuItems = [
  { title: "Dashboard", icon: LayoutDashboard, path: "/" },
  { title: "Conflict Queue", icon: AlertCircle, path: "/conflicts", badge: 4 },
  { title: "Source Reliability", icon: ShieldCheck, path: "/sources" },
  { title: "Analytics", icon: BarChart3, path: "/analytics" },
  { title: "Audit Trail", icon: History, path: "/history" },
];

export function AppSidebar() {
  const pathname = usePathname();
  const { state, toggleSidebar } = useSidebar();
  const user = {
    displayName: "District Health Officer",
    isAnonymous: false
  };
  const router = useRouter();
  const handleSignOut = () => {
    router.push("/login");
  };

  return (
    <Sidebar variant="sidebar" collapsible="icon" className="border-r border-border bg-sidebar shadow-xl">
      <SidebarHeader className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div className={cn("flex items-center gap-3 transition-all", state === "collapsed" && "hidden")}>
            <div className="bg-primary p-2 rounded-lg text-white">
              <Database size={24} />
            </div>
            <div>
              <h1 className="font-headline font-bold text-lg text-primary leading-tight">HealthSync</h1>
              <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Karnataka Hub</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={toggleSidebar} className="h-8 w-8 rounded-lg">
            {state === "expanded" ? <ChevronLeft size={16} /> : <ChevronRight size={16} className="mx-auto" />}
          </Button>
        </div>
      </SidebarHeader>
      
      <SidebarContent className="px-3 py-6">
        <SidebarGroup>
          <SidebarGroupLabel className={cn("px-4 text-[10px] font-bold text-muted-foreground uppercase tracking-widest mb-2", state === "collapsed" && "hidden")}>
            Main Navigation
          </SidebarGroupLabel>
          <SidebarMenu>
            {menuItems.map((item) => (
              <SidebarMenuItem key={item.path}>
                <SidebarMenuButton 
                  asChild 
                  isActive={pathname === item.path}
                  tooltip={item.title}
                  className="px-4 py-6 transition-all duration-200"
                >
                  <Link href={item.path} className="flex items-center w-full gap-3">
                    <item.icon className={pathname === item.path ? "text-primary" : "text-muted-foreground"} size={20} />
                    <span className={cn("font-medium transition-opacity", state === "collapsed" && "opacity-0 w-0")}>{item.title}</span>
                    {item.badge && state === "expanded" && (
                      <span className="ml-auto bg-destructive text-destructive-foreground text-[10px] px-2 py-0.5 rounded-full font-bold">
                        {item.badge}
                      </span>
                    )}
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-4 border-t border-border/50">
        <div className="flex items-center justify-between mb-4 px-2">
           <ThemeToggle />
           <Button variant="ghost" size="icon" onClick={handleSignOut} className="rounded-xl h-10 w-10 text-muted-foreground hover:text-destructive">
             <LogOut size={18} />
           </Button>
        </div>
        <div className={cn("flex items-center gap-3 p-2 bg-muted/30 rounded-xl transition-all overflow-hidden", state === "collapsed" && "p-0 bg-transparent justify-center")}>
          <Avatar className="h-10 w-10 border-2 border-primary/20 shrink-0">
            <AvatarImage src={user?.photoURL || "https://picsum.photos/seed/user1/100/100"} />
            <AvatarFallback>{user?.displayName?.substring(0, 2) || "US"}</AvatarFallback>
          </Avatar>
          <div className={cn("flex-1 overflow-hidden transition-all", state === "collapsed" && "w-0 hidden")}>
            <p className="text-sm font-bold truncate">{user?.displayName || "Supervisor User"}</p>
            <p className="text-xs text-muted-foreground truncate">{user?.isAnonymous ? "Guest Session" : "District Lead"}</p>
          </div>
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
