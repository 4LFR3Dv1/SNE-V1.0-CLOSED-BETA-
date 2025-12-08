# 🎨 COMO ADICIONAR ÍCONE AO SNE_RADAR.app

Guia completo para adicionar um ícone personalizado ao aplicativo macOS.

---

## 📋 PRÉ-REQUISITOS

1. **Imagem PNG** (recomendado: 1024x1024 pixels)
2. **macOS** (para converter PNG → ICNS)
3. **Script de conversão** (fornecido abaixo)

---

## 🚀 OPÇÃO 1: Usando Script Automático (Recomendado)

### **Passo 1: Preparar Imagem**

Coloque sua imagem PNG na pasta `assets/`:
```bash
mkdir -p assets
# Copie sua imagem para: assets/logo_sne.png (1024x1024 recomendado)
```

### **Passo 2: Converter para ICNS**

Execute o script:
```bash
chmod +x criar_icone.sh
./criar_icone.sh assets/logo_sne.png
```

Isso criará: `assets/logo_sne.icns`

### **Passo 3: Atualizar Build**

O script já atualiza automaticamente os arquivos de build. Se não, edite manualmente:

**Para PyInstaller (`build_mac.spec`):**
```python
icon='assets/logo_sne.icns',  # Linha 124
```

**Para Nuitka (`build_nuitka.sh`):**
```bash
--macos-app-icon=assets/logo_sne.icns \
```

### **Passo 4: Rebuildar**

```bash
# Com PyInstaller
./build_with_launcher.sh

# OU com Nuitka
./build_nuitka.sh
```

---

## 🛠️ OPÇÃO 2: Manual (Usando Iconutil)

### **Passo 1: Criar Estrutura de Ícones**

```bash
mkdir -p assets/logo_sne.iconset
```

### **Passo 2: Criar Tamanhos Necessários**

Você precisa de múltiplos tamanhos. Use o script `criar_icone.sh` ou crie manualmente:

```bash
# Tamanhos necessários para macOS:
# - icon_16x16.png
# - icon_16x16@2x.png (32x32)
# - icon_32x32.png
# - icon_32x32@2x.png (64x64)
# - icon_128x128.png
# - icon_128x128@2x.png (256x256)
# - icon_256x256.png
# - icon_256x256@2x.png (512x512)
# - icon_512x512.png
# - icon_512x512@2x.png (1024x1024)
```

### **Passo 3: Converter para ICNS**

```bash
iconutil -c icns assets/logo_sne.iconset -o assets/logo_sne.icns
```

### **Passo 4: Configurar Build**

Edite `build_mac.spec`:
```python
icon='assets/logo_sne.icns',
```

Edite `build_nuitka.sh`:
```bash
--macos-app-icon=assets/logo_sne.icns \
```

---

## 📝 CONFIGURAÇÃO NOS ARQUIVOS DE BUILD

### **build_mac.spec (PyInstaller)**

```python
app = BUNDLE(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='SNE_RADAR.app',
    icon='assets/logo_sne.icns',  # ← Adicione aqui
    bundle_identifier='com.sne.radar',
    # ... resto da configuração
)
```

### **build_nuitka.sh (Nuitka)**

```bash
python3 -m nuitka \
    --standalone \
    # ... outras opções ...
    --macos-create-app-bundle \
    --macos-app-icon=assets/logo_sne.icns \  # ← Adicione aqui
    --macos-app-name="SNE RADAR" \
    # ... resto da configuração
```

---

## 🎨 ESPECIFICAÇÕES DO ÍCONE

### **Tamanho Recomendado:**
- **1024x1024 pixels** (PNG)
- Formato: PNG com transparência (opcional)

### **Tamanhos Gerados Automaticamente:**
O script `criar_icone.sh` gera automaticamente todos os tamanhos necessários:
- 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
- Versões @2x (Retina) para cada tamanho

### **Dicas de Design:**
- ✅ Use cores vibrantes
- ✅ Mantenha elementos simples (detalhes se perdem em tamanhos pequenos)
- ✅ Teste em diferentes tamanhos
- ✅ Considere fundo transparente ou sólido

---

## ✅ VERIFICAÇÃO

Após rebuildar, verifique:

```bash
# Verificar se ícone foi incluído
ls -la dist/SNE_RADAR.app/Contents/Resources/*.icns

# Verificar Info.plist
plutil -p dist/SNE_RADAR.app/Contents/Info.plist | grep -i icon
```

---

## 🔧 TROUBLESHOOTING

### **Ícone não aparece:**
1. Verifique se o caminho está correto no `.spec` ou `.sh`
2. Verifique se o arquivo `.icns` existe
3. Limpe o build anterior: `rm -rf build/ dist/`
4. Rebuild novamente

### **Ícone aparece pixelado:**
- Use imagem de alta resolução (1024x1024)
- Certifique-se de que todos os tamanhos foram gerados

### **Erro ao converter:**
- Verifique se `iconutil` está disponível (macOS nativo)
- Verifique se a estrutura `.iconset` está correta

---

## 📦 ESTRUTURA FINAL

```
projeto/
├── assets/
│   ├── logo_sne.png          # Imagem original
│   ├── logo_sne.icns         # Ícone final (gerado)
│   └── logo_sne.iconset/     # Tamanhos intermediários (gerado)
├── build_mac.spec            # Configurado com icon='assets/logo_sne.icns'
├── build_nuitka.sh           # Configurado com --macos-app-icon=assets/logo_sne.icns
└── criar_icone.sh            # Script de conversão
```

---

## 🚀 PRÓXIMOS PASSOS

1. ✅ Criar pasta `assets/` (se não existir)
2. ✅ Adicionar sua imagem PNG (1024x1024)
3. ✅ Executar `./criar_icone.sh assets/logo_sne.png`
4. ✅ Rebuildar o app
5. ✅ Verificar o ícone no Finder/Dock

---

**Para mais detalhes, veja:** `criar_icone.sh`

