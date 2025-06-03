import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


DEFAULT_API_URL = 'http://127.0.0.1:8000/api/v1/'

@dataclass
class LoginResponse:
    token: str
    user_id: int
    email: str
    perfil: str
    expires_at: Optional[datetime] = None

class APIClient:
    def __init__(self, base_url: Optional[str] = None, token: Optional[str] = None):
        self.base_url = (base_url or DEFAULT_API_URL).rstrip('/')
        self.session = requests.Session()
        if token:
            # Django REST Framework usa 'Token' o 'Bearer' para autenticación
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        # Añadir headers comunes para Django REST Framework
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            # Manejar errores específicos de Django REST Framework
            if response.status_code == 401:
                raise Exception("Error de autenticación. Token inválido o expirado.")
            elif response.status_code == 403:
                raise Exception("No tienes permisos para realizar esta acción.")
            elif response.status_code == 404:
                raise Exception("El recurso solicitado no existe.")
            raise e

class ActividadAPI(APIClient):
    def get_actividades(self) -> List[Dict]:
        """Get all activities"""
        response = self._make_request('GET', 'actividad/')
        return response.json()
    
    def get_actividad(self, actividad_id: int) -> Dict:
        """Get a specific activity by ID"""
        response = self._make_request('GET', f'actividad/{actividad_id}/')
        return response.json()
    
    def create_actividad(self, data: Dict) -> Dict:
        """Create a new activity"""
        response = self._make_request('POST', 'actividad/', json=data)
        return response.json()
    
    def update_actividad(self, actividad_id: int, data: Dict) -> Dict:
        """Update an existing activity"""
        response = self._make_request('PUT', f'actividad/{actividad_id}/', json=data)
        return response.json()
    
    def delete_actividad(self, actividad_id: int) -> None:
        """Delete an activity"""
        self._make_request('DELETE', f'actividad/{actividad_id}/')

class InscripcionAPI(APIClient):
    def get_inscripciones(self) -> List[Dict]:
        """Get all inscriptions"""
        response = self._make_request('GET', 'inscripcion/')
        return response.json()
    
    def get_inscripcion(self, inscripcion_id: int) -> Dict:
        """Get a specific inscription by ID"""
        response = self._make_request('GET', f'inscripcion/{inscripcion_id}/')
        return response.json()
    
    def create_inscripcion(self, data: Dict) -> Dict:
        """Create a new inscription"""
        response = self._make_request('POST', 'inscripcion/', json=data)
        return response.json()
    
    def update_inscripcion(self, inscripcion_id: int, data: Dict) -> Dict:
        """Update an existing inscription"""
        response = self._make_request('PUT', f'inscripcion/{inscripcion_id}/', json=data)
        return response.json()
    
    def delete_inscripcion(self, inscripcion_id: int) -> None:
        """Delete an inscription"""
        self._make_request('DELETE', f'inscripcion/{inscripcion_id}/')

class AuthAPI(APIClient):
    def login(self, email: str, password: str) -> LoginResponse:

        try:
            response = self._make_request(
                'POST',
                'auth/login/',
                json={
                    'email': email,
                    'password': password
                }
            )
            data = response.json()
            
            # Actualizar el token en la sesión
            self.session.headers.update({'Authorization': f'Bearer {data["token"]}'})
            
            return LoginResponse(
                token=data['token'],
                user_id=data['user_id'],
                email=data['email'],
                perfil=data['perfil'],
                expires_at=datetime.fromisoformat(data['expires_at']) if 'expires_at' in data else None
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Credenciales inválidas")
            raise e
