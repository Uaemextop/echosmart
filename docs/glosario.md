# EchoSmart — Glosario Técnico

Definiciones de los términos técnicos utilizados en la documentación de EchoSmart.

---

## A

**Actuador**
Dispositivo que ejecuta una acción física en el invernadero (riego, ventilación, iluminación) controlado por el sistema.

**ADC (Analog-to-Digital Converter)**
Convertidor analógico-digital. En EchoSmart se utiliza el ADS1115 para leer el sensor de humedad del suelo.

**Alerta**
Notificación generada cuando un valor de sensor supera un umbral configurado. Tiene estados: activa, reconocida, resuelta.

**API (Application Programming Interface)**
Interfaz de comunicación entre componentes del sistema. EchoSmart utiliza API REST (HTTP) y WebSocket.

---

## B

**Backend**
Capa de servidor en la nube que procesa datos, gestiona usuarios y orquesta alertas y reportes. Implementado con FastAPI (Python).

**BH1750**
Sensor de luminosidad digital que se comunica por bus I2C. Rango: 1 – 65,535 lux.

**Broker (MQTT)**
Servidor intermediario de mensajes MQTT. EchoSmart utiliza Mosquitto como broker local en el gateway.

---

## C

**CI/CD (Continuous Integration / Continuous Deployment)**
Prácticas de automatización que permiten integrar y desplegar código de forma continua. EchoSmart utiliza GitHub Actions.

**Cooldown**
Período mínimo entre alertas repetidas para evitar notificaciones excesivas.

**CO₂ (Dióxido de Carbono)**
Gas medido por el sensor MHZ-19C. Importante para la fotosíntesis en el invernadero. Rango óptimo: 400 – 1,000 ppm.

---

## D

**Dashboard**
Panel de control web que muestra los datos del invernadero en tiempo real con gráficas, indicadores y alertas.

**DHT22**
Sensor digital que mide temperatura y humedad relativa simultáneamente. Se comunica por GPIO.

**Docker**
Plataforma de contenedores que permite empaquetar y ejecutar aplicaciones de forma aislada y reproducible.

**DS18B20**
Sensor de temperatura digital de Dallas Semiconductor. Se comunica por protocolo 1-Wire. Precisión: ±0.5°C.

---

## E

**Edge Computing**
Procesamiento de datos en el borde de la red (en el gateway), cerca de los sensores, en lugar de en la nube. Reduce latencia y permite operación offline.

**ER (Entity-Relationship)**
Modelo de datos que describe las relaciones entre entidades (tablas) de una base de datos.

---

## F

**FastAPI**
Framework web moderno de Python para construir APIs REST de alto rendimiento. Utilizado en el backend de EchoSmart.

**Firmware**
Software embebido en el gateway que controla la lectura de sensores y la comunicación.

---

## G

**Gateway**
Dispositivo intermedio (Raspberry Pi 4B) que conecta los sensores físicos con la nube. Lee sensores, evalúa alertas localmente y sincroniza datos.

**GPIO (General Purpose Input/Output)**
Pines de entrada/salida de propósito general de la Raspberry Pi. Utilizados por el sensor DHT22.

---

## H

**HAL (Hardware Abstraction Layer)**
Capa de abstracción de hardware del gateway que unifica el acceso a diferentes protocolos (GPIO, I2C, 1-Wire, UART, ADC).

**Hot-plug**
Capacidad de conectar o desconectar sensores sin necesidad de reiniciar el gateway. Implementado mediante SSDP.

---

## I

**I2C (Inter-Integrated Circuit)**
Bus de comunicación serial utilizado por el sensor BH1750 (luminosidad) y el ADC ADS1115.

**InfluxDB**
Base de datos de series de tiempo utilizada para almacenar las lecturas de sensores con alta eficiencia.

**Invernadero Inteligente**
Estructura agrícola protegida equipada con sensores, actuadores y sistema de monitoreo IoT para optimizar las condiciones de cultivo.

**IoT (Internet of Things)**
Internet de las Cosas. Red de dispositivos físicos conectados que recopilan y comparten datos.

---

## J

**JWT (JSON Web Token)**
Estándar de autenticación utilizado para asegurar las comunicaciones entre el frontend, backend y gateway.

---

## K

**Kubernetes**
Plataforma de orquestación de contenedores utilizada para el despliegue en producción del backend.

---

## L

**Luminosidad (Lux)**
Unidad de medida de la intensidad luminosa. Medida por el sensor BH1750. Rango óptimo para invernadero: 10,000 – 30,000 lux.

---

## M

**MHZ-19C**
Sensor de CO₂ por infrarrojo no dispersivo (NDIR). Se comunica por UART. Rango: 400 – 5,000 ppm.

**MQTT (Message Queuing Telemetry Transport)**
Protocolo de mensajería ligero utilizado para la comunicación entre sensores, gateway y nube.

**Multi-tenant**
Arquitectura que permite a múltiples organizaciones (tenants) compartir la misma infraestructura con aislamiento completo de datos.

---

## N

**NOM (Norma Oficial Mexicana)**
Regulaciones técnicas de cumplimiento obligatorio en México, aplicables a agricultura, seguridad eléctrica y electrónica.

---

## O

**Offline Mode**
Capacidad del gateway de operar sin conexión a internet, almacenando datos localmente en SQLite y sincronizando al recuperar conectividad.

---

## P

**Polling**
Lectura periódica de un sensor a intervalos configurables (1-60 segundos).

**PostgreSQL**
Base de datos relacional utilizada para almacenar metadatos (usuarios, tenants, sensores, reglas de alerta).

**ppm (Partes Por Millón)**
Unidad de concentración utilizada para medir CO₂ en el aire.

---

## Q

**QoS (Quality of Service)**
Nivel de garantía de entrega en MQTT. EchoSmart utiliza QoS 1 (al menos una vez).

---

## R

**RBAC (Role-Based Access Control)**
Control de acceso basado en roles. EchoSmart define 4 roles: Superadmin, Admin, Operador, Viewer.

**React**
Biblioteca de JavaScript para construir interfaces de usuario. Utilizada en el frontend web de EchoSmart.

**Redis**
Almacén de datos en memoria utilizado como caché, almacén de sesiones y sistema de publicación/suscripción.

**Reporte**
Documento generado automáticamente (PDF o Excel) con datos históricos, gráficas y análisis del invernadero.

---

## S

**Sensor**
Dispositivo que mide una variable ambiental (temperatura, humedad, luz, CO₂, humedad del suelo) y envía los datos al gateway.

**SLA (Service Level Agreement)**
Acuerdo de nivel de servicio. EchoSmart apunta a 99.9% de disponibilidad.

**SQLite**
Base de datos embebida utilizada en el gateway como caché local de lecturas.

**SSDP (Simple Service Discovery Protocol)**
Protocolo de descubrimiento automático de dispositivos utilizado para detectar nuevos sensores conectados al gateway.

---

## T

**Tenant**
Organización o unidad que utiliza la plataforma de forma aislada. Cada tenant tiene sus propios usuarios, gateways, sensores y datos.

**TLS (Transport Layer Security)**
Protocolo de cifrado para comunicaciones seguras. Todas las comunicaciones de EchoSmart utilizan TLS 1.2+.

---

## U

**UART (Universal Asynchronous Receiver/Transmitter)**
Protocolo de comunicación serial utilizado por el sensor MHZ-19C (CO₂).

**UPS (Uninterruptible Power Supply)**
Sistema de alimentación ininterrumpida recomendado para el gateway para evitar pérdida de datos ante cortes de energía.

---

## W

**WebSocket**
Protocolo de comunicación bidireccional en tiempo real utilizado para actualizar el dashboard sin necesidad de recargar la página.

**Worker**
Proceso asíncrono del backend que ejecuta tareas en segundo plano: procesamiento de lecturas, evaluación de alertas, generación de reportes.

---

## 1-Wire

**1-Wire**
Protocolo de comunicación de Dallas Semiconductor que utiliza un solo cable de datos. Empleado por el sensor DS18B20 a través de GPIO4.

---

*Última actualización: Marzo 2026 · EchoSmart Dev Team*
