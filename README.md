# Documentação API-Sensores

## Introdução

Esse projeto foi desenvolvido para solucionar o desafio da Radix.
Foi criada uma API, com dois endpoints, e três páginas web.

## Requisitos 
1. Instalar Django Framework: `pip install django`
2. Realizar instalação do Banco de dados: `python manage.py migrate`
3. Realizar instalação do Banco de dados> `python manage.py makemigrations`
4. Instalar Matplotlib: `pip install matplotlib`
5. Rodar o servidor: `python manage.py runserver`

## Rotas - API

### ~/api/Leitura_Json (POST)
Rota que recebe um JSON do sensor, de acordo com o modelo abaixo:
```JSON
{
    "equipmentId": "EQ-12495",
    "timestamp": "2023-02-15T01:30:00.000-05:00",
    "value": 78.42
}
```
O sistema valida a leitura recebida pelo JSON e cria a leitura no banco de dados, retornando o código 201 e uma mensagem de confirmação. Caso o Sensor, que enviou o JSON, não exista no Banco de Dados, então ele é criado e persiste a leitura no banco de dados normalmente. Caso o JSON venha em um formato diferente do esperado, como no modelo acima, o JSON não é salvo no banco de dados e a API retorna 400 e uma mensagem explicando o motivo da falha.

### ~/api/Leitura_CSV (POST)
Rota que recebe um arquivo CSV, de acordo com o modelo abaixo:
```CSV
equipmentId;timestamp;value
EQ-12495;2023-02-12T01:30:00.000-05:00;78.8
EQ-12492;2023-01-12T01:30:00.000-05:00;8.8
```
O sistema valida o header e os valores de cada linha do CSV antes de inserir no banco de dados, para não ter inconsistência. Para cada linha do arquivo, se o sistema validou, a linha é inserida no banco de dados. Se todas as linhas do arquivo foram inseridas com sucesso no banco de dados, o sistema retorna 201 e uma mensagem de confirmação. Por outro lado, para cada linha do arquivo com erro, o sistema retorna o código 400 e uma mensagem, que especifica qual linha do arquivo não foi inserida no banco de dados e o motivo.


## Páginas Web

### Home - sensores.html
Página Web index, que mostra cada Sensor inserido no banco de dados. Cada Sensor possui um link dinâmico, que leva o usuário para uma outra página web com detalhes daquele Sensor. No canto superior direito da Home, temos um campo de pesquisa, onde o usuário pode pesquisar o Sensor específico, de acordo com o seu equipmentId.

### pesquisa_sensor.html -  ~/pesquisa?query={termo_busca} 
Página de Pesquisa, que busca no banco de dados os Sensores existentes, verificando seu equipmentId, de acordo com o termo de busca inserido pelo usuário. A correspondência do termo de busca e o equipmentId é parcial, ou seja, retorna retorna os equipamentos correspondentes de acordo com o termo de pesquisa.

### detalhes_sensor.html ~/leitura/{id}?hora={hora}
Página que mostra o gráfico de um Sensor específico, de acordo com o id artificial do Sensor e o parâmetro hora. A página vai mostrar um gráfico, de acordo com o período anterior, medido em horas, ao momento de acesso ao usuário na página, sendo as opções dispostas ao usuário, por meio de botões na tela, de 24 horas, que é a padrão, 48 horas, 1 semana e 1 mês. O gráfico escolhido foi o gráfico de linhas, em que as coordenadas são valor da leitura do sensor(y), por tempo(x), que é o horário do timestamp em que a leitura foi realizada.

