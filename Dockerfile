FROM python:3.12-slim

WORKDIR /app

LABEL authors="jteuf"

# Install build tools (gcc, make, dependencies)
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    make \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install spidev (and other dependencies)
RUN pip install spidev
RUN git clone https://github.com/pimoroni/inky inky
RUN pip install -r inky/requirements.txt
RUN pip install --upgrade inky

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/main.py"]