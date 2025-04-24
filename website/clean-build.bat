@echo off
echo === EGOS Clean Build ===
echo Cleaning up and rebuilding the website...

echo Removing node_modules/.cache...
if exist "node_modules\.cache" rmdir /s /q "node_modules\.cache"

echo Removing .next directory...
if exist ".next" rmdir /s /q ".next"

echo Running npm build...
npm run build

echo === Build Complete ===
