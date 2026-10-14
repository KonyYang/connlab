// @vitest-environment node
import { createServer as createHttpServer, request as httpRequest } from 'node:http';
import type { AddressInfo } from 'node:net';
import { createServer as createViteServer, type ViteDevServer } from 'vite';
import { expect, it } from 'vitest';
import config from '../../vite.config';

it('forwards same-origin profile saves through the real dev proxy without accepting foreign origins', async () => {
  let profile: { display_name: string } | null = null;
  const backend = createHttpServer((request, response) => {
    response.setHeader('Content-Type', 'application/json');
    if (request.method === 'GET') { response.end(JSON.stringify({ profile })); return; }
    if (request.headers.origin !== `http://${request.headers.host}` || request.headers['x-connlab-identity'] !== '1') {
      response.statusCode = 403; response.end('{"detail":"same-origin required"}'); return;
    }
    let body = '';
    request.on('data', chunk => { body += chunk; });
    request.on('end', () => { profile = JSON.parse(body); response.end(JSON.stringify({ profile })); });
  });
  let frontend: ViteDevServer | undefined;
  try {
    await new Promise<void>(resolve => backend.listen(0, '127.0.0.1', resolve));
    const target = `http://127.0.0.1:${(backend.address() as AddressInfo).port}`;
    const configuredProxy = config.server?.proxy?.['/api'];
    // Substitute only the owned upstream port. Keep Vite's real string/object proxy semantics.
    const proxy = typeof configuredProxy === 'string' ? target : { ...configuredProxy, target };
    frontend = await createViteServer({ ...config, configFile: false, logLevel: 'silent',
      server: { ...config.server, host: '127.0.0.1', port: 0, strictPort: false,
        proxy: { ...config.server?.proxy, '/api': proxy } } });
    await frontend.listen();
    const port = (frontend.httpServer!.address() as AddressInfo).port;
    const host = `localhost:${port}`;
    const exchange = (method: string, origin?: string) => new Promise<{ status: number; body: string }>((resolve, reject) => {
      const request = httpRequest({ host: '127.0.0.1', port, path: '/api/local-identity/profile', method,
        headers: { Host: host, 'Content-Type': 'application/json', 'X-ConnLab-Identity': '1', ...(origin ? { Origin: origin } : {}) } }, response => {
        let body = ''; response.on('data', chunk => { body += chunk; });
        response.on('end', () => resolve({ status: response.statusCode!, body }));
      });
      request.on('error', reject);
      request.setTimeout(5000, () => request.destroy(new Error('Owned proxy request timed out')));
      request.end(method === 'PUT' ? '{"display_name":"Wire probe"}' : undefined);
    });
    const saved = await exchange('PUT', `http://${host}`);
    expect(saved.status).toBe(200);
    expect(JSON.parse((await exchange('GET')).body)).toEqual({ profile: { display_name: 'Wire probe' } });
    expect((await exchange('PUT', 'https://evil.example')).status).toBe(403);
    expect((await exchange('PUT')).status).toBe(403);
  } finally {
    await frontend?.close();
    if (backend.listening) {
      backend.closeAllConnections();
      await new Promise<void>((resolve, reject) => backend.close(error => error ? reject(error) : resolve()));
    }
  }
}, 20000);
