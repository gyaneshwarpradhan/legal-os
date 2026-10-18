import {
  Claim,
  Deadline,
  DocumentChunk,
  Event,
  Expert,
  LegalDocument,
  LoginResponse,
  Matter,
  MatterDetail,
  MatterMember,
  PaginatedResponse,
  Party,
  SearchResult,
  Task,
  User,
  Witness,
} from "@/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

class ApiClient {
  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("legal_os_token");
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      if (typeof window !== "undefined") {
        localStorage.removeItem("legal_os_token");
        if (!window.location.pathname.startsWith("/login")) {
          window.location.href = "/login";
        }
      }
      throw new Error("Unauthorized. Please log in again.");
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `Request failed with status ${response.status}`
      );
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // Auth
  async login(email: string, password: string): Promise<LoginResponse> {
    return this.request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>("/auth/me");
  }

  // Matters
  async getMatters(
    page: number = 1,
    pageSize: number = 25,
    status?: string,
    search?: string
  ): Promise<PaginatedResponse<Matter>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (status && status !== "all") params.append("status", status);
    if (search) params.append("search", search);

    return this.request<PaginatedResponse<Matter>>(`/matters?${params}`);
  }

  async getMatter(id: string): Promise<MatterDetail> {
    return this.request<MatterDetail>(`/matters/${id}`);
  }

  async createMatter(data: any): Promise<MatterDetail> {
    return this.request<MatterDetail>("/matters", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateMatter(id: string, data: any): Promise<MatterDetail> {
    return this.request<MatterDetail>(`/matters/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  // Matter Members
  async getMatterMembers(matterId: string): Promise<MatterMember[]> {
    return this.request<MatterMember[]>(`/matters/${matterId}/members`);
  }

  async addMatterMember(
    matterId: string,
    userId: string,
    role: string
  ): Promise<MatterMember> {
    return this.request<MatterMember>(`/matters/${matterId}/members`, {
      method: "POST",
      body: JSON.stringify({ user_id: userId, role }),
    });
  }

  // Parties
  async getMatterParties(matterId: string): Promise<Party[]> {
    return this.request<Party[]>(`/matters/${matterId}/parties`);
  }

  async addParty(matterId: string, data: any): Promise<Party> {
    return this.request<Party>(`/matters/${matterId}/parties`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Witnesses & Experts
  async getMatterWitnesses(matterId: string): Promise<Witness[]> {
    return this.request<Witness[]>(`/matters/${matterId}/witnesses`);
  }

  async addWitness(matterId: string, data: any): Promise<Witness> {
    return this.request<Witness>(`/matters/${matterId}/witnesses`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getMatterExperts(matterId: string): Promise<Expert[]> {
    return this.request<Expert[]>(`/matters/${matterId}/experts`);
  }

  async addExpert(matterId: string, data: any): Promise<Expert> {
    return this.request<Expert>(`/matters/${matterId}/experts`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Events (Timeline)
  async getMatterEvents(matterId: string): Promise<Event[]> {
    return this.request<Event[]>(`/matters/${matterId}/events`);
  }

  async addEvent(matterId: string, data: any): Promise<Event> {
    return this.request<Event>(`/matters/${matterId}/events`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Deadlines
  async getMatterDeadlines(matterId: string): Promise<Deadline[]> {
    return this.request<Deadline[]>(`/matters/${matterId}/deadlines`);
  }

  async addDeadline(matterId: string, data: any): Promise<Deadline> {
    return this.request<Deadline>(`/matters/${matterId}/deadlines`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Tasks
  async getMatterTasks(matterId: string): Promise<Task[]> {
    return this.request<Task[]>(`/matters/${matterId}/tasks`);
  }

  async addTask(matterId: string, data: any): Promise<Task> {
    return this.request<Task>(`/matters/${matterId}/tasks`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateTask(
    matterId: string,
    taskId: string,
    data: any
  ): Promise<Task> {
    return this.request<Task>(`/matters/${matterId}/tasks/${taskId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  // Claims
  async getMatterClaims(matterId: string): Promise<Claim[]> {
    return this.request<Claim[]>(`/matters/${matterId}/claims`);
  }

  async addClaim(matterId: string, data: any): Promise<Claim> {
    return this.request<Claim>(`/matters/${matterId}/claims`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Documents & Evidence Intelligence
  async getMatterDocuments(matterId: string): Promise<LegalDocument[]> {
    return this.request<LegalDocument[]>(`/matters/${matterId}/documents`);
  }

  async getDocument(matterId: string, documentId: string): Promise<LegalDocument> {
    return this.request<LegalDocument>(`/matters/${matterId}/documents/${documentId}`);
  }

  async getDocumentChunks(
    matterId: string,
    documentId: string
  ): Promise<DocumentChunk[]> {
    return this.request<DocumentChunk[]>(
      `/matters/${matterId}/documents/${documentId}/chunks`
    );
  }

  async uploadDocument(
    matterId: string,
    file: File,
    documentType?: string
  ): Promise<LegalDocument> {
    const token = this.getToken();
    const formData = new FormData();
    formData.append("file", file);
    if (documentType) {
      formData.append("document_type", documentType);
    }

    const headers: Record<string, string> = {};
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const resp = await fetch(`${API_BASE_URL}/matters/${matterId}/documents`, {
      method: "POST",
      headers,
      body: formData,
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      throw new Error(err.detail || "Upload failed");
    }
    return resp.json();
  }

  async reclassifyDocument(
    matterId: string,
    documentId: string,
    newType: string
  ): Promise<LegalDocument> {
    return this.request<LegalDocument>(
      `/matters/${matterId}/documents/${documentId}/reclassify`,
      {
        method: "PUT",
        body: JSON.stringify({ document_type: newType }),
      }
    );
  }

  // Hybrid Matter Search
  async searchMatter(
    matterId: string,
    query: string,
    limit: number = 10
  ): Promise<SearchResult[]> {
    return this.request<SearchResult[]>(`/matters/${matterId}/search`, {
      method: "POST",
      body: JSON.stringify({ query, limit }),
    });
  }

  // AI Assistant Endpoints
  async askMatterAI(matterId: string, question: string): Promise<any> {
    return this.request<any>(`/matters/${matterId}/ai/ask`, {
      method: "POST",
      body: JSON.stringify({ question }),
    });
  }

  async summarizeDocument(matterId: string, documentId: string): Promise<any> {
    return this.request<any>(`/matters/${matterId}/ai/summarize-document/${documentId}`, {
      method: "POST",
      body: JSON.stringify({}),
    });
  }

  async extractTimeline(matterId: string, query: string): Promise<any> {
    return this.request<any>(`/matters/${matterId}/ai/extract-timeline`, {
      method: "POST",
      body: JSON.stringify({ query }),
    });
  }

}

export const api = new ApiClient();

