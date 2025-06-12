
import requests
import unittest
import os
import tempfile
from pathlib import Path

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://0054b084-7046-4e30-8484-a596d9823d1f.preview.emergentagent.com"

class AgoraComunicacionesAPITest(unittest.TestCase):
    """Test suite for Ágora Comunicaciones API endpoints"""

    def test_01_health_check(self):
        """Test the health check endpoint"""
        print("\n🔍 Testing health check endpoint...")
        response = requests.get(f"{BACKEND_URL}/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["database"], "connected")
        print("✅ Health check endpoint is working")

    def test_02_services_endpoint(self):
        """Test the services endpoint"""
        print("\n🔍 Testing services endpoint...")
        response = requests.get(f"{BACKEND_URL}/api/services")
        self.assertEqual(response.status_code, 200)
        services = response.json()
        self.assertIsInstance(services, list)
        self.assertGreaterEqual(len(services), 6)  # Should have at least 6 services
        
        # Verify service structure
        service = services[0]
        self.assertIn("id", service)
        self.assertIn("title", service)
        self.assertIn("description", service)
        self.assertIn("icon", service)
        self.assertIn("features", service)
        print(f"✅ Services endpoint returned {len(services)} services")

    def test_03_team_endpoint(self):
        """Test the team endpoint"""
        print("\n🔍 Testing team endpoint...")
        response = requests.get(f"{BACKEND_URL}/api/team")
        self.assertEqual(response.status_code, 200)
        team = response.json()
        self.assertIsInstance(team, list)
        self.assertGreaterEqual(len(team), 4)  # Should have at least 4 team members
        
        # Verify team member structure
        member = team[0]
        self.assertIn("id", member)
        self.assertIn("name", member)
        self.assertIn("role", member)
        self.assertIn("bio", member)
        self.assertIn("image", member)
        self.assertIn("linkedin", member)
        self.assertIn("email", member)
        print(f"✅ Team endpoint returned {len(team)} team members")

    def test_04_contact_endpoint(self):
        """Test the contact form submission endpoint"""
        print("\n🔍 Testing contact form submission...")
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "company": "Test Company",
            "message": "This is a test message from the API test suite."
        }
        
        response = requests.post(f"{BACKEND_URL}/api/contact", json=contact_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("id", data)
        self.assertIn("message", data)
        print("✅ Contact form submission successful")

    def test_05_quote_endpoint(self):
        """Test the quote request submission endpoint with file upload"""
        print("\n🔍 Testing quote request submission with file upload...")
        
        # Create a temporary test file
        temp_file = tempfile.NamedTemporaryFile(suffix=".txt", delete=False)
        temp_file.write(b"This is a test file for quote request submission.")
        temp_file.close()
        
        quote_data = {
            "name": "Test User",
            "email": "test@example.com",
            "phone": "123-456-7890",
            "company": "Test Company",
            "services": '["branding", "digital-marketing"]',
            "project_description": "This is a test project description.",
            "budget_range": "$5000-$15000",
            "timeline": "1 month"
        }
        
        files = {
            'files': (Path(temp_file.name).name, open(temp_file.name, 'rb'), 'text/plain')
        }
        
        response = requests.post(f"{BACKEND_URL}/api/quote", data=quote_data, files=files)
        
        # Clean up the temporary file
        os.unlink(temp_file.name)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("id", data)
        self.assertIn("message", data)
        self.assertIn("files_uploaded", data)
        self.assertEqual(data["files_uploaded"], 1)
        print("✅ Quote request submission with file upload successful")

if __name__ == "__main__":
    print("🧪 Running Ágora Comunicaciones API Tests")
    unittest.main(verbosity=2)
