@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================================
echo   EXPORTADOR DE IMAGENES DOCKER PARA DISTRIBUCION
echo ========================================================
echo.

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
        echo [ERROR] Docker Desktop no esta en ejecucion. Por favor abre Docker Desktop e intenta de nuevo.
        pause
        exit /b 1
    )
)

echo [1/3] Construyendo imagenes actualizadas del proyecto (api e interfaz)...
docker compose build
if %errorlevel% neq 0 (
    echo [ERROR] Fallo la construccion de las imagenes. Verifica que Docker Desktop este corriendo.
    pause
    exit /b 1
)

echo.
echo [2/3] Descargando/verificando imagenes base (MySQL y Gotenberg)...
docker pull mysql:8.0
docker pull gotenberg/gotenberg:8

echo.
echo [3/3] Exportando todas las imagenes a distribucion\pemex_imagenes.tar ...
echo (Esto puede tardar un par de minutos dependiendo de tu disco)
if not exist "distribucion" mkdir distribucion
copy /Y "init.sql" "distribucion\init.sql" >nul
docker save -o distribucion\pemex_imagenes.tar pemex-api:latest pemex-interfaz:latest mysql:8.0 gotenberg/gotenberg:8
if %errorlevel% neq 0 (
    echo [ERROR] Fallo al exportar las imagenes.
    pause
    exit /b 1
)

echo.
echo ========================================================
echo   EXPORTACION COMPLETADA CON EXITO
echo   La carpeta "distribucion" ya esta lista para copiarse
echo   a la maquina del usuario final.
echo ========================================================
pause
