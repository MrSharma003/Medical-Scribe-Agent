import { useEffect, useState } from "react";
import io, { Socket } from "socket.io-client";
import { RecordingSession, LiveTranscriptionData } from "../types";

interface UseSocketReturn {
  socket: Socket | null;
  isConnected: boolean;
  startRecording: (sessionId: string) => void;
  stopRecording: (sessionId: string) => void;
  sendAudioChunk: (sessionId: string, audioData: string | ArrayBuffer) => void;
}

const API_BASE_URL = "http://localhost:5001";

export const useSocket = (
  onSessionUpdate: (update: Partial<RecordingSession>) => void,
  onProcessingUpdate: (status: string) => void
): UseSocketReturn => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const newSocket = io(API_BASE_URL);
    setSocket(newSocket);

    newSocket.on("connect", () => {
      setIsConnected(true);
      console.log("Connected to server");
    });

    newSocket.on("disconnect", () => {
      setIsConnected(false);
      console.log("Disconnected from server");
    });

    newSocket.on("recording_started", (data) => {
      onSessionUpdate({ status: data.status });
    });

    newSocket.on("recording_stopped", (data) => {
      onSessionUpdate({ status: data.status });
      onProcessingUpdate("Processing recording...");
    });

    newSocket.on("processing_update", (data) => {
      onProcessingUpdate(data.status);
    });

    newSocket.on("transcription_complete", (data) => {
      onSessionUpdate({
        transcript: data.transcript,
        status: data.status,
      });
      onProcessingUpdate(data.status);
    });

    newSocket.on("soap_note_complete", (data) => {
      onSessionUpdate({
        soapNote: data.soap_note,
        status: data.status,
      });
      onProcessingUpdate("");
    });

    newSocket.on("processing_error", (data) => {
      onSessionUpdate({ status: `Error: ${data.error}` });
      onProcessingUpdate("");
    });

    // Enhanced live transcription with speaker information
    newSocket.on("live_transcription", (data: LiveTranscriptionData) => {
      console.log("Live transcription received:", {
        speaker: data.speaker,
        text: data.raw_text?.substring(0, 50) + "...",
        hasFullTranscript: !!data.full_transcript,
      });

      onSessionUpdate({
        transcript: data.full_transcript || data.transcript_chunk,
      });
    });

    return () => {
      newSocket.close();
    };
  }, [onSessionUpdate, onProcessingUpdate]);

  const startRecording = (sessionId: string) => {
    socket?.emit("start_recording", { session_id: sessionId });
  };

  const stopRecording = (sessionId: string) => {
    socket?.emit("stop_recording", { session_id: sessionId });
  };

  const sendAudioChunk = (
    sessionId: string,
    audioData: string | ArrayBuffer
  ) => {
    socket?.emit("audio_chunk", {
      session_id: sessionId,
      audio_data: audioData,
    });
  };

  return {
    socket,
    isConnected,
    startRecording,
    stopRecording,
    sendAudioChunk,
  };
};
