@echo off
echo Which game do you want to play?
echo 1. Space Shooter
echo 2. Brick Breaker
echo 3. Flappy Bird
echo 4. Snake
echo 5. City Builder
set /p choice=Enter number (1-5):

if "%choice%"=="1" .venv313\Scripts\python.exe shooter.py
if "%choice%"=="2" .venv313\Scripts\python.exe bricks.py
if "%choice%"=="3" .venv313\Scripts\python.exe main.py
if "%choice%"=="4" .venv313\Scripts\python.exe snake.py
if "%choice%"=="5" .venv313\Scripts\python.exe city.py
