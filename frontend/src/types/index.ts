export interface User {
  id: string;
  organization_id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserBrief {
  id: string;
  email: string;
  full_name: string;
  role: string;
}

export interface Matter {
  id: string;
  title: string;
  case_number: string | null;
  matter_type: string;
  status: string;
  date_opened: string;
  member_count: number;
  created_at: string;
}

export interface MatterDetail extends Matter {
  description: string | null;
  organization_id: string;
  date_closed: string | null;
  court: string | null;
  jurisdiction: string | null;
  judge: string | null;
  created_by?: UserBrief;
}

export interface MatterMember {
  id: string;
  user: UserBrief;
  role: string;
  created_at: string;
}

export interface Party {
  id: string;
  matter_id: string;
  name: string;
  party_type: string;
  entity_type: string;
  description?: string;
  contact_info?: Record<string, any>;
  created_at: string;
}

export interface Witness {
  id: string;
  matter_id: string;
  name: string;
  witness_type: string;
  description?: string;
  notes?: string;
  created_at: string;
}

export interface Expert {
  id: string;
  matter_id: string;
  name: string;
  specialty: string;
  organization_name?: string;
  retained_by: string;
  notes?: string;
  created_at: string;
}

export interface Claim {
  id: string;
  matter_id: string;
  title: string;
  description: string;
  claim_type: string;
  status: string;
  created_at: string;
}

export interface Event {
  id: string;
  matter_id: string;
  title: string;
  description?: string;
  event_date: string;
  event_type: string;
  is_ai_generated: boolean;
  confidence?: number;
  created_at: string;
}

export interface Deadline {
  id: string;
  matter_id: string;
  title: string;
  description?: string;
  due_date: string;
  deadline_type: string;
  status: string;
  is_high_risk: boolean;
  created_at: string;
}

export interface Task {
  id: string;
  matter_id: string;
  title: string;
  description?: string;
  status: string;
  priority: string;
  assigned_to_id?: string;
  due_date?: string;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface LegalDocument {
  id: string;
  matter_id: string;
  title: string;
  document_type: string;
  file_name: string;
  file_type: string;
  file_size: number;
  status: string;
  processing_status?: {
    pages_processed?: number;
    chunks_generated?: number;
    classification_confidence?: number;
    predicted_type?: string;
  };
  created_at: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  matter_id: string;
  chunk_index: number;
  content: string;
  page_number?: number;
  token_count?: number;
  created_at: string;
}

export interface SearchResult {
  chunk_id: string;
  document_id: string;
  document_title: string;
  page_number?: number;
  content: string;
  score: number;
  match_type: string;
}

