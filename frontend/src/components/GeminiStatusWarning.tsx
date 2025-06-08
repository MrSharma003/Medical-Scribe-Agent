import React from "react";
import { GeminiStatus } from "../types";

interface GeminiStatusWarningProps {
  geminiStatus: GeminiStatus;
  onCheckAgain: () => void;
}

export const GeminiStatusWarning: React.FC<GeminiStatusWarningProps> = ({
  geminiStatus,
  onCheckAgain,
}) => {
  if (geminiStatus.status === "working") {
    return (
      <div className="gemini-info">
        <p>
          ✅ Gemini API is ready! Using model:{" "}
          <strong>{geminiStatus.model}</strong>
        </p>
      </div>
    );
  }

  if (geminiStatus.status === "error") {
    return (
      <div className="gemini-warning">
        <h3>⚠️ Gemini API Issue</h3>
        <p>
          <strong>Error:</strong> {geminiStatus.message}
        </p>
        <div className="setup-instructions">
          <p>To fix this:</p>
          <ol>
            <li>
              Get a free API key from{" "}
              <a
                href="https://ai.google.dev/"
                target="_blank"
                rel="noopener noreferrer"
              >
                Google AI Studio
              </a>
            </li>
            <li>
              Add it to your <code>backend/.env</code> file:{" "}
              <code>GOOGLE_API_KEY=your_key_here</code>
            </li>
            <li>Restart the backend server</li>
          </ol>
        </div>
        <button onClick={onCheckAgain} className="refresh-button">
          🔄 Check Again
        </button>
      </div>
    );
  }

  return null;
};
