# Cumplimiento y Compliance: Templates Legales

## 📌 Visión General

Este documento proporciona **templates copy-paste** de avisos de privacidad, términos y condiciones, y consentimientos necesarios para cumplir con LFPDPPP y regulación aplicable.

⚠️ **IMPORTANTE**: Estos templates deben ser **revisados por abogado** antes de uso en producción.

---

## 🔐 Aviso de Privacidad Integral

### Template para ControlNot

```markdown
# AVISO DE PRIVACIDAD INTEGRAL
## ControlNot S.A. de C.V.

**Fecha de última actualización**: [Fecha]

---

### I. IDENTIDAD Y DOMICILIO DEL RESPONSABLE

**CONTROLNOT S.A. DE C.V.** (en adelante "ControlNot" o "el Responsable"), con domicilio en:

[Calle y número]
[Colonia], [Código Postal]
[Ciudad], [Estado], México

RFC: [RFC de la empresa]
Teléfono: [Teléfono]
Correo electrónico: privacidad@controlnot.com

---

### II. DATOS PERSONALES QUE SE RECABAN

ControlNot recaba los siguientes tipos de datos personales:

**A. Datos de Identificación y Contacto:**
- Nombre completo
- RFC
- Correo electrónico
- Teléfono
- Domicilio

**B. Datos de la Notaría (si aplica):**
- Número de notaría
- Entidad federativa
- Nombre del titular de la notaría
- Registro ante Colegio de Notarios

**C. Datos de Documentos Notariales:**
⚠️ **IMPORTANTE**: ControlNot **NO almacena el contenido completo** de escrituras o documentos notariales en blockchain.

**Lo que SÍ almacenamos**:
- Códigos hash criptográficos (SHA-256) de documentos
- Fecha y hora de certificación
- Transaction hash de blockchain
- Tipo de documento (ej. "Escritura de compraventa")

**Lo que NO almacenamos en blockchain**:
- ❌ Nombres de las partes
- ❌ Datos de identificación (INE, RFC)
- ❌ Domicilios
- ❌ Valores monetarios
- ❌ Contenido completo del documento

**D. Datos de Facturación:**
- Razón social
- RFC
- Domicilio fiscal
- Régimen fiscal

---

### III. FINALIDADES DEL TRATAMIENTO

**Finalidades Primarias** (necesarias para el servicio):

1. **Provisión del Servicio**
   - Certificar documentos mediante tecnología blockchain
   - Generar códigos QR de verificación
   - Proporcionar acceso a plataforma ControlNot

2. **Comunicación**
   - Enviar notificaciones sobre certificaciones
   - Soporte técnico
   - Facturación

3. **Cumplimiento Legal**
   - Emitir facturas electrónicas (CFDI)
   - Cumplir con obligaciones fiscales
   - Atender requerimientos de autoridades

**Finalidades Secundarias** (requieren consentimiento expreso):

4. **Mercadotecnia**
   - Enviar información sobre nuevos servicios
   - Invitaciones a eventos y capacitaciones
   - Encuestas de satisfacción

5. **Mejora del Servicio**
   - Análisis de uso de la plataforma
   - Desarrollo de nuevas funcionalidades

Para finalidades secundarias, puede manifestar su negativa mediante:
- Correo: privacidad@controlnot.com
- Configuración de cuenta en plataforma
- Llamada: [Teléfono]

---

### IV. TRANSFERENCIAS DE DATOS

ControlNot **NO transfiere** sus datos personales a terceros, EXCEPTO en los siguientes casos que NO requieren consentimiento (Art. 37 LFPDPPP):

**A. Proveedores de Servicios:**

1. **Servicios de Blockchain**
   - Proveedor: Alchemy/Infura (proveedores RPC)
   - Finalidad: Anclar hashes en blockchain Polygon
   - Datos transferidos: **SOLO códigos hash** (no datos personales)
   - Ubicación: Estados Unidos
   - **Protección**: Solo se transfieren hashes (no identifican personas)

2. **Almacenamiento en la Nube**
   - Proveedor: Supabase (PostgreSQL)
   - Finalidad: Almacenar base de datos de plataforma
   - Datos transferidos: Todos los listados en Sección II
   - Ubicación: Estados Unidos
   - **Protección**: Cifrado en tránsito y reposo, cumplimiento GDPR/SOC2

3. **Facturación Electrónica**
   - Proveedor: [Nombre del PAC]
   - Finalidad: Emitir CFDI
   - Datos transferidos: Datos de facturación (Sección II.D)
   - Ubicación: México

**B. Autoridades:**
- Servicio de Administración Tributaria (SAT)
- Autoridades judiciales (con orden)
- INAI (en caso de procedimiento)

---

### V. MEDIOS PARA EJERCER DERECHOS ARCO

Usted tiene derecho a:
- **A**cceso: Conocer qué datos tenemos
- **R**ectificación: Corregir datos inexactos
- **C**ancelación: Solicitar eliminación
- **O**posición: Negarse a ciertos usos

**¿Cómo ejercer sus derechos?**

**Solicitud por escrito a**: privacidad@controlnot.com

**Requisitos de la solicitud**:
1. Nombre completo del titular
2. Domicilio o correo electrónico para respuesta
3. Documentos que acrediten identidad (INE/IFE)
4. Descripción clara de datos sobre los que ejerce derecho
5. Derecho que desea ejercer (ARCO)
6. Cualquier elemento que facilite localización de datos

**Plazo de respuesta**: 15 días hábiles

**Formato de solicitud**: Disponible en www.controlnot.com/privacidad

**⚠️ LIMITACIÓN IMPORTANTE - DERECHO DE CANCELACIÓN EN BLOCKCHAIN**:

**Datos almacenados OFF-chain (Supabase)**:
✅ **SÍ pueden eliminarse** completamente

**Datos almacenados ON-chain (Blockchain)**:
❌ **NO pueden eliminarse** debido a naturaleza inmutable de blockchain

**Sin embargo**:
- Solo almacenamos **códigos hash** en blockchain (no datos personales)
- Códigos hash SHA-256 son **irreversibles** y **no identifican** personas
- Por tanto, **NO se considera dato personal** según LFPDPPP

**Si solicita cancelación**:
1. Eliminaremos todos sus datos de nuestra base de datos
2. Códigos hash permanecerán en blockchain (pero no lo identifican)
3. Sin acceso a nuestra base, nadie puede relacionar hash con su identidad

---

### VI. REVOCACIÓN DEL CONSENTIMIENTO

Puede revocar su consentimiento para finalidades secundarias en cualquier momento mediante:

- Correo: privacidad@controlnot.com
- Configuración de cuenta
- Llamada: [Teléfono]

**Plazo de respuesta**: 15 días hábiles

**Efectos**: Dejará de recibir comunicaciones de mercadotecnia, pero el servicio principal continuará.

---

### VII. OPCIONES PARA LIMITAR USO O DIVULGACIÓN

Puede limitar uso/divulgación de datos mediante:

1. **Registro en "Lista de Exclusión"**: privacidad@controlnot.com
2. **Configuración de privacidad** en plataforma
3. **Cancelación de cuenta** (con limitaciones blockchain explicadas arriba)

---

### VIII. USO DE COOKIES Y WEB BEACONS

Nuestro sitio web utiliza:

**Cookies esenciales** (necesarias para funcionamiento):
- Sesión de usuario
- Autenticación
- Preferencias de idioma

**Cookies analíticas** (requieren consentimiento):
- Google Analytics (análisis de tráfico)
- Hotjar (mapas de calor)

**Puede deshabilitarlas** mediante configuración de navegador.

**Más información**: www.controlnot.com/cookies

---

### IX. MENORES DE EDAD

ControlNot **NO** recaba datos de menores de 18 años intencionalmente.

Si detectamos datos de menores sin consentimiento paterno, serán eliminados de inmediato.

---

### X. CAMBIOS AL AVISO DE PRIVACIDAD

Nos reservamos el derecho de actualizar este aviso.

**Se le notificará** mediante:
- Correo electrónico
- Aviso en plataforma
- Publicación en www.controlnot.com/privacidad

**Versión vigente**: Siempre disponible en sitio web con fecha de actualización.

---

### XI. AUTORIDAD COMPETENTE

Si considera que sus derechos han sido vulnerados, puede acudir al **Instituto Nacional de Transparencia, Acceso a la Información y Protección de Datos Personales (INAI)**:

- Sitio web: www.inai.org.mx
- Teléfono: 800 835 43 24
- Correo: datos.personales@inai.org.mx

---

### XII. CONSENTIMIENTO

**He leído y comprendo el presente Aviso de Privacidad.**

Otorgo mi consentimiento para el tratamiento de mis datos personales conforme a las finalidades descritas.

**ESPECIALMENTE**, comprendo y acepto que:
1. Solo códigos hash se almacenan en blockchain (no datos personales)
2. Blockchain es inmutable y hashes no pueden eliminarse
3. Puedo solicitar eliminación de datos en base de datos (off-chain)
4. ControlNot no transfiere datos personales, solo hashes no identificables

---

**Nombre**: _______________________
**Firma**: _______________________
**Fecha**: _______________________

---

**ControlNot S.A. de C.V.**
**Fecha de emisión**: [Fecha]
**Versión**: 1.0
```

---

## 📋 Términos y Condiciones de Servicio

### Template para Plataforma ControlNot

```markdown
# TÉRMINOS Y CONDICIONES DE USO
## Plataforma ControlNot

**Fecha de última actualización**: [Fecha]

---

## 1. ACEPTACIÓN DE TÉRMINOS

Al acceder y usar la plataforma ControlNot, usted acepta estar sujeto a estos Términos y Condiciones.

Si no está de acuerdo, NO utilice el servicio.

---

## 2. DEFINICIONES

- **Plataforma**: Software y servicios proporcionados por ControlNot S.A. de C.V.
- **Usuario**: Notario público o persona autorizada por notaría
- **Certificación Blockchain**: Proceso de anclar código hash de documento en blockchain
- **Hash**: Código criptográfico SHA-256 único generado a partir de documento
- **Blockchain**: Red descentralizada Polygon donde se anclan hashes
- **QR Code**: Código de verificación generado para cada certificación

---

## 3. DESCRIPCIÓN DEL SERVICIO

ControlNot proporciona una plataforma para **certificar documentos notariales** mediante tecnología blockchain.

### 3.1. Alcance del Servicio

**ControlNot SÍ ofrece**:
✅ Generación de código hash (SHA-256) de documentos
✅ Anclaje de hash en blockchain Polygon
✅ Generación de QR code de verificación
✅ Página de verificación pública
✅ Almacenamiento de metadatos de certificación
✅ Reportes y estadísticas de uso

**ControlNot NO ofrece**:
❌ Asesoría legal o notarial
❌ Validación jurídica de documentos
❌ Reemplazo de inscripción en RPP
❌ Garantía de aceptación por autoridades
❌ Firma electrónica avanzada (FEA)

### 3.2. Carácter Complementario

**⚠️ IMPORTANTE**:

La certificación blockchain es **COMPLEMENTARIA** a los procesos notariales tradicionales y registrales.

**NO sustituye**:
- Fe pública notarial
- Inscripción en Registro Público de la Propiedad
- Requisitos legales aplicables

El usuario es responsable de cumplir con todas las obligaciones legales, independientemente del uso de ControlNot.

---

## 4. REGISTRO Y CUENTA

### 4.1. Requisitos

Para usar ControlNot debe:
- Ser notario público titulado, o
- Ser empleado autorizado de notaría, con
- Proporcionar información verídica y completa

### 4.2. Seguridad de Cuenta

Usted es responsable de:
- Mantener confidencialidad de credenciales
- Todas las actividades bajo su cuenta
- Notificar inmediatamente uso no autorizado

---

## 5. TECNOLOGÍA BLOCKCHAIN

### 5.1. Funcionamiento

**Proceso de certificación**:

1. Usuario carga documento a plataforma
2. ControlNot genera hash SHA-256
3. Hash se ancla en blockchain Polygon
4. Blockchain genera transaction hash (tx_hash)
5. ControlNot crea registro con metadatos
6. Se genera QR code de verificación

**Datos almacenados en blockchain**:
- ✅ Hash SHA-256 del documento
- ✅ Timestamp de certificación
- ✅ Dirección de contrato inteligente

**Datos NO almacenados en blockchain**:
- ❌ Contenido del documento
- ❌ Datos personales
- ❌ Información confidencial

### 5.2. Inmutabilidad de Blockchain

**⚠️ ADVERTENCIA IMPORTANTE**:

Una vez que un hash es anclado en blockchain:
- **NO puede ser modificado**
- **NO puede ser eliminado**
- **Permanece indefinidamente**

Esto es una **característica inherente** de blockchain, no un defecto.

**Protección de privacidad**:
Como solo se almacenan hashes (no datos personales), esto cumple con LFPDPPP.

### 5.3. Blockchain Pública

ControlNot utiliza **Polygon** (blockchain pública).

**Implicaciones**:
- Cualquier persona puede ver hashes anclados
- ControlNot NO controla la red Polygon
- Transacciones son verificables públicamente

**Verificación independiente**:
Hashes pueden verificarse en exploradores públicos como:
- Polygonscan.com
- Cualquier nodo de Polygon

---

## 6. LIMITACIONES DE RESPONSABILIDAD

### 6.1. Disponibilidad del Servicio

ControlNot se esfuerza por mantener servicio disponible 99.5% del tiempo (SLA).

**NO garantizamos**:
- Disponibilidad 100% ininterrumpida
- Ausencia total de errores técnicos
- Funcionamiento en todos los dispositivos

### 6.2. Blockchain de Terceros

ControlNot **NO es responsable** de:
- Fallas de red Polygon (fuera de nuestro control)
- Cambios en protocolo blockchain
- Congestión de red que afecte tiempos de confirmación
- Costos de gas (fees) de blockchain

### 6.3. Limitación de Daños

En ningún caso ControlNot será responsable por:
- Daños indirectos, consecuenciales o punitivos
- Pérdida de ganancias o ingresos
- Pérdida de datos
- Daños que excedan el monto pagado por servicio en últimos 12 meses

### 6.4. Uso por Parte de Clientes Finales

ControlNot **NO es responsable** de:
- Cómo notarios explican servicio a sus clientes
- Promesas hechas por notarios sobre efectos legales
- Malentendidos sobre alcance del servicio

**El usuario (notario) es responsable** de:
- Informar correctamente a clientes
- Obtener consentimientos necesarios
- Cumplir con regulación aplicable

---

## 7. VALIDEZ LEGAL

### 7.1. Marco Legal Mexicano

La certificación blockchain se basa en:
- Código Nacional de Procedimientos Civiles y Familiares (Arts. 349-350)
- Ley del Notariado (estatal aplicable)
- LFPDPPP

### 7.2. Sin Garantía de Aceptación

**⚠️ DISCLAIMER IMPORTANTE**:

ControlNot **NO garantiza** que:
- Autoridades judiciales acepten certificación blockchain
- Registro Público de la Propiedad reconozca blockchain
- Bancos acepten documentos certificados con blockchain
- Cambios legales futuros no afecten validez

**Recomendación**:
Consulte con abogado especializado antes de confiar exclusivamente en blockchain para efectos legales.

---

## 8. PROPIEDAD INTELECTUAL

### 8.1. Propiedad de ControlNot

La plataforma, código, diseño, marca "ControlNot" son propiedad exclusiva de ControlNot S.A. de C.V.

### 8.2. Licencia de Uso

Se otorga licencia **NO exclusiva, NO transferible** para usar plataforma conforme a estos términos.

**Prohibido**:
- Copiar, modificar, distribuir el software
- Realizar ingeniería inversa
- Usar marca ControlNot sin autorización
- Sublicenciar o revender servicio

---

## 9. PRIVACIDAD Y PROTECCIÓN DE DATOS

El tratamiento de datos personales se rige por nuestro [Aviso de Privacidad](#aviso-de-privacidad-integral).

**Resumen**:
- Solo hashes en blockchain (no datos personales)
- Datos en base de datos pueden eliminarse
- Cumplimiento LFPDPPP

---

## 10. PAGO Y FACTURACIÓN

### 10.1. Planes de Suscripción

[Describir planes: Básico, Pro, Enterprise]

### 10.2. Facturación

- Factura electrónica (CFDI 4.0)
- Mensual o anual
- Pagos mediante transferencia/tarjeta

### 10.3. Reembolsos

**Política de no reembolsos**:
Debido a la naturaleza del servicio (hashes anclados en blockchain son permanentes), **NO se ofrecen reembolsos**.

**Excepciones**:
- Error técnico comprobable de ControlNot
- Decisión discrecional de ControlNot

---

## 11. TERMINACIÓN

### 11.1. Por el Usuario

Puede cancelar suscripción en cualquier momento mediante:
- Configuración de cuenta
- Correo a: soporte@controlnot.com

**Efectos**:
- No se generarán nuevos cargos
- Acceso a plataforma termina al final del período pagado
- Hashes en blockchain permanecen (inmutables)

### 11.2. Por ControlNot

Podemos terminar servicio si:
- Incumple estos términos
- Uso fraudulento o ilegal
- Impago de suscripción

**Notificación**: 15 días antes de terminación

---

## 12. MODIFICACIONES

ControlNot puede modificar estos términos en cualquier momento.

**Notificación**:
- Correo electrónico
- Aviso en plataforma
- 30 días antes de vigencia

**Aceptación**:
Uso continuado = aceptación de nuevos términos

---

## 13. LEY APLICABLE Y JURISDICCIÓN

Estos términos se rigen por leyes de México.

**Jurisdicción**: Tribunales de [Ciudad, Estado], México.

---

## 14. DISPOSICIONES GENERALES

### 14.1. Integridad del Acuerdo

Estos términos constituyen acuerdo completo entre partes.

### 14.2. Severabilidad

Si alguna disposición es inválida, las demás permanecen vigentes.

### 14.3. Renuncia

Falta de aplicación de término no constituye renuncia.

---

## 15. CONTACTO

**ControlNot S.A. de C.V.**
- Correo: soporte@controlnot.com
- Teléfono: [Teléfono]
- Sitio web: www.controlnot.com

---

**Última actualización**: [Fecha]
**Versión**: 1.0

**Al usar ControlNot, acepta estos Términos y Condiciones.**
```

---

## ✅ Checklist de Cumplimiento

### Antes de Lanzar

- [ ] Aviso de privacidad revisado por abogado
- [ ] Términos y condiciones revisados por abogado
- [ ] Templates de consentimiento preparados
- [ ] Política de cookies implementada
- [ ] Botones de opt-in/opt-out funcionales
- [ ] Proceso de solicitudes ARCO definido
- [ ] Responsable de privacidad designado
- [ ] Capacitación a equipo en LFPDPPP

---

## 📚 Referencias

1. LFPDPPP - Ley Federal de Protección de Datos Personales
2. INAI - Guías de Avisos de Privacidad
3. Lineamientos del Aviso de Privacidad
4. NOM-151-SCFI-2016

---

**Última actualización**: Enero 2025
**Anterior**: [10. Casos Internacionales](10_CASOS_INTERNACIONALES.md)
**Siguiente**: [12. Riesgos y Mitigación](12_RIESGOS_Y_MITIGACION.md)
