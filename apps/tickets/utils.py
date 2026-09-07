import qrcode
from io import BytesIO
from django.core.signing import TimestampSigner
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage

def generate_qr_code(booking):
    """Generate signed QR code for ticket verification."""
    signer = TimestampSigner(salt='cinebook-ticket-v1')
    payload = f'{booking.booking_id}:{booking.user_id}:{booking.show_id}'
    signed = signer.sign(payload)
    
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=8, border=2)
    qr.add_data(signed)
    qr.make(fit=True)
    img = qr.make_image(fill_color='#1e293b', back_color='#ffffff')
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return signed, buffer

def generate_ticket_pdf(booking):
    """Generate professional PDF ticket using ReportLab."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=30
    )
    elements = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#0f172a'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor('#475569'),
        spaceAfter=10
    )
    
    elements.append(Paragraph('CineBook', title_style))
    elements.append(Paragraph(f"Movie: {booking.show.movie.title}", styles['Heading2']))
    
    # Show Details Table
    show_details = [
        ['Theater:', booking.show.screen.theater.name, 'Date:', booking.show.start_time.strftime('%Y-%m-%d')],
        ['Screen:', booking.show.screen.name, 'Time:', booking.show.start_time.strftime('%H:%M')],
        ['Booking ID:', str(booking.booking_id), 'Total Paid:', f"INR {booking.total_amount}"]
    ]
    t = Table(show_details, colWidths=[60, 200, 60, 150])
    t.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TEXTCOLOR', (0,0), (-1,-1), HexColor('#1e293b')),
        ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8fafc')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 20))
    
    # Seats Table
    seats_data = [['Seat', 'Category', 'Price']]
    for bs in booking.booked_seats.all():
        seats_data.append([bs.seat.seat_number, bs.seat.category, f"INR {bs.price}"])
        
    st = Table(seats_data, colWidths=[100, 150, 100])
    st.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), HexColor('#0f172a')),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor('#ffffff')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 1, HexColor('#e2e8f0')),
    ]))
    elements.append(st)
    elements.append(Spacer(1, 30))
    
    # QR Code
    _, qr_buffer = generate_qr_code(booking)
    qr_img = Image(qr_buffer, width=4*cm, height=4*cm)
    elements.append(qr_img)
    
    # Footer
    elements.append(Spacer(1, 30))
    elements.append(Paragraph('Terms & Conditions:', styles['Heading3']))
    terms = [
        "1. Tickets once booked cannot be cancelled.",
        "2. Please carry a valid ID proof.",
        "3. Show this QR code at the entrance."
    ]
    for term in terms:
        elements.append(Paragraph(term, styles['Normal']))
        
    doc.build(elements)
    buffer.seek(0)
    return buffer
