# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-27

### 🎉 Primera Versión Estable

#### ✨ Agregado

**Sistema Multi-Agente**
- Orchestrator Agent con OpenAI GPT-4o mini para routing inteligente
- Captador Agent con Groq Gemma2 para calificación de leads
- Conversacional Agent con Groq Mixtral para conversaciones naturales
- Comunicación Agent para generación automática de cotizaciones
- Identidad Agent para información corporativa
- Analítico Agent para insights de datos

**Telegram Integration**
- Bot de leads público para atención 24/7
- Bot admin privado para gestión del sistema
- Soporte para mensajes de texto y notas de voz
- Transcripción automática con Whisper
- Sistema de callbacks para botones interactivos
- Manejo de estados de conversación persistentes

**Quick Estimates (Estimados Rápidos)**
- Detección automática de servicios solicitados
- 8 categorías de servicios predefinidas
- Cálculo dinámico de precios por complejidad
- Generación instantánea de presupuestos
- Formateo en Markdown para Telegram

**Cotizaciones con IA**
- Generación automática usando GPT-4o mini
- Templates personalizables en Markdown
- Cálculo automático de subtotales e IVA
- Sistema de items con cantidades y precios
- Renderizado profesional para Telegram
- Persistencia en base de datos

**Agendamiento Conversacional**
- Flujo multi-step para captura de día y hora
- Estados de conversación (agendando_cita)
- Confirmación automática de citas
- Almacenamiento en BD para seguimiento

**API REST**
- Endpoints CRUD completos para leads
- Gestión de cotizaciones
- Sistema de reuniones
- Campañas de marketing
- Analytics y métricas
- Autenticación JWT

**Base de Datos**
- Integración con Supabase (PostgreSQL)
- Tablas: leads, conversations, cotizaciones, reuniones, agent_logs
- Migraciones SQL organizadas
- Redis para cache y sesiones

**Dashboard Frontend**
- React + TypeScript + Vite
- TailwindCSS para estilos
- Componentes reutilizables
- Páginas: Leads, Cotizaciones, Analytics

**DevOps & Infrastructure**
- Dockerización completa (backend + frontend + redis)
- Docker Compose para desarrollo local
- Nginx como proxy reverso
- Variables de entorno documentadas
- Scripts de validación y testing

**Documentación**
- README profesional de 868 líneas
- 20+ documentos técnicos en /docs
- Guías de instalación y configuración
- Diagramas de arquitectura
- Ejemplos de uso y API

#### 🔧 Configuración

**Modelos de IA Configurables**
- Orchestrator: llama-3.3-70b-versatile (Groq) o gpt-4o-mini (OpenAI)
- Captador: gemma2-9b-it
- Conversacional: mixtral-8x7b-32768
- Identidad: llama-3.1-8b-instant
- Analítico: llama-3.3-70b-versatile

**Variables de Entorno**
- Soporte para múltiples entornos (dev, staging, prod)
- Configuración de empresa personalizable
- Rate limiting configurable
- Logging niveles ajustables

#### 🐛 Correcciones

- Fix: Límite de 64 caracteres en Telegram callback_data
- Fix: Normalización de texto con acentos en detección de servicios
- Fix: Manejo de errores en generación de cotizaciones
- Fix: Botones Markdown causaban "Button_data_invalid"

#### 🔒 Seguridad

- Autenticación JWT para API REST
- Variables sensibles en .env (no committear)
- Validación de inputs con Pydantic
- Rate limiting en endpoints

#### 📊 Métricas y Logs

- Sistema de logging estructurado
- Agent logs para tracking de rendimiento
- Métricas de conversión
- Tracking de errores

---

## [0.9.0] - 2026-02-20

### 🚧 Versión Beta

#### Agregado
- Estructura base del proyecto
- Agentes básicos (Orchestrator, Captador, Conversacional)
- Integración inicial con Telegram
- Base de datos Supabase configurada
- API REST básica

#### Conocido
- Bot a veces no responde (solucionado en v1.0)
- Cotizaciones requieren intervención manual (automatizado en v1.0)
- No hay estimados rápidos (agregado en v1.0)

---

## [0.5.0] - 2026-02-10

### 🎬 Versión Alpha

#### Agregado
- Proof of concept inicial
- Orquestador básico con Groq
- Handler de mensajes Telegram
- Modelos de datos preliminares

---

## Próximas Versiones

### [1.1.0] - Planificado para 2026-03-15

#### En Desarrollo
- [ ] Integración WhatsApp Business
- [ ] Sistema de nurturing automático
- [ ] A/B testing de prompts
- [ ] Analytics con Machine Learning
- [ ] Integración Stripe
- [ ] Webhooks para CRM externos

### [2.0.0] - Futuro

#### Considerando
- [ ] Agente de voz (llamadas telefónicas)
- [ ] Multi-idioma automático
- [ ] Marketplace de agentes
- [ ] Video-llamadas con IA
- [ ] Gamificación de referidos

---

## Guía de Versionado

### Tipos de Versión

- **MAJOR** (X.0.0): Cambios incompatibles con versiones anteriores
- **MINOR** (0.X.0): Nuevas funcionalidades compatibles hacia atrás
- **PATCH** (0.0.X): Corrección de bugs compatibles

### Categorías de Cambios

- **✨ Agregado**: Nuevas características
- **🔧 Cambiado**: Cambios en funcionalidad existente
- **🗑️ Deprecado**: Funcionalidades que serán removidas
- **🔥 Removido**: Funcionalidades eliminadas
- **🐛 Corregido**: Corrección de bugs
- **🔒 Seguridad**: Vulnerabilidades corregidas

---

## Links

- [Repositorio](https://github.com/tu-usuario/orbita)
- [Issues](https://github.com/tu-usuario/orbita/issues)
- [Pull Requests](https://github.com/tu-usuario/orbita/pulls)
- [Documentación](./docs/)

---

## Contribuidores

Gracias a todos los que han contribuido a este proyecto:

- Tu Nombre (@tu-usuario) - Creador y mantenedor principal

---

_Para reportar bugs o solicitar features, abre un [issue en GitHub](https://github.com/tu-usuario/orbita/issues)._
