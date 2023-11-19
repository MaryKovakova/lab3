import requests, json
import datetime
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import re
import numpy as np
import pandas as pd
from collections import Counter

def api(params):
    url = 'https://issues.apache.org/jira/rest/api/2/search'

    global data

    response = requests.get(url, params=params)
    try:
        if response.status_code == 200:
            data = response.json()
            return data
    except IOError:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
       
def get_created_date(issue):
    created_date_str = issue['fields']['created']
    created_date = datetime.strptime(created_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    return created_date

def get_resolution_date(issue):
    resolution_date_str = issue['fields']['resolutiondate']
    resolution_date = datetime.strptime(resolution_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    return resolution_date        
            
def time_diff(time_start, time_stop):
    if isinstance(time_start, str):
        time_start = datetime.strptime(time_start, '%Y-%m-%dT%H:%M:%S.%f%z')
    if isinstance(time_stop, str):  
        time_stop = datetime.strptime(time_stop, '%Y-%m-%dT%H:%M:%S.%f%z')
    time_diff = time_stop - time_start
    time_diff = time_diff.total_seconds() / (3600 * 24)
    return time_diff
             
def changelog(data, status):
    time_diff_list = []
    for issue in data['issues']:
        for histories in issue['changelog']['histories']:
            for field in histories['items']:
                if status == 'Open' and field['fromString'] == 'Open':
                    time_start = get_created_date(issue)
                    time_stop = histories['created']
                    time_differ = time_diff(time_start, time_stop)
                    time_diff_list.append(time_differ)
                
                elif field['toString'] == status:
                    time_start = histories['created']
                elif field['fromString'] == status:
                    time_stop = histories['created']
                    time_differ = time_diff(time_start, time_stop)
                    time_diff_list.append(time_differ)
    return time_diff_list

def opened_closed_per_day(data):
    time_opened, time_closed  = [], []
    
    for issue in data['issues']:
        created_date = datetime.strptime(issue['fields']['created'][:-18], '%Y-%m-%d')
        time_opened.append(created_date)

        for histories in issue['changelog']['histories']:
            for field in histories['items']:
                if field['field'] == 'status':
                    if field['toString'] == 'Closed':
                        closed_date = datetime.strptime(histories['created'][:-18], '%Y-%m-%d')
                        time_closed.append(closed_date)
            
    counter_opened = Counter(time_opened)
    counter_closed = Counter(time_closed)
    return counter_opened, counter_closed

def assignee_reporter(data):
    assignee_list = []

    for issue in data['issues']:
        if issue['fields']['reporter']['key'] == issue['fields']['assignee']['key']:
            assignee_list.append(issue['fields']['reporter']['displayName'])

    return assignee_list  

def graph1():
    params = {
    'jql': 'project = KAFKA AND status = Closed',
    'maxResults': 1000, 
    'fields': 'created,resolutiondate'
    }
    data = api(params)
    time_diff_list = []
    
    for issue in data['issues']:
        created_date = get_created_date(issue)
        resolution_date = get_resolution_date(issue)
        time_diff_list.append(time_diff(created_date, resolution_date)) 

    plt.hist(time_diff_list, bins=20, edgecolor='k')
    plt.xlabel('Количество дней')
    # plt.xticks(np.arange(0, int(max(time_diff_list)), int(max(time_diff_list) / 20)))
    plt.tight_layout()
    plt.ylabel('Количество задач в открытом состоянии')
    plt.title('Гистограмма #1: Время, которое задача провела в открытом состоянии')
    plt.grid(True)
    plt.show()    
    
def graph2():
    status=input('Введите один из предложенных статусов (Open, Resolved, Patch Available, In Progress, Reopened): ')
    params = {
    'jql': 'project = KAFKA AND status = Closed',
    'maxResults': 1000, 
    'expand': 'changelog',
    'fields': 'created'
    }
    data = api(params)
    time_diff_list = changelog(data, status)

    plt.hist(time_diff_list, bins=40, edgecolor='k')
    plt.xlabel('Количество дней')
    plt.tight_layout()
    plt.ylabel(f'Количество задач в состоянии {status}')
    plt.title(f'Гистограмма #2: Время, которое задача провела в состоянии {status}')
    plt.grid(True)
    plt.show()

def graph3():
    date_first, date_second = input('Введите интересующий диапазон дат через пробел без кавычек, например "2023-01-12 2023-11-12": ').split() #'2023-01-12', '2023-11-12'
    params = {
        'jql': f'project = KAFKA AND createdDate >= {date_first} AND createdDate <= {date_second}',
        'maxResults': 1000, 
        'expand': 'changelog',
        'fields': 'created'
    }
    
    data = api(params)
    counter_opened, counter_closed = opened_closed_per_day(data)

    fig, ax = plt.subplots()
    plt.plot(sorted(counter_opened.keys()), counter_opened.values(), marker='o', color='r', linewidth='2')
    plt.plot(sorted(counter_closed.keys()), counter_closed.values(), marker='o', color='y', linewidth='2')
    plt.xlabel('Дата')
    plt.tight_layout()
    plt.ylabel(f'Количество задач в день')
    plt.title('График #3: Количество заведенных и закрытых задач в день')
    plt.grid(True)
    plt.show()

    plt.bar(sorted(counter_opened.keys()), np.cumsum(np.array(list(sorted(counter_opened.values())))))
    plt.bar(sorted(counter_closed.keys()), np.cumsum(np.array(list(sorted(counter_closed.values())))))
    plt.xlabel('Дата')
    plt.tight_layout()
    plt.ylabel('Количество задач в день')
    plt.title('График #3: Накопительный итог по заведенным и закрытым задачам в день')
    plt.grid(True)
    plt.show()

def graph4():    
    params = {
        'jql': 'project = KAFKA AND assignee is not EMPTY AND reporter is not EMPTY',
        'maxResults': 1000, 
        'expand': 'changelog',
        'fields': 'reporter,assignee'
    }
    data = api(params)

    assignee_list = assignee_reporter(data)

    counter_assignee = Counter(assignee_list)
    counter_assignee = dict(sorted(counter_assignee.items(), key=lambda x:x[1], reverse=True)[0:30])

    plt.plot(counter_assignee.keys(), counter_assignee.values()) 
    plt.title('График #4: Общее количество задач ТОП-30 пользователей, в которых он указан как исполнитель и репортер')
    plt.xlabel('Пользователь')
    plt.ylabel('Количество задач')
    plt.xticks(rotation='vertical') 
    plt.tight_layout()
    plt.grid(True)
    plt.show()

    plt.pie(counter_assignee.values(), labels=counter_assignee.keys())
    plt.title('Диаграмма #4: Общее количество задач ТОП-30 пользователей, в которых он указан как исполнитель и репортер')
    plt.tight_layout()
    plt.show()

def graph5():
    assignee = input('Введите имя пользователя, например nehanarkhede или junrao: ')
    params = {
        'jql': f'project = KAFKA AND status = Closed AND assignee={assignee}',
        'maxResults': 1000, 
        'expand': 'changelog',
        'fields': 'assignee, created, resolutiondate'
    }
    data = api(params)
    time_diff_list = []
    for issue in data['issues']:
            created_date = get_created_date(issue)
            resolution_date = get_resolution_date(issue)
            time_diff_list.append(time_diff(created_date, resolution_date))

    plt.hist(time_diff_list, bins=40, edgecolor='black')
    plt.title(f'Гистограмма #5: Время на выполнение задачи пользователем {assignee}')
    plt.xlabel('Количество дней')
    plt.ylabel('Количество задач')
    plt.tight_layout()
    plt.show()

def graph6():
    priority = ['Blocker', 'Critical', 'Major', 'Minor', 'Trivial']
    dict = {}
    for i in priority:
        params = {
            'jql': f'project = KAFKA and priority = {i}',
            'maxResults': 1000, 
            'fields': 'priority'
        }
        data = api(params)
        dict[i] = data['total']

    def func(pct, allvals):
        absolute = int(pct/100.*np.sum(allvals))
        return "{:.1f}%\n({:d})".format(pct, absolute)

    plt.pie(dict.values(), autopct=lambda pct: func(pct, list(dict.values())),
                                    shadow=True, pctdistance=0.6, labeldistance=0.6, startangle=90) 
    plt.legend(dict.keys(), loc="upper left")
    plt.title('Диаграмма #6: Количество задач по степени серьезности')
    plt.tight_layout()
    plt.show()

def data_for_test(): 
    global data_for_test
    data_for_test = {
    "expand": "schema,names",
    "startAt": 0,
    "maxResults": 1000,
    "total": 9266,
    "issues": [
        {
            "expand": "operations,versionedRepresentations,editmeta,changelog,renderedFields",
            "id": "13557529",
            "self": "https://issues.apache.org/jira/rest/api/2/issue/13557529",
            "key": "KAFKA-15807",
            "fields": {
                "resolutiondate": "2023-10-11T10:05:15.000+0000",
                "created": "2023-10-26T09:27:48.000+0000", 
                "reporter": {
                    "self": "https://issues.apache.org/jira/rest/api/2/user?username=apoorvmittal10",
                    "name": "apoorvmittal10",
                    "key": "apoorvmittal10",
                    "displayName": "Apoorv Mittal"
                },
                "assignee": {
                    "self": "https://issues.apache.org/jira/rest/api/2/user?username=apoorvmittal10",
                    "name": "apoorvmittal10",
                    "key": "apoorvmittal10",
                    "displayName": "Apoorv Mittal"
                }
            },
            "changelog": {
                "startAt": 0,
                "maxResults": 1,
                "total": 1,
                "histories": [
                    {
                        
                        "created": "2023-11-07T05:52:16.650+0000",
                        "items": [
                            {
                                "field": "status",
                                "fieldtype": "jira",
                                "from": "1",
                                "fromString": "Open",
                                "to": "5",
                                "toString": "Closed"
                            }
                        ]
                    }
                ]
            }
        }
    ]
}
    return data_for_test