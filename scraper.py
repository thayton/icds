#!/usr/bin/env python

import sys
import signal

from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

def sigint(signal, frame):
    sys.exit(0)

def make_waitfor_elem_updated_predicate(driver, waitfor_elem_xpath):
    elem = driver.find_element_by_xpath(waitfor_elem_xpath)

    def elem_updated(driver):
        try:
            elem.text
        except StaleElementReferenceException:
            return True
        except:
            pass

        return False

    return lambda driver: elem_updated(driver)

class Scraper(object):
    def __init__(self):
        self.url = 'http://icds-wcd.nic.in/icds/icdsawc.aspx'
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)

    def get_select(self, xpath):
        select_elem = self.driver.find_element_by_xpath(xpath)
        select = Select(select_elem)
        return select

    def select_option(self, xpath, value, waitfor_elem_xpath=None):
        if waitfor_elem_xpath:
            func = make_waitfor_elem_updated_predicate(
                self.driver, 
                waitfor_elem_xpath
            )

        select = self.get_select(xpath)
        select.select_by_value(value)

        if waitfor_elem_xpath:
            wait = WebDriverWait(self.driver, 10)
            wait.until(func)

        return self.get_select(xpath)

    def make_select_option_iterator(self, xpath, waitfor_elem_xpath):
        def next_option(xpath, waitfor_elem_xpath):
            select = self.get_select(xpath)
            select_option_values = [ 
                '%s' % o.get_attribute('value') 
                for o 
                in select.options 
                if o.text != '-Select-'
            ]

            for v in select_option_values:
                select = self.select_option(xpath, v, waitfor_elem_xpath)
                yield select.first_selected_option.text

        return lambda: next_option(xpath, waitfor_elem_xpath)

    def load_page(self):
        self.driver.get(self.url)

        def page_loaded(driver):
            path = '//select[@id="ctl00_ContentPlaceHolder1_dropstate"]'
            return driver.find_element_by_xpath(path)

        wait = WebDriverWait(self.driver, 10)
        wait.until(page_loaded)            

    def scrape(self):
        states = self.make_select_option_iterator(
            '//select[@id="ctl00_ContentPlaceHolder1_dropstate"]',
            '//select[@id="ctl00_ContentPlaceHolder1_dropdistrict"]'
        )

        districts = self.make_select_option_iterator(
            '//select[@id="ctl00_ContentPlaceHolder1_dropdistrict"]',
            '//select[@id="ctl00_ContentPlaceHolder1_dropdistrict"]'
        )

        projects = self.make_select_option_iterator(
            '//select[@id="ctl00_ContentPlaceHolder1_dropproject"]',
            None
        )

        self.load_page()

        for state in states():
            print state
            for district in districts():
                print 2*' ', district
                for project in projects():
                    print 4*' ', project

if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint)
    scraper = Scraper()
    scraper.scrape()
