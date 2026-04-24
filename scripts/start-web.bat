@echo off
echo ========================================
echo Starting Endless Canvas Web App
echo ========================================
echo.

cd apps\web

echo Starting Next.js development server...
echo Web app will be available at: http://localhost:3000
echo.

pnpm dev

cd ..\..
