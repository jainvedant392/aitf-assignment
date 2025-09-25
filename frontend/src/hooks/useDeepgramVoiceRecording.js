import { useState, useRef, useCallback, useEffect } from "react";

export function useDeepgramVoiceRecording() {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState(null);
  const [isSupported, setIsSupported] = useState(true);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);

  // Check browser support on mount
  useEffect(() => {
    const checkSupport = () => {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setIsSupported(false);
        setError("このブラウザはマイク録音をサポートしていません");
        return;
      }

      if (
        !MediaRecorder.isTypeSupported("audio/webm") &&
        !MediaRecorder.isTypeSupported("audio/wav")
      ) {
        setIsSupported(false);
        setError("このブラウザは対応する音声形式をサポートしていません");
        return;
      }

      console.log("✅ Deepgram voice recording supported");
    };

    checkSupport();
  }, []);

  const startRecording = useCallback(async () => {
    if (!isSupported || isRecording || isProcessing) {
      return;
    }

    try {
      setError(null);
      setTranscript("");
      setConfidence(0);

      console.log("🎤 Requesting microphone access...");

      // Request microphone with optimized settings for speech
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000, // Optimal for speech recognition
          channelCount: 1, // Mono audio
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      streamRef.current = stream;

      // Determine the best audio format
      let mimeType = "audio/webm";
      if (MediaRecorder.isTypeSupported("audio/webm;codecs=opus")) {
        mimeType = "audio/webm;codecs=opus";
      } else if (MediaRecorder.isTypeSupported("audio/wav")) {
        mimeType = "audio/wav";
      }

      // Create MediaRecorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType,
        audioBitsPerSecond: 64000, // Good quality for speech
      });

      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
          console.log("📊 Audio chunk recorded:", event.data.size, "bytes");
        }
      };

      mediaRecorder.onstop = async () => {
        console.log("🛑 Recording stopped, processing...");
        setIsRecording(false);
        setIsProcessing(true);

        // Stop all audio tracks
        if (streamRef.current) {
          streamRef.current.getTracks().forEach((track) => track.stop());
          streamRef.current = null;
        }

        // Create audio blob
        const audioBlob = new Blob(audioChunksRef.current, {
          type: mimeType,
        });

        console.log(
          "🎵 Audio blob created:",
          audioBlob.size,
          "bytes",
          audioBlob.type
        );

        if (audioBlob.size === 0) {
          setError("録音データが空です。もう一度お試しください");
          setIsProcessing(false);
          return;
        }

        // Send to backend for transcription
        await processAudioWithBackend(audioBlob);
      };

      mediaRecorder.onerror = (event) => {
        console.error("❌ MediaRecorder error:", event.error);
        setError(`録音エラー: ${event.error?.message || "不明なエラー"}`);
        setIsRecording(false);
        setIsProcessing(false);
      };

      // Start recording with data collection every 100ms for responsiveness
      mediaRecorder.start(100);
      setIsRecording(true);
      console.log("✅ Recording started with", mimeType);
    } catch (error) {
      console.error("❌ Failed to start recording:", error);

      let errorMessage = "録音開始に失敗しました";
      if (error.name === "NotAllowedError") {
        errorMessage =
          "マイクへのアクセスが拒否されました。ブラウザの設定を確認してください";
      } else if (error.name === "NotFoundError") {
        errorMessage =
          "マイクが見つかりません。マイクが接続されているか確認してください";
      } else if (error.name === "NotSupportedError") {
        errorMessage = "このブラウザでは録音がサポートされていません";
      }

      setError(errorMessage);
      setIsRecording(false);
    }
  }, [isSupported, isRecording, isProcessing]);

  const stopRecording = useCallback(() => {
    if (!isRecording || !mediaRecorderRef.current) {
      return;
    }

    try {
      console.log("⏹️ Stopping recording...");
      mediaRecorderRef.current.stop();
    } catch (error) {
      console.error("❌ Error stopping recording:", error);
      setError(`録音停止エラー: ${error.message}`);
      setIsRecording(false);
      setIsProcessing(false);
    }
  }, [isRecording]);

  const cancelRecording = useCallback(() => {
    console.log("❌ Cancelling recording...");

    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
    }

    // Stop audio tracks immediately
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    setIsRecording(false);
    setIsProcessing(false);
    setTranscript("");
    setConfidence(0);
    setError(null);
    audioChunksRef.current = [];
  }, [isRecording]);

  const processAudioWithBackend = async (audioBlob) => {
    try {
      console.log("🚀 Sending audio to backend for processing...");

      // Create FormData for file upload
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      formData.append("language", "ja"); // Japanese

      // Send to backend voice processing endpoint
      const response = await fetch(
        "http://localhost:5000/api/chat/voice/process",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("✅ Backend processing result:", result);

      if (result.success) {
        const transcriptionData = result.transcription;

        setTranscript(transcriptionData.transcript);
        setConfidence(transcriptionData.confidence);

        console.log(
          `🎯 Transcription: "${transcriptionData.transcript}" (confidence: ${transcriptionData.confidence})`
        );

        // The full result includes chat response, but we'll let the parent component handle that
        // Emit the full result for the chat interface to process
        if (window.deepgramResult) {
          window.deepgramResult(result);
        }
      } else {
        throw new Error(result.error || "音声処理に失敗しました");
      }
    } catch (error) {
      console.error("❌ Audio processing failed:", error);
      setError(`音声処理エラー: ${error.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const resetTranscript = useCallback(() => {
    setTranscript("");
    setConfidence(0);
    setError(null);
  }, []);

  // For compatibility with existing useVoiceRecognition interface
  const isListening = isRecording;

  return {
    // Core recording states
    isRecording,
    isProcessing,
    transcript,
    confidence,
    error,
    isSupported,

    // Control functions
    startRecording,
    stopRecording,
    cancelRecording,
    resetTranscript,

    // Compatibility with existing interface
    isListening,
    startListening: startRecording,
    stopListening: stopRecording,
  };
}
