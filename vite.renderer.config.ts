import { defineConfig } from 'vite';
import { readFileSync } from 'fs';

const pkg = JSON.parse(readFileSync('package.json', 'utf-8'));

// https://vitejs.dev/config
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify(pkg.version),
  },
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
