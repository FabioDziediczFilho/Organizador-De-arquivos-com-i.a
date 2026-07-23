# Organizador de Arquivos com IA

Organizador de arquivos inteligente em Python com interface gráfica moderna (PySide6 + Fluent Design) que utiliza IA local (Ollama + Qwen2-VL) e Google Gemini para categorizar e renomear arquivos automaticamente por contexto.

## 🎯 Objetivo

Aplicação desktop moderna para organizar imagens (.jpg, .jpeg, .png, .gif, .bmp, .webp) usando IA para analisar contexto e criar pastas temáticas (ex: "imagens_casamento"), com interface PySide6 com Fluent Design, sistema de undo e suporte a múltiplos provedores de IA.

## 🚀 Funcionalidades

- [x] Organização por extensão de arquivo
- [x] Interface gráfica moderna com PySide6 e Fluent Design
- [x] Preview de arquivos (imagens com zoom e fit-to-window)
- [x] Sistema de confirmação antes de ações
- [x] Barra de progresso durante operações
- [x] Resumo de operações realizadas
- [x] Sistema de undo com histórico completo
- [x] Integração com Ollama (Docker)
- [x] Integração com Google Gemini AI
- [x] Análise de contexto com Qwen2-VL (7B)
- [x] Renomeamento inteligente baseado em descrição
- [x] Organização por contexto (ex: casamento, praia, trabalho)
- [x] Múltipla seleção de arquivos
- [x] Chat interativo com IA
- [x] Configurações personalizáveis
- [x] Animações e transições suaves
- [x] Suporte a acessibilidade
- [x] Otimizações de performance

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Docker e Docker Compose (para Ollama)
- Windows 10/11
- Chave API Google Gemini (opcional)

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/FabioDziediczFilho/Organizador-De-arquivos-com-i.a.git
cd Organizador-De-arquivos-com-i.a
```

### 2. Crie ambiente virtual

```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Instale dependências

```bash
pip install -r requirements.txt
```

### 4. Configure Ollama com Docker (Opcional - para IA local)

```bash
docker-compose up -d
```

### 5. Baixe o modelo Qwen2-VL (Opcional - para IA local)

```bash
docker exec -it ollama ollama pull qwen2-vl:7b
```

### 6. Configure Google Gemini (Opcional - para IA cloud)

Obtenha uma API key em https://ai.google.dev/ e configure no aplicativo.

## 📁 Estrutura do Projeto

```
organizador-de-arquivos/
├── main.py                    # Ponto de entrada (Tkinter)
├── main_pyside6.py            # Ponto de entrada (PySide6)
├── requirements.txt           # Dependências
├── README.md                  # Este arquivo
├── docker-compose.yml         # Configuração Ollama
├── src/
│   ├── ui/                    # Interface gráfica PySide6
│   │   ├── main_window.py     # Janela principal
│   │   ├── settings_dialog.py # Dialog de configurações
│   │   └── components/        # Componentes UI
│   │       ├── styled_widgets.py    # Widgets estilizados
│   │       ├── file_tree.py         # Tree de arquivos
│   │       ├── image_preview.py     # Preview de imagens
│   │       ├── chat_widget.py       # Widget de chat
│   │       ├── progress_dialog.py   # Dialog de progresso
│   │       ├── animations.py        # Animações
│   │       ├── accessibility.py     # Acessibilidade
│   │       └── performance.py       # Performance
│   ├── gui/                   # Interface gráfica Tkinter (legado)
│   │   ├── main_window.py     # Janela principal
│   │   └── settings_window.py # Janela de configurações
│   ├── controllers/           # Controllers MVC
│   │   ├── main_controller.py # Controller principal
│   │   ├── ai_controller.py   # Controller de IA
│   │   └── file_controller.py # Controller de arquivos
│   ├── models/                # Models MVC
│   │   ├── file_model.py      # Model de arquivos
│   │   └── ai_model.py        # Model de IA
│   ├── core/                  # Lógica principal
│   │   ├── file_organizer.py  # Organização de arquivos
│   │   ├── file_scanner.py    # Scanner de diretórios
│   │   ├── batch_renamer.py   # Renomeamento em lote
│   │   └── extensions.py      # Definição de extensões
│   ├── ai/                    # Integração com IA
│   │   ├── ollama_client.py   # Cliente Ollama
│   │   ├── gemini_client.py   # Cliente Gemini
│   │   ├── image_analyzer.py  # Análise de imagens
│   │   └── context_classifier.py # Classificação por contexto
│   └── utils/                 # Utilitários
│       ├── config_manager.py  # Gerenciador de configurações
│       ├── logger.py          # Logging
│       └── file_utils.py      # Funções auxiliares
├── tests/                     # Testes unitários
└── logs/                      # Logs de operações
```

## 🎮 Como Usar

### Interface PySide6 (Recomendado)

1. Execute o programa:
```bash
python main_pyside6.py
```

2. Selecione o diretório para organizar
3. O programa escaneará arquivos automaticamente
4. Use as abas para diferentes funcionalidades:
   - **Organização**: Organize arquivos por categoria ou mova para pastas personalizadas
   - **IA**: Analise imagens, classifique arquivos e chat interativo com IA
   - **Histórico**: Visualize operações realizadas

5. Configure provedores de IA em Editar > Configurações:
   - **Ollama**: IA local com Qwen2-VL (requer Docker)
   - **Gemini**: IA cloud com Google Gemini (requer API key)

### Interface Tkinter (Legado)

1. Execute o programa:
```bash
python main.py
```

2. Selecione o diretório para organizar
3. O programa escaneará arquivos por extensão (.jpg, .jpeg, .png, .mp4)
4. Revise os arquivos encontrados
5. Confirme a organização
6. Arquivos serão movidos para pastas por categoria

## 🔍 Extensões Suportadas

### Imagens
- .jpg
- .jpeg
- .png
- .gif
- .bmp
- .webp

### Vídeos
- .mp4 (suporte básico)

## 🛠️ Desenvolvimento

### Arquitetura

O projeto segue o padrão MVC (Model-View-Controller):

- **Models**: `src/models/` - Estruturas de dados com signals Qt
- **Views**: `src/ui/` - Componentes de interface PySide6
- **Controllers**: `src/controllers/` - Lógica de negócio e coordenação

### Adicionar nova extensão

Edite `src/core/extensions.py` e adicione a extensão ao dicionário.

### Adicionar novo provedor de IA

1. Crie cliente em `src/ai/`
2. Adicione integração em `src/controllers/ai_controller.py`
3. Configure em `src/ui/settings_dialog.py`

## 📝 Status do Projeto

### Concluído
- ✅ Interface gráfica moderna com PySide6 e Fluent Design
- ✅ Arquitetura MVC completa
- ✅ Integração com Ollama e Google Gemini
- ✅ Sistema de configurações
- ✅ Componentes UI reutilizáveis
- ✅ Animações e acessibilidade
- ✅ Otimizações de performance

### Em Desenvolvimento
- 🔄 Testes unitários completos
- 🔄 Sistema de undo/redo avançado
- 🔄 Suporte a vídeos completo

## 🤝 Contribuindo

Este é um projeto de portfólio. Contribuições são bem-vindas!

## 📄 Licença

MIT License

## 👨‍💻 Autor

Fábio Dziedicz Filho - Freelancer Developer
