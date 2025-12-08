# 🎨 USAR O LOGO ATUAL COMO ÍCONE

## 📋 Passos para Usar o Logo Mostrado

### **Passo 1: Salvar a Imagem do Logo**

Você precisa salvar o logo que mostrou como um arquivo PNG:

1. **Se a imagem está na tela:**
   - Clique com botão direito na imagem
   - Selecione "Salvar imagem como..." ou "Save Image As..."
   - Salve como: `assets/logo_sne.png`
   - **Importante:** Use resolução alta (1024x1024 se possível)

2. **Se a imagem está em outro lugar:**
   - Exporte/salve como PNG
   - Coloque em: `assets/logo_sne.png`

### **Passo 2: Converter para ICNS**

Depois de salvar a imagem, execute:

```bash
./criar_icone.sh assets/logo_sne.png
```

Isso vai:
- ✅ Criar `assets/logo_sne.icns`
- ✅ Atualizar `build_mac.spec` automaticamente
- ✅ Atualizar `build_nuitka.sh` automaticamente

### **Passo 3: Rebuildar o App**

```bash
# Com PyInstaller
./build_with_launcher.sh

# OU com Nuitka (melhor proteção)
./build_nuitka.sh
```

### **Passo 4: Verificar**

```bash
# Ver o ícone criado
open assets/logo_sne.icns

# Testar o app
open dist/SNE_RADAR.app
```

---

## 🎨 Sobre o Logo

O logo que você mostrou tem:
- **Design:** SNE com radar circular em laranja
- **Fundo:** Preto
- **Cores:** Laranja (#FF8C00 ou similar) e preto

**Ideal para ícone:** O design circular do radar funciona muito bem como ícone de app!

---

## ⚠️ Se a Imagem Estiver em Outro Formato

Se você tiver o logo em outro formato (JPG, SVG, etc.):

### **JPG → PNG:**
```bash
# Usando sips (macOS)
sips -s format png imagem.jpg --out assets/logo_sne.png
```

### **SVG → PNG:**
- Use um conversor online ou
- Abra no Preview e exporte como PNG

### **Ajustar Tamanho:**
```bash
# Redimensionar para 1024x1024 (se necessário)
sips -z 1024 1024 assets/logo_sne.png --out assets/logo_sne.png
```

---

## ✅ Checklist

- [ ] Imagem salva em `assets/logo_sne.png`
- [ ] Imagem em formato PNG
- [ ] Tamanho adequado (1024x1024 recomendado)
- [ ] Executado `./criar_icone.sh assets/logo_sne.png`
- [ ] Rebuildado o app
- [ ] Verificado o ícone no Finder/Dock

---

**Pronto!** Depois de seguir esses passos, o logo aparecerá como ícone do app no macOS.

