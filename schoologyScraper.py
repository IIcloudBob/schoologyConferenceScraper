from selenium import webdriver
import requests
import time
from threading import Thread
from json import loads




schoolPrefix = ""     # get from the login page. All you need is whats before .schoology.com
schoolId = ""          # this value is a number. get from schoology login page link (&school=...)

username = ""
password = ""          # once filled in don't share this code with anyone or they can steal this info. We need this information to actually login to the schoology page and start extracting the course information

def getCourseInfo():
    def login():
        print("made by IIcloudBob. Enjoy!")
        a = requests.Session()
        loginRequest = a.post(f"https://{schoolPrefix}.schoology.com/login/ldap?&school={schoolId}", headers={
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-LU,en-US;q=0.9,en;q=0.8",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"97\", \"Chromium\";v=\"97\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        },
            data=f"mail={username}&pass={password}&school_nid={schoolId}&form_build_id=721e8fa-qWPtnrnKq5Uo0YZbfkRBd0fNuko_xWYygapnXzige4U&form_id=s_user_login_form",
        )
        courseRequest = a.get(f"https://{schoolPrefix}.schoology.com/iapi2/site-navigation/courses")
        courseInfo = {}
        for course in loads(courseRequest.content)["data"]["courses"]:
            courseInfo[str(course["nid"])] = course["courseTitle"]
        return a.cookies, courseInfo

    loginInfo, courseInfo = login()

    messages = list()

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")   

    #  uncomment the two above if you want the chrome browser to not be visible when scraping

    def DoWork(course, courseName, messages, options):
        global isCourseRunning
        path = 'chromedriver.exe'
        driver = webdriver.Chrome(executable_path=path, options=options)
        for c in loginInfo:
            driver.get(f'https://{schoolPrefix}.schoology.com/home')
            driver.add_cookie(
                {'name': c.name, 'value': c.value, 'path': c.path})
        driver.get(
            f'https://{schoolPrefix}.schoology.com/apps/191034318/run/course/{course}')
        time.sleep(6)
        driver.switch_to.frame(driver.find_element_by_id("schoology-app-container"))
        scripts = [i.get_attribute("outerHTML") for i in driver.find_elements_by_tag_name("script") if len(i.get_attribute("src")) < 1 and i.get_attribute("type") == "text/javascript"]
        
        if not len(scripts) == 0:
            info = scripts[0]
        # if len(children) > 1:
        if not 'info' in vars() or 'info' in globals():
            messages.append(f'Rate limit was hit. Wait a bit  and retry  (_{courseName}_)')
            return
        if '''"conferences":[]''' or  '''"status":"1"''' in info:
            # \033[92m
            messages.append(
                f'No conferences found for _{courseName}_')
        elif '''"status_display":"In progress"''' in info and '''"status":"2"''' in info:
            isCourseRunning = True
            # \033[93mgoto
            messages.insert(1,
                f'\n**NUCLEAR WARHEAD** DETONATING IN T-20 SECONDS. ALL PERSONNEL, HEAD TO THE [BLAST SHELTER](https://{schoolPrefix}.schoology.com/apps/191034318/run/course/{course}) **IMMEDIATELY**\n')

        driver.quit()

    threads = []
    for course, courseName in courseInfo.items():
        threads.append(Thread(target=DoWork, args=(
            course, courseName, messages, options,)))

    for i in threads:
        i.start()

    for i in threads:
        i.join()

    if isCourseRunning:
        printVal = '\n'.join(messages)
        print(printVal)
    else:
        printVal = '\n'.join(messages)
        print(printVal)


isCourseRunning = False         # dont change this variable.
getCourseInfo()

