from datetime import *
import calendar
from bs4 import BeautifulSoup as BS
import re
import pytz

TIMEZONE = pytz.timezone('Australia/Sydney')

class Day():
    def __init__(self, breakfast, lunch, dinner):
        self._breakfast = breakfast
        self._lunch = lunch
        self._dinner = dinner

    @property
    def breakfast(self):
        return self._breakfast

    @property
    def lunch(self):
        return self._lunch

    @property
    def dinner(self):
        return self._dinner

    def __str__(self):
        return (f"Breakfast \n{self.breakfast}\n\n"
                f"Lunch \n{self.lunch}\n\n"
                f"Dinner \n{self.dinner}"
                )

class Lunch():
    def __init__(self, main, veg, salad):
        self._main = main
        self._veg = veg
        self._salad = salad

    @property
    def main(self):
        return self._main

    @property
    def veg(self):
        return self._veg
    
    @property
    def salad(self):
        return self._salad

    def __str__(self):
        if self.veg == "sandwich bar":
            return("GET KEEN IT'S SANDWICH DAY 🥪🥪")
        elif self.main == "selection of brunch items with pastries & extras":
            return("selection of brunch items with pastries & extras")
        else:
            return (f"Main:\n {self.main}\n\n"
                    f"Vegetarian:\n {self.veg}\n\n"
                    f"Salad:\n {self.salad}\n\n")

class Dinner():
    def __init__(self, main, vegetarian, vegAndCarb, dessert):
        self._main = main.strip()
        self._vegetarian = vegetarian
        self._vegAndCarb = vegAndCarb
        self._dessert = dessert

    @property
    def main(self):
        return self._main

    @property
    def vegetarian(self):
        return self._vegetarian

    @property
    def vegAndCarb(self):
        return self._vegAndCarb

    @property
    def dessert(self):
        return self._dessert

    def __str__(self):
        if self.vegetarian == "chef’s choice":
            return(f"It's a surprise! It's the chef's choice today 👩‍🍳")
        elif self.vegetarian == "burger night":
            return(f"Burger night baby 🍔")
        elif self.vegetarian == "pizza pasta night":
            return(f"It's pizza and pasta night 🍕!!")
        else:
            return (f"Main:\n {self.main}\n\n"
                    f"Vegetarian:\n {self.vegetarian}\n\n"
                    f"Veg and Carb:\n {self.vegAndCarb}\n\n"
                    f"Dessert:\n {self.dessert}")

def getWeek():
    soup = BS(open('menu.html'), 'html.parser')
    weekMenu = {}
    tables = soup.find_all('table')
    for table in tables:
        table_body = table.find('tbody')

        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            for i, col in enumerate(cols):
                ele = col.text.strip()
                ele = ele.replace('\n', ' ')
                # print(repr(ele))
                ele = ele.replace(' \xa0', ' and ')
                if i == 0:
                    # check if main or veg/vegan
                    if ele in weekMenu:
                        ele = ele + ' dinner'
                    weekMenu[ele] = []
                    currentMeal = ele
                else:
                    weekMenu[currentMeal].append(ele)
    return weekMenu

def getDayMenu(day):
    weekMenu = getWeek()

    breakfast = weekMenu['residential breakfast'][day]
    lunch = Lunch(weekMenu['main'][day], weekMenu['vegetarian/ vegan'][day], weekMenu['salad'][day])
    dinner = Dinner(weekMenu['main dinner'][day], weekMenu['vegetarian/ vegan dinner'][day], weekMenu['Veg and salad'][day], weekMenu['dessert'][day])

    dayMenu = Day(breakfast, lunch, dinner)

    return dayMenu


if __name__ == '__main__':
    current_day = datetime.now(TIMEZONE).weekday()
    print(getDayMenu(2))
    # for i in range(7):
    #     print(getDayMenu(i))
