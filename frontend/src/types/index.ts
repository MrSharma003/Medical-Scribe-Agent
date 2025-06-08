export interface RecordingSession {
  sessionId: string;
  isRecording: boolean;
  transcript: string;
  soapNote: string;
  status: string;
}

export interface GeminiStatus {
  status: string;
  model?: string;
  message?: string;
}

export interface AudioChunk {
  session_id: string;
  audio_data: string | ArrayBuffer;
}

export interface LiveTranscriptionData {
  session_id: string;
  transcript_chunk: string;
  raw_text: string;
  speaker: number | null;
  full_transcript: string;
}

export interface TranscriptSegment {
  text: string;
  speaker: number | null;
  timestamp?: number;
}
