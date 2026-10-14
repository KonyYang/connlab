"""Loopback-only identity endpoints with strict same-origin JSON mutation protection."""
from dataclasses import asdict
import json
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool

from backend.api.dependencies import get_settings
from backend.application.local_identity_service import IdentityError, LocalIdentityService, LocalProfileService
from backend.infrastructure.storage.local_identity_store import LocalIdentityStore, LocalProfileStore
from backend.shared.config import Settings

router = APIRouter(prefix='/api/local-identity', tags=['local identity'])
COOKIE = 'connlab_local_session'
COOKIE_PATH = '/api/local-identity'


def get_identity_service(settings: Settings = Depends(get_settings)) -> LocalIdentityService:
    return LocalIdentityService(LocalIdentityStore(settings.data_dir / 'local_identity.sqlite3'))


def get_profile_service(settings: Settings = Depends(get_settings)) -> LocalProfileService:
    return LocalProfileService(LocalProfileStore(settings.data_dir / 'local_profile.sqlite3'))


@router.get('/profile')
def profile(request: Request, service: LocalProfileService = Depends(get_profile_service)):
    _local_request(request)
    value = service.profile()
    return JSONResponse({'profile': asdict(value) if value else None}, headers={'Cache-Control': 'no-store'})


@router.put('/profile')
async def update_profile(request: Request, service: LocalProfileService = Depends(get_profile_service)):
    body = await _mutation_body(request, {'display_name'})
    try:
        value = await run_in_threadpool(service.save, body.get('display_name'))
    except IdentityError as error:
        return JSONResponse({'detail': {'field': 'display_name', 'message': str(error)}}, status_code=error.status,
                            headers={'Cache-Control': 'no-store'})
    return JSONResponse({'profile': asdict(value)}, headers={'Cache-Control': 'no-store'})


def _local_request(request: Request) -> None:
    if (request.url.hostname not in ('localhost', '127.0.0.1', '::1') or not request.client
            or request.client.host not in ('localhost', '127.0.0.1', '::1')):
        raise _reject(403, 'Local identity is only available on this computer.')


def _reject(status: int, detail: str) -> HTTPException:
    return HTTPException(status, detail, headers={'Cache-Control': 'no-store'})


async def _mutation_body(request: Request, allowed: set[str]) -> dict:
    _local_request(request)
    origin = request.headers.get('origin', '')
    expected = f'{request.url.scheme}://{request.url.netloc}'
    if (request.headers.get('x-connlab-identity') != '1' or origin != expected
            or urlsplit(origin).hostname not in ('localhost', '127.0.0.1', '::1')):
        raise _reject(403, 'A same-origin local request is required.')
    if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
        raise _reject(415, 'JSON is required.')
    content = bytearray()
    async for chunk in request.stream():
        content.extend(chunk)
        if len(content) > 4096:
            raise _reject(413, 'The identity request is too large.')
    try:
        body = json.loads(content)
    except (ValueError, UnicodeDecodeError):
        raise _reject(400, 'Invalid identity request.') from None
    if not isinstance(body, dict) or set(body) - allowed:
        raise _reject(400, 'Invalid identity fields.')
    if 'remember' in body and not isinstance(body['remember'], bool):
        raise _reject(400, 'Remember login must be a boolean.')
    return body


def _response(user) -> JSONResponse:
    return JSONResponse({'user': asdict(user) if user else None}, headers={'Cache-Control': 'no-store'})


@router.get('/session')
def session(request: Request, service: LocalIdentityService = Depends(get_identity_service)):
    _local_request(request)
    # Reads never set/delete cookies: a stale GET must not erase a newer login response.
    return _response(service.session(request.cookies.get(COOKIE)))


async def _authenticate(request: Request, service: LocalIdentityService, registering: bool):
    allowed = {'username', 'password', 'remember'} | ({'display_name'} if registering else set())
    body = await _mutation_body(request, allowed)
    arguments = (body.get('username'), body.get('display_name'), body.get('password')) if registering else (body.get('username'), body.get('password'))
    method = service.register if registering else service.login
    try:
        result = await run_in_threadpool(method, *arguments, remember=body.get('remember', True), prior_token=request.cookies.get(COOKIE))
    except IdentityError as error:
        raise _reject(error.status, str(error)) from None
    response = _response(result.user)
    response.set_cookie(COOKIE, result.token, max_age=result.max_age, httponly=True, samesite='strict',
                        secure=request.url.scheme == 'https', path=COOKIE_PATH)
    return response


@router.post('/register')
async def register(request: Request, service: LocalIdentityService = Depends(get_identity_service)):
    return await _authenticate(request, service, True)


@router.post('/login')
async def login(request: Request, service: LocalIdentityService = Depends(get_identity_service)):
    return await _authenticate(request, service, False)


@router.post('/logout')
async def logout(request: Request, service: LocalIdentityService = Depends(get_identity_service)):
    await _mutation_body(request, set())
    await run_in_threadpool(service.logout, request.cookies.get(COOKIE))
    response = _response(None)
    response.delete_cookie(COOKIE, path=COOKIE_PATH, httponly=True, samesite='strict', secure=request.url.scheme == 'https')
    return response
