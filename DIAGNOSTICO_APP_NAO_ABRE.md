# 🔍 DIAGNÓSTICO: SNE_RADAR.app não abre a janela

## 📊 PROBLEMA IDENTIFICADO

O aplicativo **SNE_RADAR.app** aparece no dock do macOS, mas **não abre a janela** do aplicativo.

### ✅ O que está funcionando:
- ✅ O executável inicia corretamente
- ✅ O servidor Flask está rodando na porta 9999
- ✅ A janela webview é criada com sucesso
- ✅ O processo está ativo no sistema

### ❌ O que não está funcionando:
- ❌ A janela não aparece na tela
- ❌ O usuário não consegue ver a interface

---

## 🔍 CAUSA RAIZ

O problema está relacionado à **inicialização do NSApplication no macOS**. Quando um app é executado via PyInstaller como bundle (.app), o macOS requer que:

1. **NSApplication seja inicializado ANTES de criar qualquer janela**
2. **A política de ativação seja configurada corretamente**
3. **O app seja ativado explicitamente após criar a janela**

O código atual tenta fazer isso, mas há um problema de **timing** e **ordem de execução**.

---

## 🛠️ SOLUÇÃO

### **Problema 1: NSApplication não está sendo inicializado na ordem correta**

**Localização:** `sne_desktop.py` linhas 401-420

**Problema:** O NSApplication é inicializado, mas pode não estar pronto quando `webview.start()` é chamado.

**Solução:** Garantir que o NSApplication seja inicializado e configurado ANTES de qualquer operação de janela.

### **Problema 2: webview.start() pode estar sendo chamado muito cedo**

**Localização:** `sne_desktop.py` linha 458

**Problema:** `webview.start()` pode ser chamado antes do NSApplication estar completamente pronto.

**Solução:** Adicionar delay e verificação antes de chamar `webview.start()`.

### **Problema 3: Falta de tratamento de erros específicos do macOS**

**Problema:** Se houver erro na inicialização do NSApplication, o código continua e tenta criar a janela mesmo assim.

**Solução:** Adicionar tratamento de erros mais robusto e fallback.

---

## ✅ CORREÇÕES APLICADAS

### **1. Inicialização mais robusta do NSApplication**

```python
# Inicializar NSApplication ANTES de qualquer coisa no macOS
if platform.system() == 'Darwin':
    import AppKit
    app = AppKit.NSApplication.sharedApplication()
    
    # CRÍTICO: Configurar política ANTES de qualquer janela
    app.setActivationPolicy_(AppKit.NSApplicationActivationPolicyRegular)
    
    # Garantir que o app está pronto
    app.finishLaunching()
```

### **2. Delay após criar janela e antes de webview.start()**

```python
# Criar janela
window = create_window()

# Ativar app no macOS
if platform.system() == 'Darwin':
    app = AppKit.NSApplication.sharedApplication()
    app.activateIgnoringOtherApps_(True)
    
    # Delay crítico para macOS processar a ativação
    time.sleep(0.5)  # Aumentado de 0.3 para 0.5

# AGORA iniciar webview
webview.start(debug=False)
```

### **3. Verificação adicional de thread principal**

```python
# Garantir que estamos na thread principal
if threading.current_thread() != threading.main_thread():
    raise RuntimeError("webview.start() deve ser chamado na thread principal")

# Verificar se NSApplication está pronto (macOS)
if platform.system() == 'Darwin':
    app = AppKit.NSApplication.sharedApplication()
    if not app.isRunning():
        app.finishLaunching()
```

---

## 🧪 TESTES

### **Teste 1: Executar app diretamente**

```bash
/Users/renan/Desktop/SNE_BACKUP_CLEAN/dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

**Resultado esperado:** Janela deve aparecer em 2-3 segundos.

### **Teste 2: Verificar logs**

```bash
tail -f ~/Library/Application\ Support/SNE_RADAR/logs/sne_desktop.log
```

**O que procurar:**
- ✅ "NSApplication inicializado"
- ✅ "App ativado no macOS"
- ✅ "Iniciando webview..."
- ❌ Nenhum erro relacionado a NSApplication ou webview

### **Teste 3: Verificar se servidor está rodando**

```bash
curl http://127.0.0.1:9999
```

**Resultado esperado:** Deve retornar HTML da página inicial.

---

## 🔧 CORREÇÕES ADICIONAIS RECOMENDADAS

### **1. Remover quarentena do macOS (se necessário)**

```bash
xattr -dr com.apple.quarantine /Users/renan/Desktop/SNE_BACKUP_CLEAN/dist/SNE_RADAR.app
```

### **2. Verificar permissões do executável**

```bash
chmod +x /Users/renan/Desktop/SNE_BACKUP_CLEAN/dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

### **3. Rebuildar o app após correções**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
pyinstaller build_mac_with_launcher.spec --clean
```

---

## 📝 PRÓXIMOS PASSOS

1. ✅ Aplicar correções no código `sne_desktop.py`
2. ✅ Rebuildar o app
3. ✅ Testar se a janela aparece
4. ✅ Verificar logs para confirmar funcionamento

---

## 🐛 SE AINDA NÃO FUNCIONAR

### **Alternativa 1: Executar com console visível**

Editar `build_mac_with_launcher.spec`:
```python
console=True,  # Mudar de False para True temporariamente
```

Isso mostrará erros no terminal.

### **Alternativa 2: Verificar Console.app do macOS**

1. Abrir **Console.app** (Utilitários)
2. Filtrar por "SNE_RADAR"
3. Procurar por erros relacionados a:
   - NSApplication
   - WebView
   - Permissões

### **Alternativa 3: Executar em modo desenvolvimento**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
python3 sne_desktop.py
```

Se funcionar em modo desenvolvimento mas não como .app, o problema está no bundle do PyInstaller.

---

**Última atualização:** 2025-01-02



