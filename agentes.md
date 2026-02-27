AGENTE NEXUS (Orquestador)	ROL: Cerebro central del sistema. Recibe todas las peticiones (texto y voz), las clasifica, las distribuye al agente correcto y mantiene la coherencia de la conversación.
HERRAMIENTAS: Claude API (claude-sonnet-4-6), n8n Workflow Engine, Google Sheets API
DECIDE: ¿A qué agente delegar? ¿Requiere escalada humana? ¿Es urgente?


AGENTE CAPTADOR	ROL: Especialista en capturar y calificar leads. Procesa formularios de Google Forms, importa Excel/CSV, limpia datos duplicados, asigna etiquetas de segmentación automática y registra en Google Sheets.(agregar teoría de marketing) lead scoring 
HERRAMIENTAS: Google Forms API, Google Sheets API, Claude (clasificación), n8n
DECIDE: ¿Qué tipo de estudiante es? ¿Qué programa le interesa? ¿Qué etapa del embudo?

AGENTE CONVERSACIONAL	ROL: Atiende prospectos por Telegram con diseño conversacional humano y cercano. Responde preguntas sobre programas, genera cotizaciones, agenda reuniones. Captura peticiones de voz y las convierte en acciones. Opera 24/7.
HERRAMIENTAS: Telegram Bot API, Claude API, Google Sheets (lectura/escritura), Whisper (voz)
DECIDE: ¿Qué programa recomendar? ¿Cuándo hacer follow-up? ¿Generar cotización o escalar?


AGENTE DE IDENTIDAD (Marca USB)	ROL: Garantiza que CADA interacción lleve la voz, los valores y la identidad institucional de la USB. Inyecta el tono correcto, las frases clave y el branding en todas las comunicaciones generadas por el sistema.
HERRAMIENTAS: Claude API (system prompt especializado), templates institucionales
DECIDE: ¿El mensaje refleja los valores USB? ¿Usa el tono correcto? ¿Incluye branding apropiado?

AGENTE DE COMUNICACIÓN	ROL: Gestiona campañas de email marketing masivo a través de Google Groups. Segmenta por etiquetas, personaliza mensajes con Claude, programa envíos escalonados para evitar spam, rastrea aperturas y genera reportes.
HERRAMIENTAS: Google Groups API, Claude API, n8n (scheduler), Google Sheets
DECIDE: ¿A quién enviar? ¿Cuándo y con qué cadencia? ¿Cuántos correos por lote?


AGENTE ANALÍTICO	ROL: Procesa todos los datos del sistema en tiempo real: tasa de captación, conversión por programa, efectividad de campañas, rendimiento del equipo. Genera dashboards automáticos y alertas proactivas.
HERRAMIENTAS: Google Sheets API, Data Studio / Looker Studio, Claude (análisis), n8n
DECIDE: ¿Qué tendencias emergen? ¿Qué campañas funcionan? ¿Qué segmentos priorizar?
