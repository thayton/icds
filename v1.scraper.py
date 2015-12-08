#!/usr/bin/env python

import sys
import signal

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException

def sigint(signal, frame):
    sys.exit(0)

class Scraper(object):
    def __init__(self):
        self.url = 'http://icds-wcd.nic.in/icds/icdsawc.aspx'
        self.driver = webdriver.PhantomJS()
        self.driver.set_window_size(1120, 550)

    #--- STATE -----------------------------------------------------
    def get_state_select(self):
        path = '//select[@id="ctl00_ContentPlaceHolder1_dropstate"]'
        state_select_elem = self.driver.find_element_by_xpath(path)
        state_select = Select(state_select_elem)
        return state_select

    def select_state_option(self, value, dowait=True):
        '''
        Select state value from dropdown. Wait until district dropdown
        has loaded before returning.
        '''
        path = '//select[@id="ctl00_ContentPlaceHolder1_dropdistrict"]'
        district_select_elem = self.driver.find_element_by_xpath(path)

        def district_select_updated(driver):
            try:
                district_select_elem.text
            except StaleElementReferenceException:
                return True
            except:
                pass

            return False

        state_select = self.get_state_select()
        state_select.select_by_value(value)

        if dowait:
            wait = WebDriverWait(self.driver, 10)
            wait.until(district_select_updated)

        return self.get_state_select()

    #--- DISTRICT --------------------------------------------------
    def get_district_select(self):
        path = '//select[@id="ctl00_ContentPlaceHolder1_dropdistrict"]'
        district_select_elem = self.driver.find_element_by_xpath(path)
        district_select = Select(district_select_elem)
        return district_select

    def select_district_option(self, value, dowait=True):
        '''
        Select district value from dropdown. Wait until district dropdown
        has loaded before returning.
        '''
        path = '//select[@id="ctl00_ContentPlaceHolder1_dropdistrict"]'
        district_select_elem = self.driver.find_element_by_xpath(path)

        def district_select_updated(driver):
            try:
                district_select_elem.text
            except StaleElementReferenceException:
                return True
            except:
                pass

            return False

        district_select = self.get_district_select()
        district_select.select_by_value(value)

        if dowait:
            wait = WebDriverWait(self.driver, 10)
            wait.until(district_select_updated)

        return self.get_district_select()

    #--- PROJECT ---------------------------------------------------
    def get_project_select(self):
        path = '//select[@id="ctl00_ContentPlaceHolder1_dropproject"]'
        project_select_elem = self.driver.find_element_by_xpath(path)
        project_select = Select(project_select_elem)
        return project_select

    def select_project_option(self, value, dowait=True):
        project_select = self.get_project_select()
        project_select.select_by_value(value)
        return self.get_project_select()

    def load_page(self):
        self.driver.get(self.url)

        def page_loaded(driver):
            path = '//select[@id="ctl00_ContentPlaceHolder1_dropstate"]'
            return driver.find_element_by_xpath(path)

        wait = WebDriverWait(self.driver, 10)
        wait.until(page_loaded)            
        
    def scrape(self):
        def states():
            state_select = self.get_state_select()
            state_select_option_values = [ 
                '%s' % o.get_attribute('value') 
                for o 
                in state_select.options[1:]
            ]

            for v in state_select_option_values:
                state_select = self.select_state_option(v)
                yield state_select.first_selected_option.text

        def districts():
            district_select = self.get_district_select()
            district_select_option_values = [ 
                '%s' % o.get_attribute('value') 
                for o 
                in district_select.options 
                if o.text != '-Select-' 
            ]

            for v in district_select_option_values:
                district_select = self.select_district_option(v)
                yield district_select.first_selected_option.text
            
        def projects():
            project_select = self.get_project_select()
            project_select_option_values = [ 
                '%s' % o.get_attribute('value') 
                for o 
                in project_select.options[1:]
            ]

            for v in project_select_option_values:
                project_select = self.select_project_option(v)
                yield project_select.first_selected_option.text

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
