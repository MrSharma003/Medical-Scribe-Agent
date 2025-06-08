class PCMProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.isRecording = true;
    this.buffer = [];
    this.bufferSize = 9600; // 9600 bytes ≈ 300 ms at 16 kHz (16-bit mono)

    this.port.onmessage = (event) => {
      if (event.data === "STOP") {
        this.isRecording = false;
        this.flush();
      }
    };
  }

  flush() {
    if (this.buffer.length > 0) {
      const finalBuffer = new Uint8Array(this.buffer);
      this.port.postMessage(finalBuffer.buffer);
      this.buffer = [];
    }
  }

  process(inputs) {
    if (!this.isRecording) {
      this.flush();
      return false; // Stop processing
    }

    const input = inputs[0];
    if (input && input.length > 0) {
      const channelData = input[0]; // mono
      for (let i = 0; i < channelData.length; i++) {
        const sample = Math.max(-1, Math.min(1, channelData[i]));
        const intSample = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
        this.buffer.push(intSample & 0xff);
        this.buffer.push((intSample >> 8) & 0xff);

        if (this.buffer.length >= this.bufferSize) {
          const outputBuffer = new Uint8Array(this.buffer);
          this.port.postMessage(outputBuffer.buffer);
          this.buffer = [];
        }
      }
    }
    return true;
  }
}

registerProcessor("pcm-processor", PCMProcessor);
