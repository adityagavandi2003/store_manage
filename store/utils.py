import os
from django.http import HttpResponse,FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

# Correct absolute font path
DejaVuSans = r"D:\visualcode\Workspacse\Django\store_manage\fonts\DejaVuSans.ttf"
DejaVuSans_Bold = r"D:\visualcode\Workspacse\Django\store_manage\fonts\DejaVuSans-Bold.ttf"

pdfmetrics.registerFont(TTFont("DejaVuSans", DejaVuSans))  # font
pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", DejaVuSans_Bold))  # font

def generate_invoice(order, user, products, *args, **kwargs):
    buffer = BytesIO()
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.order_id}.pdf"'
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 3 * cm

    # Header
    p.setFont("DejaVuSans-Bold", 18)
    p.setFillColor(colors.HexColor("#2563eb"))
    p.drawString(2 * cm, y, "StoreSathi")
    p.setFillColor(colors.black)
    p.setFont("DejaVuSans", 10)
    y -= 0.7 * cm
    p.drawString(2 * cm, y, f"Invoice from {user} shop")

    # Invoice ID and date
    y -= 1.5 * cm
    p.setFont("DejaVuSans", 12)
    p.drawString(2 * cm, y, f"Invoice ID: {order.order_id}")
    p.drawString(12 * cm, y, f"Issued on: {order.order_at.strftime('%d %b %Y')}")

    # Customer Info
    y -= 1.5 * cm
    p.setFont("DejaVuSans", 11)
    p.drawString(2 * cm, y, "Bill To:")
    p.setFont("DejaVuSans", 10)
    y -= 0.5 * cm
    p.drawString(2 * cm, y, str(order.customer))
    y -= 0.4 * cm
    p.drawString(2 * cm, y, f"Phone: {order.customer_phone}")
    y -= 0.4 * cm
    p.drawString(2 * cm, y, f"Mode: {order.payment_mode}")

    # Shop Info
    y += 1.3 * cm
    p.setFont("DejaVuSans", 11)
    p.drawString(12 * cm, y, "From:")
    p.setFont("DejaVuSans", 10)
    y -= 0.5 * cm
    p.drawString(12 * cm, y, str(order.shop))
    y -= 0.4 * cm
    p.drawString(12 * cm, y, f"Email: {order.shop.email}")

    # Table Data
    y -= 2 * cm
    data = [["Description", "Quantity", "Unit Price", "Total"]]
    for item in products:
        data.append([
            item.product_name,
            item.quantity,
            f"₹{item.product_price:.2f}",
            f"₹{item.subtotal:.2f}"
        ])

    # Subtotal & Total
    data.append(["", "", "Subtotal", f"₹{order.total_amount:.2f}"])
    data.append(["", "", "Total", f"₹{order.total_amount:.2f}"])

    table = Table(data, colWidths=[7 * cm, 2 * cm, 3 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("BACKGROUND", (-2, -2), (-1, -1), colors.whitesmoke),
        ("TEXTCOLOR", (-1, -1), (-1, -1), colors.blue),
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 2 * cm, y - len(data) * 0.6 * cm)

    # Footer
    p.setFont("DejaVuSans", 9)
    p.setFillColor(colors.gray)
    p.drawCentredString(width / 2, 2 * cm, "For questions, contact support@storesathi.com")
    p.drawCentredString(width / 2, 1.5 * cm, "© 2025 StoreSathi. All rights reserved.")

    p.showPage()
    p.save()
    buffer.seek(0)

    # Save to server:
    filename = f"invoice_{order.order_id}.pdf"
    os.makedirs("media/invoices", exist_ok=True)
    with open(f"media/invoices/{filename}", "wb") as f:
        f.write(buffer.getvalue())

    pdf_data = buffer.getvalue()  # assuming you're using `io.BytesIO()`
    invoice = filename,pdf_data
    response =  HttpResponse(invoice, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

