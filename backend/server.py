from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import uuid
import shutil
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ágora Comunicaciones API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.environ.get('DB_NAME', 'agora_comunicaciones')

try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    logger.info(f"Connected to MongoDB at {MONGO_URL}")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")

# Collections
contact_requests = db.contact_requests
quote_requests = db.quote_requests

# Pydantic models
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    message: str

class QuoteRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    services: List[str]
    project_description: str
    budget_range: Optional[str] = None
    timeline: Optional[str] = None

# File upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Ágora Comunicaciones API"}

@app.get("/api/health")
async def health_check():
    try:
        # Test database connection
        db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

# Services data
@app.get("/api/services")
async def get_services():
    services = [
        {
            "id": "branding",
            "title": "Branding & Identidad Corporativa",
            "description": "Desarrollo de identidad visual completa, logos, paletas de colores y guías de marca.",
            "icon": "🎨",
            "features": ["Diseño de logo", "Manual de marca", "Paleta de colores", "Tipografías corporativas"]
        },
        {
            "id": "digital-marketing",
            "title": "Marketing Digital",
            "description": "Estrategias integrales de marketing digital para maximizar tu presencia online.",
            "icon": "📱",
            "features": ["Redes sociales", "SEO/SEM", "Email marketing", "Publicidad digital"]
        },
        {
            "id": "content-creation",
            "title": "Creación de Contenido",
            "description": "Contenido creativo y estratégico para todas tus plataformas digitales.",
            "icon": "✍️",
            "features": ["Copywriting", "Fotografía", "Videos", "Infografías"]
        },
        {
            "id": "web-design",
            "title": "Diseño Web",
            "description": "Sitios web modernos, responsivos y optimizados para conversión.",
            "icon": "💻",
            "features": ["Diseño responsivo", "UI/UX", "E-commerce", "Optimización"]
        },
        {
            "id": "print-design",
            "title": "Diseño Gráfico",
            "description": "Materiales impresos de alta calidad para fortalecer tu imagen de marca.",
            "icon": "🖨️",
            "features": ["Brochures", "Catálogos", "Packaging", "Señalética"]
        },
        {
            "id": "consulting",
            "title": "Consultoría Estratégica",
            "description": "Asesoramiento especializado para optimizar tus estrategias de comunicación.",
            "icon": "💡",
            "features": ["Análisis de mercado", "Estrategia de marca", "Plan de comunicación", "Medición de resultados"]
        }
    ]
    return services

# Team data
@app.get("/api/team")
async def get_team():
    team = [
        {
            "id": str(uuid.uuid4()),
            "name": "María González",
            "role": "Directora Creativa",
            "bio": "Más de 10 años de experiencia en publicidad y branding. Especialista en estrategias de marca.",
            "image": "https://images.unsplash.com/photo-1573496130141-209d200cebd8",
            "linkedin": "#",
            "email": "maria@agoracomunicaciones.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Carlos Rodríguez",
            "role": "Director de Marketing Digital",
            "bio": "Experto en marketing digital y SEO. Apasionado por las nuevas tecnologías y tendencias digitales.",
            "image": "https://images.unsplash.com/photo-1600880292089-90a7e086ee0c",
            "linkedin": "#",
            "email": "carlos@agoracomunicaciones.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Ana Martínez",
            "role": "Diseñadora Gráfica Senior",
            "bio": "Especialista en diseño gráfico y branding con enfoque en sostenibilidad y diseño responsable.",
            "image": "https://images.pexels.com/photos/3810753/pexels-photo-3810753.jpeg",
            "linkedin": "#",
            "email": "ana@agoracomunicaciones.com"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Diego Hernández",
            "role": "Desarrollador Web",
            "bio": "Full-stack developer especializado en crear experiencias web únicas y funcionales.",
            "image": "https://images.unsplash.com/photo-1552581234-26160f608093",
            "linkedin": "#",
            "email": "diego@agoracomunicaciones.com"
        }
    ]
    return team

@app.post("/api/contact")
async def submit_contact(contact: ContactRequest):
    try:
        contact_data = contact.dict()
        contact_data["id"] = str(uuid.uuid4())
        contact_data["created_at"] = datetime.now()
        contact_data["status"] = "new"
        
        result = contact_requests.insert_one(contact_data)
        
        return {
            "message": "Mensaje enviado exitosamente",
            "id": contact_data["id"],
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error submitting contact: {e}")
        raise HTTPException(status_code=500, detail="Error al enviar el mensaje")

@app.post("/api/quote")
async def submit_quote(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    company: str = Form(None),
    services: str = Form(...),  # JSON string of selected services
    project_description: str = Form(...),
    budget_range: str = Form(None),
    timeline: str = Form(None),
    files: List[UploadFile] = File(None)
):
    try:
        # Parse services JSON
        import json
        services_list = json.loads(services) if services else []
        
        # Handle file uploads
        uploaded_files = []
        if files:
            for file in files:
                if file.filename:
                    file_id = str(uuid.uuid4())
                    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'txt'
                    file_path = f"{UPLOAD_DIR}/{file_id}.{file_extension}"
                    
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)
                    
                    uploaded_files.append({
                        "id": file_id,
                        "original_name": file.filename,
                        "path": file_path,
                        "size": os.path.getsize(file_path)
                    })
        
        quote_data = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "phone": phone,
            "company": company,
            "services": services_list,
            "project_description": project_description,
            "budget_range": budget_range,
            "timeline": timeline,
            "files": uploaded_files,
            "created_at": datetime.now(),
            "status": "new"
        }
        
        result = quote_requests.insert_one(quote_data)
        
        return {
            "message": "Solicitud de cotización enviada exitosamente",
            "id": quote_data["id"],
            "status": "success",
            "files_uploaded": len(uploaded_files)
        }
    except Exception as e:
        logger.error(f"Error submitting quote: {e}")
        raise HTTPException(status_code=500, detail="Error al enviar la solicitud de cotización")

@app.get("/api/contact-requests")
async def get_contact_requests():
    try:
        requests = list(contact_requests.find({}, {"_id": 0}).sort("created_at", -1))
        return requests
    except Exception as e:
        logger.error(f"Error fetching contact requests: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener solicitudes de contacto")

@app.get("/api/quote-requests")
async def get_quote_requests():
    try:
        requests = list(quote_requests.find({}, {"_id": 0}).sort("created_at", -1))
        return requests
    except Exception as e:
        logger.error(f"Error fetching quote requests: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener solicitudes de cotización")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)