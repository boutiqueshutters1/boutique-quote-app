from PIL import Image
from reportlab.lib.utils import ImageReader
from streamlit_drawable_canvas import st_canvas
import io
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas as pdf_canvas

import streamlit as st

st.set_page_config(page_title="Boutique Shutters Quote", layout="centered")
st.title("Boutique Shutters Quote Calculator")

admin_mode = st.toggle("Admin mode (show pricing + costs)", value=False)

# -----------------------------
# Customer pricing
# -----------------------------
SELL_PRICE_PER_SQFT = st.number_input(
    "Sell price per sqft ($)", value=12.0, step=0.5, disabled=not admin_mode, key="sell_price_sqft"
)
SELL_LABOR_PER_SQFT = st.number_input(
    "Labor charge per sqft ($)", value=1.0, step=0.25, disabled=not admin_mode, key="sell_labor_sqft"
)
TRIP_CHARGE_TARGET = st.number_input(
    "Trip charge target ($)", value=100.0, step=10.0, disabled=not admin_mode, key="trip_charge_target"
)

MOTOR_CHARGE_AM25 = st.number_input(
    "Customer price: AM25 ($)", value=100.0, step=10.0, disabled=not admin_mode, key="motor_charge_am25"
)
MOTOR_CHARGE_AM28 = st.number_input(
    "Customer price: AM28 ($)", value=150.0, step=10.0, disabled=not admin_mode, key="motor_charge_am28"
)

CHARGER_PRICE = st.number_input(
    "Customer price: Charger ($)", value=22.0, step=1.0, disabled=not admin_mode, key="charger_price"
)
REMOTE_1CH_PRICE = st.number_input(
    "Customer price: Remote 1ch ($)", value=29.0, step=1.0, disabled=not admin_mode, key="remote_1ch_price"
)
REMOTE_16CH_PRICE = st.number_input(
    "Customer price: Remote 16ch ($)", value=45.0, step=1.0, disabled=not admin_mode, key="remote_16ch_price"
)


st.divider()


# -----------------------------
# Customer pricing (edit anytime)
# -----------------------------
if admin_mode:
    SELL_PRICE_PER_SQFT = st.number_input("Sell price per sqft ($)", value=12.0, step=0.5)
    SELL_LABOR_PER_SQFT = st.number_input("Labor charge per sqft ($)", value=1.0, step=0.25)
    TRIP_CHARGE_TARGET = st.number_input("Trip charge target ($)", value=100.0, step=10.0)

MOTOR_CHARGE_AM25 = st.number_input("Customer price: AM25 ($)", value=100.0, step=10.0)
MOTOR_CHARGE_AM28 = st.number_input("Customer price: AM28 ($)", value=150.0, step=10.0)

# Accessories selling prices (recommended defaults)
CHARGER_PRICE = st.number_input("Customer price: Charger ($)", value=22.0, step=1.0)
REMOTE_1CH_PRICE = st.number_input("Customer price: Remote 1ch ($)", value=29.0, step=1.0)
REMOTE_16CH_PRICE = st.number_input("Customer price: Remote 16ch ($)", value=45.0, step=1.0)
HUB_PRICE = st.number_input("Customer price: Hub ($)", value=99.0, step=5.0)

st.divider()

# -----------------------------
# Your costs
# -----------------------------
COGS_MANUAL_PER_SQFT = st.number_input("COGS manual per sqft ($)", value=4.0, step=0.5)
COGS_MOTORIZED_PER_SQFT = st.number_input("COGS motorized per sqft ($)", value=8.0, step=0.5)

MOTOR_COST_AM25 = st.number_input("Your cost: AM25 ($)", value=36.0, step=1.0)
MOTOR_COST_AM28 = st.number_input("Your cost: AM28 ($)", value=42.0, step=1.0)

INSTALLER_DAY_COST = st.number_input("Installer cost per day ($)", value=200.0, step=10.0)
AVG_INSTALL_SQFT_PER_DAY = st.number_input("Avg install sqft/day per installer", value=400.0, step=25.0)

TRIP_COST = st.number_input("Your trip cost ($)", value=25.0, step=5.0)

st.divider()

# Job inputs
st.subheader("Job Inputs")

mode = st.radio("Input mode", ["Fast Mode (total sqft + counts)", "Detailed Mode (per window)"], index=0)

DISCOUNT_RATE = st.number_input("Discount rate (%)", value=5.0, step=1.0) / 100.0
TAX_RATE = st.number_input("Sales tax rate (%)", value=6.0, step=0.5) / 100.0
TARGET_MARGIN = st.number_input("Target margin (%)", value=35.0, step=1.0) / 100.0

def money(x): return f"${x:,.2f}"

labor_cost_per_sqft = (INSTALLER_DAY_COST / AVG_INSTALL_SQFT_PER_DAY) if AVG_INSTALL_SQFT_PER_DAY > 0 else 0.0

# Initialize accumulators
total_sqft = 0.0
manual_sqft = 0.0
motor_sqft = 0.0
am25_count = 0
am28_count = 0

if mode.startswith("Fast"):
    total_sqft = st.number_input("Total sqft (whole job)", value=200.0, step=10.0)
    total_windows = st.number_input("Total windows", value=20, step=1)
    motorized_windows = st.number_input("Motorized windows", value=10, step=1)

    am25_count = st.number_input("AM25 count", value=8, step=1)
    am28_count = st.number_input("AM28 count", value=2, step=1)

    # Split sqft by motorized vs manual windows (simple estimate)
    if total_windows > 0:
        motor_sqft = total_sqft * (motorized_windows / total_windows)
        manual_sqft = total_sqft - motor_sqft
    else:
        manual_sqft = total_sqft
        motor_sqft = 0.0

else:
    num_windows = st.number_input("Number of windows", value=2, step=1)
    rows = []
    for i in range(int(num_windows)):
        st.markdown(f"**Window {i+1}**")
        w = st.number_input(f"Width (in) #{i+1}", value=35.0, step=1.0, key=f"w{i}")
        h = st.number_input(f"Height (in) #{i+1}", value=60.0, step=1.0, key=f"h{i}")
        motor = st.selectbox(f"Motor #{i+1}", ["none", "am25", "am28"], key=f"m{i}")

        sqft = (w * h) / 144.0
        total_sqft += sqft

        if motor == "none":
            manual_sqft += sqft
        else:
            motor_sqft += sqft
            if motor == "am25":
                am25_count += 1
            else:
                am28_count += 1

        rows.append((i+1, sqft, motor))
    st.caption("Detailed mode uses your exact per-window sqft + motor selections.")

st.divider()

# Accessories inputs

st.subheader("Accessories")
chargers = st.number_input("Chargers", value=0, step=1)
remote_1ch = st.number_input("Remotes (1ch)", value=0, step=1)
remote_16ch = st.number_input("Remotes (16ch)", value=0, step=1)
hubs = st.number_input("Hubs", value=0, step=1)

# Compute
# Revenue
revenue = total_sqft * (SELL_PRICE_PER_SQFT + SELL_LABOR_PER_SQFT)
revenue += am25_count * MOTOR_CHARGE_AM25 + am28_count * MOTOR_CHARGE_AM28
revenue += chargers * CHARGER_PRICE + remote_1ch * REMOTE_1CH_PRICE + remote_16ch * REMOTE_16CH_PRICE + hubs * HUB_PRICE

install_charge = total_sqft * SELL_LABOR_PER_SQFT
trip_charge = min(TRIP_CHARGE_TARGET, install_charge)
revenue += trip_charge

# Costs
cost = manual_sqft * COGS_MANUAL_PER_SQFT + motor_sqft * COGS_MOTORIZED_PER_SQFT
cost += total_sqft * labor_cost_per_sqft
cost += am25_count * MOTOR_COST_AM25 + am28_count * MOTOR_COST_AM28
cost += chargers * 5.50 + remote_1ch * 6.00 + remote_16ch * 8.50 + hubs * 19.00
cost += TRIP_COST

discount_amt = revenue * DISCOUNT_RATE
revenue_after_discount = revenue - discount_amt

profit = revenue_after_discount - cost
margin = (profit / revenue_after_discount) if revenue_after_discount > 0 else 0.0

tax = revenue_after_discount * TAX_RATE
customer_total = revenue_after_discount + tax

st.divider()
st.subheader("Customer Quote")

colA, colB = st.columns(2)
customer_name = colA.text_input("Customer name", "")
customer_address = colB.text_input("Address (optional)", "")

colC, colD, colE = st.columns(3)
quote_id = colC.text_input("Quote #", f"BS-{datetime.now().strftime('%y%m%d-%H%M')}")
quote_date = colD.text_input("Date", datetime.now().strftime("%m/%d/%Y"))
valid_days = colE.number_input("Valid for (days)", value=7, step=1)

notes = st.text_area("Notes (optional)", "Thank you for choosing Boutique Shutters. Pricing subject to final measurements and product availability.")

logo_file = st.file_uploader("Upload logo (PNG/JPG) (optional)", type=["png", "jpg", "jpeg"])

def build_quote_pdf():
    buf = BytesIO()
    c = pdf_canvas.Canvas(buf, pagesize=letter)
    w, h = letter

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, h - 60, "Boutique Shutters")
    c.setFont("Helvetica", 10)
    c.drawString(50, h - 78, "Phone: 404-966-7419   |   Website: boutiqueshutters.com")
    c.line(50, h - 90, w - 50, h - 90)

    # Quote meta
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, h - 120, "Quote")
    c.setFont("Helvetica", 10)
    c.drawString(50, h - 140, f"Quote #: {quote_id}")
    c.drawString(220, h - 140, f"Date: {quote_date}")
    c.drawString(360, h - 140, f"Valid: {int(valid_days)} days")

    # Customer
    y = h - 170
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Prepared for:")
    c.setFont("Helvetica", 10)
    c.drawString(140, y, customer_name or "(Name)")
    if customer_address.strip():
        c.drawString(140, y - 14, customer_address.strip())

    # Line items (customer-facing)
    y = h - 220
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Description")
    c.drawString(420, y, "Amount")
    c.line(50, y - 5, w - 50, y - 5)

    y -= 22
    def line(desc, amt):
        nonlocal y
        c.setFont("Helvetica", 10)
        c.drawString(50, y, desc)
        c.drawRightString(w - 50, y, f"${amt:,.2f}")
        y -= 16

    # These variables must already exist in your app calculations:
    # total_sqft, am25_count, am28_count, chargers, remote_1ch, remote_16ch, hubs,
    # SELL_PRICE_PER_SQFT, SELL_LABOR_PER_SQFT, MOTOR_CHARGE_AM25, MOTOR_CHARGE_AM28,
    # CHARGER_PRICE, REMOTE_1CH_PRICE, REMOTE_16CH_PRICE, HUB_PRICE,
    # trip_charge, discount_amt, revenue_after_discount, tax, customer_total

    fabric_amt = float(total_sqft) * float(SELL_PRICE_PER_SQFT)
    labor_amt  = float(total_sqft) * float(SELL_LABOR_PER_SQFT)
    motor_amt  = int(am25_count) * float(MOTOR_CHARGE_AM25) + int(am28_count) * float(MOTOR_CHARGE_AM28)
    acc_amt    = int(chargers) * float(CHARGER_PRICE) + int(remote_1ch) * float(REMOTE_1CH_PRICE) + int(remote_16ch) * float(REMOTE_16CH_PRICE) + int(hubs) * float(HUB_PRICE)

    line(f"Window Treatments (Fabric) — {float(total_sqft):.2f} sqft", fabric_amt)
    line(f"Installation — {float(total_sqft):.2f} sqft", labor_amt)

    if int(am25_count) + int(am28_count) > 0:
        line(f"Motors — AM25 x{int(am25_count)} / AM28 x{int(am28_count)}", motor_amt)

    if int(chargers) + int(remote_1ch) + int(remote_16ch) + int(hubs) > 0:
        line(f"Accessories — Chargers x{int(chargers)}, Remotes x{int(remote_1ch)+int(remote_16ch)}, Hubs x{int(hubs)}", acc_amt)

    line("Trip/Service", float(trip_charge))
    line("Discount", -float(discount_amt))

    c.line(50, y - 6, w - 50, y - 6)
    y -= 26
    line("Subtotal", float(revenue_after_discount))
    line("Sales Tax", float(tax))

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 6, "TOTAL")
    c.drawRightString(w - 50, y - 6, f"${float(customer_total):,.2f}")

    # Notes
    y -= 60
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Notes:")
    c.setFont("Helvetica", 9)
    text = c.beginText(50, y - 16)
    for ln in (notes or "").splitlines():
        text.textLine(ln)
    c.drawText(text)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

st.subheader("Deposit + Signature")

deposit_pct = st.number_input("Deposit % due today", value=50, step=5) / 100.0
deposit_due = customer_total * deposit_pct
balance_due = customer_total - deposit_due

st.write(f"**Deposit due today:** ${deposit_due:,.2f}")
st.write(f"**Balance due at install:** ${balance_due:,.2f}")

st.markdown("**Customer Signature (sign below):**")
sig_canvas = st_canvas(
    fill_color="rgba(255, 255, 255, 0.0)",
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    height=140,
    width=520,
    drawing_mode="freedraw",
    key="signature_canvas",
)

signature_png_bytes = None
if sig_canvas.image_data is not None:
    # Convert signature to PNG bytes
    img = Image.fromarray(sig_canvas.image_data.astype("uint8"))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    signature_png_bytes = buf.getvalue()
pdf_buf = build_quote_pdf()

st.download_button(
    label="⬇️ Download Professional Quote (PDF)",
    data=pdf_buf,
    file_name=f"{quote_id}.pdf",
    mime="application/pdf"
)

st.subheader("Results")
col1, col2, col3 = st.columns(3)
col1.metric("Revenue (before discount)", money(revenue))
col2.metric("Revenue (after discount)", money(revenue_after_discount))
col3.metric("Customer Total (with tax)", money(customer_total))

col4, col5, col6 = st.columns(3)
col4.metric("Estimated Cost", money(cost))
col5.metric("Profit", money(profit))
col6.metric("Margin", f"{margin*100:.1f}%")

st.caption(f"Trip charge applied: {money(trip_charge)} (capped by install charge {money(install_charge)})")

if margin < TARGET_MARGIN:
    st.warning("Below target margin.")
    needed_revenue_after_discount = cost / (1 - TARGET_MARGIN)
    needed_revenue_before_discount = needed_revenue_after_discount / (1 - DISCOUNT_RATE)
    increase_needed = needed_revenue_before_discount - revenue
    if total_sqft > 0:
        suggested_sqft_price = SELL_PRICE_PER_SQFT + (increase_needed / total_sqft)
        st.write("Increase revenue BEFORE discount by:", money(increase_needed))
        st.write("Suggested sell price per sqft:", f"${suggested_sqft_price:.2f}")
else:
    st.success("Meets or exceeds target margin.")
