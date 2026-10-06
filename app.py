from fastapi import FastAPI
from .models import GenerateRequest
from .pipeline import build_package
from .providers import ProviderRouter

app=FastAPI(title='Impossible Reality AI YouTube Studio',version='0.1.0')
router=ProviderRouter()

@app.get('/')
def root(): return {'name':'Impossible Reality AI YouTube Studio','status':'ready','docs':'/docs','generate':'/api/generate','providers':'/api/providers'}

@app.get('/api/providers')
def providers(): return router.status()

@app.post('/api/generate')
def generate(req:GenerateRequest): return build_package(req)
