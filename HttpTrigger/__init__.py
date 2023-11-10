import logging

import azure.functions as func
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request. 12:38')

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(executable_path=r"/usr/local/bin/chromedriver")

    logging.warn(options)

    driver = webdriver.Chrome(service=service, options=options)
    logging.info(driver)
    driver.get('http://www.ubuntu.com/')
    links = driver.find_elements(By.TAG_NAME, "a")
    link_list = ""
    for link in links:
        if link_list == "":
            link_list = link.text
            logging.info(link_list)
        else:
            link_list = link_list + ", " + link.text
            logging.info(link_list)

    # create blob service client and container client
    credential = DefaultAzureCredential()
    storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
    client = BlobServiceClient(account_url=storage_account_url, credential=credential)
    blob_name = "test" + str(datetime.now()) + ".txt"
    blob_client = client.get_blob_client(container=os.environ["par_storage_container_name"], blob=blob_name)
    blob_client.upload_blob(link_list)

    return func.HttpResponse(
             str(link_list),
             status_code=200
    )