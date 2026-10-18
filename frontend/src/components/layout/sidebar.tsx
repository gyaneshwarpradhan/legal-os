"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Briefcase,
  FileText,
  Home,
  LogOut,
  Scale,
  Shield,
  Sparkles,
  Users,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const navItems = [
    {
      name: "Dashboard",
      href: "/",
      icon: Home,
      active: pathname === "/",
    },
    {
      name: "Matters",
      href: "/matters",
      icon: Briefcase,
      active: pathname.startsWith("/matters"),
    },
    {
      name: "Documents",
      href: "#",
      icon: FileText,
      badge: "Phase 2",
      disabled: true,
    },
    {
      name: "Matter AI",
      href: "#",
      icon: Sparkles,
      badge: "Phase 3",
      disabled: true,
    },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-200 flex flex-col h-screen border-r border-slate-800 shrink-0">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800 flex items-center space-x-3">
        <div className="h-9 w-9 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-md">
          <Scale className="h-5 w-5" />
        </div>
        <div>
          <div className="font-semibold text-white tracking-wide text-sm">
            LEGAL OS
          </div>
          <div className="text-[11px] text-slate-400">Litigation Second Brain</div>
        </div>
      </div>

      {/* Nav List */}
      <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-1.5 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
          Workspace
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          if (item.disabled) {
            return (
              <div
                key={item.name}
                className="flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium text-slate-500 cursor-not-allowed opacity-60"
              >
                <div className="flex items-center space-x-3">
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <Badge variant="outline" className="text-[10px] py-0 px-1.5 border-slate-700 text-slate-400">
                    {item.badge}
                  </Badge>
                )}
              </div>
            );
          }

          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center justify-between px-3 py-2 rounded-md text-sm font-medium transition-colors",
                item.active
                  ? "bg-blue-600 text-white"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              )}
            >
              <div className="flex items-center space-x-3">
                <Icon className="h-4 w-4" />
                <span>{item.name}</span>
              </div>
            </Link>
          );
        })}
      </div>

      {/* Security & Matter Isolation Notice */}
      <div className="p-3 mx-3 mb-3 rounded-lg bg-slate-800/60 border border-slate-700/60 text-[11px] text-slate-400 flex items-start space-x-2">
        <Shield className="h-4 w-4 text-emerald-400 shrink-0 mt-0.5" />
        <div>
          <span className="font-medium text-slate-300">Matter Isolation</span>
          <p className="mt-0.5 text-[10px]">Strict tenant and matter-boundary access control enabled.</p>
        </div>
      </div>

      {/* User & Logout Footer */}
      <div className="p-4 border-t border-slate-800 flex items-center justify-between">
        <div className="flex flex-col min-w-0">
          <span className="text-xs font-medium text-white truncate">
            {user?.full_name || "User"}
          </span>
          <span className="text-[11px] text-slate-400 truncate capitalize">
            {user?.role?.replace("_", " ") || "Attorney"}
          </span>
        </div>
        <button
          onClick={logout}
          title="Sign out"
          className="p-1.5 text-slate-400 hover:text-white rounded-md hover:bg-slate-800 transition-colors"
        >
          <LogOut className="h-4 w-4" />
        </button>
      </div>
    </aside>
  );
}
