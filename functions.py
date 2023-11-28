import requests
import time
import json
from datetime import datetime
from email_module import send_mail_to

def get_email_user(user_id: str) -> str:
    '''
    https://support.tko-inform.ru/youtrack/api/users/23-314?fields=email,
    '''
    headers: dict = {
      'Accept': 'application/json',
      'Authorization': 'Bearer perm:123qwe',
      'Content-Type': 'application/json',
    }
    response = requests.get(f'{url}/api/users/{user_id}?fields=email', headers=headers)
    text: dict = response.json()
    return text.get('email')



def check_value(value):
    if value == 'None':
        value_2 = value
        return value_2
    elif isinstance(value, int):
        value_2 = value
        return value_2
    elif isinstance(value, dict):
        value_2 = value['name']
        return value_2
    elif isinstance(value, str):
        value_2 = value
        return value_2
    

def read_config():
  file = open('conf/config.json', 'rb')
  conf = json.load(file)
  file.close()
  return conf

def read_time():
    file = open('conf/time.txt', 'r')
    time = file.read()
    file.close()
    return time

def write_file_time(dt):
    file = open('conf/time.txt', 'w')
    file.write(str(dt))
    file.close()

conf: json = read_config()
url: str = conf["youtrack"]["baseUrl"]
url_2: str = conf["youtrack"]["baseUrl"]

def convert_timestamp(timestamp):
    conv_time = time.strftime("%H:%M:%S", time.localtime(int(str(timestamp)[:-3])))
    return conv_time

def get_all_activities(url):
  headers: dict = {
      'Accept': 'application/json',
      'Authorization': 'Bearer perm:123qwe',
      'Content-Type': 'application/json',
  }
  timestamp: str = read_time()
  data: dict = {"fields": "id,author(id,name,fullName,login,ringId),timestamp,added(text,name),target(issue(idReadable,id,project(name)),idReadable,project(id,name)),targetMember,field(id,name)","categories":"ArticleCommentAttachmentsCategory,AttachmentRenameCategory,AttachmentVisibilityCategory,AttachmentsCategory,CommentAttachmentsCategory,CommentTextCategory,CommentUsesMarkdownCategory,CommentVisibilityCategory,CommentsCategory,CustomFieldCategory,DescriptionCategory,IssueCreatedCategory,IssueResolvedCategory,IssueUsesMarkdownCategory,IssueVisibilityCategory,LinksCategory,ProjectCategory,SprintCategory,SummaryCategory,TagsCategory,TotalVotesCategory,VcsChangeCategory,VcsChangeStateCategory,VotersCategory,WorkItemCategory", "start": f'{timestamp}', "reverse": "true"} ## ,"start": f'{timestamp}',"$top":50}

  response = requests.get(f'{url}/api/activities', headers=headers, params=data)
  text: dict = response.json()
  if text is not None:
    dt = int(time.time() * 1000)
    write_file_time(dt)
  else: text = "None"
  return text


def get_list_issues()-> list:
    url: str = f'{url_2}/api/admin/projects/023660e9-9064-4bfe-afc3-d8d4702dadcc/issues?fields=id,created,reporter($type,id,name),updated,idReadable,$type,summary,description,customFields($type,id,projectCustomField($type,id,field($type,id,name)),value($type,avatarUrl,buildLink,color(id),fullName,id,isResolved,localizedName,login,minutes,name,presentation,text))&$top=9000'
    headers: dict = {
      'Accept': 'application/json',
      'Authorization': 'Bearer 123qwe',
      'Content-Type': 'application/json',
  }
    response = requests.get(f'{url}', headers=headers)
    json_data: list = json.loads(response.text)

    return json_data

def get_data_issue(issue_id,url):
  headers: dict = {
      'Accept': 'application/json',
      'Authorization': 'Bearer 123qwe',
      'Content-Type': 'application/json',
  }

  response = requests.get(f'{url}/api/issues/{issue_id}?fields=description,summary,created,reporter(ringId,login,avatarUrl),updated,customFields(projectCustomField(field(name)),value(ringId,id,avatarUrl,buildLink,fullName,isResolved,localizedName,login,minutes,name,presentation,text))', headers=headers,) #params=data)
  return response.json()

def rep_i(text):
    if text is not None:
        text: str = text.replace(".", "")
        text: str = text.replace("_", "\_")
    else: text = "None"
    return text

def rep_des(text):
    if text is not None:
        text: str = text.replace("_","\_")
        text: str = text.replace("*", "\*")
        text: str = text.replace("`", "\`")
        text: str = text.replace('«', '"')
        text: str = text.replace('»', '"')
    else: text = "None"
    return text

def rep_sum(text):
    if text is not None:
        text: str = text.replace("_","[_]")
    else: text = "None"
    return text

def rep_description(text):
    if text is not None:
        text: str = text.replace("_", "\\_")
    else: text = "None"
    return text

def check_deadline(data: list)-> None:
    dt: int = int(time.time() * 1000)
    recipients = ["esushchenko@rt-invest.com", "ekanakov@regop.ru", "eleonov@regop.ru", "OPrivalova@regop.ru","gusakova@tko-inform.ru", "dberezko@tko-inform.ru"]
    msgg = ""
    mail= ""
    for issue in data:
        for v in issue["customFields"]:
            value = v.get("value", None)
            value = check_value(value)
            if v["projectCustomField"]["field"]["name"] == "Направления":
                _ = check_value(value)
            if v["projectCustomField"]["field"]["name"] == "Приоритет":
                _ = check_value(value)
            if v["projectCustomField"]["field"]["name"] == "Состояние":
                condition = check_value(value)
            if v["projectCustomField"]["field"]["name"] == "Assignee":
                assignee = check_value(value)
                if value:
                    mail = get_email_user(v['value']['id'])
            if v["projectCustomField"]["field"]["name"] == "Спринт бэклог УК РО":
                _ = check_value(value)
            if v["projectCustomField"]["field"]["name"] == "Due Date" or v["projectCustomField"]["field"]["name"] == "Срок следующего этапа":
                due_date = check_value(value)
            if v["projectCustomField"]["field"]["name"] == "Статус":
                _ = check_value(value)
        if condition not in ['Закрыта']:
            issue_title: str = issue['idReadable']
            issue_title_2: str = issue['summary']
            link: str = f'({url}/issue/{issue_title})'
            if due_date:
                deadline_difference = due_date - dt
                deadline = datetime.fromtimestamp((due_date / 1000)).strftime('%d-%m-%y')
                if 28800000 <= deadline_difference <= 115200000:
                    deadline: str = datetime.fromtimestamp((due_date/1000)).strftime('%d-%m-%y')
                    text: str = f'❗️❗️ {issue_title}: {issue_title_2}\n{link}\nСрок следующего этапа: {deadline}\nИсполнитель: {assignee}\nСрок следующего этапа истекает завтра.\n\n'
                    # if mail != 'None':
                    if mail not in recipients:
                        recipients.insert(0,mail)
                    msgg += text
                        # send_mail_to(send_to=recipients,
                        #     subject=f"❗️❗️ Дедлайн истекает завтра: {issue_title_2}",
                        #     message=f"{text}\n",
                        #     )
                if 0 <= deadline_difference <= 28800000:
                    deadline: str = datetime.fromtimestamp((due_date/1000)).strftime('%d-%m-%y')
                    text: str = f'🔥 {issue_title}: {issue_title_2}\n{link}\nСрок следующего этапа: {deadline}\nИсполнитель: {assignee}\nСрок следующего этапа истекает сегодня.\n\n'
                    # if mail != 'None':
                    if mail not in recipients:
                        recipients.insert(0,mail)
                    msgg += text
                        # send_mail_to(send_to=recipients,
                        #         subject=f"🔥 Дедлайн истекает сегодня: {issue_title_2}",
                        #         message=f"{text}\n",
                        #         )
                if 115200000 <= deadline_difference <= 201600000:
                    deadline: str = datetime.fromtimestamp((due_date/1000)).strftime('%d-%m-%y')
                    text: str = f'❗️ {issue_title}: {issue_title_2}\n{link}\nСрок следующего этапа: {deadline}\nИсполнитель: {assignee}\nСрок следующего этапа истекает послезавтра.\n\n'
                    # if mail != 'None':
                    if mail not in recipients:
                        recipients.insert(0,mail)
                    msgg += text
                        # send_mail_to(send_to=recipients,
                        #     subject=f"❗️ Дедлайн истекает послезавтра: {issue_title_2}",
                        #     message=f"{text}\n",
                        #     )
                if deadline_difference <= 0:
                    deadline: str = datetime.fromtimestamp((due_date/1000)).strftime('%d-%m-%y')
                    text: str = f'❌ {issue_title}: {issue_title_2}\n{link}\nСрок следующего этапа: {deadline}\nИсполнитель: {assignee}\nСрок решения по задаче истёк.\n\n'
                    print(issue_title,"\n",mail)
                    # if mail != 'None':
                    if mail not in recipients:
                        recipients.insert(0,mail)
                    msgg += text
                        # send_mail_to(send_to=recipients,
                        #     subject=f"❌ Срок решения по задаче истёк: {issue_title_2}",
                        #     message=f"{text}\n",
                        #     )
    # recipients = [x for x in recipients if x is not None]
    recipients = list(filter(None, recipients))
    if msgg:
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        send_mail_to(send_to = recipients,
                                subject = f"Уведомление по подходящим срокам BUR",
                                message = f"{msgg}\n",
                                files = None
                                )
        print(f'{current_time}: mssg sendedd to:{recipients}')
    else:
        current_time = datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
        send_mail_to(send_to = recipients,
                                subject = f"Уведомление по подходящим срокам BUR",
                                message = f"В проекте BUR нет задач с истекающими сроками.\n",
                                files = None
                                )
        print(f"{current_time}: нет истекающих сроков")


def check_deadline_by_hours(data: list)-> None:
    dt: int = int(time.time() * 1000)
    recipients = ["esushchenko@rt-invest.com","ekanakov@regop.ru"]
    for issue in data:
        for v in issue["customFields"]:
                    value = v.get("value", None)
                    value = check_value(value)
                    if v["projectCustomField"]["field"]["name"] == "Направления":
                        _ = check_value(value)
                    if v["projectCustomField"]["field"]["name"] == "Приоритет":
                        _ = check_value(value)
                    if v["projectCustomField"]["field"]["name"] == "Состояние":
                        condition = check_value(value)
                    if v["projectCustomField"]["field"]["name"] == "Assignee":
                        assignee = check_value(value)
                        if value:
                            mail = get_email_user(v['value']['id'])
                    if v["projectCustomField"]["field"]["name"] == "Спринт бэклог УК РО":
                        _ = check_value(value)
                    if v["projectCustomField"]["field"]["name"] == "Due Date" or v["projectCustomField"]["field"]["name"] == "Срок следующего этапа":
                        due_date = check_value(value)
                    if v["projectCustomField"]["field"]["name"] == "Статус":
                        _ = check_value(value)
        if condition not in ['Закрыта']:
            issue_title: str = issue['idReadable']
            issue_title_2: str = issue['summary']
            if due_date:
                deadline = datetime.fromtimestamp((due_date / 1000)).strftime('%d-%m-%y')
                if -86400000 <= due_date - dt <= 0:
                    deadline: str = datetime.fromtimestamp((due_date/1000)).strftime('%d-%m-%y')
                    text: str = f' \n ❌ {issue_title}: {issue_title_2}\nДедлайн: {deadline}\nИсполнитель: {assignee}\nСрок решения по задаче истёк.'
                    if mail != 'None':
                        recipients.insert(0,mail)
                        send_mail_to(send_to=recipients,
                            subject=f"❌ Срок решения по задаче истёк: {issue_title_2}",
                            message=f"{text}\n",
                            )
                    
if __name__ == "__main__":
    print(__file__)
