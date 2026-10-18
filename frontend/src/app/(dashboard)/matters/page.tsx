"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Briefcase,
  Filter,
  Plus,
  Search,
  Users,
  X,
} from "lucide-react";
import { Header } from "@/components/layout/header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Matter } from "@/types";

export default function MattersPage() {
  const [matters, setMatters] = useState<Matter[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isCreateOpen, setIsCreateOpen] = useState(false);

  // New Matter Form State
  const [title, setTitle] = useState("");
  const [caseNumber, setCaseNumber] = useState("");
  const [matterType, setMatterType] = useState("personal_injury");
  const [dateOpened, setDateOpened] = useState(
    new Date().toISOString().split("T")[0]
  );
  const [court, setCourt] = useState("");
  const [creating, setCreating] = useState(false);

  const fetchMatters = () => {
    setLoading(true);
    api
      .getMatters(1, 50, statusFilter, search)
      .then((res) => setMatters(res.items))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMatters();
  }, [statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchMatters();
  };

  const handleCreateMatter = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreating(true);
    try {
      await api.createMatter({
        title,
        case_number: caseNumber || undefined,
        matter_type: matterType,
        date_opened: dateOpened,
        court: court || undefined,
      });
      setIsCreateOpen(false);
      setTitle("");
      setCaseNumber("");
      setCourt("");
      fetchMatters();
    } catch (err: any) {
      alert(err.message || "Failed to create matter");
    } finally {
      setCreating(false);
    }
  };

  return (
    <>
      <Header
        title="Matter Directory"
        subtitle="Manage and access confidential litigation case files"
      />

      <main className="p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Controls Bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <form
            onSubmit={handleSearchSubmit}
            className="relative flex-1 w-full sm:max-w-md"
          >
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
            <Input
              placeholder="Search by case title or docket number..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 bg-white border-slate-200"
            />
          </form>

          <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
            <div className="flex items-center bg-white rounded-lg border border-slate-200 p-1 text-xs">
              {["all", "active", "closed"].map((st) => (
                <button
                  key={st}
                  onClick={() => setStatusFilter(st)}
                  className={`px-3 py-1 rounded-md capitalize font-medium transition-colors ${
                    statusFilter === st
                      ? "bg-slate-900 text-white shadow-sm"
                      : "text-slate-600 hover:text-slate-900"
                  }`}
                >
                  {st}
                </button>
              ))}
            </div>

            <Button
              onClick={() => setIsCreateOpen(true)}
              className="bg-blue-600 hover:bg-blue-500 text-white space-x-1.5 shrink-0"
            >
              <Plus className="h-4 w-4" />
              <span>New Matter</span>
            </Button>
          </div>
        </div>

        {/* Create Matter Modal */}
        {isCreateOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
            <Card className="w-full max-w-lg bg-white border-slate-200 shadow-2xl">
              <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900">
                    Open New Legal Matter
                  </h3>
                  <p className="text-xs text-slate-500">
                    Establishes an isolated AI case workspace
                  </p>
                </div>
                <button
                  onClick={() => setIsCreateOpen(false)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleCreateMatter} className="p-6 space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">
                    Case Title *
                  </label>
                  <Input
                    required
                    placeholder="e.g. Smith v. Acme Corporation"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">
                      Docket / Case Number
                    </label>
                    <Input
                      placeholder="e.g. 2024-CV-10492"
                      value={caseNumber}
                      onChange={(e) => setCaseNumber(e.target.value)}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">
                      Practice Area *
                    </label>
                    <select
                      value={matterType}
                      onChange={(e) => setMatterType(e.target.value)}
                      className="w-full h-9 rounded-md border border-input bg-transparent px-3 text-sm"
                    >
                      <option value="personal_injury">Personal Injury</option>
                      <option value="wage_hour">Wage & Hour</option>
                      <option value="wrongful_death">Wrongful Death</option>
                      <option value="employment">Employment Litigation</option>
                      <option value="lead_paint">Lead Paint Litigation</option>
                      <option value="ada">ADA Litigation</option>
                      <option value="commercial">Commercial / Other</option>
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">
                      Court / Venue
                    </label>
                    <Input
                      placeholder="e.g. Alameda County Superior Court"
                      value={court}
                      onChange={(e) => setCourt(e.target.value)}
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-semibold text-slate-700">
                      Date Opened
                    </label>
                    <Input
                      type="date"
                      value={dateOpened}
                      onChange={(e) => setDateOpened(e.target.value)}
                    />
                  </div>
                </div>

                <div className="pt-4 flex justify-end space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsCreateOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={creating}
                    className="bg-blue-600 hover:bg-blue-500 text-white"
                  >
                    {creating ? "Opening Matter..." : "Create Matter Workspace"}
                  </Button>
                </div>
              </form>
            </Card>
          </div>
        )}

        {/* Matters Directory Table */}
        <Card className="border-slate-200 shadow-sm overflow-hidden bg-white">
          <Table>
            <TableHeader className="bg-slate-50">
              <TableRow>
                <TableHead className="w-36 text-xs font-semibold">Docket #</TableHead>
                <TableHead className="text-xs font-semibold">Matter Name</TableHead>
                <TableHead className="text-xs font-semibold">Practice Area</TableHead>
                <TableHead className="text-xs font-semibold">Status</TableHead>
                <TableHead className="text-xs font-semibold">Team</TableHead>
                <TableHead className="text-xs font-semibold">Opened</TableHead>
                <TableHead className="text-right text-xs font-semibold">Workspace</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-12 text-sm text-slate-400">
                    Loading cases...
                  </TableCell>
                </TableRow>
              ) : matters.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-12 text-sm text-slate-400">
                    No matters matching current query.
                  </TableCell>
                </TableRow>
              ) : (
                matters.map((m) => (
                  <TableRow key={m.id} className="hover:bg-slate-50/80">
                    <TableCell className="font-mono text-xs font-medium text-slate-600">
                      {m.case_number || "—"}
                    </TableCell>
                    <TableCell className="font-semibold text-slate-900">
                      <Link
                        href={`/matters/${m.id}`}
                        className="hover:text-blue-600"
                      >
                        {m.title}
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
                    <TableCell>
                      <div className="flex items-center space-x-1 text-xs text-slate-500">
                        <Users className="h-3.5 w-3.5 text-slate-400" />
                        <span>{m.member_count}</span>
                      </div>
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
                          <span>Open</span>
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
      </main>
    </>
  );
}
