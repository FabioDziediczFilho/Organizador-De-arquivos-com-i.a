@echo off
REM Script de instalação para Organizador de Arquivos com IA
REM Autor: Fábio Dziedicz Filho

echo ========================================
echo Organizador de Arquivos com IA - Instalador
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado. Por favor, instale Python 3.10 ou superior.
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Criar ambiente virtual
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo [OK] Ambiente virtual criado
) else (
    echo [OK] Ambiente virtual ja existe
)

echo.

REM Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao ativar ambiente virtual
    pause
    exit /b 1
)
echo [OK] Ambiente virtual ativado
echo.

REM Atualizar pip
echo [INFO] Atualizando pip...
python -m pip install --upgrade pip
echo [OK] Pip atualizado
echo.

REM Instalar dependências
echo [INFO] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas
echo.

REM Verificar Docker (opcional)
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [AVISO] Docker nao encontrado. IA local (Ollama) nao estara disponivel.
    echo         Para usar IA local, instale Docker Desktop.
) else (
    echo [OK] Docker encontrado
    echo [INFO] Para configurar Ollama, execute: docker-compose up -d
    echo [INFO] Para baixar o modelo, execute: docker^ exec -it ollama ollama pull qwen2-vl:7b
)

echo.
echo ========================================
echo [SUCESSO] Instalacao concluida!
echo ========================================
echo.
echo Para executar o aplicativo:
echo   - Interface PySide6 (Recomendado): python main_pyside6.py
echo   - Interface Tkinter (Legado):     python main.py
echo.
echo Para configurar IA:
echo   - Abra o aplicativo e va em Editar ^> Configuracoes
echo   - Configure Ollama (IA local) ou Gemini (IA cloud)
echo.
pause
