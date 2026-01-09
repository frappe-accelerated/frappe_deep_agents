import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import Icons from 'unplugin-icons/vite'

export default defineConfig({
  plugins: [
    vue(),
    Icons({
      compiler: 'vue3',
    }),
  ],
  base: '/assets/frappe_deep_agents/frontend/',
  build: {
    outDir: '../frappe_deep_agents/public/frontend',
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      output: {
        manualChunks: {
          'frappe-ui': ['frappe-ui'],
          'socket': ['socket.io-client'],
          'markdown': ['marked', 'highlight.js']
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 8081,
    proxy: {
      '^/(api|assets|files)': {
        target: 'http://localhost:8000',
        ws: true,
        router: function (req) {
          const site_name = req.headers.host.split(':')[0]
          return `http://${site_name}:8000`
        }
      },
      '/socket.io': {
        target: 'http://localhost:9000',
        ws: true
      }
    }
  }
})
