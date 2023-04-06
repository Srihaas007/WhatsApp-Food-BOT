import json, os

from typing import List, NewType, Union
from tinydb import Query, TinyDB


db = TinyDB(os.path.abspath('db.json'))
Order_Table = db.table('Order')

class Pizza():
    availableToppings = [
        "cheese","pepperoni", "sausage", "bacon"
    ]
    def __init__(self, toppings: Union[int, List[int]]):
        if type(toppings) == list:
            self.toppings = [Pizza.availableToppings[val - 1] for val in toppings]
        else:
            self.toppings = []
            self.toppings.append(Pizza.availableToppings[toppings - 1])

class Drink():
    availableDrinks = [
        "Coke","Fanta", "Sprite"
    ]
    def __init__(self, choice: Union[int, List[int]]):
        if type(choice) == list:
            self.choice = [Drink.availableDrinks[val - 1] for val in choice]
        else:
            self.choice = []
            self.choice.append(Drink.availableDrinks[choice - 1])

class Order():
    """
    create an order 
    """
    def __init__(self, address=None, orderLocation=None, id=None, phone_no=None, possible_locations=None, cart=None) -> None:
        self.orderStatus = "incomplete"
        self.address = address
        self.orderLocation = orderLocation
        if cart == None:
            self.cart = []
        else:    
            self.cart = cart
        self.id = id
        self.phone_no = phone_no
        self.possible_locations = possible_locations

    @staticmethod
    def orderFromStore(order_dict: dict):
        """
        parameterized constructor
        """
        return Order(orderLocation=order_dict['orderLocation'], id=order_dict['id'], 
        phone_no=order_dict['phone_no'], possible_locations=order_dict['possible_locations'], 
        cart=order_dict['cart'], address=order_dict['address'])

    def addToCart(self, item):
        self.cart.append(item)

    def addLocation(self, location):
        self.orderLocation = location

    def removeFromCart(self, item):
        self.cart.remove(item)

    @staticmethod
    def deleteFromStore(id):
        """
        docstring
        """
        User = Query()
        Order_Table.remove(User.id == id)

    def completeOrder(self):
        self.orderStatus = "complete"

    def store(self):
        User = Query()
        order_dict = json.loads(json.dumps(self.__dict__))
        if(Order_Table.get(User.id == self.id) == None):
            Order_Table.insert(order_dict)
        else:
            Order_Table.update(order_dict)

    @staticmethod
    def getOrder(id):
        User = Query()
        order = Order_Table.get(User.id == id)
        return json.loads(json.dumps(order))
