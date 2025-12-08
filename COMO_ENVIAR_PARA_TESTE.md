# 🚀 COMO ENVIAR SNE_RADAR.app PARA TESTE

**Resumo rápido para distribuição segura**

---

## ⚡ OPÇÃO RÁPIDA (Para Enviar Agora)

```bash
# 1. Criar pacote de distribuição
./criar_pacote_distribuicao.sh

# 2. Enviar o arquivo ZIP criado em:
#    dist/SNE_RADAR_DISTRIBUICAO_[data].zip
```

**O pacote inclui:**
- ✅ SNE_RADAR.app
- ✅ EULA (Termos de uso)
- ✅ Instruções de instalação
- ✅ Avisos de propriedade intelectual

---

## 🛡️ OPÇÃO COM MELHOR PROTEÇÃO (Recomendado)

```bash
# 1. Rebuildar com Nuitka (protege melhor o código)
./build_nuitka.sh

# 2. Criar pacote de distribuição
./criar_pacote_distribuicao.sh

# 3. Enviar o arquivo ZIP
```

**Vantagem:** Código compilado para C++ (muito mais difícil de extrair)

**Tempo:** 15-30 minutos

---

## 📋 O QUE ESTÁ PROTEGIDO

### Com PyInstaller (atual):
- ⚠️ Código pode ser extraído (não protege efetivamente)
- ✅ EULA legal protege contra uso indevido
- ✅ Avisos desencorajam engenharia reversa

### Com Nuitka (recomendado):
- ✅ Código compilado para C++ (muito difícil de reverter)
- ✅ EULA legal protege contra uso indevido
- ✅ Múltiplas camadas de proteção

---

## ⚠️ AVISOS IMPORTANTES

**Para o colega:**
- Este é um build de **TESTE**
- **NÃO compartilhar** com terceiros
- **NÃO fazer engenharia reversa**
- **NÃO usar comercialmente** sem autorização

**Para você:**
- PyInstaller não protege código efetivamente
- EULA cria barreira legal
- Nuitka oferece melhor proteção técnica

---

## 📞 PRÓXIMOS PASSOS

1. ✅ Executar `./criar_pacote_distribuicao.sh`
2. ✅ Enviar o ZIP para o colega (WeTransfer, Google Drive, etc.)
3. ✅ Lembrar o colega de ler o EULA antes de usar

---

**Para mais detalhes, veja:** `GUIA_DISTRIBUICAO_SEGURA.md`

