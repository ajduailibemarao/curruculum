# Construtor de Currículos API

Aplicação FastAPI para leitura, padronização e criação de currículos profissionais em PDF ou Word, totalmente em português do Brasil.

## Recursos

- Upload de currículos em PDF ou Word com extração automática das informações principais.
- API para renderizar o currículo em diferentes layouts modernos pré-configurados.
- Possibilidade de enviar os dados estruturados manualmente para gerar documentos personalizados em PDF ou DOCX.
- Templates prontos com estilos moderno, clássico, minimalista e executivo.

## Requisitos

- Python 3.11+
- Dependências listadas em `requirements.txt`

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Executando a aplicação

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em `http://localhost:8000`. Acesse `http://localhost:8000/docs` para explorar os endpoints interativamente.

## Endpoints principais

- `GET /templates`: Lista de templates disponíveis.
- `POST /resume/parse`: Recebe um arquivo PDF ou Word e retorna os dados estruturados do currículo.
- `POST /resume/render`: Recebe os dados do currículo, template escolhido e formato desejado (pdf ou docx) e retorna o arquivo gerado.
- `GET /health`: Endpoint simples para monitoramento.

## Layouts disponíveis

| ID                 | Nome                  | Descrição                                                       |
|--------------------|-----------------------|-----------------------------------------------------------------|
| `moderno-azul`      | Moderno Azul          | Layout moderno com destaques em azul escuro.                     |
| `classico-serifado` | Clássico Serifado     | Layout clássico com tipografia serifada.                         |
| `minimalista-grade` | Minimalista em Grade  | Layout minimalista em duas colunas com blocos informativos.      |
| `executivo-dourado` | Executivo Dourado     | Layout sofisticado com destaques em dourado e foco em resultados. |

## Estrutura dos dados

Exemplo de payload aceito em `/resume/render`:

```json
{
  "layout_id": "moderno-azul",
  "formato": "pdf",
  "curriculo": {
    "contato": {
      "nome_completo": "Ana Silva",
      "email": "ana.silva@example.com",
      "telefone": "+55 11 91234-5678",
      "localizacao": "São Paulo, Brasil",
      "linkedin": "linkedin.com/in/anasilva"
    },
    "resumo_profissional": "Profissional com 8 anos de experiência em desenvolvimento de software.",
    "experiencias": [
      {
        "cargo": "Desenvolvedora Sênior",
        "empresa": "Tech Corp",
        "data_inicio": "Jan 2020",
        "data_fim": "Atual",
        "conquistas": [
          "Liderança de equipe com 6 pessoas",
          "Redução do tempo de deploy em 30%"
        ]
      }
    ],
    "formacoes": [
      {
        "curso": "Bacharelado em Ciência da Computação",
        "instituicao": "Universidade XYZ",
        "detalhes": "2010 - 2014"
      }
    ],
    "competencias": ["Python", "FastAPI", "PostgreSQL"],
    "projetos": [
      {
        "nome": "Portal de Vendas",
        "descricao": "Aplicação web para e-commerce",
        "link": "https://github.com/anasilva/portal"
      }
    ]
  }
}
```

## Observações

A extração de informações de currículos é heurística e pode variar conforme o formato do documento. Recomenda-se revisar e ajustar os dados retornados antes de gerar a versão final.
