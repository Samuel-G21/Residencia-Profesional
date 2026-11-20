@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================================
echo   INSTALADOR / ACTUALIZADOR DEL SISTEMA PEMEX (DOCKER)
echo ========================================================
echo.

if not exist "pemex_imagenes.tar" (
    echo [ERROR] No se encontro el archivo pemex_imagenes.tar en esta carpeta.
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\Docker\Docker\Docker Desktop.exe" (
        echo [INFO] Iniciando Docker Desktop automaticamente, espera unos segundos...
        start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
        :wait_docker
        timeout /t 5 /nobreak >nul
        docker info >nul 2>&1
        if %errorlevel% neq 0 goto wait_docker
        echo [OK] Docker Desktop listo.
        echo.
    ) else (
        echo [ERROR] Docker Desktop no esta abierto. Por favor abre Docker Desktop e intenta de nuevo.
        pause
        exit /b 1
    )
)

echo [1/2] Cargando imagenes de Docker (esto puede tardar unos minutos)...
docker load -i pemex_imagenes.tar
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la carga de imagenes. Verifica que Docker Desktop este abierto.
    pause
    exit /b 1
)

echo.
echo [2/2] Iniciando y actualizando los contenedores del sistema...
docker compose up -d --force-recreate
if %errorlevel% neq 0 (
    echo [ERROR] No se pudieron iniciar los contenedores.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   SISTEMA INICIADO Y ACTUALIZADO CORRECTAMENTE
echo   Abre en tu navegador: http://localhost:3000
echo ========================================================
pause
