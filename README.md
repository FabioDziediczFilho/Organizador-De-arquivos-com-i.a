# Organizador de Arquivos com IA

Organizador de arquivos inteligente em Python com interface gráfica que utiliza IA local (Ollama + Qwen2-VL) para categorizar e renomear arquivos automaticamente por contexto.

## 🎯 Objetivo

Aplicação desktop para organizar imagens (.jpg, .jpeg, .png) e vídeos (.mp4) usando IA para analisar contexto e criar pastas temáticas (ex: "imagens_casamento"), com interface gráfica completa e sistema de undo.

## 🚀 Funcionalidades

- [x] Organização por extensão de arquivo
- [ ] Interface gráfica com tkinter
- [ ] Preview de arquivos (imagens e thumbnails de vídeos)
- [ ] Sistema de confirmação antes de ações
- [ ] Barra de progresso durante operações
- [ ] Resumo de operações realizadas
- [ ] Sistema de undo com histórico completo
- [ ] Integração com Ollama (Docker)
- [ ] Análise de contexto com Qwen2-VL (7B)
- [ ] Renomeamento inteligente baseado em descrição
- [ ] Organização por contexto (ex: casamento, praia, trabalho)
- [ ] Testes unitários

## 📋 Pré-requisitos

- Python 3.10 ou superior
- Docker e Docker Compose
- Windows 10/11

## 🔧 Instalação

### 1. Clone o repositório

```bash
git clone <seu-repositorio>
cd organizador-de-arquivos
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

### 4. Configure Ollama com Docker

```bash
docker-compose up -d
```

### 5. Baixe o modelo Qwen2-VL

```bash
docker exec -it ollama ollama pull qwen2-vl:7b
```

## 📁 Estrutura do Projeto

```
organizador-de-arquivos/
├── main.py                    # Ponto de entrada
├── requirements.txt           # Dependências
├── README.md                  # Este arquivo
├── docker-compose.yml         # Configuração Ollama
├── src/
│   ├── gui/                   # Interface gráfica
│   │   ├── main_window.py     # Janela principal
│   │   ├── file_preview.py    # Preview de arquivos
│   │   └── progress_dialog.py # Barra de progresso
│   ├── core/                  # Lógica principal
│   │   ├── file_organizer.py  # Organização de arquivos
│   │   ├── file_scanner.py    # Scanner de diretórios
│   │   └── extensions.py      # Definição de extensões
│   ├── ai/                    # Integração com IA
│   │   ├── ollama_client.py   # Cliente Ollama
│   │   ├── image_analyzer.py  # Análise de imagens
│   │   └── context_classifier.py # Classificação por contexto
│   └── utils/                 # Utilitários
│       ├── undo_manager.py    # Sistema de undo
│       ├── logger.py          # Logging
│       └── file_utils.py      # Funções auxiliares
├── tests/                     # Testes unitários
└── logs/                      # Logs de operações
```

## 🎮 Como Usar

### Modo Manual (Sem IA)

1. Execute o programa:
```bash
python main.py
```

2. Selecione o diretório para organizar
3. O programa escaneará arquivos por extensão (.jpg, .jpeg, .png, .mp4)
4. Revise os arquivos encontrados
5. Confirme a organização
6. Arquivos serão movidos para pastas por categoria

### Modo com IA

1. Certifique-se que Ollama está rodando:
```bash
docker-compose ps
```

2. Ative a opção "Usar IA" na interface
3. O programa analisará cada imagem/vídeo com Qwen2-VL
4. Arquivos serão categorizados por contexto (ex: "casamento", "praia")
5. Arquivos serão renomeados com base no conteúdo

## 🔍 Extensões Suportadas

### Imagens
- .jpg
- .jpeg
- .png

### Vídeos
- .mp4

## 🛠️ Desenvolvimento

### Rodar testes

```bash
pytest tests/
```

### Adicionar nova extensão

Edite `src/core/extensions.py` e adicione a extensão ao dicionário.

## 📝 Próximos Passos

- [ ] Implementar GUI básica
- [ ] Criar módulo de extensões
- [ ] Implementar organizador de arquivos
- [ ] Adicionar sistema de undo
- [ ] Integrar com Ollama
- [ ] Implementar análise de contexto
- [ ] Adicionar preview de arquivos
- [ ] Criar testes

## 🤝 Contribuindo

Este é um projeto de portfólio. Contribuições são bem-vindas!

## 📄 Licença

MIT License

## 👨‍💻 Autor

Seu Nome - Freelancer Developer
