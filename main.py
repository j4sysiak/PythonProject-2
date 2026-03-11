from menu import Menu, MenuItem
from coffee_maker import CoffeeMaker
from money_machine import MoneyMachine



# 1. Tworzenie obiektów z klas
money_machine = MoneyMachine()
coffee_maker = CoffeeMaker()
menu = Menu()

is_on = True

# 2. Główna pętla programu
while is_on:
    options = menu.get_items()
    choice = input(f"What would you like? ({options}): ")

    if choice == "off":
        is_on = False
    elif choice == "report":
        coffee_maker.report()
        money_machine.report()
    else:
        drink = menu.find_drink(choice)
        # Jeśli napój istnieje, sprawdzamy zasoby i płatność
        if drink is not None:
            if coffee_maker.is_resource_sufficient(drink) and money_machine.make_payment(drink.cost):
                coffee_maker.make_coffee(drink)