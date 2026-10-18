"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  Briefcase,
  Calendar,
  CheckCircle2,
  Clock,
  Plus,
  Scale,
  Shield,
  Users,
} from "lucide-react";
import { Header } from "@/components/layout/header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import { formatDate } from "@/lib/utils";
import { Matter } from "@/types";

export default function DashboardPage() {
  const { user } = useAuth();
  const [matters, setMatters] = useState<Matter[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .getMatters(1, 5)
      .then((res) => {
        setMatters(res.items);
      })
      .catch((err) => console.error("Failed to load matters", err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <Header
        title="Litigation Command Center"
        subtitle={`Welcome back, ${user?.full_name || "Counselor"}`}
      />

      <main className="p-8 space-y-8 max-w-7xl mx-auto w-full">
        {/* KPI Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Active Matters
              </CardTitle>
              <Briefcase className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">
                {loading ? "—" : matters.length}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Authorized case workspaces
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Court Deadlines
              </CardTitle>
              <Calendar className="h-4 w-4 text-amber-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">2</div>
              <p className="text-xs text-amber-600 font-medium mt-1">
                Upcoming within 60 days
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Discovery Tasks
              </CardTitle>
              <Clock className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-slate-900">2</div>
              <p className="text-xs text-muted-foreground mt-1">
                Assigned action items
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
              <CardTitle className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                Matter Isolation
              </CardTitle>
              <Shield className="h-4 w-4 text-emerald-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-emerald-600">Enforced</div>
              <p className="text-xs text-muted-foreground mt-1">
                Zero cross-case leakage
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Matters Table & Quick Action */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-semibold text-slate-900">
                Authorized Matters
              </h2>
              <p className="text-xs text-slate-500">
                You have active attorney access to the following legal cases
              </p>
            </div>
            <Link href="/matters">
              <Button size="sm" className="bg-blue-600 hover:bg-blue-500 text-white space-x-1.5">
                <Plus className="h-4 w-4" />
                <span>Matter Directory</span>
              </Button>
            </Link>
          </div>

          <Card className="border-slate-200 shadow-sm overflow-hidden">
            <Table>
              <TableHeader className="bg-slate-50">
                <TableRow>
                  <TableHead className="w-32 text-xs font-semibold">Case Number</TableHead>
                  <TableHead className="text-xs font-semibold">Case Title</TableHead>
                  <TableHead className="text-xs font-semibold">Practice Area</TableHead>
                  <TableHead className="text-xs font-semibold">Status</TableHead>
                  <TableHead className="text-xs font-semibold">Opened</TableHead>
                  <TableHead className="text-right text-xs font-semibold">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-sm text-slate-400">
                      Loading authorized matters...
                    </TableCell>
                  </TableRow>
                ) : matters.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-sm text-slate-400">
                      No matters currently assigned to your profile.
                    </TableCell>
                  </TableRow>
                ) : (
                  matters.map((m) => (
                    <TableRow key={m.id} className="hover:bg-slate-50/80">
                      <TableCell className="font-mono text-xs font-medium text-slate-600">
                        {m.case_number || "Unassigned"}
                      </TableCell>
                      <TableCell className="font-semibold text-slate-900">
                        <Link
                          href={`/matters/${m.id}`}
                          className="hover:text-blue-600 flex items-center space-x-1.5"
                        >
                          <span>{m.title}</span>
                        </Link>
                      </TableCell>
                      <TableCell className="text-xs capitalize text-slate-600">
                        {m.matter_type.replace("_", " ")}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={m.status === "active" ? "success" : "secondary"}
                          className="text-[11px] capitalize"
                        >
                          {m.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-xs text-slate-500">
                        {formatDate(m.date_opened)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Link href={`/matters/${m.id}`}>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 text-xs"
                          >
                            <span>Open Workspace</span>
                            <ArrowRight className="h-3 w-3 ml-1" />
                          </Button>
                        </Link>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </div>
      </main>
    </>
  );
}
