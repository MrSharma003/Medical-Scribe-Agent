import { useRef, useCallback } from "react";

interface UseAudioRecordingReturn {
  startRecording: (
    onAudioChunk: (data: string | ArrayBuffer) => void
  ) => Promise<void>;
  stopRecording: () => void;
}

export const useAudioRecording = (): UseAudioRecordingReturn => {
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const workletNodeRef = useRef<AudioWorkletNode | null>(null);

  const encodeArrayBufferToBase64 = (arrayBuffer: ArrayBuffer): string => {
    const bytes = new Uint8Array(arrayBuffer);
    let binary = "";
    bytes.forEach((b) => (binary += String.fromCharCode(b)));
    return btoa(binary);
  };

  const startRecording = useCallback(
    async (onAudioChunk: (data: string | ArrayBuffer) => void) => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            channelCount: 1,
          },
        });

        streamRef.current = stream;

        // Create AudioContext (defaults to 48 kHz on most browsers)
        const audioContext = new AudioContext();
        audioContextRef.current = audioContext;

        // Load the PCM worklet
        await audioContext.audioWorklet.addModule("/pcm-processor.js");

        const source = audioContext.createMediaStreamSource(stream);
        const workletNode = new AudioWorkletNode(audioContext, "pcm-processor");
        workletNodeRef.current = workletNode;

        // Handle ArrayBuffer chunks from the worklet
        workletNode.port.onmessage = (event) => {
          if (event.data) {
            const base64Data = encodeArrayBufferToBase64(
              event.data as ArrayBuffer
            );
            onAudioChunk(base64Data);
          }
        };

        // Connect the graph: microphone -> worklet (no output)
        source.connect(workletNode);
        console.log(
          `Started recording with AudioWorklet PCM streaming (sampleRate=${audioContext.sampleRate})`
        );
      } catch (error) {
        console.error("Error starting recording:", error);
        throw new Error("Could not access microphone");
      }
    },
    []
  );

  const stopRecording = useCallback(() => {
    // Stop worklet processing
    if (workletNodeRef.current) {
      workletNodeRef.current.port.postMessage("STOP");
      workletNodeRef.current.disconnect();
      workletNodeRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }, []);

  return {
    startRecording,
    stopRecording,
  };
};
