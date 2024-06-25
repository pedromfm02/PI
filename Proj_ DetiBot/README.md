# detiBot

[Website](https://detibot.pages.dev)

## Tecnologias Utilizadas

- **Storing**: MySQL, Qdrant
- **Web Scraping**: Selenium, BeautifulSoup
- **RAG**: LangChain
- **LLM**: Ollama llama3
- **FrontEnd**: React
- **Deployment**: Docker

## Comandos para Executar a Aplicação

### Executar a Aplicação Completa

```sh
docker-compose up mysql qdrant ollama
docker exec -it ollama ollama run llama3
docker-compose up update api chat admin manager
```

### Executar Backend

```sh
docker-compose up mysql qdrant ollama
docker exec -it ollama ollama run llama3
docker-compose up update api
```
ou se preferires correr localmente
```sh
docker-compose up mysql qdrant ollama
docker exec -it ollama ollama run llama3
uvicorn controller:app --reload
```