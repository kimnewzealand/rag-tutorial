"""
Create a dummy PDF document for RAG testing
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

def create_sample_pdf():
    """Create a dummy PDF with IT compliance agreement content including LLM usage and timelines"""
    
    # Create PDF
    c = canvas.Canvas("sample_document.pdf", pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*inch, 10*inch, "IT Compliance Agreement for using AI")
    
    content = [
        "Data Classification Policy",
        "Company data is classified into three levels: Public, Internal, and Confidential. Public data can be shared externally. Internal data is for company use only. Confidential data requires special handling and encryption. All new data must be classified within 24 hours of creation.",
        
        "LLM Usage Compliance",
        "All Large Language Model usage must be approved by the IT Security team within 48 hours of request. Employees must not input confidential company data into public LLM services. Approved LLM tools must be logged and monitored. All LLM-generated content must be reviewed for accuracy within 24 hours before use.",
        
        "AI Content Generation Policy",
        "AI-generated content must be clearly labeled as such. Employees using AI tools for content creation must verify factual accuracy within 48 hours. No sensitive customer or business data can be processed through AI tools without explicit approval within 72 hours. All AI usage must be documented within 24 hours of use.",
        
        "Access Control Standards",
        "User access is granted based on job role and follows the principle of least privilege. Access reviews are conducted quarterly by the 30th of March, June, September, and December. Terminated employees have their access revoked immediately upon departure. Access requests must be approved within 3 business days.",
        
        "Compliance Monitoring",
        "Regular audits are conducted to ensure compliance with all IT policies. Non-compliance issues are addressed within 30 days of discovery. Annual training is required for all employees on security policies and procedures by December 31st each year. Compliance reports are due quarterly by the 15th of each quarter."
    ]
    
    # Add content to PDF
    y_position = 9*inch
    c.setFont("Helvetica", 12)
    
    for i, text in enumerate(content):
        if i % 2 == 0:  # Section headers
            c.setFont("Helvetica-Bold", 14)
            c.drawString(1*inch, y_position, text)
            y_position -= 0.3*inch
        else:  # Section content
            c.setFont("Helvetica", 12)
            # Split long text into lines
            words = text.split()
            lines = []
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) < 70:
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                c.drawString(1*inch, y_position, line)
                y_position -= 0.2*inch
            
            y_position -= 0.3*inch
    
    c.save("data/documents/sample_document.pdf")
    print("✅ Created sample_document.pdf")

if __name__ == "__main__":
    create_sample_pdf() 