#!/usr/bin/env node
/**
 * Start the Django development server after Sass has been built.
 *
 * Resolves `uv` from PATH or common install locations (~/.local/bin).
 * If the project `.venv` is missing, runs `uv sync --all-groups` first.
 * Falls back to `.venv/bin/python` when `uv` is unavailable but the venv exists.
 *
 * Honours PORT (default 8000) and HOST (default 0.0.0.0).
 */

import { spawn } from 'node:child_process';
import { accessSync, constants } from 'node:fs';
import { homedir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(fileURLToPath(new URL('.', import.meta.url)), '..');
const host = process.env.HOST || '0.0.0.0';
const port = process.env.PORT || '8000';
const bind = `${host}:${port}`;

const venvPython = join(
  root,
  '.venv',
  process.platform === 'win32' ? 'Scripts/python.exe' : 'bin/python',
);

function exists(path) {
  try {
    accessSync(path, constants.X_OK);
    return true;
  } catch {
    try {
      accessSync(path, constants.F_OK);
      return true;
    } catch {
      return false;
    }
  }
}

function whichOnPath(name) {
  const pathEnv = process.env.PATH || '';
  const sep = process.platform === 'win32' ? ';' : ':';
  for (const dir of pathEnv.split(sep)) {
    if (!dir) continue;
    const candidate = process.platform === 'win32' ? join(dir, `${name}.exe`) : join(dir, name);
    if (exists(candidate)) return candidate;
  }
  return null;
}

function resolveUv() {
  const fromPath = whichOnPath('uv');
  if (fromPath) return fromPath;

  const home = homedir();
  const candidates = [
    join(home, '.local', 'bin', 'uv'),
    join(home, '.cargo', 'bin', 'uv'),
    '/opt/homebrew/bin/uv',
    '/usr/local/bin/uv',
  ];
  for (const candidate of candidates) {
    if (exists(candidate)) return candidate;
  }
  return null;
}

function printUvInstallHelp() {
  console.error(`
uv is required to install Python dependencies and run this example.

Install uv, then sync and start again:

  curl -LsSf https://astral.sh/uv/install.sh | sh
  source "$HOME/.local/bin/env"   # or restart your shell
  uv sync --all-groups
  npm start

Docs: https://docs.astral.sh/uv/getting-started/installation/
`);
}

function run(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'inherit',
      shell: false,
      cwd: root,
      ...options,
    });
    child.on('error', reject);
    child.on('exit', (code, signal) => {
      if (signal) {
        reject(new Error(`Process killed by ${signal}`));
        return;
      }
      if (code !== 0) {
        reject(new Error(`${command} exited with code ${code}`));
        return;
      }
      resolve();
    });
  });
}

function attachSignals(child) {
  for (const signal of ['SIGINT', 'SIGTERM']) {
    process.on(signal, () => {
      child.kill(signal);
    });
  }
  child.on('exit', (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }
    process.exit(code ?? 1);
  });
}

async function main() {
  const uv = resolveUv();
  const hasVenv = exists(venvPython);

  if (!hasVenv) {
    if (!uv) {
      printUvInstallHelp();
      process.exit(1);
    }
    console.error('Python environment missing — running `uv sync --all-groups`…');
    await run(uv, ['sync', '--all-groups']);
  }

  if (uv) {
    const child = spawn(uv, ['run', 'python', 'manage.py', 'runserver', bind], {
      stdio: 'inherit',
      shell: false,
      cwd: root,
    });
    child.on('error', (err) => {
      console.error(err.message);
      process.exit(1);
    });
    attachSignals(child);
    return;
  }

  if (hasVenv) {
    console.error('uv not found on PATH; using existing .venv. Install uv for `uv sync` / tests:');
    console.error('  curl -LsSf https://astral.sh/uv/install.sh | sh');
    const child = spawn(venvPython, ['manage.py', 'runserver', bind], {
      stdio: 'inherit',
      shell: false,
      cwd: root,
    });
    child.on('error', (err) => {
      console.error(err.message);
      process.exit(1);
    });
    attachSignals(child);
    return;
  }

  printUvInstallHelp();
  process.exit(1);
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
