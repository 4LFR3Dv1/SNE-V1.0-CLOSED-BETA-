# 🖥️ SNE RADAR - Modo Desktop Nativo

Transforme o SNE RADAR em uma **aplicação desktop nativa** usando `pywebview`.

---

## 🚀 Início Rápido

### Opção 1: Build Automático (RECOMENDADO)

```bash
# Script que verifica tudo e builda automaticamente
./build_auto.sh
```

Isso vai:
- ✅ Verificar todos os pré-requisitos
- ✅ Instalar dependências faltantes
- ✅ Buildar o frontend automaticamente
- ✅ Criar o executável `.app` standalone

**O executável final NÃO precisa de:**
- ❌ Python instalado
- ❌ Node.js instalado  
- ❌ Dependências instaladas
- ✅ **TUDO está incluído no executável!**

### Opção 2: Build Manual

```bash
# 1. Instalar dependências
pip install pywebview pyinstaller

# 2. Build executável (builda frontend automaticamente)
./build_standalone.sh
```

### Opção 3: Testar Sem Compilar (Desenvolvimento)

```bash
# 1. Buildar frontend primeiro
cd frontend
npm install
npm run build
cd ..

# 2. Executar
python3 sne_desktop.py
```

Isso vai:
- ✅ Iniciar o servidor Flask em background
- ✅ Abrir uma janela nativa do macOS
- ✅ Carregar o dashboard Vue.js
- ✅ **Sem barra de endereço, sem botões de navegador**

---

## 🎨 Personalização

### Visual "Cyberpunk" (Frameless)

Para remover a barra de título e criar um visual futurista:

1. Edite `sne_desktop.py`
2. Descomente a linha `frameless=True`
3. Adicione botões de fechar/minimizar no Vue.js

```python
window = webview.create_window(
    title='SNE RADAR',
    url='http://127.0.0.1:9999',
    width=1400,
    height=900,
    frameless=True,  # <-- Visual Cyberpunk
    easy_drag=True,  # <-- Permite arrastar a janela
    # ...
)
```

### Tamanho da Janela

Ajuste `width` e `height` em `sne_desktop.py`:

```python
width=1920,   # Largura
height=1080,  # Altura
min_size=(1024, 768),  # Tamanho mínimo
```

### Ícone da Aplicação

1. Crie um arquivo `.icns` (macOS) ou `.ico` (Windows)
2. Coloque em `assets/logo_sne.icns`
3. Atualize `build_mac.spec`:

```python
icon='assets/logo_sne.icns',
```

---

## 🔧 Troubleshooting

### Erro: "pywebview não instalado"

```bash
pip install pywebview
```

### Erro: "Frontend não encontrado"

```bash
cd frontend
npm run build
cd ..
```

### Erro: "Servidor não responde"

- Verifique se a porta 9999 está livre
- Verifique os logs em `logs/`
- Tente mudar a porta em `sne_desktop.py`

### Janela não abre

- Execute com `python3 sne_desktop.py` e veja os logs
- Verifique se o Flask está rodando: `curl http://127.0.0.1:9999`

### Build falha

- Certifique-se de que o frontend foi buildado
- Verifique se todas as dependências estão instaladas
- Tente: `pyinstaller build_mac.spec --clean`

---

## 📦 Distribuição

### macOS

```bash
# Build
./build_standalone.sh

# Criar ZIP para distribuição
cd dist
zip -r SNE_RADAR_macOS_v1.0.0.zip SNE_RADAR.app
```

### Windows (Futuro)

Crie `build_windows.spec` similar ao `build_mac.spec` mas com:

```python
exe = EXE(
    # ...
    console=False,
    icon='assets/logo_sne.ico',
)
```

### Linux

O script `build_standalone.sh` já detecta Linux e cria executável.

---

## 🎯 Diferenças do Modo Web

| Característica | Modo Web | Modo Desktop |
|----------------|----------|--------------|
| Barra de endereço | ✅ Sim | ❌ Não |
| Botões navegador | ✅ Sim | ❌ Não |
| Abas | ✅ Sim | ❌ Não |
| Ícone na Dock | ❌ Não | ✅ Sim |
| Janela dedicada | ❌ Não | ✅ Sim |
| Experiência | Site | App Nativo |

---

## 🚀 Próximos Passos

1. ✅ Adicionar auto-atualização
2. ✅ Criar ícone profissional
3. ✅ Adicionar notificações desktop
4. ✅ Implementar menu nativo (File, Edit, etc.)
5. ✅ Adicionar atalhos de teclado

---

**Status:** ✅ Funcional - Pronto para uso!

