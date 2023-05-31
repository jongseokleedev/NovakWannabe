from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import schedule
import os
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
from selenium.webdriver.common.by import By
import telegram
from dotenv import load_dotenv
import asyncio
import re

#@TODO
#1.SMS 전송 (Done)
#2.오전,오후 시간 구분해서 로깅 (Done)
#3.전체페이지에서 하나씩 클릭해서 들어가기 (URL 변경 회피) (TODO)


def is_element_exist(class_name):
    try:
        driver.find_elements(By.CLASS_NAME,class_name)
        return True
    except NoSuchElementException:
        return False

async def send_message(message):
    if message in sent_messages:
        print("Message already sent before: " + message)
        return
    load_dotenv()
    telegram_token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    bot=telegram.Bot(token=telegram_token)
    await bot.sendMessage(chat_id, text=message, parse_mode="Markdown")
    sent_messages.add(message)
    print("messgae sent done")


def court_reservation(url_list):
    # 시간 로깅
    print("탐색 시작 시간 ", datetime.now().strftime("%I:%M:%S %p"))

    # url 접속
    for i, url in enumerate(url_list):
        print("@@@@@@@@@@@@@@@@@@@@@@@@@@@ Court No. ", i+1, " Check Start @@@@@@@@@@@@@@@@@@@@@@@@@@2")
        print("current url is " + url)
        driver.get(url)
        # 웹 로딩될 때까지 sleep
        time.sleep(1)

        # calendar-date를 찾을 수 있는 경우에만 실행
        has_calendar = is_element_exist("calendar-date")
        if has_calendar:
            time_available=False
            time_section_list = driver.find_elements(By.CLASS_NAME,'lst_time')  # 오전 / 오후
            time_element_list = map(lambda time_section: time_section.find_elements(By.XPATH,".//li"),
                                    time_section_list)  # [['8:00'], ['9:00']]
            flatten_time_element_list = [y for x in list(time_element_list) for y in x]  # ['8:00', '9:00']
            # 오전 시간별 로직 실행
            for time_element in flatten_time_element_list:
                time_element_link=time_element.find_element(By.TAG_NAME,'a')
                time_element_color = time_element_link.find_element(By.TAG_NAME,'span').value_of_css_property(
                    'background-color')
                # time_index = time_element_link.get_attribute('data-time-index')
                # 시간 색상이 연두색 (rgba = (224, 254, 211, 1))이라면 예약알림 로직 실행
                if time_element_color == "rgba(224, 254, 211, 1)":
                    time_available = True
            if time_available == True:
                court_monthly_reservation()
            else:
                #예약 가능한 일자 하나도 없는 경우
                continue;
        else:
            # calendar가 없으면
            print("ERROR: no calendar")


def court_monthly_reservation():
    day_count = 0
    title_text = driver.find_element(By.CLASS_NAME,"service_info_tit").text
    
    current_month = title_text[0]
    court_name = title_text[3:]
    month_element = driver.find_element(By.CLASS_NAME,"calendar-title")
    month_next_element = driver.find_element(By.CLASS_NAME,"calendar-btn-next-mon")
    current_selected_month=month_element.find_element(By.XPATH, '//span[@ng-bind="$ctrl.baseDate.get(\'month\') + 1"]').text
    
    # 현재 체크하고있는 달과 캘린더의 달이 다른 경우(전체 달력이 표현되지 않고 일부만 표현되는 경우), 다음을 클릭하여 현재 달로 넘어간다.
    if(current_selected_month!=current_month):
        month_next_element.click()
        time.sleep(0.5)

    day_elements = driver.find_elements(By.CLASS_NAME,"calendar-date")
    
    # 일자 별 Logic 실행
    for day in day_elements:
        day_num_element = day.find_element(By.CLASS_NAME,"num")
        day_num_text = day_num_element.text
        # day 색이 회색 (hex = e4e4e4 / rgba = (228, 228, 228, 1))이 아닐때 실행
        if day_num_element.value_of_css_property('color') != "rgba(228, 228, 228, 1)":
            print(day_num_text, "일 확인 중..")

            # 일자 클릭
            day.click()
            # 일자 클릭 후 time list 로딩까지 sleep
            time.sleep(1)
            # 오전 시간 list 추출
            am_time_section_list = driver.find_element(By.CLASS_NAME,'am').find_elements(By.CLASS_NAME,'lst_time')  # 오전 / 오후
            am_time_element_list = map(lambda time_section: time_section.find_elements(By.XPATH,".//li"),
                                    am_time_section_list)  # [['8:00'], ['9:00']]
            am_flatten_time_element_list = [y for x in list(am_time_element_list) for y in x]  # ['8:00', '9:00']
            # 오전 시간별 로직 실행
            for time_element in am_flatten_time_element_list:
                time_element_link=time_element.find_element(By.TAG_NAME,'a')
                time_element_color = time_element_link.find_element(By.TAG_NAME,'span').value_of_css_property(
                    'background-color')
                time_index = time_element_link.get_attribute('data-time-index')
                # 시간 색상이 연두색 (rgba = (224, 254, 211, 1))이라면 예약알림 로직 실행
                if time_element_color == "rgba(224, 254, 211, 1)" and (time_index =="8" or time_index == "9" or time_index =="6" or time_index =="7"):
                    # 요일 정보 추출
                    sub_title_text = driver.find_element(By.CLASS_NAME,"service_info_dsc").text                                                
                    match = re.search(r'\((.*?)\)', sub_title_text)
                    if match:
                        day_info = match.group(1)
                    else:
                        day_info = "ERR: No match"
                    # time_element.click()
                    message="{} {}일 오전 {}시 {}요일 예약 가능합니다.".format(court_name, day_num_text, time_index, day_info)
                    print(message)
                    asyncio.run(send_message(message))



            # 오후 시간 list 추출
            pm_time_section_list = driver.find_element(By.CLASS_NAME,'pm').find_elements(By.CLASS_NAME,'lst_time')  # 오전 / 오후
            pm_time_element_list = map(lambda time_section: time_section.find_elements(By.XPATH,".//li"),
                                    pm_time_section_list)  # [['8:00'], ['9:00']]
                                                
            pm_flatten_time_element_list = [y for x in list(pm_time_element_list) for y in x]  # ['8:00', '9:00']
            # 오후 시간별 로직 실행
            for time_element in pm_flatten_time_element_list:
                time_element_link=time_element.find_element(By.TAG_NAME,'a')
                time_element_color = time_element_link.find_element(By.TAG_NAME,'span').value_of_css_property(
                    'background-color')
                time_index = time_element_link.get_attribute('data-time-index')
                # 시간 색상이 연두색 (rgba = (224, 254, 211, 1))이라면 예약알림 로직 실행
                if time_element_color == "rgba(224, 254, 211, 1)" and (time_index =="8" or time_index == "9" or time_index =="6" or time_index =="7"):
                    sub_title_text = driver.find_element(By.CLASS_NAME,"service_info_dsc").text                                                
                    # 요일 정보 추출
                    match = re.search(r'\((.*?)\)', sub_title_text)
                    if match:
                        day_info = match.group(1)
                    else:
                        day_info = "ERR: No match"
                    # time_element.click()
                    
                    message="{} {}일 오후 {}시 {}요일 예약 가능합니다.".format(court_name, day_num_text, time_index, day_info)
                    print(message)
                    asyncio.run(send_message(message))

        day_count += 1

def get_driver(driver_path):
    # localhost:9222 포트로 실행된 크롬 option 설정
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    # 다운로드 받은 chrome driver 경로 설정
    driver = webdriver.Chrome(driver_path, options=chrome_options)
    return driver


def main(schedule_cycle, url_list):
    # load_dotenv()
    # telegram_token = os.environ.get('TELEGRAM_TOKEN')
    # bot=telegram.Bot(token=telegram_token)
    # updates=await bot.getUpdates()
    # for update in updates:
    #     print(update.message)
    # job 수행 주기 및 수행할 함수 등록
    schedule.every(schedule_cycle).seconds.do(lambda: court_reservation(url_list))

    # 종료할때까지 무한 Loop
    while True:
        # 1초 주기로 등록된 스케쥴 job 의 계획을 확인 및 수행
        schedule.run_pending()
        time.sleep(1)

# 크롬 제어를 위한 웹드라이버 설정 (웹드라이버 설치 경로)
sent_messages = set()
driver_path = "/opt/homebrew/bin/chromedriver"
driver = get_driver(driver_path)

# job 수행 주기 설정 (단위: 초)
schedule_cycle = 5
#양재
url_list=[
    # "https://booking.naver.com/booking/10/bizes/210031/items/4394832",  # 야외 1번 코트
    # "https://booking.naver.com/booking/10/bizes/210031/items/4394834",  # 야외 2번 코트
    # "https://booking.naver.com/booking/10/bizes/210031/items/4394835",  # 야외 3번 코트
    # "https://booking.naver.com/booking/10/bizes/210031/items/4394836",  # 야외 4번 코트
    # "https://booking.naver.com/booking/10/bizes/210031/items/4394837",  # 야외 5번 코트
    # "https://booking.naver.com/booking/10/bizes/210031/items/4394839",  # 야외 6번 코트
    "https://booking.naver.com/booking/10/bizes/210031/items/4394840",  # 야외 7번 코트
    "https://booking.naver.com/booking/10/bizes/210031/items/4394841",   # 야외 8번 코트
    "https://booking.naver.com/booking/10/bizes/210031/items/4394828",  # 실내 A 코트
    "https://booking.naver.com/booking/10/bizes/210031/items/4394829",  # 실내 B 코트
    "https://booking.naver.com/booking/10/bizes/210031/items/4394830",  # 실내 C 코트
]

#내곡
# url_list=[
#     "https://booking.naver.com/booking/10/bizes/217811/items/4404094", # 내곡 1번
#     "https://booking.naver.com/booking/10/bizes/217811/items/4404095", # 내곡 2번
#     "https://booking.naver.com/booking/10/bizes/217811/items/4404097", # 내곡 3번
#     "https://booking.naver.com/booking/10/bizes/217811/items/4404098", # 내곡 4번
#     "https://booking.naver.com/booking/10/bizes/217811/items/4404101", # 내곡 5번
#     "https://booking.naver.com/booking/10/bizes/217811/items/4404102", # 내곡 6번
# ]

# [참고] 양재 매헌시민의 숲 메인 주소
# https://booking.naver.com/booking/10/bizes/210031
# [참고] 내곡 주소
# https://booking.naver.com/booking/10/bizes/217811

# 메인 로직 실행
main(schedule_cycle, url_list)
