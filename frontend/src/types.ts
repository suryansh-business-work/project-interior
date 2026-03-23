export interface User {
  id: string;
  name: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Project {
  id: string;
  name: string;
  description: string | null;
  user_id: string;
  site_plan_url: string | null;
  detected_style: string | null;
  style_confidence: number | null;
  style_probabilities: Record<string, number> | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  project_id: string;
  role: 'user' | 'assistant';
  message: string;
  image_url: string | null;
  design_suggestions: DesignSuggestion[] | null;
  created_at: string;
}

export interface DesignSuggestion {
  category: string;
  suggestion: string;
  style: string;
  reference_images?: string[];
}

export interface StyleInfo {
  name: string;
  display_name: string;
  description: string;
  colors: string[];
  materials: string[];
  preview_tip: string;
}
