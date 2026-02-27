#!/usr/bin/env node
/**
 * Script de validación de credenciales ORBITA Frontend
 * Verifica que todas las variables VITE_ estén configuradas
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ANSI Colors
const colors = {
  GREEN: '\x1b[92m',
  RED: '\x1b[91m',
  YELLOW: '\x1b[93m',
  BLUE: '\x1b[94m',
  RESET: '\x1b[0m',
  BOLD: '\x1b[1m',
};

function checkVar(varName, required = true, description = '') {
  const value = process.env[varName];
  const status = value ? '✅' : (required ? '❌' : '⚠️');
  
  let displayValue = '';
  if (value) {
    if (['TOKEN', 'KEY', 'SECRET', 'PASSWORD'].some(s => varName.includes(s))) {
      displayValue = value.length > 20 ? `${value.substring(0, 10)}...${value.substring(value.length - 10)}` : '***';
    } else {
      displayValue = value;
    }
    console.log(`${status} ${varName.padEnd(45)} = ${displayValue}`);
  } else {
    const suffix = required ? `${colors.RED}[REQUERIDO]${colors.RESET}` : `${colors.YELLOW}[OPCIONAL]${colors.RESET}`;
    console.log(`${status} ${varName.padEnd(45)} ${suffix}`);
  }
  
  return !!value;
}

// Cargar .env
const envFile = path.join(__dirname, '.env');
if (fs.existsSync(envFile)) {
  const envContent = fs.readFileSync(envFile, 'utf-8');
  envContent.split('\n').forEach(line => {
    line = line.trim();
    if (line && !line.startsWith('#')) {
      const [key, value] = line.split('=');
      if (key && value) {
        process.env[key.trim()] = value.trim();
      }
    }
  });
}

console.log(`\n${colors.BLUE}${'='.repeat(80)}${colors.RESET}`);
console.log(`${colors.BOLD}${colors.BLUE}VALIDACIÓN DE CREDENCIALES - ORBITA FRONTEND${colors.RESET}`);
console.log(`${colors.BLUE}${'='.repeat(80)}${colors.RESET}\n`);

let allRequiredOk = true;

// 1. SUPABASE
console.log(`${colors.BOLD}1. SUPABASE CLIENT${colors.RESET}`);
allRequiredOk &= checkVar('VITE_SUPABASE_URL', true);
allRequiredOk &= checkVar('VITE_SUPABASE_ANON_KEY', true);
console.log();

// 2. BACKEND API
console.log(`${colors.BOLD}2. BACKEND API${colors.RESET}`);
allRequiredOk &= checkVar('VITE_API_URL', true);
console.log();

// 3. ENVIRONMENT
console.log(`${colors.BOLD}3. ENVIRONMENT${colors.RESET}`);
checkVar('VITE_ENV', false);
console.log();

// Resumen
console.log(`${colors.BLUE}${'='.repeat(80)}${colors.RESET}`);
if (allRequiredOk) {
  console.log(`${colors.GREEN}${colors.BOLD}✅ TODAS LAS CREDENCIALES REQUERIDAS ESTÁN CONFIGURADAS${colors.RESET}`);
  console.log(`${colors.BLUE}${'='.repeat(80)}${colors.RESET}\n`);
  process.exit(0);
} else {
  console.log(`${colors.RED}${colors.BOLD}❌ FALTAN CREDENCIALES REQUERIDAS${colors.RESET}`);
  console.log(`${colors.YELLOW}Por favor, configura el archivo .env en:${colors.RESET}`);
  console.log(`  • orbita_frontend/.env`);
  console.log(`${colors.BLUE}${'='.repeat(80)}${colors.RESET}\n`);
  process.exit(1);
}
