import { defineConfig } from 'vite';

// https://vitejs.dev/config
export default defineConfig({
  server: {
    watch: {
      // Ignore Python directories to prevent HMR from reloading when pipeline modifies files
      ignored: [
        '**/python/**',
        '**/AI-Tourism-Opinion-Analyzer-Pipeline/**',
      ],
    },
  },
});
