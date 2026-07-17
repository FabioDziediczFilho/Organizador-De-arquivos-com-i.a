# Contexto do Projeto - Organizador de Arquivos com IA

## 📅 Data: 17/07/2026
## 👤 Desenvolvedor: Seu Nome (Freelancer)

## 🎯 Status Atual: INÍCIO DO PROJETO

### ✅ O que já foi feito:

1. **Planejamento completo** - Plano detalhado criado em `.windsurf/plans/plano-organizador-arquivos-9bd319.md`
2. **Estrutura de diretórios** - Criada a seguinte estrutura:
   ```
   organizador-de-arquivos/
   ├── src/
   │   ├── gui/
   │   ├── core/
   │   ├── ai/
   │   └── utils/
   ├── tests/
   └── logs/
   ```
3. **requirements.txt** - Criado com dependências iniciais:
   - Pillow (manipulação de imagens)
   - requests (cliente HTTP para Ollama)
   - pytest (testes)
4. **README.md** - Documentação inicial do projeto

### ⏳ O que precisa ser feito AGORA (Próximos passos imediatos):

#### Passo 1: Criar arquivos __init__.py
Você precisa criar estes arquivos VAZIOS nas respectivas pastas:
- `src/__init__.py`
- `src/gui/__init__.py`
- `src/core/__init__.py`
- `src/ai/__init__.py`
- `src/utils/__init__.py`

**Por que?** Para tornar os diretórios em pacotes Python importáveis.

#### Passo 2: Criar módulo de extensões
Arquivo: `src/core/extensions.py`

Este módulo definirá:
- Extensões suportadas: .jpg, .jpeg, .png, .mp4
- Mapeamento extensão → categoria
- Função para detectar tipo de arquivo

**Código base para começar:**
```python
# src/core/extensions.py

# Extensões suportadas e suas categorias
EXTENSIONS_MAP = {
    '.jpg': 'imagem',
    '.jpeg': 'imagem',
    '.png': 'imagem',
    '.mp4': 'video'
}

def get_file_category(file_path: str) -> str:
    """Retorna a categoria do arquivo baseado na extensão."""
    import os
    _, ext = os.path.splitext(file_path)
    return EXTENSIONS_MAP.get(ext.lower(), 'desconhecido')

def get_supported_extensions() -> list:
    """Retorna lista de extensões suportadas."""
    return list(EXTENSIONS_MAP.keys())
```

#### Passo 3: Criar scanner de arquivos
Arquivo: `src/core/file_scanner.py`

Este módulo irá:
- Escanear diretório recursivamente
- Filtrar arquivos por extensões suportadas
- Retornar lista com metadados

#### Passo 4: Criar organizador de arquivos
Arquivo: `src/core/file_organizer.py`

Este módulo irá:
- Mover arquivos para pastas por categoria
- Criar estrutura de pastas se não existir
- Tratar conflitos de nomes

#### Passo 5: Criar GUI básica
Arquivo: `src/gui/main_window.py`

Interface com:
- Seleção de diretório
- Botão para escanear
- Lista de arquivos encontrados
- Botão para organizar

## 🎓 Conceitos que você vai aprender:

1. **Modularização em Python** - Separar código em módulos reutilizáveis
2. **tkinter** - Biblioteca padrão para GUI em Python
3. **Manipulação de arquivos** - os, shutil, pathlib
4. **Type hints** - Anotações de tipo para melhor código
5. **Logging** - Registrar operações para debug e undo
6. **API REST** - Integração com Ollama via HTTP
7. **Docker** - Containerização do Ollama
8. **Visão computacional** - Análise de imagens com IA

## 🤖 Integração com Cascade (IA Assistente)

### Como usar a Cascade no seu PC pessoal:

1. **Instale a Cascade** no seu IDE (VS Code, Windsurf, etc.)
2. **Abra este projeto** no seu PC
3. **Use este arquivo de contexto** para explicar onde parou
4. **Peça à Cascade para continuar** a partir do passo onde parou

### Comandos úteis para a Cascade:

- "Continuar a partir do Passo 2 do contexto"
- "Me ajude a criar o módulo extensions.py"
- "Explique como funciona o get_file_category"
- "Como testar o módulo de extensões?"
- "O que vem depois do file_organizer?"

## 📝 Notas importantes:

- **Python 3.10+** é necessário
- **Ambiente virtual** recomendado: `python -m venv venv`
- **Ative o venv** antes de instalar: `venv\Scripts\activate`
- **Instale dependências**: `pip install -r requirements.txt`

## 🔗 Arquivos de referência:

- **Plano completo**: `.windsurf/plans/plano-organizador-arquivos-9bd319.md`
- **README**: `README.md`
- **Dependências**: `requirements.txt`

## 💡 Dicas para continuar:

1. **Um passo de cada vez** - Não tente fazer tudo de uma vez
2. **Teste cada módulo** - Crie pequenos testes para validar
3. **Peça ajuda à Cascade** - Use a IA para explicar conceitos
4. **Documente seu progresso** - Atualize este arquivo conforme avança
5. **Commit frequentemente** - Use git para salvar progresso

## 🚀 Próximo passo quando voltar:

1. Criar os arquivos `__init__.py` vazios
2. Criar `src/core/extensions.py` com o código base acima
3. Testar o módulo de extensões
4. Pedir à Cascade para continuar com `file_scanner.py`

---

**Última atualização**: 17/07/2026 - Estrutura base criada, aguardando criação dos __init__.py e módulo extensions.py
