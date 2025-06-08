import React from "react";
import { TranscriptSegment } from "../types";

interface TranscriptDisplayProps {
  transcript: string;
}

const parseTranscriptWithSpeakers = (
  transcript: string
): TranscriptSegment[] => {
  if (!transcript) return [];

  const segments: TranscriptSegment[] = [];
  const lines = transcript.split(/(?=Speaker \d+:)/);

  lines.forEach((line) => {
    if (!line.trim()) return;

    const speakerMatch = line.match(/^Speaker (\d+):\s*(.+)/);
    if (speakerMatch) {
      segments.push({
        text: speakerMatch[2].trim(),
        speaker: parseInt(speakerMatch[1]),
      });
    } else {
      // Text without speaker label
      segments.push({
        text: line.trim(),
        speaker: null,
      });
    }
  });

  return segments;
};

const getSpeakerColor = (speaker: number | null): string => {
  if (!speaker) return "#666";

  const colors = [
    "#2563eb", // blue - Speaker 1 (often provider)
    "#dc2626", // red - Speaker 2 (often patient)
    "#16a34a", // green - Speaker 3 (often nurse)
    "#ca8a04", // amber - Speaker 4 (often family)
    "#9333ea", // purple - Speaker 5+
    "#c2410c", // orange - Speaker 6+
  ];

  return colors[(speaker - 1) % colors.length];
};

export const TranscriptDisplay: React.FC<TranscriptDisplayProps> = ({
  transcript,
}) => {
  if (!transcript) return null;

  const segments = parseTranscriptWithSpeakers(transcript);

  return (
    <div className="transcript-section">
      <h2>Visit Transcript</h2>
      <div
        className="transcript-content"
        style={{
          maxHeight: "400px",
          overflowY: "auto",
          padding: "16px",
          border: "1px solid #e5e7eb",
          borderRadius: "8px",
          backgroundColor: "#fafafa",
        }}
      >
        {segments.length > 0 ? (
          segments.map((segment, index) => (
            <div
              key={index}
              style={{
                marginBottom: "8px",
                padding: "8px",
                borderLeft: `4px solid ${getSpeakerColor(segment.speaker)}`,
                backgroundColor: "white",
                borderRadius: "4px",
              }}
            >
              {segment.speaker && (
                <span
                  style={{
                    fontWeight: "bold",
                    color: getSpeakerColor(segment.speaker),
                    fontSize: "14px",
                  }}
                >
                  Speaker {segment.speaker}:{" "}
                </span>
              )}
              <span style={{ fontSize: "14px", lineHeight: "1.5" }}>
                {segment.text}
              </span>
            </div>
          ))
        ) : (
          <pre style={{ fontSize: "14px", lineHeight: "1.5", margin: 0 }}>
            {transcript}
          </pre>
        )}
      </div>
    </div>
  );
};
