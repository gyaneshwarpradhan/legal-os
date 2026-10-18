"use client";

import React from "react";
import { ShieldCheck } from "lucide-react";

interface HeaderProps {
  title?: string;
  subtitle?: string;
}

export function Header({ title = "Litigation Operating System", subtitle }: HeaderProps) {
  const today = new Date().toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "short",
    day: "numeric",
  });

  return (
    <header className="h-16 border-b border-border bg-white px-8 flex items-center justify-between shrink-0">
      <div>
        <h1 className="text-lg font-semibold text-slate-900 tracking-tight">
          {title}
        </h1>
        {subtitle && (
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        )}
      </div>

      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5 text-xs text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
          <ShieldCheck className="h-3.5 w-3.5" />
          <span className="font-medium">RBAC Active</span>
        </div>
        <div className="text-xs text-muted-foreground">{today}</div>
      </div>
    </header>
  );
}
