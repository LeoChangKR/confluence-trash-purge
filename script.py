from atlassian import Confluence
import json
import requests
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from time import sleep
personal_access_token_prod = "$YOUR TOKEN$"
production_server = "https://$YOUR CONFLUENCE URL$"
  
confluence = Confluence(url = production_server, token = personal_access_token_prod)
current_day = datetime.strftime(datetime.today(), '%Y_%m_%d')
def clean_pages_from_space(space_key, limit = 500):
    flag = True
    max_retries = 0
    while flag:
        try:
            values = confluence.get_all_pages_from_space_trash(space = space_key, start = 0, limit = limit, content_type = "page")
            if not values or len(values) == 0:
                flag = False
                print("The trashed page of the space {} is empty.".format(space_key))
            else:
                print("Found {} pages trashed in the space {}.".format(len(values),space_key))
                for value in values:
                    url = value["_links"]["self"]
                    head = {"Authorization": "Bearer  {}".format(personal_access_token_prod)}
                    one_week = datetime.strptime(datetime.strftime(datetime.today() + relativedelta(days = -7), '%Y-%m-%d'), '%Y-%m-%d')
                    json_data = requests.get(url, headers = head, timeout=1000).json()
                    deletion_date = datetime.strptime(str(json_data["version"]["when"]).split("T")[0], '%Y-%m-%d')
                    if (deletion_date <= one_week):
                        print("Removing page with title {}.".format(value["title"].strip()))
                        try:
                            confluence.remove_page_from_trash(value["id"])
                        except:
                            print("Failed to remove page with title {}. Skipping...".format(value["title"].strip()))
                            flag = False
                    else:
                        print("It has not been 1 week or longer since the page {} was deleted. Skipping...".format(value["title"].strip()))
                        flag = False
        except:
            if (max_retries <10):
                max_retries = max_retries + 1
                print("Timeout error. Retrying...")
                sleep(5)
                pass
            else:
                max_retries = 0
                print("Max retries exceeded. Skipping...")
                flag = false
      
def clean_blog_posts_from_space(space_key, limit = 500):
    flag = True
    max_retries = 0
    while flag:
        try:
            values = confluence.get_all_pages_from_space_trash(space = space_key, start = 0, limit = limit, content_type = "blogpost")
            if not values or len(values) == 0:
                flag = False
                print("The trashed blog post of the space {} is empty.".format(space_key))
            else:
                print("Found {} blog posts trashed in the space {}.".format(len(values),space_key))
                for value in values:
                    url = value["_links"]["self"]
                    head = {"Authorization": "Bearer  {}".format(personal_access_token_prod)}
                    one_week = datetime.strptime(datetime.strftime(datetime.today() + relativedelta(days = -7), '%Y-%m-%d'), '%Y-%m-%d')
                    json_data = requests.get(url, headers = head, timeout=1000).json()
                    deletion_date = datetime.strptime(str(json_data["version"]["when"]).split("T")[0], '%Y-%m-%d')
                    if (deletion_date <= one_week):
                        print("Removing blog post with title {}.".format(value["title"].strip()))
                        try:
                            confluence.remove_page_from_trash(value["id"])
                        except:
                            print("Failed to remove blog post with title {}. Skipping...".format(value["title"].strip()))
                            flag = False
                    else:
                        print("It has not been 1 week or longer since the blog post {} was deleted. Skipping...".format(value["title"].strip()))
                        flag = False
        except:
            if (max_retries <10):
                max_retries = max_retries + 1
                print("Timeout error. Retrying...")
                sleep(5)
                pass
            else:
                max_retries = 0
                print("Max retries exceeded. Skipping...")
                flag = false
  
def clean_all_trash_pages_from_all_spaces():
    limit = 50
    now = datetime.now()
    flag = True
    i = 0
    while flag:
        space_lists = confluence.get_all_spaces(start = i * limit, limit = limit)
        if space_lists["results"] and len(space_lists) != 0:
            i += 1
            for space_list in space_lists["results"]:
                print("Checking space with key {}.".format(space_list["key"]))
                clean_pages_from_space(space_key = space_list["key"])
                clean_blog_posts_from_space(space_key = space_list["key"])
        else:
            flag = False
    print("started at")
    print(now)
    now = datetime.now()
    print("finished at")
    print(now)
    
    slack_webhook_payload = { "channel":"$YOUR CHANNEL$", "message": "Trash purge finished" }
    slack_webhook_url = '$YOUR API URL FOR SENDING SLACK MESSAGE$'
    requests.post(slack_webhook_url, data=slack_webhook_payload).json()
    return 0
  
  
if __name__ == "__main__":
    clean_all_trash_pages_from_all_spaces()
