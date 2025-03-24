import { defineConfig } from 'vite';
const { defineConfig } = require('vite');
const react = require('@vitejs/plugin-react');


module.exports = defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    watch: {
      usePolling: true,
    },
    hmr: {
      clientPort: 5173,
      host: 'localhost',
    },
  },
  build: {
    rollupOptions: {
      input: '/src/main.jsx',
    },
    outDir: 'dist',
    sourcemap: true,
  },
  preview: {
    port: 5173,
    host: true,
  },
});

export default defineConfig({
  preview: {
    port: process.env.PORT || 4173
  }
})