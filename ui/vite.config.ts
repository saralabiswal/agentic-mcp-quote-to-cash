/* Author: Sarala Biswal */
/* Code documentation: Vite configuration for the React decision-support frontend. */
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { port: 3000 },
});
