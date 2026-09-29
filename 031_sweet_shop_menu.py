# sweet_shop_menu.py
# Run with: python sweet_shop_menu.py

from decimal import Decimal

sweets = {
    1: {"name": "Chocolate Bar", "price": Decimal("1.50"), "stock": 10},
    2: {"name": "Gummy Bears", "price": Decimal("2.25"), "stock": 8},
    3: {"name": "Lollipop", "price": Decimal("0.75"), "stock": 15},
    4: {"name": "Fudge", "price": Decimal("3.00"), "stock": 5},
}

basket = {}


def show_menu():
    print("\nSWEET SHOP MENU")
    for number, sweet in sweets.items():
        print(
            f"{number}. {sweet['name']:<16} "
            f"£{sweet['price']:.2f} "
            f"({sweet['stock']} available)"
        )
    print("5. View basket")
    print("6. Checkout")
    print("7. Exit")


def add_to_basket(number):
    sweet = sweets[number]

    try:
        quantity = int(input("Quantity: "))
    except ValueError:
        print("Enter a whole number.")
        return

    if quantity <= 0:
        print("Quantity must be greater than zero.")
    elif quantity > sweet["stock"]:
        print("Not enough stock available.")
    else:
        basket[number] = basket.get(number, 0) + quantity
        sweet["stock"] -= quantity
        print(f"Added {quantity} × {sweet['name']}.")


def show_basket():
    if not basket:
        print("\nYour basket is empty.")
        return Decimal("0.00")

    print("\nYOUR BASKET")
    total = Decimal("0.00")

    for number, quantity in basket.items():
        sweet = sweets[number]
        line_total = sweet["price"] * quantity
        total += line_total
        print(
            f"{sweet['name']}: {quantity} × "
            f"£{sweet['price']:.2f} = £{line_total:.2f}"
        )

    print(f"Total: £{total:.2f}")
    return total


def checkout():
    total = show_basket()
    if total == 0:
        return

    confirm = input("Confirm purchase? (yes/no): ").strip().lower()
    if confirm == "yes":
        print(f"Thank you! Amount due: £{total:.2f}")
        basket.clear()
    else:
        print("Checkout cancelled.")


while True:
    show_menu()
    choice = input("Choose an option: ").strip()

    if choice in {"1", "2", "3", "4"}:
        add_to_basket(int(choice))
    elif choice == "5":
        show_basket()
    elif choice == "6":
        checkout()
    elif choice == "7":
        print("Goodbye!")
        break
    else:
        print("Choose a number from 1 to 7.")