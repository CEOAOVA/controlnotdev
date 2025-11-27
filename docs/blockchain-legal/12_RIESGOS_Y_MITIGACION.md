# Matriz de Riesgos y Estrategias de Mitigación

## 📌 Visión General

Análisis completo de riesgos asociados con implementación de blockchain para documentos notariales, con estrategias específicas de mitigación.

---

## 🎯 Metodología de Evaluación

### Escala de Probabilidad

| Nivel | Descripción | Porcentaje |
|-------|-------------|------------|
| **Muy Baja** | Casi imposible | <5% |
| **Baja** | Poco probable | 5-20% |
| **Media** | Posible | 20-50% |
| **Alta** | Probable | 50-80% |
| **Muy Alta** | Casi seguro | >80% |

### Escala de Impacto

| Nivel | Descripción | Consecuencias |
|-------|-------------|---------------|
| **Muy Bajo** | Insignificante | Sin consecuencias materiales |
| **Bajo** | Menor | Molestias menores, fácilmente resoluble |
| **Medio** | Moderado | Afecta operaciones, requiere atención |
| **Alto** | Severo | Daño significativo, costos altos |
| **Muy Alto** | Catastrófico | Amenaza existencia del servicio |

### Matriz de Riesgo

```
IMPACTO →    Muy Bajo  Bajo   Medio   Alto   Muy Alto
PROBABILIDAD ↓
Muy Alta     🟨       🟨     🟧      🟥     🟥
Alta         🟩       🟨     🟨      🟧     🟥
Media        🟩       🟩     🟨      🟨     🟧
Baja         🟩       🟩     🟩      🟨     🟨
Muy Baja     🟩       🟩     🟩      🟩     🟨

🟩 Riesgo Bajo (Aceptable)
🟨 Riesgo Medio (Monitorear)
🟧 Riesgo Alto (Mitigar urgentemente)
🟥 Riesgo Crítico (Eliminar o no proceder)
```

---

## 1. RIESGOS LEGALES

### 1.1. Conflicto con Derecho al Olvido (LFPDPPP)

**Descripción**: Blockchain inmutable vs derecho de cancelación de datos

**Probabilidad**: Media (30%)
**Impacto**: Muy Alto (multas hasta $38.4M MXN)
**Nivel de Riesgo**: 🟧 ALTO

**Escenario**:
```
1. Cliente solicita cancelación de datos personales
2. ControlNot elimina datos de base de datos
3. Hashes permanecen en blockchain (inmutable)
4. INAI investiga y determina incumplimiento
5. Multa millonaria + cierre de operaciones
```

**Mitigación**:

✅ **Solución Primaria**: **SOLO anclar hashes SHA-256**
```python
# ❌ NUNCA hacer esto
blockchain.anchor({
    "nombre": "Juan Pérez",  # Dato personal
    "rfc": "PEGJ860101AAA"   # Dato personal
})

# ✅ SIEMPRE hacer esto
document_hash = sha256(document_bytes).hexdigest()
blockchain.anchor({
    "hash": "a1b2c3d4e5f6...",  # No es dato personal
    "type": "document_hash"
})
```

✅ **Aviso de Privacidad Robusto**:
- Explicar claramente que solo hashes
- Hash no es dato personal (irreversible)
- Datos en base de datos SÍ son eliminables

✅ **Consentimiento Informado**:
```markdown
**CONSENTIMIENTO ESPECIAL - BLOCKCHAIN**

Comprendo que:
1. Solo un código hash (no mis datos personales) se almacenará en blockchain
2. Este código hash NO me identifica ni puede revertirse a mis datos
3. Blockchain es inmutable por naturaleza de la tecnología
4. Puedo solicitar eliminación de mis datos en la base de datos de ControlNot
5. La eliminación de datos de la base hará imposible relacionar el hash con mi identidad

☐ ACEPTO que ControlNot ancle el código hash de mi documento en blockchain

Firma: _______________
```

**Monitoreo**:
- [ ] Revisión legal semestral
- [ ] Seguimiento de resoluciones INAI
- [ ] Actualización de avisos ante cambios legislativos

---

### 1.2. Cambio Regulatorio Adverso

**Descripción**: Nueva ley prohíbe o restringe severamente uso de blockchain

**Probabilidad**: Baja (10%)
**Impacto**: Muy Alto (fin del servicio blockchain)
**Nivel de Riesgo**: 🟨 MEDIO

**Escenario**:
```
1. Congreso aprueba ley restringiendo blockchain en documentos legales
2. Requiere licencias especiales o prohíbe uso privado
3. ControlNot debe cesar operaciones o transformarse completamente
```

**Mitigación**:

✅ **Feature Flags**:
```python
# config.py
class Settings:
    BLOCKCHAIN_ENABLED: bool = env.bool("BLOCKCHAIN_ENABLED", True)
    BLOCKCHAIN_PROVIDER: str = env.str("BLOCKCHAIN_PROVIDER", "polygon")

# Fácil desactivación si regulación cambia
if not settings.BLOCKCHAIN_ENABLED:
    return {"status": "blockchain_disabled"}
```

✅ **Arquitectura Modular**:
- Blockchain como módulo independiente
- Plataforma funciona sin blockchain
- Migración rápida posible

✅ **Diversificación de Servicios**:
- No depender 100% de blockchain
- Ofrecer otros valores (templates, WhatsApp, etc.)
- Blockchain como diferenciador, no única propuesta

**Monitoreo**:
- [ ] Seguimiento de iniciativas legislativas
- [ ] Lobby proactivo con Colegios de Notarios
- [ ] Relación con asociaciones tech

**Contingencia**:
```markdown
## PLAN B: Si blockchain se prohíbe

1. Desactivar feature flags (1 día)
2. Comunicar a clientes (3 días)
3. Migrar a alternativas:
   - Certificación NOM-151 tradicional
   - Firma electrónica avanzada
   - Timestamping services alternativos
4. Mantener plataforma core funcionando
```

---

### 1.3. Demanda por Responsabilidad Notarial

**Descripción**: Cliente demanda a notario por uso de blockchain

**Probabilidad**: Baja (5%)
**Impacto**: Alto (costos legales, reputación)
**Nivel de Riesgo**: 🟨 MEDIO

**Escenario**:
```
1. Notario usa ControlNot para certificar escritura
2. RPP rechaza documento por "certificación no autorizada"
3. Cliente pierde oportunidad de negocio
4. Demanda a notario por daños y perjuicios
5. Notario demanda a ControlNot (responsabilidad cascada)
```

**Mitigación**:

✅ **Disclaimers Explícitos**:
```markdown
## DISCLAIMER EN CERTIFICADO BLOCKCHAIN

⚠️ IMPORTANTE: Esta certificación blockchain es COMPLEMENTARIA
y NO sustituye:
- Inscripción en Registro Público de la Propiedad
- Requisitos legales aplicables
- Trámites oficiales obligatorios

El Notario recomienda completar todos los procesos legales
requeridos independientemente de esta certificación.
```

✅ **Contrato de Servicio con Indemnización**:
```markdown
## CLÁUSULA DE INDEMNIZACIÓN

ControlNot indemnizará al Notario por reclamaciones derivadas de:
- Fallas técnicas del sistema ControlNot
- Errores en generación de hashes
- Incumplimiento de SLA

Límite de indemnización: $500,000 MXN por incidente

ControlNot NO indemnizará por:
- Uso inadecuado del servicio por el Notario
- Promesas hechas por Notario fuera de alcance del servicio
- Decisiones de autoridades sobre aceptación de blockchain
```

✅ **Seguro de Responsabilidad Civil**:
- Cobertura: $1,000,000 MXN
- Incluye defensa legal
- Cubre daños a terceros

✅ **Capacitación Obligatoria**:
- Notarios deben completar curso antes de usar
- Certificado de comprensión de limitaciones
- Actualizaciones obligatorias

---

## 2. RIESGOS TÉCNICOS

### 2.1. Falla de Blockchain (Polygon)

**Descripción**: Red Polygon experimenta caída prolongada o ataque 51%

**Probabilidad**: Muy Baja (<1%)
**Impacto**: Alto (servicio inoperante temporalmente)
**Nivel de Riesgo**: 🟨 MEDIO

**Escenario**:
```
1. Polygon sufre ataque de consenso o bug crítico
2. Red se detiene por horas/días
3. Hashes no pueden anclarse
4. Clientes no pueden verificar documentos existentes
```

**Mitigación**:

✅ **Multi-Blockchain Support**:
```python
# Arquitectura preparada para múltiples blockchains
class BlockchainService:
    def __init__(self):
        self.providers = {
            "polygon": PolygonProvider(),
            "ethereum": EthereumProvider(),  # Backup
            "base": BaseProvider()            # Backup
        }

    async def anchor(self, hash: str):
        primary = "polygon"
        backup = "ethereum"

        try:
            return await self.providers[primary].anchor(hash)
        except BlockchainDownError:
            logger.warning(f"{primary} down, using {backup}")
            return await self.providers[backup].anchor(hash)
```

✅ **Redundancia de Datos**:
```python
# Almacenar copia local de hashes
class CertificationService:
    async def certify(self, document):
        doc_hash = hash_document(document)

        # 1. Anclar en blockchain
        tx_hash = await blockchain.anchor(doc_hash)

        # 2. Guardar en base de datos
        await db.save({
            "document_hash": doc_hash,
            "tx_hash": tx_hash,
            "blockchain": "polygon",
            "status": "confirmed"
        })

        # 3. Backup local adicional
        await local_storage.backup(doc_hash, tx_hash)
```

✅ **Página de Verificación Offline**:
```javascript
// Frontend: Verificación sin depender de blockchain en tiempo real
async function verifyDocument(documentFile, expectedHash) {
    // 1. Calcular hash local
    const localHash = await calculateSHA256(documentFile);

    // 2. Comparar con hash esperado
    if (localHash === expectedHash) {
        return {
            status: "valid",
            message: "Documento íntegro (verificación local)"
        };
    }

    // 3. Solo si necesario, verificar en blockchain
    try {
        const onChainHash = await fetchFromBlockchain(txHash);
        // ...
    } catch (error) {
        // Si blockchain está caído, verificación local es suficiente
        return { status: "local_verified" };
    }
}
```

---

### 2.2. Error en Generación de Hash

**Descripción**: Bug causa que hash incorrecto sea anclado en blockchain

**Probabilidad**: Baja (5%)
**Impacto**: Alto (documento no verificable, reputación)
**Nivel de Riesgo**: 🟨 MEDIO

**Escenario**:
```
1. Bug en código de generación de hash
2. Hash anclado no coincide con documento real
3. Cliente intenta verificar documento meses después
4. Verificación falla
5. Pérdida de confianza, posible demanda
```

**Mitigación**:

✅ **Testing Exhaustivo**:
```python
# tests/test_hashing.py
def test_hash_consistency():
    """Hash debe ser idéntico para mismo documento"""
    doc = b"Escritura de compraventa..."

    hash1 = generate_hash(doc)
    hash2 = generate_hash(doc)
    hash3 = generate_hash(doc)

    assert hash1 == hash2 == hash3

def test_hash_sensitivity():
    """Hash debe cambiar con mínimo cambio en documento"""
    doc1 = b"Escritura version 1"
    doc2 = b"Escritura version 2"  # Cambio mínimo

    hash1 = generate_hash(doc1)
    hash2 = generate_hash(doc2)

    assert hash1 != hash2

def test_hash_format():
    """Hash debe ser SHA-256 válido (64 caracteres hex)"""
    doc = b"Documento de prueba"
    hash_result = generate_hash(doc)

    assert len(hash_result) == 64
    assert all(c in '0123456789abcdef' for c in hash_result)
```

✅ **Verificación Doble**:
```python
async def anchor_with_verification(document: bytes):
    # 1. Generar hash
    doc_hash = generate_hash(document)

    # 2. VERIFICAR INMEDIATAMENTE regenerando
    verification_hash = generate_hash(document)
    if doc_hash != verification_hash:
        raise HashGenerationError("Hash inconsistente")

    # 3. Anclar solo si verificación pasa
    tx_hash = await blockchain.anchor(doc_hash)

    # 4. VERIFICAR que hash anclado es correcto
    time.sleep(5)  # Esperar confirmación
    on_chain_hash = await blockchain.get_hash(tx_hash)
    if on_chain_hash != doc_hash:
        raise AnchorVerificationError("Hash en blockchain no coincide")

    return tx_hash
```

✅ **Auditoría Externa**:
- Code review por terceros
- Auditoría de seguridad anual
- Bug bounty program

---

### 2.3. Pérdida de Acceso a Supabase

**Descripción**: Base de datos Supabase corrupta, hackeada o inaccesible

**Probabilidad**: Muy Baja (2%)
**Impacto**: Muy Alto (pérdida de metadatos)
**Nivel de Riesgo**: 🟨 MEDIO

**Mitigación**:

✅ **Backups Automáticos**:
```python
# services/backup_service.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

class BackupService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def daily_backup(self):
        """Backup completo diario"""
        timestamp = datetime.now().isoformat()

        # 1. Exportar toda la base de datos
        data = await supabase.from_("certifications").select("*").execute()

        # 2. Guardar en múltiples ubicaciones
        await save_to_s3(f"backup-{timestamp}.json", data)
        await save_to_local(f"/backups/backup-{timestamp}.json", data)

    async def start(self):
        # Backup diario a las 3 AM
        self.scheduler.add_job(
            self.daily_backup,
            'cron',
            hour=3,
            minute=0
        )
        self.scheduler.start()
```

✅ **Recuperación desde Blockchain**:
```python
async def rebuild_database_from_blockchain():
    """
    En caso catastrófico, reconstruir base de datos
    leyendo eventos de blockchain
    """
    contract = get_document_registry_contract()

    # Leer todos los eventos DocumentAnchored
    events = await contract.events.DocumentAnchored.get_all_entries()

    for event in events:
        # Recrear registros en base de datos
        await db.insert({
            "document_hash": event.args.documentHash,
            "tx_hash": event.transactionHash.hex(),
            "timestamp": event.args.timestamp,
            "blockchain": "polygon"
        })
```

---

## 3. RIESGOS DE NEGOCIO

### 3.1. Baja Adopción por Notarios

**Descripción**: Notarios no ven valor o tienen resistencia al cambio

**Probabilidad**: Alta (60%)
**Impacto**: Alto (ingresos bajos, modelo no viable)
**Nivel de Riesgo**: 🟧 ALTO

**Escenario**:
```
1. ControlNot lanza blockchain feature
2. Solo 5-10 notarías lo adoptan en 12 meses
3. Ingresos no cubren costos de desarrollo/mantenimiento
4. Feature debe descontinuarse
```

**Mitigación**:

✅ **Educación Proactiva**:
```markdown
## PROGRAMA DE EDUCACIÓN

**Fase 1: Awareness** (Mes 1-3)
- Webinars gratuitos "Blockchain para Notarios 101"
- Videos explicativos cortos (2-3 min)
- Casos de éxito internacionales

**Fase 2: Demostración** (Mes 4-6)
- Demos en vivo
- Pruebas gratuitas 30 días
- "Certifica tu primera escritura gratis"

**Fase 3: Adopción** (Mes 7-12)
- Descuentos early adopters
- Programa de referidos
- Certificación oficial
```

✅ **Pricing Estratégico**:
```markdown
## MODELO FREEMIUM

**Plan Gratuito** (hook inicial):
- 5 certificaciones/mes
- Verificación pública
- QR codes

**Plan Profesional** ($500 MXN/mes):
- 50 certificaciones/mes
- Marca personalizada
- Reportes mensuales

**Plan Enterprise** ($2,000 MXN/mes):
- Ilimitado
- API access
- Soporte prioritario
```

✅ **Partnerships Estratégicos**:
- Alianza con Colegios de Notarios
- Convenios con proveedores de software notarial
- Integraciones con CRMs notariales

---

### 3.2. Competencia con Solución Gubernamental

**Descripción**: Gobierno implementa blockchain oficial, volviendo ControlNot obsoleto

**Probabilidad**: Media (30%)
**Impacto**: Muy Alto (fin del modelo de negocio)
**Nivel de Riesgo**: 🟧 ALTO

**Escenario**:
```
1. Gobierno de CDMX lanza plataforma blockchain oficial
2. Integrada con RPP
3. Gratuita o subsidiada
4. Obligatoria para notarios
5. ControlNot pierde propuesta de valor
```

**Mitigación**:

✅ **Diferenciación**:
```markdown
## VENTAJAS VS SOLUCIÓN GUBERNAMENTAL

ControlNot siempre será:
- ✅ Más rápido (sin burocracia)
- ✅ Mejor UX (enfoque usuario)
- ✅ Más innovador (iteración rápida)
- ✅ Multi-estado (no solo CDMX)
- ✅ Integraciones privadas (WhatsApp, CRM, etc.)
```

✅ **Pivotear a Complementario**:
```markdown
Si gobierno implementa blockchain:

**Plan A**: Integrarnos con solución gubernamental
- API bridge entre ControlNot y sistema oficial
- ControlNot como capa UX sobre infraestructura pública
- Monetizar features adicionales

**Plan B**: Enfoque B2B
- Vender tecnología a gobiernos estatales
- Licenciar plataforma a otros países LATAM
- Servicios de consultoría en blockchain notarial
```

---

## 4. RIESGOS REPUTACIONALES

### 4.1. Caso de Fraude Usando ControlNot

**Descripción**: Alguien usa ControlNot para certificar documento fraudulento

**Probabilidad**: Baja (10%)
**Impacto**: Muy Alto (medios de comunicación, pérdida de confianza)
**Nivel de Riesgo**: 🟨 MEDIO

**Escenario**:
```
1. Actor malicioso crea documento falso
2. Lo certifica con ControlNot (blockchain solo certifica hash, no valida contenido)
3. Usa certificación blockchain para engañar a terceros
4. Fraude se descubre
5. Medios: "Blockchain ControlNot usada en fraude inmobiliario"
```

**Mitigación**:

✅ **Disclaimers Prominentes**:
```markdown
## EN TODA COMUNICACIÓN

⚠️ ControlNot certifica la INTEGRIDAD del documento
(que no ha sido alterado desde certificación).

ControlNot NO certifica:
- ❌ Veracidad del contenido
- ❌ Legalidad del acto jurídico
- ❌ Identidad de las partes
- ❌ Validez legal del documento

Solo notarios públicos pueden dar FE PÚBLICA.
```

✅ **KYC de Notarios**:
```python
# Proceso de registro riguroso
class NotaryOnboarding:
    async def verify_notary(self, applicant):
        # 1. Verificar cédula profesional
        cedula_valid = await verify_with_sep(applicant.cedula)

        # 2. Verificar registro ante Colegio
        colegio_valid = await verify_with_colegio(
            applicant.notary_number,
            applicant.state
        )

        # 3. Verificar que esté activo (no suspendido)
        status = await check_notary_status(applicant.notary_number)

        if not (cedula_valid and colegio_valid and status == "active"):
            raise NotaryVerificationError("Notario no válido")

        return True
```

✅ **Plan de Crisis de Comunicación**:
```markdown
## PROTOCOLO DE RESPUESTA A CRISIS

Si hay caso de fraude:

**Hora 0-2**:
1. Investigar internamente
2. Recopilar evidencia técnica
3. Contactar notario involucrado

**Hora 2-24**:
4. Comunicado oficial preparado
5. Contacto con medios proactivamente
6. Mensaje clave: "ControlNot fue mal usado, no falla técnica"

**Día 1-7**:
7. Colaborar con autoridades si hay investigación
8. Publicar post mortem técnico
9. Implementar medidas preventivas adicionales
```

---

## 🎯 Resumen de Riesgos por Prioridad

### 🟥 RIESGOS CRÍTICOS (Atención Inmediata)

Ninguno identificado (buena señal)

### 🟧 RIESGOS ALTOS (Mitigar Antes de Lanzar)

1. **Derecho al Olvido** → Solo anclar hashes ✅
2. **Baja Adopción** → Plan educación + freemium ✅
3. **Competencia Gubernamental** → Diferenciación clara ✅

### 🟨 RIESGOS MEDIOS (Monitorear y Preparar)

1. Cambio regulatorio
2. Demanda por responsabilidad notarial
3. Falla de blockchain
4. Error en hashing
5. Pérdida de Supabase
6. Caso de fraude

### 🟩 RIESGOS BAJOS (Aceptables)

Riesgos técnicos menores, manejables con buenas prácticas estándar

---

## 📋 Plan de Acción Pre-Lanzamiento

**Antes de lanzar blockchain, completar**:

- [ ] Revisión legal de aviso de privacidad ✅
- [ ] Implementar solo-hash architecture ✅
- [ ] Testing exhaustivo de hashing ✅
- [ ] Backups automáticos configurados ✅
- [ ] Seguro de responsabilidad civil contratado ⏳
- [ ] Plan de crisis redactado ✅
- [ ] Feature flags implementados ✅
- [ ] Multi-blockchain support (al menos 2 blockchains) ⏳
- [ ] KYC process para notarios ⏳
- [ ] Disclaimers en toda comunicación ✅

---

## 📚 Referencias

1. ISO 31000:2018 - Risk Management
2. NIST Cybersecurity Framework
3. LFPDPPP - Ley de Protección de Datos
4. Mejores prácticas blockchain security

---

**Última actualización**: Enero 2025
**Anterior**: [11. Cumplimiento y Compliance](11_CUMPLIMIENTO_COMPLIANCE.md)
**Siguiente**: [13. Recomendaciones de Implementación](13_RECOMENDACIONES_IMPLEMENTACION.md)
