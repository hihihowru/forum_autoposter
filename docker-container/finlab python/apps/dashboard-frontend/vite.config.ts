import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8007',  // dashboard-api 端口
        changeOrigin: true,
        secure: false,
      },
      '/trending': {
        target: 'http://localhost:8004',  // trending-api 端口
        changeOrigin: true,
        secure: false,
      },
      '/extract-keywords': {
        target: 'http://localhost:8004',  // trending-api 端口
        changeOrigin: true,
        secure: false,
      },
      '/search-stocks-by-keywords': {
        target: 'http://localhost:8004',  // trending-api 端口
        changeOrigin: true,
        secure: false,
      },
      '/extract-and-search': {
        target: 'http://localhost:8004',  // trending-api 端口
        changeOrigin: true,
        secure: false,
      },
      '/analyze-topic': {
        target: 'http://localhost:8004',  // trending-api 端口
        changeOrigin: true,
        secure: false,
      },
      '/generate-search-strategy': {
        target: 'http://localhost:8004',  // trending-api 端口
        changeOrigin: true,
        secure: false,
      },
      '/generate-content': {
        target: 'http://localhost:8004',  // trending-api 端口
        changeOrigin: true,
        secure: false,
      },
      '/intelligent-extract-keywords': {
        target: 'http://localhost:8004',  // trending-api 端口
        changeOrigin: true,
        secure: false,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
