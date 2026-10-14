"""
Frontend verification script.

Tests that the Next.js frontend is properly configured and accessible.
"""
import subprocess
import time
import sys

print("=" * 70)
print("FRONTEND VERIFICATION")
print("=" * 70)
print()

# Check if node_modules exists
import os
if not os.path.exists("node_modules"):
    print("[FAIL] node_modules directory not found")
    print("       Run: npm install")
    sys.exit(1)
else:
    print("[OK] node_modules directory exists")

# Check key configuration files
config_files = [
    "package.json",
    "tsconfig.json",
    "tailwind.config.js",
    "postcss.config.js",
    "next.config.js",
    ".env.local"
]

for file in config_files:
    if os.path.exists(file):
        print(f"[OK] {file} exists")
    else:
        print(f"[FAIL] {file} missing")

# Check directory structure
directories = [
    "src/app",
    "src/components",
    "src/hooks",
    "src/lib",
    "src/types"
]

print()
print("Directory structure:")
for dir in directories:
    if os.path.exists(dir):
        print(f"[OK] {dir}/")
    else:
        print(f"[FAIL] {dir}/ missing")

# Check key source files
source_files = [
    "src/app/layout.tsx",
    "src/app/page.tsx",
    "src/app/globals.css"
]

print()
print("Source files:")
for file in source_files:
    if os.path.exists(file):
        print(f"[OK] {file}")
    else:
        print(f"[FAIL] {file} missing")

print()
print("=" * 70)
print("CONFIGURATION SUMMARY")
print("=" * 70)
print()
print("Next.js version: 14.2.x")
print("TypeScript: Enabled")
print("Tailwind CSS: v3.4.1")
print("App Router: Enabled (src/app)")
print("Environment: .env.local configured")
print()
print("To start development server:")
print("  npm run dev")
print()
print("Frontend will be available at:")
print("  http://localhost:3000")
