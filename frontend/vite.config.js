import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['vue', 'vue-router', 'pinia'],
          'charts': ['lightweight-charts'],
          'three': ['three']
        }
      }
    }
  },
  server: {
    port: 5173,
    strictPort: false,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:9999',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path,
        configure: (proxy, _options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('🔄 [Vite Proxy] Proxying:', req.method, req.url, '→', `http://localhost:9999${req.url}`)
          })
          proxy.on('proxyRes', (proxyRes, req, res) => {
            console.log('✅ [Vite Proxy] Response:', proxyRes.statusCode, req.url)
          })
          proxy.on('error', (err, req, res) => {
            console.error('❌ [Vite Proxy] Error:', err.message)
          })
        }
      },
      '/socket.io': {
        target: 'http://localhost:9999',
        ws: true,
        changeOrigin: true
      }
    }
  }
})

