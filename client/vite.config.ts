import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Dev: forward WebSocket to the Python backend
      '/ws': {
        target: 'ws://localhost:8000',
        ws: true,
      },
    },
  },
})
