FROM mcr.microsoft.com/azure-functions/python:4-python3.10

# 0. Install essential packages
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. Install Chrome (root image is debian)
# See https://stackoverflow.com/questions/49132615/installing-chrome-in-docker-file
# ARG CHROME_VERSION="google-chrome-stable"
RUN apt-get update
RUN wget --no-verbose -O /tmp/chrome.deb https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb \
  && apt-get install -y --allow-downgrades /tmp/chrome.deb

# 2. Install Chrome driver used by Selenium
RUN LATEST=$(wget -q -O - http://chromedriver.storage.googleapis.com/LATEST_RELEASE) && \
    wget http://chromedriver.storage.googleapis.com/$LATEST/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && ln -s $PWD/chromedriver /usr/local/bin/chromedriver

ENV PATH="/usr/local/bin/chromedriver:${PATH}"

# 3. Install selenium in Python

RUN pip install -U selenium

# 4. Finally, copy python code to image
COPY . /home/site/wwwroot

# 5. Install other packages in requirements.txt
RUN cd /home/site/wwwroot && \
    pip install -r requirements.txt

# コマンドの実行
CMD ["python", "C:/Users/t-mitsunaga/azure-function-selenium/scrapeKPIUrlList/__init__.py"]