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

    driver = webdriver.Chrome(service=service, options=options)
    logging.info(driver)
    driver.get('http://abehiroshi.la.coocan.jp/')
    links = driver.find_elements(By.TAG_NAME, "a")
    link_list = ""
    for link in links:
        if link_list == "":
            link_list = link.text
        else:
            link_list = link_list + ", " + link.text

    # # create blob service client and container client
    # credential = DefaultAzureCredential()
    # storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
    # client = BlobServiceClient(account_url=storage_account_url, credential=credential)
    blob_name = "testscrape" + str(datetime.now()) + ".txt"

    logging.info(link_list)

    # BLOBへの接続
    connect_str = os.getenv("AzureWebJobsStorage")
    
    # Create a blob client using the local file name as the name for the blob
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client("scrapefile", blob=blob_name)

    blob_client.upload_blob(link_list)

    return func.HttpResponse(
             str(link_list),
             status_code=200
    )