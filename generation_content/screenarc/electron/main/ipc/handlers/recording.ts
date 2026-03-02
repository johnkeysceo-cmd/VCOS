// Handlers for recording-related IPC (recording).

import { startRecording, loadVideoFromFile, stopRecording } from '../../features/recording-manager'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function handleStartRecording(_event: any, options: any) {
  return startRecording(options)
}

export function handleLoadVideoFromFile() {
  return loadVideoFromFile()
}

export async function handleStopRecording() {
  await stopRecording()
}
