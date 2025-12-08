# 🚀 Launcher Wrapper - Solução Definitiva

## O que é?

O launcher é um script wrapper que garante que o app funcione corretamente quando aberto com **duplo clique** no macOS.

## Como Funciona?

1. **macOS executa** `launcher.sh` quando você clica duas vezes
2. **Launcher verifica** se tudo está correto
3. **Launcher executa** o binário Python compilado
4. **Launcher trata erros** e mostra diálogos se necessário

## 🏗️ Build com Launcher

### Opção 1: Build Automático (Recomendado)

```bash
./build_with_launcher.sh
```

Isso vai:
- ✅ Buildar o frontend
- ✅ Criar o executável
- ✅ Configurar o launcher
- ✅ Remover quarentena

### Opção 2: Build Manual

```bash
# 1. Garantir que launcher.sh tem permissão
chmod +x launcher.sh

# 2. Buildar
python3 -m PyInstaller build_mac_with_launcher.spec --clean --noconfirm

# 3. Configurar launcher
cp launcher.sh dist/SNE_RADAR.app/Contents/MacOS/launcher.sh
chmod +x dist/SNE_RADAR.app/Contents/MacOS/launcher.sh

# 4. Remover quarentena
xattr -dr com.apple.quarantine dist/SNE_RADAR.app
```

## ✅ Testar

Após o build, teste:

1. **Duplo clique** no `SNE_RADAR.app` - deve funcionar!
2. Se não funcionar, **botão direito > Abrir** (primeira vez)

## 📝 Logs

O launcher cria logs em:

```
~/Library/Application Support/SNE_RADAR/logs/launcher.log
```

Isso ajuda a diagnosticar problemas.

## 🔧 Como o Launcher Funciona

O `launcher.sh`:

1. **Detecta** o diretório do app automaticamente
2. **Verifica** se o executável existe
3. **Configura** variáveis de ambiente
4. **Executa** o app Python
5. **Trata erros** e mostra diálogos no macOS

## 🎯 Vantagens

- ✅ **Funciona com duplo clique** sempre
- ✅ **Trata erros** graciosamente
- ✅ **Logs** para debug
- ✅ **Diálogos** informativos no macOS
- ✅ **Compatível** com todas as versões do macOS

## 🐛 Troubleshooting

### Launcher não executa

Verifique permissões:

```bash
chmod +x dist/SNE_RADAR.app/Contents/MacOS/launcher.sh
```

### Info.plist não está correto

Verifique se `CFBundleExecutable` aponta para `launcher.sh`:

```bash
cat dist/SNE_RADAR.app/Contents/Info.plist | grep CFBundleExecutable
```

Deve mostrar: `<string>launcher.sh</string>`

### App não abre

1. Verifique logs: `cat ~/Library/Application\ Support/SNE_RADAR/logs/launcher.log`
2. Execute manualmente: `./dist/SNE_RADAR.app/Contents/MacOS/launcher.sh`

---

**Status:** ✅ Solução definitiva implementada!


