import { GeminiStatus } from "../types";

const API_BASE_URL = "http://localhost:5001";

export class ApiService {
  static async checkGeminiStatus(): Promise<GeminiStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/gemini-status`);
      return await response.json();
    } catch (error) {
      return {
        status: "error",
        message: "Could not check Gemini API status",
      };
    }
  }

  static async getSession(sessionId: string) {
    try {
      const response = await fetch(`${API_BASE_URL}/get_session/${sessionId}`);
      return await response.json();
    } catch (error) {
      throw new Error("Failed to get session data");
    }
  }
}
