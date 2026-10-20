# sweet_shop_menu.py
# Run with: python sweet_shop_menu.py
# Browse sweets, add quantities to a basket, and confirm a sample purchase.
# Stock and basket contents are held in memory and reset when restarted.

from decimal import Decimal

# Use decimal strings to represent prices without binary floating-point rounding.
# Each menu number identifies a product with its price and available stock.
sweets = {
    1: {"name": "Chocolate Bar", "price": Decimal("1.50"), "stock": 10},
    2: {"name": "Gummy Bears", "price": Decimal("2.25"), "stock": 8},
    3: {"name": "Lollipop", "price": Decimal("0.75"), "stock": 15},
    4: {"name": "Fudge", "price": Decimal("3.00"), "stock": 5},
}

# Map product numbers to the quantities currently reserved in the basket.
basket = {}


def show_menu():
    # Display products with aligned names, two-decimal prices, and current stock.
    print("\nSWEET SHOP MENU")
    for number, sweet in sweets.items():
        print(
            f"{number}. {sweet['name']:<16} "
            f"£{sweet['price']:.2f} "
            f"({sweet['stock']} available)"
        )

    # Provide separate options for reviewing, purchasing, and leaving.
    print("5. View basket")
    print("6. Checkout")
    print("7. Exit")


def add_to_basket(number):
    # Retrieve the product selected through the menu.
    # The calling code supplies one of the known product numbers.
    sweet = sweets[number]

    try:
        # Accept whole-number quantities only.
        quantity = int(input("Quantity: "))
    except ValueError:
        print("Enter a whole number.")
        return

    # Reject invalid quantities before changing stock or basket contents.
    if quantity <= 0:
        print("Quantity must be greater than zero.")
    elif quantity > sweet["stock"]:
        print("Not enough stock available.")
    else:
        # Combine repeated selections of the same product.
        basket[number] = basket.get(number, 0) + quantity

        # Reserve stock immediately so it cannot be added to the basket again.
        sweet["stock"] -= quantity
        print(f"Added {quantity} × {sweet['name']}.")


def show_basket():
    # Return a zero total when there is nothing to purchase.
    if not basket:
        print("\nYour basket is empty.")
        return Decimal("0.00")

    print("\nYOUR BASKET")
    total = Decimal("0.00")

    # Calculate each product's subtotal and accumulate the basket total.
    for number, quantity in basket.items():
        sweet = sweets[number]
        line_total = sweet["price"] * quantity
        total += line_total
        print(
            f"{sweet['name']}: {quantity} × "
            f"£{sweet['price']:.2f} = £{line_total:.2f}"
        )

    # Return the total so checkout can reuse the calculation.
    print(f"Total: £{total:.2f}")
    return total


def checkout():
    # Show the basket before requesting purchase confirmation.
    total = show_basket()
    if total == 0:
        return

    # Ignore surrounding spaces and capitalization in the response.
    confirm = input("Confirm purchase? (yes/no): ").strip().lower()
    if confirm == "yes":
        # Confirm the sample purchase without processing a payment.
        # Stock was already reduced when items entered the basket.
        print(f"Thank you! Amount due: £{total:.2f}")
        basket.clear()
    else:
        # Keep the basket and its reserved stock for a later checkout attempt.
        print("Checkout cancelled.")


# Keep accepting menu selections until the customer chooses Exit.
while True:
    show_menu()
    choice = input("Choose an option: ").strip()

    if choice in {"1", "2", "3", "4"}:
        # Convert a validated product selection into its dictionary key.
        add_to_basket(int(choice))
    elif choice == "5":
        show_basket()
    elif choice == "6":
        checkout()
    elif choice == "7":
        # Exit the program; no basket or stock data is saved.
        print("Goodbye!")
        break
    else:
        # Explain the accepted range and display the menu again.
        print("Choose a number from 1 to 7.")