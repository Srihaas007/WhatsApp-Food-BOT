import requests, os, json

from uuid import uuid4
from flask import Flask, request, session
from dotenv import load_dotenv
from twilio import twiml
from twilio.twiml.messaging_response import MessagingResponse 
from pprint import pprint
from utils import Drink, Order, Pizza

load_dotenv()

with open("db.json", "w") as db:
    db.close()

app = Flask(__name__)
googleApiKey = os.getenv('GOOGLE_API_KEY')
# gmaps = googlemaps.Client(key=googleApiKey)

secret_key = str(uuid4())
app.secret_key = secret_key

def printMenuToUser(twilResp: MessagingResponse):
    twilResp.message("1 - Pizza")
    twilResp.message("2 - Soft Drinks")

def cartCleanReplace(item: str):
    conditions = {'1': '{','2': '}', '3': '\\', '4':'"', '5':'[',
        '6':'{', '7':'}', '8':']', '9': ':', '10': ' '}
    for _, value in conditions.items():
        item = item.replace(value, '')
    return item

def createUser():
    if 'user' not in session:
        session['user'] = str(uuid4())

def printPizzaToppings(twilResp: MessagingResponse):
    twilResp.message("1 - Cheese")
    twilResp.message("2 - Pepperoni")
    twilResp.message("3 - Sausage")
    twilResp.message("4 - Bacon")

def printDrinksMenu(twilResp: MessagingResponse):
    twilResp.message("1 - Coke")
    twilResp.message("2 - Fanta")
    twilResp.message("3 - Sprite")


# The main endpoint where messages arrive
@app.route('/', methods=['POST'])
def pizza():
    incoming_msg = request.values.get('Body', '')
    resp = MessagingResponse()
    msg = resp.message()
    responded = False
    if 'exit' == incoming_msg:
        if 'user' in session:
            Order.deleteFromStore(session['user'])
        session.clear()
        msg.body("Your order has been cancelled. Thank you for trying out The Pizza Bot and have a good day!")
        responded = True

    elif 'menu' == incoming_msg:
        msg.body("Here is the menu for the day: ")
        printMenuToUser(resp)
        responded = True            

    elif 'pizza' == incoming_msg:
        # return a pizza quote, ask for user address and create session for user
        session.clear()
        createUser()
        msg.body('Pizza party coming right up! Please enter your address to view the closest restaurants delivering pizza.')
        responded = True

    elif 'done' == incoming_msg:
        msg.body("Please type in the phone number you can be reached at: ")
        session['orderStatus'] = 'complete'
        responded = True

    else:
        if 'user' in session:
            # user enters address
            if 'location' not in session:
                location = str(incoming_msg)
                
                # save the location of the user in order
                session['location'] = location
                
                # convert incoming location to http-request friendly
                prepped_location = location.replace(' ', '+')

                # grab coordinates of user location
                r = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={prepped_location}&key={googleApiKey}')
                if r.status_code == 200:
                    geo_details = r.json()['results'][0]['geometry']['location']
                    latitude = geo_details['lat']
                    longitude = geo_details['lng']                     

                    # check for available pizza places within 5km
                    r = requests.get(f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={latitude},{longitude}&rankby=distance&keyword=pizza&key={googleApiKey}')
                    if r.status_code == 200:
                        results = r.json()['results']
                        if results == []:
                            resp.message("We're so sorry. There are no available locations close to you.")
                        else:
                            # pick top 3 pizza locations
                            pprint(results)
                            places = [place for place in results if ('opening_hours' in place) and (place['opening_hours']['open_now'] or place['business_status'] == 'OPERATIONAL') and results.index(place) < 3]
                            if places != []:
                                msg.body("Here are the 3 closest available locations. Please select a location using the number in front of the location: ")
                                count = 1
                                for place in places:
                                    message = f"{count} - {place['name']} - {place['vicinity']}"
                                    resp.message(message)
                                    count += 1
                                order = Order(id=session['user'], orderLocation=location, possible_locations=places, phone_no=None)
                                order.store()
                                session['places'] = True
                            else:
                                resp.message("There are no open locations within 5km of you.")

                else:
                    msg.body('Could not find your location. Please try again.')
                responded = True
            else:
                # user picks an order location
                if 'orderLocation' not in session:
                    # grab user location choice and add to order
                    location_choice = int(incoming_msg)
                    order_dict = Order.getOrder(session['user'])
                    possible_locations = order_dict['possible_locations']
                    order_dict['address'] = session['location']

                    # save user order location choice to store
                    selected_location = possible_locations[location_choice - 1]
                    order_dict['orderLocation'] = selected_location
                    order = Order.orderFromStore(order_dict=order_dict)
                    order.store()
                    session['orderLocation'] = True

                    # respond to user
                    msg.body(f'You have selected {selected_location["name"]} and your location has been saved')
                    msg.body("You can type menu to print the menu for the day")
                    printMenuToUser(twilResp=resp)
                    responded = True
                else:
                    if 'orderStatus' in session:                        
                        order_dict = Order.getOrder(session['user'])
                        order_dict['phone_no'] = incoming_msg
                        msg.body("Here is your cart: ")
                        for item in order_dict['cart']:
                            if "drink" in item:
                                drinks = cartCleanReplace(item['drink'].replace("choice", ""))
                                resp.message(f"Drinks - {drinks}")
                            if "pizza" in item:
                                toppings = cartCleanReplace(item['pizza'].replace("toppings", ""))
                                resp.message(f"Pizza with - {toppings}")
                        order = Order.orderFromStore(order_dict=order_dict)
                        order.completeOrder()
                        order.store()
                        resp.message("Your order has been succesfully submitted and will be delivered shortly." + 
                        " Thank you for trying out The Pizza Bot!")
                        session.clear()
                        responded = True
                    else:
                        val = ''
                        try:
                            val = int(str(incoming_msg))
                        except ValueError as err:
                            val = str(incoming_msg).replace(',', ' ').strip().split(" ")
                            for value in val:
                                try:
                                    value = int(value)
                                except ValueError as err:
                                    val.remove(value)
                            val = [int(value) for value in val]
                        
                        if 'pizza' in session:
                            order_pizza = Pizza(toppings=val)
                            order_dict = Order.getOrder(id=session['user'])
                            order = Order.orderFromStore(order_dict=order_dict)
                            pizza_dict = {
                                'pizza': (json.dumps(order_pizza.__dict__))
                            }
                            order.addToCart(pizza_dict)
                            order.store()
                            msg.body(f"Your pizza has been added to your cart!")
                            session.pop('pizza')
                            resp.message("Remember you can type 'done' to complete your order! You can text 'menu' to see the menu again!")
                            printMenuToUser(twilResp=resp)
                            responded = True
                        elif 'drinks' in session:
                            order_drink = Drink(choice=val)
                            order_dict = Order.getOrder(id=session['user'])
                            order = Order.orderFromStore(order_dict=order_dict)
                            drink_dict = {
                                'drink': (json.dumps(order_drink.__dict__))
                            }
                            order.addToCart(drink_dict)
                            order.store()
                            msg.body(f"Your drink(s) has/have been added to your cart!")
                            session.pop('drinks')
                            resp.message("Remember you can type 'done' to complete your order! You can text 'menu' to see the menu again!")
                            printMenuToUser(twilResp=resp)
                            responded = True
                        else:
                            if int(incoming_msg) == 1:
                                session['pizza'] = True
                                msg.body("You have selected Pizza. Please select the toppings you would like separated by commas. " + 
                                "For example, for extra cheese and pepperoni, text - 1, 2")
                                printPizzaToppings(twilResp=resp)
                                responded = True
                            if int(incoming_msg) == 2:
                                session['drinks'] = True
                                msg.body("You have selected Drinks. They all come in 75cl bottles." + 
                                " Please select the drink you would like separated by commas. " + 
                                " For example, for Coke and Fanta, text - 1, 2")
                                printDrinksMenu(twilResp=resp)
                                responded = True
                            
    if not responded:
        if 'user' in session:
            msg.body("Seems like an invalid command was used! Please follow the last prompt")
        else:
            msg.body("Hi there! I'm The Pizza Bot! I'm here to help you order delicious pizza! " +
                    "You can begin an order with the command: pizza. " + 
                    "You can complete an order with the command: done. " +
                    "You can see my available items on the menu at any time with the command: menu. " +
                    "You can cancel the process at any time by texting the command: exit.")
    return str(resp)


if __name__ == '__main__':
    app.run(debug=False)
