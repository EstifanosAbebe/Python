from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
from fractions import Fraction
from mimetypes import init
from selenium import webdriver
from selenium.webdriver.chrome import service
import time 
import jellyfish

'''
path = "C:\\Users\\estifo\\Desktop\\coronometer scrapper\\chromedriver.exe"

webdriver_service = service.Service(path)
webdriver_service.start()


driver  = webdriver.Chrome(path)
option = webdriver.ChromeOptions()
#option.add_argument('headless')
#option.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(path,options=option)
driver.get("https://cronometer.com/login/")
time.sleep(3)
input_email = driver.find_element_by_xpath("//input[@type='email']")
input_email = driver.find_element_by_xpath("//input[@type='email']")input_pass = driver.find_element_by_xpath("//input[@type='password']")
login_button  = driver.find_element_by_xpath("//button[@id='login-button']")
time.sleep(5)
input_email.send_keys('userimage')
time.sleep(3)
input_pass.send_keys('97DurOh$9egK#d!W1hHEB^BBO')
time.sleep(3)
login_button.click()
time.sleep(30)
pr_day = driver.find_element_by_xpath("/html/body/div[1]/div[4]/div[2]/div[1]/div/table/tbody/tr/td[1]/div/div[2]/div/button[1]")
pr_day.click()
'''

unit_measure = ['teaspoon', 'Cups','tsp', 'tablespoon', 'small' , 'sl' , 'tbl', 'tbs', 'tbsp', 'c', 'ts', 'dessertspoon', 'dsp', 'dssp', 'dstspn', 'fluid ounce', 'fl oz', 'gill', 'cup', 'can', 'pint', 'pt', 'fl pt', 'quart', 'qt', 'fl qt', 'gallon', 'gal', 'ml', 'milliliter', 'millilitre', 'cc', 'l', 'liter', 'litre', 'dl', 'deciliter', 'decilitre', 'pound', 'lb', 'ounce', 'oz', 'mg', 'milligram', 'milligramme', 'g', 'gram', 'gramme', 'kg', 'kilogram', 'kilogramme', 'drop', 'dr', 'smidgen', 'smdg', 'smi', 'pinch', 'pn', 'Dash of', 'ds', 'saltspoon', 'scruple', 'ssp', 'coffeespoon', 'csp', 'fluid dram', 'fl.dr', 'wineglass', 'wgf', 'gill', 'teacup', 'tcf', 'cup', ' C', 'pottle', 'pot', 'splash']
processing = ['crushed', 'finely sliced', 'thinly sliced', 'peeled and sliced', 'peeled', 'sliced', 'finely chopped', 'chopped', 'shred', 'shredded', 'shucked', 'sieved', 'skewered', 'snipped', 'stirred', 'cut into small pieces', 'cut into large pieces', 'cut in large chunks', 'crushed', 'grated', 'mashed', 'melted', 'mulled', 'parboiled', 'rolled', 'seared', 'drained and rinsed', 'minced', 'quartered', 'al dente', 'roasted', 'steamed', 'fried', 'skin removed', 'skin and stone removed', 'to taste', 'crushed', '(optional)', 'Dash of', 'zested', 'toasted', 'rinsed and drained', 'peeled and diced', 'separated into rings', 'split, toasted', 'halved', 'cut in half', 'for garnish', 'optional', 'seeded', 'pitted', 'torn', 'coarsely broken']
fractions = {'½': 1/2, '¼': 1/4, '⅓': 1/3, '⅔': 2/3, '¾': 3/4, '⅛': 1/8, '⅜': 3/8, '⅝': 5/8, '⅞': 7/8, '⅐': 1/7, '⅑': 1/9, '⅒': 1/10}
strange_char =['Â', 'â…', 'â…“']

def ireplace(old, new, text):

    idx = 0
    while idx < len(text):
        index_l = text.lower().find(old.lower(), idx)
        if index_l == -1:
            return text
        text = text[:index_l] + new + text[index_l + len(old):]
        idx = index_l + len(new)
    return text


with open("HighProtein-PlantBased-Recipes.txt", "r") as file:
    receipes = file.read()
formatted_list_meals = receipes.split("-----")

# Search for unit and unit measure eg 1 tbsp
i = 0
receipe_names = []
rr_name = ""
for r in receipes.split("\n"):
    # food = r
    if set(r) == set('-'):  # r == "-----":
        # print('SET', r, set(r), set(r) == set('-') )
        print()
        i = 0
    elif i == 0:
        receipe_name = r
        print('Receipe Name:', receipe_name)
        receipe_names.append(receipe_name)
        i += 1
    else:
        unit = ''
        if '/' in r:  # Search for any number with fraction eg '3 1/2 cups' or '1/3 oz' in recipe
            last_num = re.findall(r'\d+', r)[-1]  # Finds the last number
            pos = r.find(last_num)
            frac = r[:pos+len(last_num)].strip()   #  eg '3 1/2'
            # print('last num', last_num, pos, r[:pos+len(last_num)].strip())
            # if ' ' in frac: #  eg '3 1/2'
            #    res = re.sub(r'^(\d+)\s+(\d+)/(\d+)$', lambda m: str(float(int(m.group(1)) + int(m.group(2)) / int(m.group(3)))), frac)
            # else:
            res = round(float(sum(Fraction(s) for s in frac.split())), 3)
            unit = res
        else:
            res = re.search('[0-9]+', r)  # find any numbers in string
            if res:  # if there is a result get first number
                unit = res.group(0)
                # food = food.replace(str(unit), '')
                # print('Unit:', unit)

        # Check for fraction characters eg ½, ¼  and convert to decimal
        for c in strange_char:
            if c in r.split()[0]:
                frac = r.split()[0].replace(c, '')
                # print('Frac', r.split()[0], frac, c)
                # food = food.replace(str(frac), '')

                if frac in fractions:  # Check if fraction in dictionary
                    unit = fractions[frac]
                    # print('Unit frac:', unit, type(unit))

        measure = ''
        if unit != '':
            measure = r.split(' ')[1].replace(',', '')  # assume the second word is the measure
            for u in unit_measure:
                # units = r.split(u)  #
                # a_string.partition('.')
                if u+' ' in r:
                    measure = u
                    # food = r.replace(measure, '')
                    break
                    # print('Measure:', measure)

        food = r[r.index(measure) + len(measure):].replace(',', '').lower().strip()
        # print('Food: ', food)
        for c in strange_char:
            if c in food:
                # print('Found', c)
                food = food.replace(c, '')
            # print('Food1: ', food)

        processed = ''
        for p in processing:
            if p in food:
                # print('Found', p)
                processed = p
                food = food.replace(p, '')  # Case sensitive
                # food = ireplace(p, '', food)  # Case insensitive
            # print('Food2: ', food)
        
        food = food.replace(';', '')

        print(r.ljust(55), 'Unit:', str(unit).ljust(6), 'Measure:', measure.ljust(10), 'Food:', food.ljust(45), 'Processing:', processed)
'''
        if(rr_name == receipe_name):
            print()
        else:
            next_day = driver.find_element_by_xpath("/html/body/div[1]/div[4]/div[2]/div[1]/div/table/tbody/tr/td[1]/div/div[2]/div/button[2]")
            next_day.click()
            add_note = driver.find_element_by_xpath("/html/body/div[1]/div[4]/div[2]/div[1]/div/table/tbody/tr/td[2]/div/div[1]/button[4]")
            add_note.click()
            time.sleep(3)

            add_note_diary = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div[1]/textarea")
            add_note_diary.click()
            add_note_diary.send_keys(receipe_name)     # "My name"
            time.sleep(3)
            

            save_note = driver.find_element_by_xpath("/html/body/div[5]/div/div/div[2]/div[5]/button[2]")
            save_note.click()

            rr_name = receipe_name
        
        time.sleep(3)
        #add food
        add_food_button = driver.find_element_by_xpath("/html/body/div[1]/div[4]/div[2]/div[1]/div/table/tbody/tr/td[2]/div/div[1]/button[1]")
        add_food_button.click()
        #search food
        time.sleep(10)
        item_search_bar = driver.find_element_by_xpath("/html/body/div[@class='prettydialog']/div[@class='popupContent']/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/input")
        text = str(food.ljust(45))
        item_search_bar.send_keys(text)
        time.sleep(3)
        table = driver.find_element_by_xpath("//html/body/div[@class='prettydialog']/div[@class='popupContent']/div[1]/div[2]/div[1]/div[1]/div[5]/div[1]/div[1]/div[1]/table/tbody")
        tt = table.find_elements_by_xpath(".//*")
        time.sleep(3)
        total_len = len(tt)
        total_len = total_len - 5
        max_amount = total_len / 5

        list_length = 0
        if(max_amount >= 5):
            list_length = 5
        else:
            list_length = max_amount
        if(list_length > 0):
            max = 1 + list_length*5
            num = 6
            list = []
            while(num <= max):
                list.append([0,tt[num].text,num])
                num = num + 5
            #comparition
            score = 0
            pin =0
            while(pin < list_length):
                text_tocompare = list[pin][1]
                score = jellyfish.jaro_distance(text_tocompare,text)
                score = int(score * 0.9 * 100)
                score = score + 10 - pin*2
                list[pin][0] = score
                pin = pin + 1
            #find highest
            higest_score = list[0][2]
            comp_score = list[0][0]
            for i in list:
                if(i[0]>comp_score):
                    higest_score = i[2]
                comp_score = i[0]
            tt[higest_score].click()
            time.sleep(3)
            value_input = driver.find_element_by_xpath("/html/body/div[@class='prettydialog']/div[@class='popupContent']/div[1]/div[2]/div[1]/div[1]/div[7]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/input")
            value_input.send_keys(str(unit).ljust(6))
            time.sleep(3)
            d_list = driver.find_element_by_xpath("/html/body/div[@class='prettydialog']/div[@class='popupContent']/div[1]/div[2]/div[1]/div[1]/div[7]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/select")
            droplist = d_list.find_elements_by_xpath(".//*")
            pp = len(droplist)
            zr = 0
            unit = (measure).ljust(6)
            
            if(unit == 's'):
                unit = "small"
            
            print(unit)
            while(zr<pp):
                if(unit in str(droplist[zr].text)):
                    droplist[zr].click()
                    print(unit + "clicked")
                print(zr)
                zr = zr + 1
            add_buttod = driver.find_element_by_xpath("/html/body/div[@class='prettydialog']/div[@class='popupContent']/div[1]/div[2]/div[1]/div[1]/div[7]/div[1]/div[1]/div[3]/div[2]/div[1]/div[1]/div[3]/div[2]/div[1]/div/button")
            add_buttod.click()
        else:
            print('the text ')
        
'''
