/* Records the microphone as a 16 kHz mono WAV file.
   WAV, because Gnani's speech-to-text docs list WAV but not the WebM that browsers record by default. */
(() => {
  'use strict';

  const TARGET_RATE = 16000;

  function mergeChunks(chunks) {
    const length = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const samples = new Float32Array(length);
    let offset = 0;
    chunks.forEach((chunk) => { samples.set(chunk, offset); offset += chunk.length; });
    return samples;
  }

  // Average each block of input samples into one output sample (a simple low-pass + decimate).
  function downsample(samples, fromRate) {
    if (fromRate <= TARGET_RATE) return samples;
    const ratio = fromRate / TARGET_RATE;
    const out = new Float32Array(Math.floor(samples.length / ratio));
    for (let i = 0; i < out.length; i += 1) {
      const start = Math.floor(i * ratio);
      const end = Math.min(Math.floor((i + 1) * ratio), samples.length);
      let sum = 0;
      for (let j = start; j < end; j += 1) sum += samples[j];
      out[i] = sum / Math.max(end - start, 1);
    }
    return out;
  }

  function encodeWav(samples) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);
    const text = (offset, value) => { for (let i = 0; i < value.length; i += 1) view.setUint8(offset + i, value.charCodeAt(i)); };
    text(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    text(8, 'WAVE');
    text(12, 'fmt ');
    view.setUint32(16, 16, true); // fmt chunk size
    view.setUint16(20, 1, true); // PCM
    view.setUint16(22, 1, true); // mono
    view.setUint32(24, TARGET_RATE, true);
    view.setUint32(28, TARGET_RATE * 2, true); // bytes per second
    view.setUint16(32, 2, true); // bytes per frame
    view.setUint16(34, 16, true); // bits per sample
    text(36, 'data');
    view.setUint32(40, samples.length * 2, true);
    samples.forEach((sample, i) => {
      const clipped = Math.max(-1, Math.min(1, sample));
      view.setInt16(44 + i * 2, clipped < 0 ? clipped * 0x8000 : clipped * 0x7fff, true);
    });
    return new Blob([view], { type: 'audio/wav' });
  }

  async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true } });
    const context = new AudioContext();
    const source = context.createMediaStreamSource(stream);
    // ScriptProcessor is old but needs no extra worklet file, and every current browser has it.
    const processor = context.createScriptProcessor(4096, 1, 1);
    const chunks = [];
    processor.onaudioprocess = (event) => chunks.push(new Float32Array(event.inputBuffer.getChannelData(0)));
    source.connect(processor);
    processor.connect(context.destination);

    return {
      async stop() {
        processor.disconnect();
        source.disconnect();
        stream.getTracks().forEach((track) => track.stop());
        const rate = context.sampleRate;
        await context.close();
        return encodeWav(downsample(mergeChunks(chunks), rate));
      },
      cancel() {
        processor.disconnect();
        source.disconnect();
        stream.getTracks().forEach((track) => track.stop());
        context.close();
      },
    };
  }

  window.PakkamRecorder = {
    supported: Boolean(navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.AudioContext),
    start,
  };
})();
