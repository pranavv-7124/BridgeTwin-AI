/** Start the actual Python API and Vite in one process tree. Also supports Vite's forwarded flags. */
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const win = process.platform === 'win32';
const candidates = [resolve(root, 'backend/.venv', win ? 'Scripts/python.exe' : 'bin/python'), resolve(root, '.venv', win ? 'Scripts/python.exe' : 'bin/python')];
const python = process.env.BRIDGETWIN_PYTHON || candidates.find(existsSync) || (win ? 'python' : 'python3');
const children = [];
function start(command, args, cwd) { const child = spawn(command, args, { cwd, stdio: 'inherit', env: process.env }); children.push(child); child.on('error', e => { console.error(`Cannot start ${command}: ${e.message}`); stop(1); }); child.on('exit', code => { if (code && !stopping) stop(code); }); return child; }
let stopping = false;
function stop(code = 0) { if (stopping) return; stopping = true; children.forEach(c => c.kill()); setTimeout(() => process.exit(code), 400).unref(); }
let apiRunning = false;
try { const response = await fetch('http://127.0.0.1:8000/api/health', { signal: AbortSignal.timeout(1000) }); const data = await response.json(); apiRunning = response.ok && data.status === 'ok'; } catch {}
if (!apiRunning) start(python, ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], resolve(root, 'backend'));
start(process.execPath, [resolve(root, 'frontend/node_modules/vite/bin/vite.js'), ...process.argv.slice(2)], resolve(root, 'frontend'));
process.on('SIGINT', () => stop()); process.on('SIGTERM', () => stop());
