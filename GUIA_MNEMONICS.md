# 🔐 Guia de Uso - Gerador de Mnemonics

Script para gerar e validar mnemonics (seed phrases) válidos seguindo o padrão BIP39.

## 📦 Instalação

Primeiro, instale a dependência necessária:

```bash
pip install mnemonic
```

Ou instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

### Modo Interativo (Recomendado)

Execute o script sem argumentos:

```bash
python3 gerar_mnemonics.py
```

Você verá um menu com as seguintes opções:
- **1**: Gerar 1 mnemonic de 12 palavras
- **2**: Gerar 1 mnemonic de 24 palavras
- **3**: Gerar múltiplos mnemonics
- **4**: Validar um mnemonic existente
- **5**: Sair

### Modo Linha de Comando

#### Gerar um mnemonic de 12 palavras:
```bash
python3 gerar_mnemonics.py --gerar 12
```

#### Gerar um mnemonic de 24 palavras:
```bash
python3 gerar_mnemonics.py --gerar 24
```

#### Gerar múltiplos mnemonics:
```bash
python3 gerar_mnemonics.py --gerar 12 --qtd 5
```

#### Validar um mnemonic:
```bash
python3 gerar_mnemonics.py --validar "palavra1 palavra2 palavra3 ..."
```

#### Ver ajuda:
```bash
python3 gerar_mnemonics.py --help
```

## 📝 Exemplos

### Exemplo 1: Gerar um mnemonic de 12 palavras
```bash
$ python3 gerar_mnemonics.py --gerar 12
abandon ability able about above absent absorb abstract absurd abuse access accident
```

### Exemplo 2: Gerar 3 mnemonics de 24 palavras
```bash
$ python3 gerar_mnemonics.py --gerar 24 --qtd 3
```

### Exemplo 3: Validar um mnemonic
```bash
$ python3 gerar_mnemonics.py --validar "abandon ability able about above absent absorb abstract absurd abuse access accident"
✅ MNEMONIC VÁLIDO
```

## ⚠️ Segurança

**IMPORTANTE:**
- Guarde seus mnemonics em local seguro
- Nunca compartilhe seus mnemonics
- Use geradores criptograficamente seguros (este script usa `secrets` do Python)
- Faça backup físico dos seus mnemonics

## 🔧 Uso Programático

Você também pode importar as funções em outros scripts:

```python
from gerar_mnemonics import gerar_mnemonic, validar_mnemonic

# Gerar um mnemonic
mnemonic = gerar_mnemonic(12)
print(mnemonic)

# Validar um mnemonic
if validar_mnemonic(mnemonic):
    print("Válido!")
```

## 📚 Sobre BIP39

Os mnemonics gerados seguem o padrão BIP39 (Bitcoin Improvement Proposal 39), que é amplamente usado em carteiras de criptomoedas. Cada mnemonic representa uma seed criptográfica que pode ser usada para derivar chaves privadas.

- **12 palavras**: 128 bits de entropia
- **24 palavras**: 256 bits de entropia




