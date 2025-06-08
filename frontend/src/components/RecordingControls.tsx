import React from "react";
import { RecordingSession, GeminiStatus } from "../types";

interface RecordingControlsProps {
  session: RecordingSession;
  isConnected: boolean;
  geminiStatus: GeminiStatus | null;
  processingStatus: string;
  onStartRecording: () => void;
  onStopRecording: () => void;
}

export const RecordingControls: React.FC<RecordingControlsProps> = ({
  session,
  isConnected,
  geminiStatus,
  processingStatus,
  onStartRecording,
  onStopRecording,
}) => {
  return (
    <div className="recording-section">
      <h2>Visit Recording</h2>
      <div className="recording-controls">
        <button
          onClick={onStartRecording}
          disabled={
            session.isRecording ||
            !isConnected ||
            geminiStatus?.status !== "working"
          }
          className="start-button"
        >
          {session.isRecording ? "🔴 Recording..." : "🎙️ Start Visit Recording"}
        </button>

        <button
          onClick={onStopRecording}
          disabled={!session.isRecording}
          className="stop-button"
        >
          ⏹️ Stop Recording
        </button>
      </div>

      <div className="status">
        <strong>Status:</strong> {session.status}
      </div>

      {processingStatus && (
        <div className="processing-status">
          <div className="spinner"></div>
          {processingStatus}
        </div>
      )}
    </div>
  );
};
