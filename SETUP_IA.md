# Configuração do Sistema de IA (Ollama + Qwen2-VL)

## Requisitos de Hardware

Para rodar o modelo Qwen2-VL (7B) com Ollama, você precisa:

**Mínimo recomendado:**
- CPU: 4+ cores
- RAM: 8GB+
- GPU (opcional): NVIDIA com 4GB+ VRAM para melhor performance

**Ideal:**
- CPU: 8+ cores
- RAM: 16GB+
- GPU: NVIDIA com 8GB+ VRAM

## Instalação do Ollama

### Windows

1. Baixe o Ollama em: https://ollama.com/download
2. Execute o instalador
3. Abra o terminal e verifique a instalação:
   ```bash
   ollama --version
   ```

### Linux/Mac

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

## Baixar o Modelo Qwen2-VL

Após instalar o Ollama, baixe o modelo:

```bash
ollama pull qwen2-vl:7b
```

Isso baixará aproximadamente 4-5GB.

## Verificar Instalação

Verifique se o Ollama está rodando:

```bash
ollama list
```

Deve mostrar o modelo `qwen2-vl:7b` na lista.

## Testar o Modelo

Teste se o modelo está funcionando:

```bash
ollama run qwen2-vl:7b "Olá, como você está?"
```

## Configurar o Projeto

1. Instale as dependências Python:
   ```bash
   pip install -r requirements.txt
   ```

2. O projeto está configurado para usar `localhost:11434` por padrão

3. Se precisar mudar a configuração, edite `src/ai/ollama_client.py`:
   ```python
   client = OllamaClient(host="http://localhost:11434", model="qwen2-vl:7b")
   ```

## Testar a Integração

Crie um script de teste `test_ai.py`:

```python
from src.ai.ollama_client import OllamaClient
from src.ai.image_analyzer import ImageAnalyzer
from src.ai.context_classifier import ContextClassifier

# Testar conexão
client = OllamaClient()
if client.check_connection():
    print("✓ Ollama conectado com sucesso!")
else:
    print("✗ Erro ao conectar com Ollama")
    exit(1)

# Testar análise de imagem
analyzer = ImageAnalyzer(client)
result = analyzer.analyze_image_context("caminho/para/sua/imagem.jpg")
print(f"Contexto: {result}")

# Testar classificação
classifier = ContextClassifier(analyzer)
classification = classifier.classify_image("caminho/para/sua/imagem.jpg")
print(f"Classificação: {classification}")
```

## Solução de Problemas

### Ollama não inicia
- Verifique se o serviço Ollama está rodando
- No Windows: Verifique se o Ollama está nos serviços do Windows
- No Linux/Mac: `ollama serve`

### Erro de conexão
- Verifique se a porta 11434 não está bloqueada
- Tente `curl http://localhost:11434/api/tags` no terminal

### Modelo muito lento
- Se não tiver GPU, o modelo rodará na CPU (mais lento)
- Considere usar um modelo menor se necessário

### Memória insuficiente
- Feche outros programas
- Considere usar um modelo menor (ex: qwen2-vl:2b)

## Modo de Simulação (sem Ollama)

Se quiser testar a GUI sem Ollama, o sistema funciona normalmente para organização básica por extensão (imagem/vídeo). A funcionalidade de IA será desabilitada automaticamente se Ollama não estiver disponível.
