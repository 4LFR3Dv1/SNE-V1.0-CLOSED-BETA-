# 🔧 Troubleshooting - Janela Não Abre

## Problema
O servidor Flask inicia, mas a janela do pywebview não aparece.

## ✅ Soluções

### 1. Verificar se pywebview está funcionando

Execute o script de debug:

```bash
python3 sne_desktop_debug.py
```

Isso vai testar se o pywebview consegue criar janelas no seu sistema.

### 2. Executar com console visível

O app foi buildado com `console=True` para mostrar erros. Execute:

```bash
./dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

Isso vai mostrar todos os logs e erros no terminal.

### 3. Verificar permissões do macOS

```bash
# Remover quarentena
xattr -dr com.apple.quarantine dist/SNE_RADAR.app

# Dar permissões
chmod +x dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

### 4. Verificar se o servidor está rodando

Abra no navegador manualmente:

```bash
open http://127.0.0.1:9999
```

Se abrir no navegador, o problema é só com o pywebview.

### 5. Problema conhecido: pywebview no macOS

O pywebview pode ter problemas no macOS em certas versões. Alternativas:

#### Opção A: Usar modo desenvolvimento

```bash
# Terminal 1
cd frontend && npm run dev

# Terminal 2  
python3 sne_desktop.py
```

#### Opção B: Abrir no navegador como fallback

O código já tem fallback automático - se a janela não abrir, abre no navegador.

#### Opção C: Usar Electron (mais robusto)

Se pywebview continuar dando problema, podemos migrar para Electron.

### 6. Verificar logs

```bash
# Logs do app
cat ~/Library/Application\ Support/SNE_RADAR/logs/error.log

# Logs do sistema macOS
log show --predicate 'process == "SNE_RADAR"' --last 5m
```

### 7. Testar pywebview isoladamente

```python
import webview
webview.create_window('Teste', 'https://www.google.com')
webview.start()
```

Se isso não funcionar, o problema é com a instalação do pywebview.

## 🔍 Diagnóstico Rápido

Execute este comando e me mostre a saída:

```bash
python3 -c "
import webview
import sys
print('pywebview:', webview.__version__ if hasattr(webview, '__version__') else 'OK')
print('Python:', sys.version)
import platform
print('macOS:', platform.mac_ver())
"
```

## 💡 Solução Temporária

Enquanto isso, você pode usar o app via navegador:

1. Execute: `python3 sne_desktop.py`
2. Abra manualmente: `open http://127.0.0.1:9999`
3. Ou use o fallback automático que já está no código

---

**Status:** Investigando problema com pywebview no macOS bundle


