from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from django.conf import settings
import os

def generate_certificate(user, score):
    # Path to the signature and stamp images
    signature_path = os.path.join(settings.STATIC_ROOT, 'signature.png')
    stamp_path = os.path.join(settings.STATIC_ROOT, 'stamp.png')

    # Create a PDF file
    pdf_path = os.path.join(settings.MEDIA_ROOT, f'certificates/{user.username}_certificate.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)
    
    # Draw the certificate content
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(4.25*inch, 10*inch, "Certificate of Completion")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(4.25*inch, 9*inch, f"This is to certify that")
    
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(4.25*inch, 8.5*inch, f"{user.first_name} {user.last_name}")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(4.25*inch, 8*inch, f"has successfully completed the Cybersecurity Maturity Assessment Tool (CSMAT)")
    c.drawCentredString(4.25*inch, 7.5*inch, f"with a score of {score} out of 100.")
    
    # Add the stamp
    c.drawImage(stamp_path, 3*inch, 5.5*inch, width=1*inch, height=1*inch, mask='auto')
    
    # Add the signature
    c.drawImage(signature_path, 4*inch, 5.5*inch, width=2*inch, height=1*inch, mask='auto')
    
    c.setFont("Helvetica", 12)
    c.drawCentredString(4.25*inch, 5*inch, "Date of Issue: 2024-07-02")
    
    c.save()
    
    return pdf_path
