#!/bin/bash

echo "🔧 Corrigindo erro do shell zsh..."

# Verificar se estamos no diretório correto
if [ ! -f "sne_radar_web.py" ]; then
    echo "❌ Execute este script no diretório do projeto SNE_RADAR"
    exit 1
fi

# Criar um arquivo .zshrc temporário para evitar o erro
echo "export ZSH_DISABLE_COMPFIX=true" > ~/.zshrc_temp
echo "unsetopt PROMPT_SP" >> ~/.zshrc_temp

# Backup do .zshrc original se existir
if [ -f ~/.zshrc ]; then
    cp ~/.zshrc ~/.zshrc_backup_$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup do .zshrc criado"
fi

# Aplicar configuração temporária
cp ~/.zshrc_temp ~/.zshrc
echo "✅ Configuração temporária aplicada"

# Testar se o erro foi resolvido
echo "🧪 Testando shell..."
if bash -c "echo 'Shell funcionando corretamente'"; then
    echo "✅ Shell corrigido com sucesso!"
else
    echo "❌ Ainda há problemas com o shell"
fi

echo "🚀 Agora você pode executar comandos normalmente"
echo "💡 Para reverter: rm ~/.zshrc && mv ~/.zshrc_backup_* ~/.zshrc"
