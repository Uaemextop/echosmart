#!/usr/bin/env node
import { execFileSync } from 'child_process';

const args = process.argv.slice(2).filter(a => !a.startsWith('--watchAll'));
try {
  execFileSync('npx', ['vitest', 'run', ...args], { stdio: 'inherit' });
} catch {
  process.exit(1);
}
