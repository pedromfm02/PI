Deti - BackEnd

o backend esta organizado da seguinte forma: 

    MySql - onde é guardado as tables que irao guardar informação dos diferentes tipos de sources

    controller.py -   API FastAPI que fornece todos os endpoints usados no projeto

    update.py - atualiza informação dos url baseado no seu update_time
    
    Services - restante codigo responsavel pelo loading, indexaçao, storing e querying

para colocar o backend a funcionar é necessário:

1- docker-compose up qdrant mysql ollama

2- verificar se os 3 containers em cima estão prontos para o funcionamento:

    -> qdrant: verificar apenas se está a rodar no docker ou então fazer localhost:6333/dashboard

    -> mysql: ver se esta mansagem já apareceu: [System] [MY-011323] [Server] X Plugin ready for connections. Bind-address: '::' port: 33060, socket: /var/run/mysqld/mysqlx.sock

    -> ollama: dps de verificar q o container está a rodar fazer na linha de comandos:
        -> docker exec -it ollama ollama run llama3/(outro llm suportado pelo ollama)

3- apôs os passos acima estarem compridos e verificados rodar o backend: 
    
    -> local: uvicorn controller:app --reload 
    -> docker: 
        full app: docker-compose up update api


