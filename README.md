# Missing Finder - Backend #

Os passos a seguir descrevem como configurar o ambiente para desenvolvimento em um host linux.

## Preparando o ambiente de desenvolvimento

Configurar PIP e Python para desenvolvimento.
``` 
sudo apt update

sudo apt-get install python3-venv
sudo apt-get install python3-dev
```

Ativar o ambiente virtual python
```
python3 -m venv env
source env/bin/activate
```

Entre os módulos contidos no requirements.txt temos o flask, o qual pode necessitar a instalação de outras dependencias, entre elas as listas a seguir: 

```
pip install wheel
#pip3 install --upgrade pip wheel setuptools
```

Para instalar o requirement psycopg2 pode ser necessario atualizar o libpq-dev

```
sudo apt-get install libpq-dev    ## necessario para o psycopg2
```

Instalar as dependencias listadas no requirements.txt
``` 
pip install -r requirements.txt
```

Pode ser necessário atualizar o ambiente Linux com instalação/atualização das libs: 
```
# sudo apt-get install build-essential cmake

# sudo apt-get install libgtk-3-dev

# sudo apt-get install libboost-all-dev
```

## Configurando Docker, Dockstation e Postgree

[Tutorial](https://www.techrepublic.com/article/how-to-install-and-use-dockstation-for-easy-container-builds/)
 explicando como instalar o docker + dockstation

### Docker 

```
sudo apt update
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER
log out
log in
```

### Dockstation

* [Dockstation](https://dockstation.io/)
* Minimal system requirement:
* Docker v1.10.0+
* Docker Compose v1.6.0+
* Ubuntu 14.04 LTS or 16.04 LTS 

Faça o download a partir do [site](https://dockstation.io/)

Instalar o arquivo *.deb
```
sudo dpkg -i dockstation*.deb
```


### Postgre SQL

Utilizaremos o PostgreSQL em um container docker.

[postgres:alpine](https://hub.docker.com/_/postgres/)

Utilizar as configurações contidas no script setup_posgres.py

Para manipular o banco de dados você pode utilizar uma das opções:
* [DBeaver](https://dbeaver.io/download/)
* pgadmin4, em outro docker
* pgadminer, em outro docker

Para instalar o dbeaver, o caminho mais simples é através de um snap:
```
Caso tenha o snap instalado:
sudo snap install dbeaver-ce
```

Para conectar ao banco de dados
 
Através do pdadmin4 ou adminer
utilizar no campo host o nome do container do postgreSQL
Através do dbeaver, utilizar localhost

```
host: missingfinder-postgres
POSTGRES_PASSWORD: 'mysecretpassword'
POSTGRES_USER: 'postgres'
POSTGRES_DB: 'postgres'
PGADMIN_DEFAULT_EMAIL: 'umemail@qualquer.com'
PGADMIN_DEFAULT_PASSWORD: 'PgAdmin2020'
```

Após iniciar o container
* abrir um terminal
* carregar o ambient virtual python
* executar o script
```
python setup_postgres.py
```


# Referencias
(PostgreSQL + pgAdmin 4 + Docker Compose: montando rapidamente um ambiente para uso)
https://medium.com/@renato.groffe/postgresql-pgadmin-4-docker-compose-montando-rapidamente-um-ambiente-para-uso-55a2ab230b89



# Amazon AWS
Instalação do AWS cli
https://aws.amazon.com/pt/cli/

Caso não esteja criado, criar o diretorio ~/.aws no home.

Sobre a utilização do BOTO3 com o AWS
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration

```
https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html#cliv2-linux-install

curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

# Flutter
Instalar o flutter e android studio

## Instalar o Flutter: 
```
sudo snap install flutter --classic
```


