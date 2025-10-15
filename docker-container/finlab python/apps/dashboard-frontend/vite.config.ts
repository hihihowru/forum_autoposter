import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default ({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  
  return defineConfig({
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    define: {
      'process.env': env,
    },
    build: {
      sourcemap: true,
      outDir: 'dist',
      emptyOutDir: true,
    },
    server: {
      port: 3000,
      open: true,
      proxy: {
        '/intraday-trigger': {
          target: 'https://forumautoposter-production.up.railway.app',
          changeOrigin: true,
          secure: true,
        },
      },
    },
  });
};
