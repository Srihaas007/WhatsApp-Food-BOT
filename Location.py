def main_menu():
    print("1. Enter location manually")
    print("2. Do it automatically")
    selection = input("Enter your choice: ")
    if selection == "1":
        manual()
    elif selection == "2":
        automatic()
    else:
        print("Invalid choice. Enter 1 or 2")
        main_menu()

def manual():
    locations = {
        "location1": {
            "restaurant1": ["item1", "item2", "item3"],
            "restaurant2": ["item4", "item5", "item6"],
            "restaurant3": ["item7", "item8", "item9"]
        },
        "location2": {
            "restaurant1": ["item1", "item2", "item3"],
            "restaurant2": ["item4", "item5", "item6"],
            "restaurant3": ["item7", "item8", "item9"]
        }
    }
    print("Select a location:")
    for i, location in enumerate(locations.keys()):
        print(f"{i + 1}. {location}")
    selection = input("Enter your choice: ")
    if selection.isdigit() and 1 <= int(selection) <= len(locations):
        location = list(locations.keys())[int(selection) - 1]
        print(f"Select a restaurant for {location}:")
        for i, restaurant in enumerate(locations[location].keys()):
            print(f"{i + 1}. {restaurant}")
        selection = input("Enter your choice: ")
        if selection.isdigit() and 1 <= int(selection) <= len(locations[location]):
            restaurant = list(locations[location].keys())[int(selection) - 1]
            print(f"Select an item from the menu of {restaurant}:")
            for i, item in enumerate(locations[location][restaurant]):
                print(f"{i + 1}. {item}")
            selection = input("Enter your choice: ")
            if selection.isdigit() and 1 <= int(selection) <= len(locations[location][restaurant]):
                item = locations[location][restaurant][int(selection) - 1]
                print(f"You selected {item} from {restaurant} in {location}.")
                return
    print("Invalid choice.")
    manual()

def automatic():
    import requests

    res = requests.get('https://ipinfo.io/')
    data = res.json()

    city = data['city']

    location = data['loc'].split(',')
    latitude = location[0]
    longitude = location[1]
    print("Latitude : ", latitude)
    print("Longitude : ", longitude)
    print("City : ", city)

main_menu()
