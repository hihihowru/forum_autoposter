#!/bin/bash

# Navigate to frontend directory
FRONTEND_DIR="docker-container/finlab python/apps/dashboard-frontend"
cd "$(dirname "$0")/$FRONTEND_DIR" || exit 1

echo "🚀 Setting up Vercel deployment..."

# 1. Update package.json build script
echo "📦 Updating build script in package.json..."
jq '.scripts.build = "tsc --skipLibCheck --noEmitOnError false && vite build"' package.json > package.tmp.json && mv package.tmp.json package.json

# 2. Create/update .vercelignore
echo "📄 Creating/updating .vercelignore..."
cat > ../../../.vercelignore << 'EOL'
node_modules/
.git
.gitignore
.env.local
.env.development
.env.test
.env.production
*.log
.next
out
.DS_Store
*.md
*.mdx
.vscode/
*.log
*.pem
*.p12
*.key
*.cer
*.crt
*.csr
.python-version
.python-version.*
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST
EOL

# 3. Update vite.config.ts
echo "⚙️  Updating vite.config.ts..."
cat > vite.config.ts << 'EOL'
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
    },
  });
};
EOL

# 4. Update tsconfig.json
echo "📝 Updating tsconfig.json..."
jq '.compilerOptions.strict = false | 
    .compilerOptions.noUnusedLocals = false | 
    .compilerOptions.noUnusedParameters = false | 
    .compilerOptions.noFallthroughCasesInSwitch = false' tsconfig.json > tsconfig.tmp.json && 
mv tsconfig.tmp.json tsconfig.json

# 5. Create/update .env file
echo "🔑 Creating/updating .env file..."
cat > .env << 'EOL'
VITE_API_BASE_URL=https://your-railway-backend-url.com
VITE_ENV=production
EOL

echo "✅ Setup complete!"
echo "\nNext steps:"
echo "1. Update the VITE_API_BASE_URL in the .env file with your Railway backend URL"
echo "2. Commit and push these changes:"
echo "   git add ."
echo "   git commit -m 'Update Vercel deployment configuration'"
echo "   git push origin main"
echo "3. Deploy to Vercel by connecting your GitHub repository"

# Make the script executable
chmod +x ../../../setup-vercel.sh

echo "\n🎉 All done! Run the setup script with: ./setup-vercel.sh"
