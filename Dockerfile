FROM python:3.12

WORKDIR /civil_tools_server
ADD . /civil_tools_server

# 设置 pip 镜像源（清华源）
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --upgrade pip 

# 安装系统依赖和中文字体
RUN mv /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list.d/debian.sources.bak
ADD ./source.list /etc/apt/sources.list.d/debian.sources
# 先单独运行 apt-get update，利用 Docker 缓存
RUN apt-get update

# 再安装依赖
RUN apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        fonts-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/*

# 复制 requirements.txt 到工作目录
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
