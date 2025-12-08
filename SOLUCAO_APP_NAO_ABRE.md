# ✅ SOLUÇÃO: SNE_RADAR.app não abre a janela

## 🔍 PROBLEMA IDENTIFICADO

O aplicativo **SNE_RADAR.app** aparece no dock do macOS, mas a janela não abre. O processo está rodando e o servidor Flask funciona, mas a interface gráfica não aparece.

### **Causa Raiz:**
O problema está na **inicialização do NSApplication no macOS**. Quando um app é criado com PyInstaller, o macOS requer uma sequência específica de inicialização:

1. NSApplication deve ser inicializado ANTES de criar janelas
2. A política de ativação deve ser configurada corretamente
3. O app deve ser ativado explicitamente após criar a janela
4. Deve haver um delay adequado para o macOS processar a ativação

---

## ✅ CORREÇÕES APLICADAS

### **1. Inicialização mais robusta do NSApplication**

**Arquivo:** `sne_desktop.py` (linhas ~401-420)

**Mudanças:**
- ✅ Adicionado `app.finishLaunching()` para garantir que o app está completamente inicializado
- ✅ Verificação se o app está rodando antes de inicializar
- ✅ Melhor tratamento de erros

### **2. Ativação melhorada após criar janela**

**Arquivo:** `sne_desktop.py` (linhas ~443-470)

**Mudanças:**
- ✅ Verificação se o app está rodando antes de ativar
- ✅ Delay aumentado de 0.3s para 0.8s (crítico para macOS processar)
- ✅ Melhor logging para debug

### **3. Verificação final antes de webview.start()**

**Arquivo:** `sne_desktop.py` (linhas ~480-490)

**Mudanças:**
- ✅ Verificação final se NSApplication está rodando
- ✅ Tentativa de inicializar se necessário

---

## 🚀 PRÓXIMOS PASSOS

### **1. Rebuildar o aplicativo**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN

# Rebuildar o app com as correções
pyinstaller build_mac_with_launcher.spec --clean
```

### **2. Remover quarentena do macOS (se necessário)**

```bash
xattr -dr com.apple.quarantine dist/SNE_RADAR.app
```

### **3. Testar o aplicativo**

```bash
# Abrir o app
open dist/SNE_RADAR.app

# OU executar diretamente para ver logs
dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

### **4. Verificar logs**

```bash
# Ver logs em tempo real
tail -f ~/Library/Application\ Support/SNE_RADAR/logs/sne_desktop.log
```

**O que procurar nos logs:**
- ✅ "NSApplication inicializado e pronto"
- ✅ "NSApplication finishLaunching() chamado"
- ✅ "App ativado no macOS"
- ✅ "Iniciando webview..."
- ❌ Nenhum erro relacionado a NSApplication

---

## 🧪 TESTES

### **Teste 1: Verificar se o servidor está rodando**

```bash
# Após abrir o app, verificar se o servidor está ativo
curl http://127.0.0.1:9999
```

**Resultado esperado:** Deve retornar HTML da página inicial.

### **Teste 2: Verificar processo**

```bash
ps aux | grep SNE_RADAR | grep -v grep
```

**Resultado esperado:** Deve mostrar o processo rodando.

### **Teste 3: Verificar porta**

```bash
lsof -i :9999
```

**Resultado esperado:** Deve mostrar o processo SNE_RADAR usando a porta 9999.

---

## 🐛 SE AINDA NÃO FUNCIONAR

### **Solução 1: Executar com console visível**

Editar `build_mac_with_launcher.spec`:
```python
console=True,  # Mudar de False para True temporariamente
```

Depois rebuildar:
```bash
pyinstaller build_mac_with_launcher.spec --clean
```

Isso mostrará erros no terminal quando você executar o app.

### **Solução 2: Verificar Console.app do macOS**

1. Abrir **Console.app** (Utilitários)
2. Filtrar por "SNE_RADAR"
3. Procurar por erros relacionados a:
   - NSApplication
   - WebView
   - Permissões
   - Crashes

### **Solução 3: Executar em modo desenvolvimento**

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
python3 sne_desktop.py
```

Se funcionar em modo desenvolvimento mas não como .app, o problema está no bundle do PyInstaller.

### **Solução 4: Verificar permissões**

```bash
# Verificar permissões do executável
ls -la dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR

# Dar permissão de execução (se necessário)
chmod +x dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

### **Solução 5: Verificar Info.plist**

```bash
# Verificar configuração do Info.plist
plutil -p dist/SNE_RADAR.app/Contents/Info.plist | grep -E "CFBundleExecutable|LSUIElement"
```

**Deve mostrar:**
- `CFBundleExecutable` => `SNE_RADAR`
- `LSUIElement` => `0` (0 = mostra no dock, 1 = não mostra)

---

## 📝 RESUMO DAS MUDANÇAS

### **Arquivos modificados:**
1. ✅ `sne_desktop.py` - Correções na inicialização do NSApplication

### **Arquivos criados:**
1. ✅ `DIAGNOSTICO_APP_NAO_ABRE.md` - Documentação detalhada do problema
2. ✅ `SOLUCAO_APP_NAO_ABRE.md` - Este arquivo com instruções

---

## 🎯 RESULTADO ESPERADO

Após rebuildar o app e testar:

1. ✅ O app deve aparecer no dock
2. ✅ A janela deve abrir automaticamente em 2-3 segundos
3. ✅ O dashboard Vue.js deve carregar em `http://127.0.0.1:9999`
4. ✅ Nenhum erro nos logs relacionados a NSApplication ou webview

---

**Última atualização:** 2025-01-02  
**Status:** Correções aplicadas - Aguardando rebuild e teste
