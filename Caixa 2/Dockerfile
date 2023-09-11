FROM python:3.8-slim

# Definir diretório de trabalho no container
WORKDIR /app

# Copie os arquivos necessários para o container
COPY Caixa2.py /app/
COPY requeriments.txt /app/

# Instale as dependências
RUN pip install --no-cache-dir -r requeriments.txt

EXPOSE 3389

# Comando para executar quando o container for iniciado
CMD ["python", "Caixa2.py"]
