import React, { useState, useEffect, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import "./App.css";

// Types
import { RecordingSession, GeminiStatus } from "./types";

// Services
import { ApiService } from "./services/apiService";

// Hooks
import { useSocket } from "./hooks/useSocket";
import { useAudioRecording } from "./hooks/useAudioRecording";

// Components
import { StatusIndicator } from "./components/StatusIndicator";
import { GeminiStatusWarning } from "./components/GeminiStatusWarning";
import { RecordingControls } from "./components/RecordingControls";
import { TranscriptDisplay } from "./components/TranscriptDisplay";
import { SoapNoteDisplay } from "./components/SoapNoteDisplay";

const App: React.FC = () => {
  const [session, setSession] = useState<RecordingSession>({
    sessionId: "",
    isRecording: false,
    transcript: "",
    soapNote: "",
    status: "Ready to start recording",
  });
  const [processingStatus, setProcessingStatus] = useState("");
  const [geminiStatus, setGeminiStatus] = useState<GeminiStatus | null>(null);

  const {
    socket,
    isConnected,
    startRecording: socketStartRecording,
    stopRecording: socketStopRecording,
    sendAudioChunk,
  } = useSocket(
    useCallback((update: Partial<RecordingSession>) => {
      setSession((prev) => ({ ...prev, ...update }));
    }, []),
    setProcessingStatus
  );

  const {
    startRecording: audioStartRecording,
    stopRecording: audioStopRecording,
  } = useAudioRecording();

  // API calls
  const checkGeminiStatus = async () => {
    const status = await ApiService.checkGeminiStatus();
    setGeminiStatus(status);
  };

  // Effects
  useEffect(() => {
    checkGeminiStatus();
  }, []);

  // Handlers
  const handleStartRecording = async () => {
    try {
      const sessionId = uuidv4();

      setSession((prev) => ({
        ...prev,
        sessionId,
        isRecording: true,
        transcript: "",
        soapNote: "",
        status: "Recording in progress...",
      }));

      // Start socket recording
      socketStartRecording(sessionId);

      // Start audio recording
      await audioStartRecording((audioData) => {
        sendAudioChunk(sessionId, audioData);
      });
    } catch (error) {
      console.error("Error starting recording:", error);
      setSession((prev) => ({
        ...prev,
        status: "Error: Could not access microphone",
      }));
    }
  };

  const handleStopRecording = () => {
    if (session.isRecording) {
      audioStopRecording();
      socketStopRecording(session.sessionId);
      setSession((prev) => ({ ...prev, isRecording: false }));
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Medical Scribe Agent</h1>
        <StatusIndicator
          isConnected={isConnected}
          geminiStatus={geminiStatus}
        />
      </header>

      {geminiStatus && (
        <GeminiStatusWarning
          geminiStatus={geminiStatus}
          onCheckAgain={checkGeminiStatus}
        />
      )}

      <main className="main-content">
        <RecordingControls
          session={session}
          isConnected={isConnected}
          geminiStatus={geminiStatus}
          processingStatus={processingStatus}
          onStartRecording={handleStartRecording}
          onStopRecording={handleStopRecording}
        />

        <TranscriptDisplay transcript={session.transcript} />
        <SoapNoteDisplay soapNote={session.soapNote} />
      </main>
    </div>
  );
};

export default App;
