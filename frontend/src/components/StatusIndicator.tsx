import React from "react";
import { GeminiStatus } from "../types";

interface StatusIndicatorProps {
  isConnected: boolean;
  geminiStatus: GeminiStatus | null;
}

export const StatusIndicator: React.FC<StatusIndicatorProps> = ({
  isConnected,
  geminiStatus,
}) => {
  const getGeminiStatusColor = () => {
    if (!geminiStatus) return "gray";
    switch (geminiStatus.status) {
      case "working":
        return "green";
      case "error":
        return "red";
      default:
        return "gray";
    }
  };

  return (
    <div className="status-indicators">
      <div
        className={`connection-status ${
          isConnected ? "connected" : "disconnected"
        }`}
      >
        {isConnected ? "🟢 Server Connected" : "🔴 Server Disconnected"}
      </div>
      <div className={`gemini-status ${geminiStatus?.status || "unknown"}`}>
        <span style={{ color: getGeminiStatusColor() }}>●</span>
        Gemini API:{" "}
        {geminiStatus?.status === "working"
          ? "Ready"
          : geminiStatus?.status === "error"
          ? "Error"
          : "Checking..."}
      </div>
    </div>
  );
};
