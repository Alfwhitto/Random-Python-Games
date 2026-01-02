print("Use command help to see available commands.")

import time
import random
import json
import os

SAVE_FILE = "data/savedata.txt"

# Default game state
default_state = {
    "money": 20,
    "inventory_slots": 10,
    "store_items": {
        "Crisps": {"price": 1, "qty": 0},
        "Pizza": {"price": 2, "qty": 0},
        "Green tea": {"price": 3, "qty": 0},
        "Chocolate": {"price": 4, "qty": 0},
        "Dubai Chocolate": {"price": 5, "qty": 0},
        "Gas tank": {"price": 10, "qty": 0},
        "Smartwatch": {"price": 15, "qty": 0},
        "Old analogue watch": {"price": 20, "qty": 0},
        "Laptop": {"price": 50, "qty": 0},
        "Phone": {"price": 100, "qty": 0}
    }
}

# Load or start new game
def load_or_new_game():
    if os.path.exists(SAVE_FILE):
        choice = input("Load existing game? (y/n): ").strip().lower()
        if choice == "y":
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            print("Game loaded!")
            return state
    print("Starting new game!")
    return default_state.copy()

# Save current state
def save_game(state):
    os.makedirs("data", exist_ok=True)
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
    print("Game saved!")

# Initialize game state
state = load_or_new_game()
money = state["money"]
inventory_slots = state["inventory_slots"]
store_items = state["store_items"]

# Shop setup (auto-register from store items)
shop_items = {}
for item_name, info in store_items.items():
    shop_items[item_name] = {"cost": info["price"]}

# Functions
def show_my_store():
    print("\n--- Your Store ---")
    for item, info in store_items.items():
        print(f"{item} - Price: £{info['price']} - Qty: {info['qty']}")
    print(f"Money: £{money}")
    print(f"Slots used: {sum(i['qty'] for i in store_items.values())}/{inventory_slots}")

def show_shop():
    print("\n--- Shop ---")
    for item, info in shop_items.items():
        print(f"{item} - Cost: £{info['cost']}")

def reprice(item_name, new_price):
    global store_items
    # Case-insensitive lookup
    actual_item = None
    for item in store_items:
        if item.lower() == item_name.lower():
            actual_item = item
            break
    if actual_item:
        store_items[actual_item]["price"] = new_price
        print(f"{actual_item} price updated to £{new_price}")
        save_current_state()
    else:
        print("Item not in your store")

def buy_item(item_name, qty):
    global money, store_items
    # Case-insensitive lookup
    actual_item = None
    for item in store_items:
        if item.lower() == item_name.lower():
            actual_item = item
            break

    if not actual_item:
        print("Item does not exist in the shop")
        return

    total_slots = sum(i["qty"] for i in store_items.values())
    if total_slots + qty > inventory_slots:
        print("Not enough space in your store")
        return
    total_cost = shop_items[actual_item]["cost"] * qty
    if total_cost > money:
        print("Not enough money to buy this stock")
        return
    money -= total_cost
    store_items[actual_item]["qty"] += qty
    print(f"Bought {qty} {actual_item}(s) for £{total_cost}")
    save_current_state()

def buy_shelf(amount):
    global inventory_slots, money
    shelf_cost = 10
    total_cost = shelf_cost * amount
    if total_cost > money:
        print(f"Not enough money to buy {amount} shelf(s). You need £{total_cost}, you have £{money}.")
        return
    money -= total_cost
    inventory_slots += 5 * amount
    print(f"Bought {amount} shelf(s). Inventory slots increased by {5 * amount}. Total slots: {inventory_slots}. Money left: £{money}")
    save_current_state()

def save_current_state():
    global money, inventory_slots, store_items
    state = {
        "money": money,
        "inventory_slots": inventory_slots,
        "store_items": store_items
    }
    save_game(state)

def start_day():
    global money, store_items
    print("\n--- Day Started ---")
    customers = 5
    bills = [1, 5, 10, 20, 50]

    for c in range(customers):
        print(f"\nCustomer {c+1} arrives!")
        time.sleep(1)

        items_to_check = list(store_items.keys())
        random.shuffle(items_to_check)

        items_bought = {}
        total_amount = 0

        for item_name in items_to_check:
            info = store_items[item_name]
            max_price = shop_items[item_name]["cost"] * 5

            if info["qty"] > 0 and info["price"] <= max_price:
                qty_to_buy = min(info["qty"], random.randint(1, 2))
                total_price = info["price"] * qty_to_buy
                items_bought[item_name] = qty_to_buy
                total_amount += total_price
            else:
                if info["qty"] == 0:
                    reason = "no stock left"
                elif info["price"] > max_price:
                    reason = f"price too high (max they would pay: £{max_price})"
                else:
                    reason = "unknown reason"
                print(f"Customer ignored {item_name} because {reason}")

        if items_bought:
            bought_items_str = " and ".join(f"{v} {k}" for k, v in items_bought.items())
            print(f"Customer {c+1} bought {bought_items_str} for £{total_amount}.")

            payment_method = random.choice(["cash", "card"])

            if payment_method == "cash":
                customer_bill = min(b for b in bills if b >= total_amount)
                print(f"Customer is paying by cash. They give £{customer_bill}. How much change?")
                while True:
                    player_input = input("Enter change to give: ")
                    try:
                        player_change = float(player_input)
                        if player_change >= 0:
                            print("Transaction complete!")
                            money += total_amount
                            for item_name, qty in items_bought.items():
                                store_items[item_name]["qty"] -= qty
                            save_current_state()
                            break
                        else:
                            print("Change must be zero or more.")
                    except ValueError:
                        print("Enter a number.")
            else:
                print(f"Customer pays by card. Amount is £{total_amount}. Please input the amount.")
                while True:
                    player_input = input("Enter amount charged: ")
                    try:
                        player_amount = float(player_input)
                        if player_amount == total_amount:
                            print("Payment successful!")
                            money += total_amount
                            for item_name, qty in items_bought.items():
                                store_items[item_name]["qty"] -= qty
                            save_current_state()
                            break
                        else:
                            print("Incorrect amount, try again.")
                    except ValueError:
                        print("Enter a number.")
        time.sleep(1)

    print(f"\nEnd of day. Money: £{money}")
    print("Inventory left:")
    for item_name, info in store_items.items():
        print(f"{item_name}: {info['qty']}")
    save_current_state()

def show_help():
    print("\n--- Help: Commands ---")
    print("store my                 -> Show your store, prices, stock, money, and slots used")
    print("store buy                -> Show shop items you can buy and their costs")
    print("reprice <item> <price>   -> Change the price of an item in your store")
    print("buy <item> <quantity>    -> Buy a quantity of an item from the shop")
    print("buy shelf <amount>       -> Buy <amount> of shelves (5 slots per shelf)")
    print("start                    -> Start the day and serve customers")
    print("exit                     -> Exit the game")
    print("help                     -> Show this help message")


# Main loop
while True:
    cmd = input("\n> ").strip()

    if cmd.lower() == "store my":
        show_my_store()
    elif cmd.lower() == "store buy":
        show_shop()
    elif cmd.lower().startswith("reprice "):
        parts = cmd.split()
        if len(parts) == 3 and parts[2].isdigit():
            reprice(parts[1], int(parts[2]))
        else:
            print("Usage: reprice <item_name> <new_price>")
    elif cmd.lower().startswith("buy shelf "):
        parts = cmd.split()
        if len(parts) == 3 and parts[2].isdigit():
            buy_shelf(int(parts[2]))
        else:
            print("Usage: buy shelf <amount>")
    elif cmd.lower().startswith("buy "):
        rest = cmd[4:].strip()
        if " " in rest:
            item_name, qty_str = rest.rsplit(" ", 1)
            if qty_str.isdigit():
                buy_item(item_name, int(qty_str))
            else:
                print("Usage: buy <item_name> <quantity>")
        else:
            print("Usage: buy <item_name> <quantity>")
    elif cmd.lower() == "start":
        start_day()
    elif cmd.lower() == "exit":
        print("Exiting game")
        break
    elif cmd.lower() == "help":
        show_help()
    else:
        print("Unknown command")
