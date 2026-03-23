import { create } from 'zustand';
import api from './api';
import type { User, Project, ChatMessage } from './types';

interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  loadFromStorage: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    set({ user: data.user, token: data.access_token, isAuthenticated: true });
  },

  register: async (name, email, password) => {
    const { data } = await api.post('/auth/register', { name, email, password });
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    set({ user: data.user, token: data.access_token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ user: null, token: null, isAuthenticated: false });
  },

  loadFromStorage: () => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr);
        set({ user, token, isAuthenticated: true });
      } catch {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
  },
}));

interface ProjectStore {
  projects: Project[];
  currentProject: Project | null;
  loading: boolean;
  fetchProjects: () => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (name: string, description?: string) => Promise<Project>;
  deleteProject: (id: string) => Promise<void>;
  uploadSitePlan: (projectId: string, file: File) => Promise<Project>;
  setCurrentProject: (project: Project | null) => void;
}

export const useProjectStore = create<ProjectStore>((set, get) => ({
  projects: [],
  currentProject: null,
  loading: false,

  fetchProjects: async () => {
    set({ loading: true });
    const { data } = await api.get('/projects/');
    set({ projects: data, loading: false });
  },

  fetchProject: async (id) => {
    const { data } = await api.get(`/projects/${id}`);
    set({ currentProject: data });
  },

  createProject: async (name, description) => {
    const { data } = await api.post('/projects/', { name, description });
    set((state) => ({ projects: [data, ...state.projects] }));
    return data;
  },

  deleteProject: async (id) => {
    await api.delete(`/projects/${id}`);
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== id),
      currentProject: state.currentProject?.id === id ? null : state.currentProject,
    }));
  },

  uploadSitePlan: async (projectId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post(`/projects/${projectId}/upload-plan`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    set((state) => ({
      currentProject: data,
      projects: state.projects.map((p) => (p.id === projectId ? data : p)),
    }));
    return data;
  },

  setCurrentProject: (project) => set({ currentProject: project }),
}));

interface ChatStore {
  messages: ChatMessage[];
  loading: boolean;
  sending: boolean;
  fetchMessages: (projectId: string) => Promise<void>;
  sendMessage: (projectId: string, message: string) => Promise<void>;
  clearMessages: () => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  loading: false,
  sending: false,

  fetchMessages: async (projectId) => {
    set({ loading: true });
    const { data } = await api.get(`/projects/${projectId}/chat/`);
    set({ messages: data, loading: false });
  },

  sendMessage: async (projectId, message) => {
    set({ sending: true });
    const { data } = await api.post(`/projects/${projectId}/chat/`, { message });
    set((state) => ({
      messages: [
        ...state.messages,
        { ...data, role: 'user' as const, message, id: `temp-${Date.now()}`, project_id: projectId, image_url: null, design_suggestions: null, created_at: new Date().toISOString() },
      ].filter((m, i, arr) => i === arr.findIndex((a) => a.id === m.id) || m.id.startsWith('temp-')),
      sending: false,
    }));
    // Re-fetch to get proper messages
    const { data: msgs } = await api.get(`/projects/${projectId}/chat/`);
    set({ messages: msgs });
  },

  clearMessages: () => set({ messages: [] }),
}));
