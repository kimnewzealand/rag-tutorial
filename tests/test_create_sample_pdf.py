"""
Test module for create_sample_pdf functionality
"""

import sys
import os
import unittest
import PyPDF2

# Add scripts directory to path for imports
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))

from scripts.create_sample_pdf import create_sample_pdf, get_content


class TestCreateSamplePDF(unittest.TestCase):
    """Test cases for PDF creation and content verification"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pdf_path = "data/documents/sample_IT_compliance_document.pdf"
        self.content = get_content()

        # Delete existing PDF if it exists
        if os.path.exists(self.pdf_path):
            os.remove(self.pdf_path)
    
    def test_pdf_creation(self):
        """Test that PDF file is created successfully"""
        # Create PDF
        create_sample_pdf()

        # Check if file exists
        self.assertTrue(os.path.exists(self.pdf_path), "PDF file should be created")
    
    def test_pdf_contains_content_zero(self):
        """Test that PDF contains content[0]"""
        # Create PDF
        create_sample_pdf()
        
        # Get expected content
        expected_content = self.content[0]
        
        # Read PDF content
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
        
        # Verify content[0] exists in PDF
        self.assertIn(expected_content, pdf_text, 
                     f"PDF should contain '{expected_content}'")
    
    def test_pdf_contains_multiple_content_items(self):
        """Test that PDF contains multiple content items"""
        # Create PDF
        create_sample_pdf()
        
        # Read PDF content
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text()
        
        # Test first few content items
        test_items = [self.content[0], self.content[2], self.content[6]]
        for item in test_items:
            with self.subTest(content_item=item):
                self.assertIn(item, pdf_text, 
                             f"PDF should contain '{item}'")
    
    def test_pdf_has_pages(self):
        """Test that PDF has at least one page"""
        # Create PDF
        create_sample_pdf()
        
        # Read PDF
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
        
        self.assertGreater(page_count, 0, "PDF should have at least one page")
    
    def tearDown(self):
        """Clean up after tests"""
        # Remove test PDF file if it exists
        if os.path.exists(self.pdf_path):
            os.remove(self.pdf_path)
        pass


if __name__ == "__main__":
    # Ensure data/documents directory exists
    os.makedirs("data/documents", exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)
