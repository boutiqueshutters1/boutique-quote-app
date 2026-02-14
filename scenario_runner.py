# Real-world scenario runner (no prompts)

SELL_PRICE_PER_SQFT = 12.0
SELL_LABOR_PER_SQFT = 1.0
TRIP_CHARGE_TARGET = 100.0

MOTOR_CHARGE = {"am25": 100.0, "am28": 150.0}
MOTOR_COST   = {"am25": 36.0,  "am28": 42.0}

COGS_MANUAL_PER_SQFT = 4.0
COGS_MOTORIZED_PER_SQFT = 8.0

INSTALLER_DAY_COST = 200.0
AVG_INSTALL_SQFT_PER_DAY = 400.0
TRIP_COST = 25.0

CHARGER_PRICE = 15.0
REMOTE_PRICE = 20.0
HUB_PRICE = 99.0

CHARGER_COST = 5.50
REMOTE_COST = 6.00
HUB_COST = 19.00

DISCOUNT_RATE = 0.05
TAX_RATE = 0.06

def money(x): return f"${x:,.2f}"

# -------- SCENARIO INPUTS (EDIT THESE) --------
total_windows = 20
total_sqft = 200.0          # your typical house estimate
motorized_windows = 10
am25_count = 8
am28_count = 2
chargers = 10
remotes = 3
hubs = 1
# ---------------------------------------------

manual_sqft = total_sqft * (total_windows - motorized_windows) / total_windows
motor_sqft  = total_sqft * motorized_windows / total_windows

labor_cost_per_sqft = INSTALLER_DAY_COST / AVG_INSTALL_SQFT_PER_DAY

# Revenue
revenue = total_sqft * (SELL_PRICE_PER_SQFT + SELL_LABOR_PER_SQFT)
revenue += am25_count * MOTOR_CHARGE["am25"] + am28_count * MOTOR_CHARGE["am28"]
revenue += chargers * CHARGER_PRICE + remotes * REMOTE_PRICE + hubs * HUB_PRICE

install_charge = total_sqft * SELL_LABOR_PER_SQFT
trip_charge = min(TRIP_CHARGE_TARGET, install_charge)
revenue += trip_charge

# Costs
cost = manual_sqft * COGS_MANUAL_PER_SQFT + motor_sqft * COGS_MOTORIZED_PER_SQFT
cost += total_sqft * labor_cost_per_sqft
cost += am25_count * MOTOR_COST["am25"] + am28_count * MOTOR_COST["am28"]
cost += chargers * CHARGER_COST + remotes * REMOTE_COST + hubs * HUB_COST
cost += TRIP_COST

# Discount + tax
discount = revenue * DISCOUNT_RATE
revenue_after_discount = revenue - discount
profit = revenue_after_discount - cost
margin = profit / revenue_after_discount if revenue_after_discount > 0 else 0
tax = revenue_after_discount * TAX_RATE
customer_total = revenue_after_discount + tax

print("\n=== REAL-WORLD SCENARIO ===")
print("Windows:", total_windows, "| Total sqft:", total_sqft)
print(f"Motors: {motorized_windows} (AM25={am25_count}, AM28={am28_count})")
print(f"Accessories: chargers={chargers}, remotes={remotes}, hubs={hubs}")
print("Trip charge:", money(trip_charge))

print("\n--- RESULTS ---")
print("Revenue (before discount):", money(revenue))
print("Discount (5%):           -", money(discount))
print("Revenue (after discount):", money(revenue_after_discount))
print("Total cost:", money(cost))
print("Profit:", money(profit))
print("Margin:", f"{margin*100:.1f}%")
print("Tax (6%):", money(tax))
print("Customer total:", money(customer_total))
