/**
 * EchoSmart Demo — GitHub Models AI Client
 *
 * Integrates with GitHub Models inference API to generate
 * AI-powered greenhouse analysis reports.
 *
 * Security: The API token is NEVER stored in source code.
 * Users enter their token at runtime; it is kept only in
 * sessionStorage (cleared when the browser tab closes).
 *
 * Model: openai/gpt-4.1 — Most advanced model available on
 * GitHub Models for structured analysis and reasoning.
 *
 * @module github-models-client
 */

/** GitHub Models inference endpoint */
const INFERENCE_URL = "https://models.github.ai/inference/chat/completions";

/** Model — GPT-5.4: Most advanced model on GitHub Models.
 *  Highest reasoning depth, 1M+ context window, best for
 *  professional agentic analysis. Outperforms o3, o4-mini,
 *  and all GPT-4 generation models in analysis benchmarks. */
const MODEL_ID = "openai/gpt-5.4";

/** sessionStorage key for the runtime token */
const TOKEN_STORAGE_KEY = "echosmart_ghmodels_token";

/**
 * Retrieve the stored token from sessionStorage.
 * @returns {string|null}
 */
export function getStoredToken() {
  try {
    return sessionStorage.getItem(TOKEN_STORAGE_KEY);
  } catch {
    return null;
  }
}

/**
 * Store the token in sessionStorage (never persisted to disk/code).
 * @param {string} token
 */
export function storeToken(token) {
  try {
    sessionStorage.setItem(TOKEN_STORAGE_KEY, token);
  } catch {
    /* sessionStorage unavailable — token lives only in memory */
  }
}

/**
 * Clear the stored token.
 */
export function clearToken() {
  try {
    sessionStorage.removeItem(TOKEN_STORAGE_KEY);
  } catch {
    /* no-op */
  }
}

/**
 * Check if a token is available.
 * @returns {boolean}
 */
export function hasToken() {
  return !!getStoredToken();
}

/**
 * Build the system prompt — detailed instructions for the AI model
 * on how to analyze greenhouse sensor data and generate the report.
 * @returns {string}
 */
function buildSystemPrompt() {
  return `Eres un sistema experto de inteligencia artificial especializado en agronomía de precisión, fitopatología y gestión ambiental de invernaderos inteligentes. Trabajas para la plataforma EchoSmart, un sistema IoT de monitoreo de invernaderos.

═══════════════════════════════════════
CONTEXTO DEL SISTEMA
═══════════════════════════════════════
- Plataforma: EchoSmart — Invernadero Inteligente
- Sensores instalados: DS18B20 (temperatura), DHT22 (humedad), BH1750 (luminosidad), ADS1115+sonda (humedad de suelo), MH-Z19C (CO₂)
- Zonas del invernadero: Zona A (producción principal), Zona B (semilleros y almácigos), Zona C (área de aclimatación)
- Cultivos típicos: tomate, pepino, chile, lechuga en sistemas protegidos

═══════════════════════════════════════
RANGOS ÓPTIMOS DE REFERENCIA (verificados por ingeniería agronómica)
═══════════════════════════════════════
| Parámetro        | Mín Óptimo | Máx Óptimo | Crítico bajo | Crítico alto |
|------------------|------------|------------|--------------|--------------|
| Temperatura      | 18°C       | 28°C       | <12°C        | >35°C        |
| Humedad relativa | 60%        | 80%        | <40%         | >90%         |
| CO₂              | 400 ppm    | 1000 ppm   | <350 ppm     | >1500 ppm    |
| Luminosidad      | 10,000 lux | 30,000 lux | <5,000 lux   | >50,000 lux  |
| Humedad de suelo | 50%        | 80%        | <30%         | >90%         |

═══════════════════════════════════════
INSTRUCCIONES DE ANÁLISIS (OBLIGATORIAS)
═══════════════════════════════════════

1. **ANÁLISIS POR CADA SENSOR**: Para cada uno de los 5 sensores, debes:
   - Evaluar el valor actual vs. el rango óptimo
   - Analizar la tendencia en las últimas 24h (mín, máx, promedio)
   - Determinar si hay variabilidad excesiva (diferencia máx-mín)
   - Identificar si la tendencia es ascendente, descendente o estable

2. **CORRELACIÓN CRUZADA**: Analizar combinaciones peligrosas:
   - Alta humedad + temperatura moderada → riesgo de hongos (Botrytis, Mildiu, Fusarium)
   - Alta temperatura + baja humedad → estrés hídrico, quemaduras foliares
   - Baja luminosidad + alta humedad → etiolación, debilitamiento
   - Alto CO₂ + baja ventilación → toxicidad, cierre estomático
   - Baja humedad de suelo + alta temperatura → marchitamiento permanente

3. **ENFERMEDADES A EVALUAR** (para cada una analizar probabilidad):
   - Botrytis cinerea (moho gris): humedad >80%, temp 18-25°C
   - Mildiu (Peronospora/Phytophthora): humedad >80%, temp 15-22°C, poca ventilación
   - Fusarium oxysporum: temp suelo >25°C, humedad suelo variable
   - Oídio (Erysiphe spp.): humedad 50-70%, temp 20-30°C, baja circulación
   - Pythium: humedad suelo >85%, temp >20°C
   - Virus del mosaico: vectores favorecidos por temp alta + humedad baja
   - Estrés abiótico: térmico, hídrico, lumínico

4. **RECOMENDACIONES DE INGENIERÍA**: Incluir mínimo 4 recomendaciones técnicas:
   - Calibración y mantenimiento de sensores específicos
   - Ajustes al sistema de ventilación/climatización
   - Programación de riego y fertirrigación
   - Manejo integrado de plagas (MIP) preventivo
   - Optimización energética del invernadero

5. **NIVEL DE DETALLE**: Las explicaciones deben ser técnicas y útiles para un ingeniero agrónomo. Incluir:
   - Valores numéricos específicos
   - Nombres científicos de patógenos
   - Mecanismos fisiológicos afectados
   - Productos o técnicas específicas recomendadas

═══════════════════════════════════════
FORMATO DE RESPUESTA (JSON ESTRICTO)
═══════════════════════════════════════

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown, sin \`\`\`, sin texto fuera del JSON):

{
  "resumen": "Párrafo de 3-5 oraciones describiendo el estado general del invernadero, condiciones predominantes, y nivel general de riesgo fitosanitario",
  "enfermedades": [
    {
      "nombre": "Nombre científico y común de la enfermedad o condición de riesgo",
      "riesgo": "ALTO|MEDIO|BAJO",
      "analisis": "Explicación técnica detallada (mínimo 2 oraciones) de por qué existe este riesgo, citando los valores específicos de los sensores que lo causan y los mecanismos fisiológicos involucrados",
      "accion": "Acciones correctivas específicas y técnicas (mínimo 2 oraciones). Incluir productos, técnicas, valores objetivo, y tiempos de aplicación cuando sea relevante"
    }
  ],
  "recomendaciones": [
    {
      "titulo": "Título conciso de la recomendación técnica",
      "descripcion": "Descripción técnica detallada (mínimo 2 oraciones) con especificaciones numéricas, frecuencias, y criterios de evaluación para el ingeniero"
    }
  ]
}

IMPORTANTE:
- Incluir mínimo 2 enfermedades/riesgos en el array, incluso si el riesgo es BAJO
- Incluir mínimo 4 recomendaciones de ingeniería
- Si todo está en rango óptimo, incluir riesgos preventivos y recomendaciones de optimización
- Usar lenguaje técnico en español apropiado para ingenieros agrónomos`;
}

/**
 * Build the user prompt with current sensor data — comprehensive data for analysis.
 * @param {object} sensorData — Flattened sensor readings and stats
 * @returns {string}
 */
function buildUserPrompt(sensorData) {
  const now = new Date();
  const dateStr = now.toLocaleDateString("es-MX", { year: "numeric", month: "long", day: "numeric" });
  const timeStr = now.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" });
  const tempRange = sensorData.tempMax - sensorData.tempMin;
  const humRange = sensorData.humMax - sensorData.humMin;

  return `SOLICITUD DE ANÁLISIS — ${dateStr}, ${timeStr} hrs

═══ DATOS EN TIEMPO REAL DE SENSORES ═══

📊 SENSOR DS18B20 — Temperatura Ambiente:
  • Valor actual: ${sensorData.temperature.toFixed(1)}°C
  • Mínimo últimas 24h: ${sensorData.tempMin}°C
  • Máximo últimas 24h: ${sensorData.tempMax}°C
  • Promedio últimas 24h: ${sensorData.tempAvg}°C
  • Variabilidad (rango): ${tempRange.toFixed(1)}°C
  • Rango óptimo: 18–28°C

📊 SENSOR DHT22 — Humedad Relativa:
  • Valor actual: ${sensorData.humidity.toFixed(0)}%
  • Mínimo últimas 24h: ${sensorData.humMin}%
  • Máximo últimas 24h: ${sensorData.humMax}%
  • Promedio últimas 24h: ${sensorData.humAvg}%
  • Variabilidad (rango): ${humRange.toFixed(0)}%
  • Rango óptimo: 60–80%

📊 SENSOR MH-Z19C — Dióxido de Carbono:
  • Valor actual: ${sensorData.co2.toFixed(0)} ppm
  • Mínimo últimas 24h: ${sensorData.co2Min} ppm
  • Máximo últimas 24h: ${sensorData.co2Max} ppm
  • Promedio últimas 24h: ${sensorData.co2Avg} ppm
  • Rango óptimo: 400–1000 ppm

📊 SENSOR BH1750 — Luminosidad:
  • Valor actual: ${sensorData.light.toFixed(0)} lux
  • Mínimo últimas 24h: ${sensorData.lightMin} lux
  • Máximo últimas 24h: ${sensorData.lightMax} lux
  • Promedio últimas 24h: ${sensorData.lightAvg} lux
  • Rango óptimo: 10,000–30,000 lux

📊 SENSOR ADS1115 + Sonda — Humedad de Suelo:
  • Valor actual: ${sensorData.soil.toFixed(0)}%
  • Mínimo últimas 24h: ${sensorData.soilMin}%
  • Máximo últimas 24h: ${sensorData.soilMax}%
  • Promedio últimas 24h: ${sensorData.soilAvg}%
  • Rango óptimo: 50–80%

═══ DISTRIBUCIÓN POR ZONAS ═══

🏠 Zona A (Producción principal):
  Temp: ${sensorData.temperature.toFixed(1)}°C | HR: ${sensorData.humidity.toFixed(0)}% | CO₂: ${sensorData.co2.toFixed(0)} ppm

🏠 Zona B (Semilleros):
  Luz: ${sensorData.light.toFixed(0)} lux | Suelo: ${sensorData.soil.toFixed(0)}% | CO₂: ${sensorData.co2.toFixed(0)} ppm

🏠 Zona C (Aclimatación):
  Temp: ${(sensorData.temperature - 1.2).toFixed(1)}°C | HR: ${sensorData.humidity.toFixed(0)}%

Por favor genera el análisis completo en formato JSON siguiendo las instrucciones del sistema.`;
}

/**
 * Call the GitHub Models API with the most advanced model.
 * @param {string} token — GitHub PAT with models scope
 * @param {object} sensorData — Flattened sensor readings and stats
 * @returns {Promise<object>} Parsed AI response
 * @throws {Error} On API or parse failure
 */
export async function callGitHubModels(token, sensorData) {
  const response = await fetch(INFERENCE_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`,
    },
    body: JSON.stringify({
      model: MODEL_ID,
      messages: [
        { role: "system", content: buildSystemPrompt() },
        { role: "user", content: buildUserPrompt(sensorData) },
      ],
      temperature: 0.2,
      max_tokens: 4000,
    }),
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    if (response.status === 401) {
      clearToken();
      throw new Error("Token inválido o expirado. Por favor ingresa un nuevo token.");
    }
    if (response.status === 429) {
      throw new Error("Límite de solicitudes alcanzado. Intenta de nuevo en unos minutos.");
    }
    throw new Error(`Error de API (${response.status}): ${errorText}`);
  }

  const data = await response.json();
  const content = data.choices?.[0]?.message?.content;

  if (!content) {
    throw new Error("La respuesta de la IA no contiene contenido.");
  }

  /* Parse JSON — handle markdown code blocks if present */
  const jsonStr = content.replace(/^```json?\s*/i, "").replace(/\s*```$/i, "").trim();

  try {
    return JSON.parse(jsonStr);
  } catch {
    throw new Error("No se pudo parsear la respuesta de la IA como JSON.");
  }
}

/**
 * Prepare flattened sensor data for the API prompt.
 * @param {Record<string, { value: number, history: number[] }>} sensors
 * @param {object} stats — Pre-computed stats per sensor { temp, hum, co2, light, soil }
 * @returns {object} Flat data object
 */
export function prepareSensorData(sensors, stats) {
  return {
    temperature: sensors.temperature.value,
    tempMin: stats.temp.min, tempMax: stats.temp.max, tempAvg: stats.temp.avg,
    humidity: sensors.humidity.value,
    humMin: stats.hum.min, humMax: stats.hum.max, humAvg: stats.hum.avg,
    co2: sensors.co2.value,
    co2Min: stats.co2.min, co2Max: stats.co2.max, co2Avg: stats.co2.avg,
    light: sensors.light.value,
    lightMin: stats.light.min, lightMax: stats.light.max, lightAvg: stats.light.avg,
    soil: sensors.soil.value,
    soilMin: stats.soil.min, soilMax: stats.soil.max, soilAvg: stats.soil.avg,
  };
}
