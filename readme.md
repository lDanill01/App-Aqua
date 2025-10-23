# Sistema de Arraçoamento 📈

Um sistema inteligente para gerenciar e calcular o crescimento de peixes em cultivo, com base em parâmetros como temperatura, tamanho do alevino e sobrevivência. A aplicação integra dados de crescimento com recomendações de ração nutricionalmente balanceada.

## Características

- **Cálculo de Crescimento Dinâmico**: Baseado em temperatura e peso inicial do alevino
- **Banco de Dados de Produtos**: Gerenciamento de rações com informações nutricionais
- **Consulta Inteligente**: Interpolação automática para valores não encontrados exatamente
- **Visualização em Tempo Real**: Tabelas e gráficos interativos
- **Interface Amigável**: Desenvolvida com Streamlit para fácil uso

## Estrutura do Projeto

```
sistema_arracoamento/
├── .gitignore
├── README.md
├── requirements.txt
├── app.py                          # Aplicação principal Streamlit
├── converter_para_json.py          # Script para processar dados CSV
├── teste_lookup.py                 # Testes da classe LookupTabela
│
├── data/
│   ├── produtos_racao.json         # Database de produtos/rações
│   └── tabela_consulta.json        # Database de crescimento por temperatura
│
└── utils/
    ├── __init__.py
    ├── database.py                 # Classe DatabaseProdutos
    └── lookup_tabela.py            # Classe LookupTabela
```

## Instalação

### Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)

### Passo 1: Clonar ou Preparar o Repositório

```bash
cd sistema_arracoamento
```

### Passo 2: Criar Ambiente Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

## Uso

### 1. Gerar o Database (Primeira Vez)

Se você tem os dados em CSV/TSV, execute:

```bash
python converter_para_json.py
```

Isso criará o arquivo `data/tabela_consulta.json` com os dados de crescimento por temperatura.

### 2. Testar a Classe de Consulta

```bash
python teste_lookup.py
```

Você deve ver resultados como:

```
✓ Lookup carregado com sucesso: data/tabela_consulta.json
Teste 1 - Alevino 1g a 18°C:
{'status': 'exato', 'g_dia': 0.09, 'biomassa_pct': 4.0}
```

### 3. Executar a Aplicação Streamlit

```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`

## Como Usar a Aplicação

### 1. Inserir Parâmetros

Na seção "Parâmetros de Cultivo", preencha:
- **Espécie**: Tambaqui ou Tilápia
- **Tipo de Cultivo**: Tanque Escavado ou Tanque-Rede
- **Temperatura**: 18°C a 33°C
- **Tamanho do Alevino**: Peso em gramas (ex: 7g)
- **Sobrevivência Final**: Percentual esperado
- **Outros parâmetros**: Densidade, quantidade de peixes, valor do milheiro, etc.

### 2. Consultar Dados

Clique no botão "Consultar Dados" para:
1. Buscar no database o g/dia para aquele peso e temperatura
2. Calcular o crescimento para as 57 semanas
3. Associar os produtos de ração recomendados

### 3. Visualizar Resultados

- **Tabela**: Dados completos de crescimento por semana
- **Gráfico**: Evolução do crescimento (g/dia) ao longo das semanas
- **Métricas**: Resumo dos parâmetros consultados

## Estrutura dos Databases

### 1. `produtos_racao.json`

Define os produtos de ração por período:

```json
{
  "configuracoes": [
    {
      "id": 1,
      "semanas_inicio": 1,
      "semanas_fim": 1,
      "produto": "NUTRIPISCIS AL55",
      "proteina": 55,
      "granulometria": "0.5 MM",
      "preco": 150.00,
      "observacao": "Alevino inicial"
    }
  ]
}
```

### 2. `tabela_consulta.json`

Contém dados de crescimento por dia, peso e temperatura:

```json
{
  "dados": [
    {
      "dia": 1,
      "peso_g": 1.0,
      "valores": [
        {"temp": 18, "g_dia": 0.09, "biomassa_pct": 4.0},
        {"temp": 19, "g_dia": 0.10, "biomassa_pct": 5.0}
      ]
    }
  ]
}
```

## Classes Principais

### DatabaseProdutos

Gerencia o database de produtos de ração.

```python
from utils.database import DatabaseProdutos

db = DatabaseProdutos('data/produtos_racao.json')

# Obter produto para semana 5
produto = db.obter_produto(5)  # "NUTRIPISCIS AL 36 2 A 3 MM"

# Obter proteína
proteina = db.obter_proteina(5)  # 36

# Validar cobertura
validacao = db.validar_cobertura(57)
```

### LookupTabela

Consulta o database de crescimento com interpolação automática.

```python
from utils.lookup_tabela import LookupTabela

lookup = LookupTabela('data/tabela_consulta.json')

# Consulta simples
resultado = lookup.consultar(peso_g=7.0, temperatura=26)
# {
#   'status': 'interpolado',
#   'g_dia': 0.79,
#   'biomassa_pct': 2.31,
#   'fator_interpolacao': 0.76
# }

# Obter temperaturas disponíveis
temps = lookup.obter_temperaturas_disponiveis()  # [18, 19, 20, ...]

# Gerar relatório para um peso
relatorio = lookup.gerar_relatorio(peso_g=2.5)
```

## Fluxo de Dados

```
┌─────────────────────────────┐
│   Entrada de Dados          │
│  - Temperatura              │
│  - Tamanho Alevino          │
│  - Espécie                  │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   LookupTabela              │
│   Busca g/dia + biomassa    │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   Cálculo de Crescimento    │
│   - 57 semanas              │
│   - PI/PF por semana        │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   DatabaseProdutos          │
│   - Ração por semana        │
│   - Proteína                │
│   - Granulometria           │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│   Visualização              │
│   - Tabela                  │
│   - Gráfico                 │
│   - Métricas                │
└─────────────────────────────┘
```

## Exemplos de Uso

### Exemplo 1: Consultar com Temperatura 26°C

```
Parâmetros:
- Temperatura: 26°C
- Tamanho Alevino: 7g
- Espécie: Tambaqui

Resultado:
- g/dia inicial: 0.79
- Semana 1: g/dia 0.79, PI 7g, PF ~12g
- Semana 2: g/dia 0.80, PI ~12g, PF ~17g
- ... até semana 57
```

## Requisitos

Veja `requirements.txt`:

```
streamlit>=1.28.0
pandas>=2.0.0
matplotlib>=3.7.0
numpy>=1.24.0
```

## Adição de Novas Temperaturas

Para incluir mais temperaturas (21°C a 33°C):

1. Prepare os dados no formato TSV
2. Execute o conversor:
   ```bash
   python converter_para_json.py
   ```
3. O arquivo `tabela_consulta.json` será atualizado automaticamente

## Troubleshooting

### Erro: "Arquivo não encontrado"

```
FileNotFoundError: [Errno 2] No such file or directory: 'data/tabela_consulta.json'
```

**Solução**: Execute o conversor primeiro:
```bash
python converter_para_json.py
```

### Erro: "ModuleNotFoundError: No module named 'utils'"

**Solução**: Certifique-se de estar na raiz do projeto quando executar:
```bash
cd sistema_arracoamento
python app.py
```

### Temperatura não disponível

Se receber erro para temperatura fora do intervalo (18-33°C):
- Verifique o intervalo disponível
- Veja `lookup.obter_temperaturas_disponiveis()`

## Contribuindo

Para adicionar novas funcionalidades:

1. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
2. Faça suas alterações
3. Teste: `python teste_lookup.py`
4. Commit: `git commit -m "Add: descrição"`
5. Push: `git push origin feature/nova-funcionalidade`

## Licença

Este projeto está disponível sob licença MIT.

## Suporte

Para dúvidas ou problemas:

1. Verifique o arquivo `teste_lookup.py` para exemplos
2. Consulte os docstrings das classes em `utils/`
3. Verifique os logs da aplicação Streamlit

## Roadmap

- [ ] Adicionar mais temperaturas (21-33°C)
- [ ] Exportar relatórios em PDF/Excel
- [ ] Histórico de cálculos
- [ ] Múltiplas espécies com parâmetros específicos
- [ ] Análise de custos totais
- [ ] Gráficos adicionais (biomassa, proteína)
- [ ] Autenticação de usuários

## Changelog

### v1.0 (2025-10-22)
- Versão inicial
- 3 temperaturas implementadas (18°C, 19°C, 20°C)
- Consultas com interpolação
- Interface Streamlit funcional