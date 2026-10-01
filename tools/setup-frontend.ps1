$ErrorActionPreference = "Continue"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
npm create vite@latest frontend -- --template react-ts
Set-Location (Join-Path $root "frontend")
npm install
npm install @tanstack/react-query react-router-dom react-hook-form @hookform/resolvers zod tailwindcss @tailwindcss/vite lucide-react recharts clsx
Write-Host "Frontend scaffolded and dependencies installed."
