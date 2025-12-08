# 🚀 Como Abrir o SNE RADAR.app

## ✅ Método 1: Via Terminal (SEMPRE FUNCIONA)

```bash
./dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

**Ou simplesmente:**

```bash
open dist/SNE_RADAR.app
```

## ✅ Método 2: Duplo Clique (Após Configuração)

### Passo 1: Executar script de fix

```bash
./fix_double_click.sh
```

### Passo 2: Tentar duplo clique

- Clique duas vezes no `SNE_RADAR.app`

### Se não abrir:

1. **Clique com BOTÃO DIREITO** no app
2. Selecione **"Abrir"**
3. No diálogo de segurança, clique em **"Abrir"**

Isso é necessário na **primeira vez** porque o macOS bloqueia apps não assinados.

## ✅ Método 3: Arrastar para Applications

1. Arraste `SNE_RADAR.app` para a pasta **Applications**
2. Abra pelo Launchpad ou Applications
3. Na primeira vez, pode pedir permissão - clique em **"Abrir"**

## ✅ Método 4: Criar Atalho no Dock

1. Execute o app via terminal uma vez
2. O ícone aparecerá no Dock
3. Clique com botão direito no ícone do Dock
4. Selecione **"Opções" > "Manter no Dock"**

## 🔧 Se Nada Funcionar

### Verificar permissões:

```bash
# Ver atributos
xattr -l dist/SNE_RADAR.app

# Remover quarentena manualmente
xattr -dr com.apple.quarantine dist/SNE_RADAR.app

# Dar permissões
chmod +x dist/SNE_RADAR.app/Contents/MacOS/SNE_RADAR
```

### Permitir no Sistema:

1. Vá em **Preferências do Sistema** > **Segurança e Privacidade**
2. Se aparecer mensagem sobre o app bloqueado
3. Clique em **"Abrir mesmo assim"**

## 💡 Solução Definitiva: Criar Launcher

Se quiser que funcione sempre com duplo clique, podemos criar um wrapper script dentro do .app que garante a execução correta.

---

**Nota:** O app **funciona perfeitamente** via terminal. O problema do duplo clique é apenas uma questão de permissões/segurança do macOS com apps não assinados.


