from bs4 import BeautifulSoup
import requests
from word2number import w2n
import pandas as pd
from datetime import datetime


def __get_number(text):
    try:
        return w2n.word_to_num(text)
    except Exception as e:
        return 1


def __parser(text):
    # Everything to lower
    text = text.lower().split()
    num = __get_number(text[0])
    if 'tampa' in text and ('student' in text or 'students' in text
                            or 'student-employee:' in text):
        return 'Tampa', 'Student', num
    elif 'tampa' in text and ('employee' in text or 'employees' in text):
        return 'Tampa', 'Employee', num
    elif 'st.' in text and ('student' in text or 'students' in text):
        return 'St. Pete', 'Student', num
    elif 'st.' in text and ('employee' in text or 'employees' in text):
        return 'St. Pete', 'Employee', num
    elif ('health' in text or 'medical'
          in text) and ('employee' in text or 'employees' in text
                        or 'resident' in text or 'residents' in text):
        return 'Health', 'Employee', num
    elif ('health' in text or 'medical' in text) and ('student' in text
                                                      or 'students' in text):
        return 'Health', 'Student', num
    elif 'sarasota-manatee' in text and ('student' in text
                                         or 'students' in text):
        return 'Sarasota Manatee', 'Student', num
    elif 'sarasota-manatee' in text and ('employee' in text
                                         or 'employees' in text):
        return 'Sarasota Manatee', 'Employee', num
    else:
        print('__parser has an error')
        #TODO Include Sarasota campus when cases increase significantly
        return -1, -1, -1


def __get_data():
    url = "https://www.usf.edu/coronavirus/updates/usf-cases.aspx"
    response = requests.get(url)
    pageContent = response.content
    soup = BeautifulSoup(pageContent, 'html.parser')
    dataDiv = soup.find('div', {'class': 'article-body'})

    # Get all the available dates
    datesTag = dataDiv.find_all('h3')
    datesText = []
    for date in datesTag:
        datesText.append(date.get_text())

    # Get all the data regarding cases
    # Lists for data frame
    dataDict = {'dates': [], 'locations': [], 'occupations': [], 'cases': []}

    casesTag = dataDiv.find_all('ul')
    for case, date in zip(casesTag, datesText):
        dailyContent = case.find_all('li')
        for text in dailyContent:
            location, occupation, numOfCases = __parser(text.get_text())
            dataDict.get('locations').append(location)
            dataDict.get('occupations').append(occupation)
            dataDict.get('cases').append(numOfCases)
            dataDict.get('dates').append(
                (date + ' ' + str(datetime.today().year)).title())
    # + ' ' +str(datetime.today().year)
    # df['dates'] = df['dates'].apply(lambda date: datetime.strptime(date, '%B %d %Y'))
    df = pd.DataFrame(dataDict)
    df = df.reindex(index=df.index[::-1])
    df = df.groupby(['dates', 'locations', 'occupations'],
                    sort=False,
                    as_index=False).sum()
    return df.to_json()