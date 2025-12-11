import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import os


# get API KEY from .dotenv file 
load_dotenv()
API_KEY=os.getenv("API_KEY")

# set the BASE URL for the http request
BASE_URL="https://api.clashroyale.com/v1"


