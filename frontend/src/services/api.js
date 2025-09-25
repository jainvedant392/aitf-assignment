// import axios from "axios";

// // API Configuration
// const API_BASE_URL = "http://localhost:5000";

// const api = axios.create({
//   baseURL: API_BASE_URL,
//   timeout: 30000,
//   headers: {
//     "Content-Type": "application/json",
//   },
// });

// // Request/Response interceptors for debugging
// api.interceptors.request.use((config) => {
//   console.log(
//     "🚀 API Request:",
//     config.method?.toUpperCase(),
//     config.url,
//     config.data
//   );
//   return config;
// });

// api.interceptors.response.use(
//   (response) => {
//     console.log("✅ API Response:", response.status, response.data);
//     return response;
//   },
//   (error) => {
//     console.error("❌ API Error:", error.response?.data || error.message);
//     return Promise.reject(error);
//   }
// );

// /**
//  * Chat API - Direct integration with Flask /api/chat/ endpoint
//  */
// export const chatAPI = {
//   async sendMessage({ message, session_id = null, language = "japanese" }) {
//     try {
//       const response = await api.post("/api/chat/", {
//         message: message.trim(),
//         session_id,
//         language,
//       });
//       return response.data;
//     } catch (error) {
//       throw new Error(
//         error.response?.data?.error || "チャット送信に失敗しました"
//       );
//     }
//   },
// };

// /**
//  * Weather API - Direct integration with Flask /api/weather/current
//  */
// export const weatherAPI = {
//   async getCurrentWeather(city = "Tokyo", country = "JP") {
//     try {
//       const response = await api.get("/api/weather/current", {
//         params: { city, country },
//       });
//       return response.data;
//     } catch (error) {
//       throw new Error(
//         error.response?.data?.error || "天気データの取得に失敗しました"
//       );
//     }
//   },
// };

// export default api;

import axios from "axios";

// API Configuration
const API_BASE_URL = "http://localhost:5000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // Increased timeout for voice processing
  headers: {
    "Content-Type": "application/json",
  },
});

// Request/Response interceptors for debugging
api.interceptors.request.use((config) => {
  console.log(
    "🚀 API Request:",
    config.method?.toUpperCase(),
    config.url,
    config.data ? "with data" : "no data"
  );
  return config;
});

api.interceptors.response.use(
  (response) => {
    console.log("✅ API Response:", response.status, response.data);
    return response;
  },
  (error) => {
    console.error("❌ API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * Chat API - Direct integration with Flask /api/chat/ endpoint
 */
export const chatAPI = {
  async sendMessage({ message, session_id = null, language = "japanese" }) {
    try {
      const response = await api.post("/api/chat/", {
        message: message.trim(),
        session_id,
        language,
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.error || "チャット送信に失敗しました"
      );
    }
  },

  /**
   * Process voice input through Deepgram transcription + intelligent chat
   * @param {FormData} formData - Contains audio file and optional parameters
   * @returns {Promise} - Complete voice processing result
   */
  async processVoiceInput(formData) {
    try {
      console.log("🎤 Sending voice input for processing...");

      const response = await fetch(`${API_BASE_URL}/api/chat/voice/process`, {
        method: "POST",
        body: formData,
        // Don't set Content-Type header - let browser set it with boundary for FormData
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.error || `HTTP ${response.status}: Voice processing failed`
        );
      }

      const result = await response.json();
      console.log("✅ Voice processing completed:", result.success);

      return result;
    } catch (error) {
      console.error("❌ Voice processing error:", error);
      throw new Error(error.message || "音声処理に失敗しました");
    }
  },

  /**
   * Get voice processing capabilities and status
   * @returns {Promise} - Voice system status and capabilities
   */
  async getVoiceStatus() {
    try {
      const response = await api.get("/api/chat/voice/status");
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.error || "音声システムの状態取得に失敗しました"
      );
    }
  },

  /**
   * Analyze query capabilities without processing
   * @param {string} message - Message to analyze
   * @returns {Promise} - Query analysis result
   */
  async analyzeQuery(message) {
    try {
      const response = await api.post("/api/chat/analyze", {
        message: message.trim(),
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.error || "クエリ分析に失敗しました"
      );
    }
  },
};

/**
 * Weather API - Direct integration with Flask /api/weather/current
 */
export const weatherAPI = {
  async getCurrentWeather(city = "Tokyo", country = "JP") {
    try {
      const response = await api.get("/api/weather/current", {
        params: { city, country },
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.error || "天気データの取得に失敗しました"
      );
    }
  },

  async getForecast(city = "Tokyo", country = "JP", days = 5) {
    try {
      const response = await api.get("/api/weather/forecast", {
        params: { city, country, days },
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.error || "天気予報の取得に失敗しました"
      );
    }
  },

  async searchLocations(query) {
    try {
      const response = await api.get("/api/weather/locations/search", {
        params: { query, limit: 5 },
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.error || "場所検索に失敗しました");
    }
  },
};

/**
 * Agriculture API - Specialized agricultural endpoints
 */
export const agricultureAPI = {
  async getCropRecommendations(city = "Tokyo", country = "JP") {
    try {
      const response = await api.get("/api/agriculture/crops/recommendations", {
        params: { city, country },
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.error || "作物推奨情報の取得に失敗しました"
      );
    }
  },

  async getPestRiskAssessment(
    city = "Tokyo",
    country = "JP",
    cropType = "general"
  ) {
    try {
      const response = await api.get("/api/agriculture/pest/risk-assessment", {
        params: { city, country, crop_type: cropType },
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.error || "病害虫リスク評価の取得に失敗しました"
      );
    }
  },

  async getSeasonalAdvice(city = "Tokyo", country = "JP") {
    try {
      const response = await api.get("/api/agriculture/seasonal/advice", {
        params: { city, country },
      });
      return response.data;
    } catch (error) {
      throw new Error(
        error.response?.data?.error || "季節アドバイスの取得に失敗しました"
      );
    }
  },
};

/**
 * Utility functions for API management
 */
export const apiUtils = {
  /**
   * Check overall API health
   */
  async checkHealth() {
    try {
      const response = await api.get("/");
      return response.data;
    } catch (error) {
      throw new Error("API接続に失敗しました");
    }
  },

  /**
   * Get API documentation
   */
  async getApiDocs() {
    try {
      const response = await api.get("/api");
      return response.data;
    } catch (error) {
      throw new Error("API文書の取得に失敗しました");
    }
  },

  /**
   * Create FormData for voice input
   * @param {Blob} audioBlob - Audio data
   * @param {Object} options - Additional options (session_id, language)
   * @returns {FormData} - Ready to send FormData
   */
  createVoiceFormData(audioBlob, options = {}) {
    const formData = new FormData();

    // Add audio file with proper filename and type
    const filename = `recording.${
      audioBlob.type.includes("webm") ? "webm" : "wav"
    }`;
    formData.append("audio", audioBlob, filename);

    // Add optional parameters
    if (options.session_id) {
      formData.append("session_id", options.session_id);
    }

    formData.append("language", options.language || "ja");

    return formData;
  },

  /**
   * Validate audio blob before sending
   * @param {Blob} audioBlob - Audio data to validate
   * @returns {Object} - Validation result
   */
  validateAudioBlob(audioBlob) {
    const result = {
      valid: true,
      warnings: [],
      errors: [],
    };

    // Check if blob exists and has data
    if (!audioBlob || audioBlob.size === 0) {
      result.valid = false;
      result.errors.push("Audio data is empty");
      return result;
    }

    // Check file size (500MB limit)
    const maxSize = 500 * 1024 * 1024; // 500MB
    if (audioBlob.size > maxSize) {
      result.valid = false;
      result.errors.push(
        `Audio file too large: ${(audioBlob.size / 1024 / 1024).toFixed(
          1
        )}MB (max: 500MB)`
      );
    }

    // Check minimum size (at least 1KB for meaningful audio)
    if (audioBlob.size < 1024) {
      result.warnings.push("Audio file very small - may not contain speech");
    }

    // Check audio type
    const supportedTypes = [
      "audio/webm",
      "audio/wav",
      "audio/mp3",
      "audio/ogg",
    ];
    if (!supportedTypes.some((type) => audioBlob.type.includes(type))) {
      result.warnings.push(`Audio type ${audioBlob.type} may not be optimal`);
    }

    return result;
  },
};

export default api;
