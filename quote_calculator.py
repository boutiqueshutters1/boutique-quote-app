# Boutique Shutters Quote Tool v11
# Motors + Accessories separated
# Real motor costs included

# -----------------------------
# CUSTOMER PRICING
# -----------------------------
SELL_PRICE_PER_SQFT = 12.0
SELL_LABOR_PER_SQFT = 1.0

TRIP_CHARGE_TARGET = 100.0

MOTOR_CHARGE = {"none": 0.0, "am25": 100.0, "am28": 150.0}

CHARGER_PRICE = 15.0
REMOTE_PRICE = 20.0
HUB_PRICE = 99.0

# -----------------------------
# YOUR COSTS
# -----------------------------
COGS_MANUAL_PER_SQFT = 4.0
COGS_MOTORIZED_PER_SQFT = 8.0

MOTOR_COST = {"none": 0.0, "am25": 36.0, "am28": 42.0}

CHARGER_COST = 5.50
REMOTE_COST = 6.00
HUB_COST = 19.00

INSTALLER_DAY_COST = 200.0
AVG_INSTALL_SQFT_PER_DAY = 400.0
TRIP_COST = 25.0

DISCOUNT_RATE = 0.05
TAX_RATE = 0.06
TARGET_MARGIN = 0.35

# -----------------------------

def money(x):
    return f"${x:,.2f}"

def labor_cost_per_sqft():
    return INSTALLER_DAY_COST / AVG_INSTALL_SQFT_PER_DAY

num_windows = int(input("How many windows? "))

revenue = 0
cost = 0
total_sqft = 0

for i in range(num_windows):
    print(f"\nWindow {i+1}")

    width = float(input("Width (inches): "))
    height = float(input("Height (inches): "))
    motor = input("Motor (none/am25/am28): ").strip().lower()

    if motor not in MOTOR_CHARGE:
        motor = "none"

    sqft = (width * height) / 144
    total_sqft += sqft

    # Revenue
    revenue += sqft * SELL_PRICE_PER_SQFT
    revenue += sqft * SELL_LABOR_PER_SQFT
    revenue += MOTOR_CHARGE[motor]

    # Cost
    cogs_per_sqft = COGS_MANUAL_PER_SQFT if motor == "none" else COGS_MOTORIZED_PER_SQFT
    cost += sqft * cogs_per_sqft
    cost += sqft * labor_cost_per_sqft()
    cost += MOTOR_COST[motor]

# Accessories
chargers = int(input("\nHow many chargers? "))
remotes = int(input("How many remotes? "))
hubs = int(input("How many hubs? "))

revenue += chargers * CHARGER_PRICE
revenue += remotes * REMOTE_PRICE
revenue += hubs * HUB_PRICE

cost += chargers * CHARGER_COST
cost += remotes * REMOTE_COST
cost += hubs * HUB_COST

# Trip charge rule
install_charge = total_sqft * SELL_LABOR_PER_SQFT
trip_charge = min(TRIP_CHARGE_TARGET, install_charge)

revenue += trip_charge
cost += TRIP_COST

# Discount
discount = revenue * DISCOUNT_RATE
revenue_after_discount = revenue - discount

# Profit
profit = revenue_after_discount - cost
margin = profit / revenue_after_discount if revenue_after_discount > 0 else 0

tax = revenue_after_discount * TAX_RATE
customer_total = revenue_after_discount + tax

print("\n===== JOB SUMMARY =====")
print("Total sqft:", round(total_sqft,2))
print("Revenue before discount:", money(revenue))
print("Revenue after discount:", money(revenue_after_discount))
print("Total cost:", money(cost))
print("Profit:", money(profit))
print("Margin:", f"{margin*100:.1f}%")
print("Customer total w/tax:", money(customer_total))

if margin < TARGET_MARGIN:
    print("\n⚠️ Below 35% target")
else:
    print("\n✅ Margin above 35%")
