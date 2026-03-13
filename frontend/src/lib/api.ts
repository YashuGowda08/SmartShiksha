import axios from "axios";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

function authHeaders(token: string) {
  return { headers: { Authorization: `Bearer ${token}` } };
}

// ── Auth ─────────────────────────────────────────────────────────────

export const authAPI = {
  register: (token: string) => api.post("/auth/register", {}, authHeaders(token)),

  getMe: (token: string) => api.get("/auth/me", authHeaders(token)),

  updateProfile: (data: Record<string, unknown>, token: string) =>
    api.patch("/auth/me", data, authHeaders(token)),

  onboarding: (data: Record<string, unknown>, token: string) =>
    api.post("/auth/onboarding", data, authHeaders(token)),
};

// ── Content (Subjects / Chapters / Topics) ───────────────────────────

export const contentAPI = {
  getSubjects: (studentClass?: string, board?: string) => {
    const params: Record<string, string> = {};
    if (studentClass) params.student_class = studentClass;
    if (board) params.board = board;
    return api.get("/content/subjects", { params });
  },

  getChapters: (subjectId: string, studentClass?: string, board?: string) => {
    const params: Record<string, string> = {};
    if (studentClass) params.student_class = studentClass;
    if (board) params.board = board;
    return api.get(`/content/subjects/${subjectId}/chapters`, { params });
  },

  getTopics: (chapterId: string) =>
    api.get(`/content/chapters/${chapterId}/topics`),

  getTopic: (topicId: string, language?: string) => {
    const params: Record<string, string> = {};
    if (language) params.language = language;
    return api.get(`/content/topics/${topicId}`, { params });
  },
};

// ── Progress ─────────────────────────────────────────────────────────

export const progressAPI = {
  getDashboard: (token: string) =>
    api.get("/progress/dashboard", authHeaders(token)),

  updateProgress: (data: Record<string, unknown>, token: string) =>
    api.post("/progress/update", data, authHeaders(token)),
};

// ── Mock Tests ───────────────────────────────────────────────────────

export const mockTestAPI = {
  listTests: (params?: {
    student_class?: string;
    subject_name?: string;
    test_type?: string;
  }) => api.get("/mock-tests/", { params }),

  getTest: (testId: string) => api.get(`/mock-tests/${testId}`),

  submitTest: (data: Record<string, unknown>, token: string) =>
    api.post(`/mock-tests/${data.test_id}/submit`, data, authHeaders(token)),
};

// ── Exam Generator ───────────────────────────────────────────────────

export const examAPI = {
  generatePaper: (data: Record<string, unknown>, token: string) =>
    api.post("/exams/generate", data, {
      ...authHeaders(token),
      responseType: "blob",
    }),
};

// ── AI Tutor ─────────────────────────────────────────────────────────

export const aiTutorAPI = {
  chat: (data: Record<string, unknown>, token: string) =>
    api.post("/ai-tutor/chat", data, authHeaders(token)),
};

// ── Community ────────────────────────────────────────────────────────

export const communityAPI = {
  getPosts: (subject?: string) => {
    const params: Record<string, string> = {};
    if (subject) params.subject = subject;
    return api.get("/community/posts", { params });
  },

  createPost: (formData: FormData, token: string) =>
    api.post("/community/posts", formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    }),

  getReplies: (postId: string) =>
    api.get(`/community/posts/${postId}/replies`),

  createReply: (postId: string, formData: FormData, token: string) =>
    api.post(`/community/posts/${postId}/replies`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    }),
};

// ── Admin ────────────────────────────────────────────────────────────

export const adminAPI = {
  getStats: (token: string) =>
    api.get("/admin/stats", authHeaders(token)),

  uploadQuestions: (file: File, token: string) => {
    const fd = new FormData();
    fd.append("file", file);
    return api.post("/admin/upload-questions", fd, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    });
  },
};

// ── Textbooks ────────────────────────────────────────────────────────

export const textbookAPI = {
  listTextbooks: (params?: { student_class?: string }) =>
    api.get("/textbooks/", { params }),

  uploadTextbook: (formData: FormData, token: string) =>
    api.post("/textbooks/", formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "multipart/form-data",
      },
    }),
};
