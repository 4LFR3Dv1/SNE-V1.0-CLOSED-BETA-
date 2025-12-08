# 🔧 Como Abrir o App no macOS

Se o app não abrir com duplo clique, siga estes passos:

## ✅ Solução 1: Remover Quarentena (Mais Comum)

O macOS bloqueia apps não assinados. Execute:

```bash
./fix_app_permissions.sh
```

Ou manualmente:

```bash
xattr -dr com.apple.quarantine dist/SNE_RADAR.app
```

## ✅ Solução 2: Abrir via Terminal

```bash
open dist/SNE_RADAR.app
```

Ou:

```bash
./dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

## ✅ Solução 3: Clicar com Botão Direito

1. Clique com botão direito no `SNE_RADAR.app`
2. Selecione "Abrir"
3. Clique em "Abrir" no diálogo de segurança

## ✅ Solução 4: Permitir no Sistema

1. Vá em **Preferências do Sistema** > **Segurança e Privacidade**
2. Se aparecer uma mensagem sobre o app bloqueado
3. Clique em **"Abrir mesmo assim"**

## 🐛 Verificar Logs

Se o app não abrir, verifique os logs:

```bash
# Logs do app
cat ~/Library/Application\ Support/SNE_RADAR/logs/sne_desktop.log

# Ou logs do sistema
log show --predicate 'process == "SNE_RADAR"' --last 5m
```

## 🔍 Testar Executável Direto

```bash
./test_app.sh
```

Isso vai executar o app e mostrar todos os logs no terminal.

---

**Nota:** No macOS, apps não assinados precisam de permissão explícita na primeira execução.


