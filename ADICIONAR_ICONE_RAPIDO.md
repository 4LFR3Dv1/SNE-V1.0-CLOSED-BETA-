# ⚡ ADICIONAR ÍCONE - GUIA RÁPIDO

## 🚀 Passos Rápidos

### 1. Preparar Imagem
```bash
# Coloque sua imagem PNG (1024x1024 recomendado) em:
mkdir -p assets
# Copie: assets/logo_sne.png
```

### 2. Converter para ICNS
```bash
./criar_icone.sh assets/logo_sne.png
```

Isso vai:
- ✅ Criar `assets/logo_sne.icns`
- ✅ Atualizar `build_mac.spec` automaticamente
- ✅ Atualizar `build_nuitka.sh` automaticamente

### 3. Rebuildar
```bash
# Com PyInstaller
./build_with_launcher.sh

# OU com Nuitka
./build_nuitka.sh
```

### 4. Verificar
```bash
# Ver ícone
open assets/logo_sne.icns

# Verificar no app
open dist/SNE_RADAR.app
```

---

## 📋 Requisitos

- **macOS** (para usar `sips` e `iconutil`)
- **Imagem PNG** (1024x1024 pixels recomendado)

---

## 🎨 Se Não Tiver Imagem

Você pode:
1. Criar uma imagem simples com qualquer editor
2. Usar um gerador online de ícones
3. Converter um logo existente

---

**Para mais detalhes:** `COMO_ADICIONAR_ICONE.md`

