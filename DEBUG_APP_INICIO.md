# 🔍 DEBUG: App Não Inicia Automaticamente

## ✅ Correções Aplicadas

1. **Logs detalhados** adicionados em `start_background_services()`
2. **Configuração de path** melhorada para modo bundle
3. **Tratamento de erros** mais robusto

## 🧪 Como Testar

### 1. Rebuildar o App

```bash
cd /Users/renan/Desktop/SNE_BACKUP_CLEAN
./build_completo.sh
```

### 2. Verificar Logs ao Abrir o App

Quando abrir o app, os logs devem aparecer em:

```bash
# Ver logs em tempo real
tail -f ~/Library/Application\ Support/SNE_RADAR/logs/scanner.log

# Ou verificar se há arquivo de log do desktop
ls -la ~/Library/Application\ Support/SNE_RADAR/logs/
```

### 3. Verificar se Monitor Está Rodando

**Via Terminal:**
```bash
# Verificar status
curl http://127.0.0.1:9999/api/v1/notifications/monitor/status

# Ver estatísticas
curl http://127.0.0.1:9999/api/v1/notifications/stats
```

**Via Interface:**
1. Abra o app
2. Acesse: `http://127.0.0.1:9999/wick-radar`
3. Verifique se mostra "Monitor Ativo"

## 🔍 Troubleshooting

### Se o Monitor Não Iniciar

1. **Verificar logs:**
   ```bash
   # Ver últimos logs
   tail -50 ~/Library/Application\ Support/SNE_RADAR/logs/scanner.log
   ```

2. **Verificar se módulos estão no bundle:**
   ```bash
   # Verificar estrutura do app
   ls -la dist/SNE_RADAR.app/Contents/Resources/
   
   # Deve mostrar:
   # - monitors/
   # - scanners/
   # - notifications/
   ```

3. **Testar importação manual:**
   ```bash
   # Executar dentro do bundle
   cd dist/SNE_RADAR.app/Contents/MacOS
   ./SNE_RADAR
   
   # Ver mensagens de erro no terminal
   ```

### Se o App Não Abrir

1. **Verificar permissões:**
   ```bash
   chmod +x dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
   ```

2. **Remover quarentena:**
   ```bash
   xattr -dr com.apple.quarantine dist/SNE_RADAR.app
   ```

3. **Assinar novamente:**
   ```bash
   codesign --force --deep --sign - dist/SNE_RADAR.app
   ```

## 📊 O Que Esperar

### Logs Esperados ao Iniciar:

```
🔄 Tentando importar OpportunityMonitor...
   ROOT_DIR: /path/to/app
   sys.path[0]: /path/to/app
   ✅ Adicionado ao path: /path/to/app
   ✅ OpportunityMonitor importado com sucesso
   ✅ sne_radar_web importado com sucesso
🔄 Criando instância do monitor...
   ✅ Monitor criado com sucesso
   ✅ Monitor compartilhado com sne_radar_web
🔄 Iniciando monitor...
✅ Monitor de oportunidades iniciado em background
   Status: Rodando
```

### Se Ver Erros:

- **ImportError**: Módulos não encontrados no bundle
- **PathError**: Diretórios não encontrados
- **PermissionError**: Problemas de permissão

## 🎯 Próximos Passos

1. **Rebuildar o app** com as correções
2. **Abrir o app** e verificar logs
3. **Verificar status** via API ou interface
4. **Reportar erros** se ainda não funcionar

---

**Status:** ✅ Correções aplicadas  
**Ação:** Rebuildar e testar



