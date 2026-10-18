"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import {
  AlertCircle,
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  Briefcase,
  Calendar,
  CheckCircle2,
  Clock,
  Eye,
  FileSearch,
  FileText,
  Gavel,
  Layers,
  Plus,
  Scale,
  Search,
  Shield,
  Sparkles,
  Upload,
  UserCheck,
  Users,
  X,
} from "lucide-react";
import { Header } from "@/components/layout/header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { api } from "@/lib/api";
import { formatDate, formatDateTime } from "@/lib/utils";
import {
  Claim,
  Deadline,
  DocumentChunk,
  Event,
  Expert,
  LegalDocument,
  MatterDetail,
  MatterMember,
  Party,
  SearchResult,
  Task,
  Witness,
} from "@/types";

export default function MatterWorkspacePage() {
  const params = useParams();
  const matterId = params.matterId as string;

  const [matter, setMatter] = useState<MatterDetail | null>(null);
  const [members, setMembers] = useState<MatterMember[]>([]);
  const [parties, setParties] = useState<Party[]>([]);
  const [witnesses, setWitnesses] = useState<Witness[]>([]);
  const [experts, setExperts] = useState<Expert[]>([]);
  const [events, setEvents] = useState<Event[]>([]);
  const [deadlines, setDeadlines] = useState<Deadline[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [documents, setDocuments] = useState<LegalDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Document UI State
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadType, setUploadType] = useState<string>("");
  const [uploading, setUploading] = useState(false);

  // Document Chunk Inspector State
  const [inspectDoc, setInspectDoc] = useState<LegalDocument | null>(null);
  const [inspectChunks, setInspectChunks] = useState<DocumentChunk[]>([]);
  const [loadingChunks, setLoadingChunks] = useState(false);

  // Hybrid Search State
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const fetchMatterData = () => {
    if (!matterId) return;

    setLoading(true);
    Promise.all([
      api.getMatter(matterId),
      api.getMatterMembers(matterId),
      api.getMatterParties(matterId),
      api.getMatterWitnesses(matterId),
      api.getMatterExperts(matterId),
      api.getMatterEvents(matterId),
      api.getMatterDeadlines(matterId),
      api.getMatterTasks(matterId),
      api.getMatterClaims(matterId),
      api.getMatterDocuments(matterId),
    ])
      .then(
        ([
          matterData,
          membersData,
          partiesData,
          witnessesData,
          expertsData,
          eventsData,
          deadlinesData,
          tasksData,
          claimsData,
          documentsData,
        ]) => {
          setMatter(matterData);
          setMembers(membersData);
          setParties(partiesData);
          setWitnesses(witnessesData);
          setExperts(expertsData);
          setEvents(eventsData);
          setDeadlines(deadlinesData);
          setTasks(tasksData);
          setClaims(claimsData);
          setDocuments(documentsData);
        }
      )
      .catch((err) => {
        console.error(err);
        setError(err.message || "Failed to load matter workspace");
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchMatterData();
  }, [matterId]);

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile) return;

    setUploading(true);
    try {
      await api.uploadDocument(matterId, uploadFile, uploadType || undefined);
      setIsUploadOpen(false);
      setUploadFile(null);
      setUploadType("");
      // Refresh documents
      const docs = await api.getMatterDocuments(matterId);
      setDocuments(docs);
    } catch (err: any) {
      alert(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleInspectDocument = async (doc: LegalDocument) => {
    setInspectDoc(doc);
    setLoadingChunks(true);
    try {
      const chunks = await api.getDocumentChunks(matterId, doc.id);
      setInspectChunks(chunks);
    } catch (err: any) {
      alert("Failed to load document chunks");
    } finally {
      setLoadingChunks(false);
    }
  };

  const handleSearchSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setSearching(true);
    setHasSearched(true);
    try {
      const results = await api.searchMatter(matterId, searchQuery.trim(), 10);
      setSearchResults(results);
    } catch (err: any) {
      alert("Search failed: " + err.message);
    } finally {
      setSearching(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="flex flex-col items-center space-y-3">
          <div className="h-8 w-8 rounded-full border-2 border-blue-600 border-t-transparent animate-spin" />
          <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">
            Loading Matter Intelligence...
          </p>
        </div>
      </div>
    );
  }

  if (error || !matter) {
    return (
      <div className="p-8 max-w-4xl mx-auto space-y-4">
        <div className="p-4 rounded-lg bg-red-50 border border-red-200 text-red-700 flex items-center space-x-3">
          <AlertCircle className="h-5 w-5 shrink-0" />
          <div>
            <h4 className="font-semibold text-sm">Access Restricted</h4>
            <p className="text-xs mt-0.5">{error || "Matter not found."}</p>
          </div>
        </div>
        <Link href="/matters">
          <Button variant="outline" size="sm" className="space-x-1.5">
            <ArrowLeft className="h-4 w-4" />
            <span>Return to Matter Directory</span>
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <>
      <Header
        title={matter.title}
        subtitle={`Docket: ${matter.case_number || "Unassigned"} • ${matter.court || "Jurisdiction Pending"}`}
      />

      <main className="p-8 space-y-6 max-w-7xl mx-auto w-full">
        {/* Navigation Breadcrumb & Isolation Banner */}
        <div className="flex items-center justify-between">
          <Link
            href="/matters"
            className="text-xs text-slate-500 hover:text-slate-900 flex items-center space-x-1"
          >
            <ArrowLeft className="h-3.5 w-3.5" />
            <span>All Matters</span>
          </Link>

          <div className="flex items-center space-x-2 text-xs text-slate-600 bg-white px-3 py-1 rounded-full border border-slate-200 shadow-sm">
            <Shield className="h-3.5 w-3.5 text-emerald-600" />
            <span className="font-medium text-slate-800">
              Isolated Case Boundary
            </span>
            <span className="text-slate-300">•</span>
            <span className="text-slate-500">{matter.id.slice(0, 8)}</span>
          </div>
        </div>

        {/* Matter Hero Card */}
        <Card className="border-slate-200 shadow-sm bg-white">
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="space-y-1.5">
                <div className="flex items-center space-x-3">
                  <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                    {matter.title}
                  </h2>
                  <Badge
                    variant={matter.status === "active" ? "success" : "secondary"}
                    className="capitalize text-xs"
                  >
                    {matter.status}
                  </Badge>
                  <Badge variant="outline" className="text-xs capitalize">
                    {matter.matter_type.replace("_", " ")}
                  </Badge>
                </div>
                {matter.description && (
                  <p className="text-xs text-slate-600 max-w-3xl leading-relaxed">
                    {matter.description}
                  </p>
                )}
              </div>

              <div className="flex items-center space-x-2 shrink-0">
                <Button
                  onClick={() => setIsUploadOpen(true)}
                  size="sm"
                  className="bg-blue-600 hover:bg-blue-500 text-white space-x-1.5"
                >
                  <Upload className="h-4 w-4" />
                  <span>Upload Evidence</span>
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled
                  className="space-x-1.5 opacity-60 cursor-not-allowed"
                >
                  <Sparkles className="h-4 w-4 text-purple-600" />
                  <span>Matter Q&A (Phase 3)</span>
                </Button>
              </div>
            </div>

            {/* Quick Metadata Strip */}
            <div className="mt-6 pt-4 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-slate-400 block font-medium">Court</span>
                <span className="font-semibold text-slate-800 mt-0.5 block truncate">
                  {matter.court || "—"}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Presiding Judge</span>
                <span className="font-semibold text-slate-800 mt-0.5 block truncate">
                  {matter.judge || "—"}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Date Opened</span>
                <span className="font-semibold text-slate-800 mt-0.5 block">
                  {formatDate(matter.date_opened)}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block font-medium">Lead Counsel</span>
                <span className="font-semibold text-slate-800 mt-0.5 block truncate">
                  {matter.created_by?.full_name || "Assigned Partner"}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Upload Document Modal */}
        {isUploadOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
            <Card className="w-full max-w-lg bg-white border-slate-200 shadow-2xl">
              <div className="p-6 border-b border-slate-100 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900">
                    Ingest Case Document / Evidence
                  </h3>
                  <p className="text-xs text-slate-500">
                    Auto-extracts text, classifies document, and generates semantic chunks
                  </p>
                </div>
                <button
                  onClick={() => setIsUploadOpen(false)}
                  className="text-slate-400 hover:text-slate-600"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <form onSubmit={handleUploadSubmit} className="p-6 space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">
                    Select File (PDF, DOCX, TXT, CSV, Image) *
                  </label>
                  <Input
                    type="file"
                    required
                    onChange={(e) =>
                      setUploadFile(e.target.files ? e.target.files[0] : null)
                    }
                    className="cursor-pointer file:cursor-pointer"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-700">
                    Document Type Override (Optional)
                  </label>
                  <select
                    value={uploadType}
                    onChange={(e) => setUploadType(e.target.value)}
                    className="w-full h-9 rounded-md border border-input bg-transparent px-3 text-sm"
                  >
                    <option value="">Auto-Detect via AI Classifier</option>
                    <option value="complaint">Complaint / Pleading</option>
                    <option value="answer">Answer / Defenses</option>
                    <option value="motion">Motion</option>
                    <option value="discovery_request">Discovery Request</option>
                    <option value="discovery_response">Discovery Response</option>
                    <option value="deposition">Deposition Transcript</option>
                    <option value="medical_record">Medical Record</option>
                    <option value="expert_report">Expert Report</option>
                    <option value="court_order">Court Order</option>
                    <option value="exhibit">Exhibit</option>
                    <option value="correspondence">Correspondence / Email</option>
                  </select>
                </div>

                <div className="pt-4 flex justify-end space-x-2">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsUploadOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={uploading || !uploadFile}
                    className="bg-blue-600 hover:bg-blue-500 text-white"
                  >
                    {uploading ? "Extracting & Indexing..." : "Upload & Process"}
                  </Button>
                </div>
              </form>
            </Card>
          </div>
        )}

        {/* Document Chunk Inspector Drawer */}
        {inspectDoc && (
          <div className="fixed inset-0 z-50 bg-black/50 flex justify-end">
            <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col">
              <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50">
                <div>
                  <h3 className="font-semibold text-slate-900 text-sm">
                    Document Knowledge Inspector
                  </h3>
                  <p className="text-xs text-slate-500 truncate max-w-md">
                    {inspectDoc.title} ({inspectDoc.file_name})
                  </p>
                </div>
                <button
                  onClick={() => setInspectDoc(null)}
                  className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="p-4 border-b border-slate-100 bg-white grid grid-cols-3 gap-2 text-xs">
                <div>
                  <span className="text-slate-400 block">Classified As</span>
                  <Badge variant="outline" className="capitalize mt-0.5 text-[10px]">
                    {inspectDoc.document_type}
                  </Badge>
                </div>
                <div>
                  <span className="text-slate-400 block">File Size</span>
                  <span className="font-medium text-slate-800">
                    {(inspectDoc.file_size / 1024).toFixed(1)} KB
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block">Chunks Indexed</span>
                  <span className="font-medium text-slate-800">
                    {inspectChunks.length} segments
                  </span>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {loadingChunks ? (
                  <div className="text-center py-12 text-xs text-slate-400">
                    Loading segmented chunks...
                  </div>
                ) : inspectChunks.length === 0 ? (
                  <div className="text-center py-12 text-xs text-slate-400">
                    No text chunks indexed for this document.
                  </div>
                ) : (
                  inspectChunks.map((c) => (
                    <div
                      key={c.id}
                      className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2 text-xs"
                    >
                      <div className="flex items-center justify-between text-[11px] text-slate-500 font-medium">
                        <span className="font-mono bg-slate-200 px-1.5 py-0.5 rounded">
                          Chunk #{c.chunk_index + 1}
                        </span>
                        <div className="flex items-center space-x-2">
                          {c.page_number && (
                            <span className="bg-blue-50 text-blue-700 px-1.5 py-0.5 rounded border border-blue-200">
                              Page {c.page_number}
                            </span>
                          )}
                          <span>{c.token_count || "~"} tokens</span>
                        </div>
                      </div>
                      <p className="text-slate-800 font-sans leading-relaxed whitespace-pre-wrap">
                        {c.content}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {/* Tabbed Case Intelligence Modules */}
        <Tabs defaultValue="documents" className="space-y-4">
          <TabsList className="bg-white border border-slate-200 p-1 rounded-lg">
            <TabsTrigger value="documents" className="text-xs font-medium">
              Evidence & Documents ({documents.length})
            </TabsTrigger>
            <TabsTrigger value="search" className="text-xs font-medium">
              Case Knowledge Search
            </TabsTrigger>
            <TabsTrigger value="overview" className="text-xs font-medium">
              Case Overview
            </TabsTrigger>
            <TabsTrigger value="parties" className="text-xs font-medium">
              Parties ({parties.length})
            </TabsTrigger>
            <TabsTrigger value="witnesses" className="text-xs font-medium">
              Witnesses & Experts ({witnesses.length + experts.length})
            </TabsTrigger>
            <TabsTrigger value="timeline" className="text-xs font-medium">
              Timeline ({events.length})
            </TabsTrigger>
            <TabsTrigger value="deadlines" className="text-xs font-medium">
              Deadlines ({deadlines.length})
            </TabsTrigger>
            <TabsTrigger value="tasks" className="text-xs font-medium">
              Tasks ({tasks.length})
            </TabsTrigger>
            <TabsTrigger value="claims" className="text-xs font-medium">
              Causes of Action ({claims.length})
            </TabsTrigger>
          </TabsList>

          {/* 1. DOCUMENTS & EVIDENCE TAB (PHASE 2 CORE) */}
          <TabsContent value="documents" className="space-y-4">
            <Card className="border-slate-200 bg-white">
              <Table>
                <TableHeader className="bg-slate-50">
                  <TableRow>
                    <TableHead className="text-xs font-semibold">Document Title</TableHead>
                    <TableHead className="text-xs font-semibold">Classification</TableHead>
                    <TableHead className="text-xs font-semibold">Source File</TableHead>
                    <TableHead className="text-xs font-semibold">Size</TableHead>
                    <TableHead className="text-xs font-semibold">Status</TableHead>
                    <TableHead className="text-xs font-semibold">Uploaded</TableHead>
                    <TableHead className="text-right text-xs font-semibold">Inspector</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {documents.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-12 text-xs text-slate-400">
                        No documents uploaded to this matter yet. Click "Upload Evidence" to ingest records.
                      </TableCell>
                    </TableRow>
                  ) : (
                    documents.map((doc) => (
                      <TableRow key={doc.id} className="hover:bg-slate-50/80">
                        <TableCell className="font-semibold text-xs text-slate-900">
                          {doc.title}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-[10px] capitalize">
                            {doc.document_type.replace("_", " ")}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-slate-500 font-mono">
                          {doc.file_name}
                        </TableCell>
                        <TableCell className="text-xs text-slate-500">
                          {(doc.file_size / 1024).toFixed(1)} KB
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={doc.status === "ready" ? "success" : "secondary"}
                            className="text-[10px] capitalize"
                          >
                            {doc.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-slate-500">
                          {formatDate(doc.created_at)}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleInspectDocument(doc)}
                            className="text-blue-600 hover:text-blue-700 hover:bg-blue-50 text-xs space-x-1"
                          >
                            <Layers className="h-3.5 w-3.5" />
                            <span>Chunks</span>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          </TabsContent>

          {/* 2. CASE KNOWLEDGE SEARCH TAB (HYBRID RETRIEVAL) */}
          <TabsContent value="search" className="space-y-4">
            <Card className="border-slate-200 p-6 bg-white space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">
                  Permission-Aware Case Retrieval
                </h3>
                <p className="text-xs text-slate-500">
                  Searches all chunks strictly isolated within this matter using hybrid semantic vectors + keyword ranking.
                </p>
              </div>

              <form onSubmit={handleSearchSubmit} className="flex gap-2">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-400" />
                  <Input
                    placeholder="Search testimony, exhibits, injuries, prior notice..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 bg-slate-50 border-slate-200"
                  />
                </div>
                <Button
                  type="submit"
                  disabled={searching || !searchQuery.trim()}
                  className="bg-blue-600 hover:bg-blue-500 text-white shrink-0"
                >
                  {searching ? "Retrieving..." : "Search Case Knowledge"}
                </Button>
              </form>

              {/* Results Display */}
              <div className="space-y-3">
                {hasSearched && searchResults.length === 0 && !searching && (
                  <div className="p-8 text-center text-xs text-slate-400">
                    No relevant passages found in this matter's documents matching your query.
                  </div>
                )}

                {searchResults.map((r) => (
                  <div
                    key={r.chunk_id}
                    className="p-4 rounded-lg border border-slate-200 bg-slate-50/50 space-y-2 text-xs hover:border-slate-300 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="font-semibold text-slate-900">
                          {r.document_title}
                        </span>
                        {r.page_number && (
                          <Badge variant="outline" className="text-[10px]">
                            Page {r.page_number}
                          </Badge>
                        )}
                        <Badge
                          variant="secondary"
                          className="text-[10px] capitalize text-slate-600"
                        >
                          {r.match_type}
                        </Badge>
                      </div>
                      <span className="text-[11px] font-mono text-emerald-600 font-semibold">
                        {(r.score * 100).toFixed(1)}% Relevance
                      </span>
                    </div>

                    <p className="text-slate-700 leading-relaxed font-sans bg-white p-3 rounded border border-slate-100">
                      "{r.content}"
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          </TabsContent>

          {/* 3. OVERVIEW TAB */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="md:col-span-2 space-y-4">
                <Card className="border-slate-200">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold text-slate-900">
                      Litigation Synopsis & Theory
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="text-xs text-slate-700 leading-relaxed">
                    {matter.description ||
                      "No synopsis currently entered for this case."}
                  </CardContent>
                </Card>

                <Card className="border-slate-200">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold text-slate-900">
                      Active Causes of Action
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {claims.length === 0 ? (
                      <p className="text-xs text-slate-400">No claims filed yet.</p>
                    ) : (
                      claims.map((c) => (
                        <div
                          key={c.id}
                          className="p-3 rounded-lg border border-slate-100 bg-slate-50/50 flex items-start justify-between"
                        >
                          <div>
                            <span className="font-semibold text-xs text-slate-900">
                              {c.title}
                            </span>
                            <p className="text-xs text-slate-600 mt-0.5">
                              {c.description}
                            </p>
                          </div>
                          <Badge variant="outline" className="text-[10px] capitalize">
                            {c.status}
                          </Badge>
                        </div>
                      ))
                    )}
                  </CardContent>
                </Card>
              </div>

              {/* Team Members */}
              <div className="space-y-4">
                <Card className="border-slate-200">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm font-semibold text-slate-900 flex items-center justify-between">
                      <span>Case Legal Team</span>
                      <Users className="h-4 w-4 text-slate-400" />
                    </CardTitle>
                    <CardDescription className="text-xs">
                      Authorized attorneys & staff
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-2.5">
                    {members.map((m) => (
                      <div
                        key={m.id}
                        className="flex items-center justify-between p-2 rounded-lg bg-slate-50 border border-slate-100"
                      >
                        <div className="min-w-0">
                          <span className="text-xs font-semibold text-slate-900 block truncate">
                            {m.user?.full_name}
                          </span>
                          <span className="text-[10px] text-slate-500 block truncate">
                            {m.user?.email}
                          </span>
                        </div>
                        <Badge
                          variant="secondary"
                          className="text-[10px] capitalize shrink-0"
                        >
                          {m.role.replace("_", " ")}
                        </Badge>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* 4. PARTIES TAB */}
          <TabsContent value="parties">
            <Card className="border-slate-200">
              <Table>
                <TableHeader className="bg-slate-50">
                  <TableRow>
                    <TableHead className="text-xs font-semibold">Party Name</TableHead>
                    <TableHead className="text-xs font-semibold">Designation</TableHead>
                    <TableHead className="text-xs font-semibold">Entity Type</TableHead>
                    <TableHead className="text-xs font-semibold">Description & Notes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {parties.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-xs text-slate-400">
                        No parties entered.
                      </TableCell>
                    </TableRow>
                  ) : (
                    parties.map((p) => (
                      <TableRow key={p.id}>
                        <TableCell className="font-semibold text-xs text-slate-900">
                          {p.name}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-[10px] capitalize">
                            {p.party_type}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs capitalize text-slate-600">
                          {p.entity_type}
                        </TableCell>
                        <TableCell className="text-xs text-slate-600">
                          {p.description || "—"}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          </TabsContent>

          {/* 5. WITNESSES & EXPERTS TAB */}
          <TabsContent value="witnesses" className="space-y-6">
            <Card className="border-slate-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-slate-900">
                  Fact Witnesses & Interviewees
                </CardTitle>
              </CardHeader>
              <Table>
                <TableHeader className="bg-slate-50">
                  <TableRow>
                    <TableHead className="text-xs font-semibold">Name</TableHead>
                    <TableHead className="text-xs font-semibold">Role</TableHead>
                    <TableHead className="text-xs font-semibold">Observations & Notes</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {witnesses.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={3} className="text-center py-6 text-xs text-slate-400">
                        No witnesses logged yet.
                      </TableCell>
                    </TableRow>
                  ) : (
                    witnesses.map((w) => (
                      <TableRow key={w.id}>
                        <TableCell className="font-semibold text-xs text-slate-900">
                          {w.name}
                        </TableCell>
                        <TableCell className="text-xs capitalize text-slate-600">
                          {w.witness_type} Witness
                        </TableCell>
                        <TableCell className="text-xs text-slate-600">
                          {w.notes || w.description || "—"}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>

            <Card className="border-slate-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-slate-900">
                  Expert Witnesses & Specialists
                </CardTitle>
              </CardHeader>
              <Table>
                <TableHeader className="bg-slate-50">
                  <TableRow>
                    <TableHead className="text-xs font-semibold">Expert Name</TableHead>
                    <TableHead className="text-xs font-semibold">Specialty</TableHead>
                    <TableHead className="text-xs font-semibold">Affiliation</TableHead>
                    <TableHead className="text-xs font-semibold">Retained By</TableHead>
                    <TableHead className="text-xs font-semibold">Scope of Opinion</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {experts.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-6 text-xs text-slate-400">
                        No expert witnesses designated.
                      </TableCell>
                    </TableRow>
                  ) : (
                    experts.map((exp) => (
                      <TableRow key={exp.id}>
                        <TableCell className="font-semibold text-xs text-slate-900">
                          {exp.name}
                        </TableCell>
                        <TableCell className="text-xs text-slate-700">
                          {exp.specialty}
                        </TableCell>
                        <TableCell className="text-xs text-slate-600">
                          {exp.organization_name || "—"}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-[10px] capitalize">
                            {exp.retained_by}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-slate-600">
                          {exp.notes || "—"}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          </TabsContent>

          {/* 6. TIMELINE TAB */}
          <TabsContent value="timeline">
            <Card className="border-slate-200 p-6">
              <div className="relative border-l border-slate-200 ml-4 space-y-6">
                {events.length === 0 ? (
                  <p className="text-xs text-slate-400 pl-4">
                    No timeline events currently registered.
                  </p>
                ) : (
                  events.map((ev) => (
                    <div key={ev.id} className="relative pl-6">
                      <div className="absolute -left-1.5 top-1.5 h-3 w-3 rounded-full border-2 border-white bg-blue-600 shadow" />
                      <div className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-bold text-slate-900">
                            {formatDateTime(ev.event_date)}
                          </span>
                          <Badge variant="secondary" className="text-[10px] capitalize">
                            {ev.event_type}
                          </Badge>
                        </div>
                        <h4 className="text-xs font-semibold text-slate-800">
                          {ev.title}
                        </h4>
                        {ev.description && (
                          <p className="text-xs text-slate-600 leading-relaxed">
                            {ev.description}
                          </p>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </TabsContent>

          {/* 7. DEADLINES TAB */}
          <TabsContent value="deadlines">
            <Card className="border-slate-200">
              <Table>
                <TableHeader className="bg-slate-50">
                  <TableRow>
                    <TableHead className="text-xs font-semibold">Due Date</TableHead>
                    <TableHead className="text-xs font-semibold">Deadline Title</TableHead>
                    <TableHead className="text-xs font-semibold">Type</TableHead>
                    <TableHead className="text-xs font-semibold">Risk Level</TableHead>
                    <TableHead className="text-xs font-semibold">Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {deadlines.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={5} className="text-center py-8 text-xs text-slate-400">
                        No pending deadlines.
                      </TableCell>
                    </TableRow>
                  ) : (
                    deadlines.map((d) => (
                      <TableRow key={d.id}>
                        <TableCell className="font-semibold text-xs text-slate-900">
                          {formatDateTime(d.due_date)}
                        </TableCell>
                        <TableCell className="text-xs font-medium text-slate-800">
                          {d.title}
                        </TableCell>
                        <TableCell className="text-xs capitalize text-slate-600">
                          {d.deadline_type}
                        </TableCell>
                        <TableCell>
                          {d.is_high_risk ? (
                            <Badge variant="destructive" className="text-[10px]">
                              High Risk (Statutory)
                            </Badge>
                          ) : (
                            <Badge variant="outline" className="text-[10px]">
                              Standard
                            </Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-[10px] capitalize">
                            {d.status}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          </TabsContent>

          {/* 8. TASKS TAB */}
          <TabsContent value="tasks">
            <Card className="border-slate-200">
              <Table>
                <TableHeader className="bg-slate-50">
                  <TableRow>
                    <TableHead className="text-xs font-semibold">Task</TableHead>
                    <TableHead className="text-xs font-semibold">Priority</TableHead>
                    <TableHead className="text-xs font-semibold">Status</TableHead>
                    <TableHead className="text-xs font-semibold">Due Date</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tasks.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-xs text-slate-400">
                        No assigned tasks.
                      </TableCell>
                    </TableRow>
                  ) : (
                    tasks.map((t) => (
                      <TableRow key={t.id}>
                        <TableCell className="font-medium text-xs text-slate-900">
                          <div>
                            <span>{t.title}</span>
                            {t.description && (
                              <p className="text-[11px] text-slate-500 mt-0.5">
                                {t.description}
                              </p>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge
                            variant={
                              t.priority === "urgent"
                                ? "destructive"
                                : t.priority === "high"
                                ? "warning"
                                : "outline"
                            }
                            className="text-[10px] capitalize"
                          >
                            {t.priority}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-[10px] capitalize">
                            {t.status.replace("_", " ")}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-slate-500">
                          {formatDateTime(t.due_date)}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          </TabsContent>

          {/* 9. CLAIMS TAB */}
          <TabsContent value="claims">
            <Card className="border-slate-200">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-slate-900">
                  Claims & Legal Theories
                </CardTitle>
                <CardDescription className="text-xs">
                  Causes of action asserted in current pleadings
                </CardDescription>
              </CardHeader>
              <Table>
                <TableHeader className="bg-slate-50">
                  <TableRow>
                    <TableHead className="text-xs font-semibold">Cause of Action</TableHead>
                    <TableHead className="text-xs font-semibold">Classification</TableHead>
                    <TableHead className="text-xs font-semibold">Status</TableHead>
                    <TableHead className="text-xs font-semibold">Factual & Legal Grounds</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {claims.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={4} className="text-center py-8 text-xs text-slate-400">
                        No causes of action entered.
                      </TableCell>
                    </TableRow>
                  ) : (
                    claims.map((c) => (
                      <TableRow key={c.id}>
                        <TableCell className="font-semibold text-xs text-slate-900">
                          {c.title}
                        </TableCell>
                        <TableCell className="text-xs text-slate-600 capitalize">
                          {c.claim_type.replace("_", " ")}
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="text-[10px] capitalize">
                            {c.status}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-xs text-slate-600 leading-relaxed">
                          {c.description}
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </>
  );
}
