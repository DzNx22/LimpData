# Serve pra gerar o executável do LimpData a partir do código fonte. Deve ser executado no PowerShell 5.1 ou superior 
# Gera dist\LimpData.exe (arquivo único).
# Uso: .\build.ps1   (com o ambiente virtual criado e requirements-dev instalado)
# Erros são verificados por $LASTEXITCODE: o PyInstaller escreve seu log no
# stderr, o que o PowerShell 5.1 trataria como falha com ErrorAction Stop.
$python = ".\.venv\Scripts\python.exe"

& $python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Testes falharam; build cancelado." }

& $python -m PyInstaller --noconfirm limpdata.spec
if ($LASTEXITCODE -ne 0) { throw "Falha ao gerar o executável." }

Write-Host "Executável gerado em dist\LimpData.exe"
