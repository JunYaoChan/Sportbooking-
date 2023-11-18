import sys
from time import sleep
from datetime import time, datetime, timezone, timedelta
from typing import Tuple
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

booking_site_url = "https://soton.leisurecloud.net/Connect/mrmProductStatus.aspx"

begin_time = datetime.combine(datetime.today().date(), time(21, 00, 0))
# Calculate tomorrow's date by adding one day
tomorrow_date = datetime.today().date() + timedelta(1)

# Set the time to 12:01 AM (00:01:00)
tomorrow_time = time(0, 0,0)

# Combine the date and time to get tomorrow's datetime
end_time = datetime.combine(tomorrow_date, tomorrow_time)

max_try = 5

email = sys.argv[1]
password = sys.argv[2]
court = int(sys.argv[3])
reservation_time = int(sys.argv[4])

options = Options()
# Add any desired options to the 'options' object here

driver = webdriver.Chrome(options)
uk_timezone = timezone(timedelta(0), 'UK')


def check_current_time(begin_time: datetime, end_time: datetime) -> Tuple[datetime, bool]:
    '''
    Check if the current time is between 23:59:55 and 00:01:00.
    Returns the current time and if it is between the specified range.
    '''
    current_time = datetime.now()

    return current_time, (begin_time <= current_time) and (current_time < end_time)


def make_a_reservation(email: str, password: str, reservation_time: int) -> bool:
    '''
    Make a reservation for the given time and name at the booking site.
    Return the status if the reservation is made successfully or not.
    '''
    try:
        driver.get(booking_site_url)
        wait = WebDriverWait(driver, 10)
        # Find and fill in the username and password fields
        username = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_InputLogin"]')
        username.send_keys(email)

        password = driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_InputPassword"]')
        password.send_keys(password)

        # Click the login button
        password.send_keys(Keys.RETURN)
        driver.find_element(By.XPATH,
                            '//*[@id="ctl00_MainContent__advanceSearchResultsUserControl_Activities_ctrl2_lnkActivitySelect_lg"]').click()

        # go to next week's page
        for i in range(7):
            element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ctl00_MainContent_Button2"]')))
            element.click()

        time_difference = end_time - datetime.now()
        sleep(time_difference.total_seconds())
        # click the given reservation time's box
        driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_Button2"]').click()
        sleep(0.5)
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'//*[@id="ctl00_MainContent_grdResourceView"]/tbody/tr[{reservation_time - 5}]/td[{court - 4}]/input'))).click()

        driver.find_element(By.XPATH, '//*[@id="ctl00_MainContent_btnBasket"]').click()

        # fill in the name
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        # close the drivers
        driver.quit()


def try_booking(email: str, password: str, reservation_time: int) -> None:
    '''
    Try booking a reservation until either one reservation is made successfully or the attempt time reaches the max_try
    '''
    # initialize the params
    current_time, is_during_running_time = check_current_time(begin_time, end_time)
    reservation_completed = False
    try_num = 1

    # repeat booking a reservation every second
    while True:
        if not is_during_running_time:
            print(f'Not Running the program. It is {current_time} and not between {begin_time} and {end_time}')

            # sleep less as the time gets close to the begin_time
            if current_time >= datetime.combine(datetime.today().date(), time(23, 59, 55)):
                sleep(0.001)
            elif datetime.combine(datetime.today().date(), time(23, 59, 54)) <= current_time < datetime.combine(
                    datetime.today().date(), time(23, 59, 55)):
                sleep(0.5)
            else:
                sleep(1)

            try_num += 1
            current_time, is_during_running_time = check_current_time(begin_time, end_time)
            continue

        print(f'----- try : {try_num} -----')
        # try to get ticket
        reservation_completed = make_a_reservation(email, password, reservation_time,court)

        if reservation_completed:
            print('Got a ticket!!')
            break
        elif try_num == max_try:
            print(f'Tried {try_num} times, but couldn\'t get tickets..')
            break
        else:
            sleep(1)
            try_num += 1
            current_time, is_during_running_time = check_current_time(begin_time, end_time)


if __name__ == '__main__':
    try_booking(email, password, reservation_time)
