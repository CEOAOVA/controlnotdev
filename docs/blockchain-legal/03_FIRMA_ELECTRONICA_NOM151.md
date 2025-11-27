# NOM-151 y Firma Electrónica Avanzada

## 📌 Visión General

**NOM-151-SCFI-2016** es la Norma Oficial Mexicana que establece requisitos para:
- Conservación de mensajes de datos
- Digitalización de documentos
- Integridad y autenticidad de información electrónica

**Relación con Blockchain**: Son **COMPATIBLES** y pueden usarse conjuntamente.

---

## 📜 NOM-151-SCFI-2016

### Publicación Oficial

**Diario Oficial de la Federación**: 30 marzo 2017

**Fuente**: [NOM-151 Qué es - Mifiel](https://blog.mifiel.com/nom-151/)

### Objeto de la Norma

Establecer requisitos que deben observarse para la:
1. **Conservación de mensajes de datos**
2. **Digitalización de documentos**

Garantizando:
- ✅ Integridad
- ✅ Autenticidad
- ✅ Confidencialidad
- ✅ Disponibilidad

### Alcance

**Aplica a**:
- Prestadores de Servicios de Certificación (PSC)
- Instituciones públicas y privadas
- Cualquiera que conserve documentos electrónicos

**NO es obligatoria** para firma electrónica, pero sí complementaria.

---

## 🔐 Firma Electrónica Avanzada (FEA)

### Marco Legal

**Fuente**: [Guía Legalidad Firma Electrónica](https://www.webdoxclm.com/es-mx/guia-de-legalidad-de-firma-electronica)

### Tipos de Firma en México

| Tipo | Regulación | Validez Legal | Uso |
|------|-----------|---------------|-----|
| **Firma Manuscrita** | Código Civil | ✅ Plena | Documentos físicos |
| **Firma Electrónica Simple** | Código de Comercio | 🟡 Limitada | Contratos privados |
| **Firma Electrónica Avanzada (FEA)** | Ley específica | ✅ Plena | Actos jurídicos |
| **e.firma (FIEL)** | SAT | ✅ Plena | Trámites fiscales |

### Requisitos FEA

Para que una firma electrónica sea **Avanzada**:

1. **Creación única del firmante**
   - Certificado digital personal
   - Clave privada exclusiva

2. **Identificación del firmante**
   - Asociación inequívoca con persona
   - Verificable por terceros

3. **Integridad del documento**
   - Detecta cualquier modificación posterior
   - Hash criptográfico

4. **Control exclusivo**
   - Solo firmante tiene acceso a clave privada
   - Protección mediante password/biometría

---

## 🔗 NOM-151 + Blockchain: Integración

### Compatibilidad Técnica

**Fuente**: [Firma Electrónica y Blockchain - NCC](https://noticiasncc.com/plumas-ncc/03/26/plumas-ncc-firma-electronica-y-blockchain/)

### Cómo se Complementan

```
Documento Original (Word/PDF)
          ↓
    Firma Electrónica Avanzada (FEA)
          ↓
    Hash SHA-256 del documento firmado
          ↓
    Blockchain (Polygon) - Anchoring
          ↓
    Certificado NOM-151
```

### Beneficios de la Combinación

1. **FEA**: Identifica al firmante
2. **Blockchain**: Certifica integridad temporal
3. **NOM-151**: Garantiza conservación adecuada

**Resultado**: Triple protección legal

### Proveedores que Combinan Ambas

**Fuente**: [Conceptos Firma Digital](https://help.cincel.digital/conceptos-relacionados-con-la-firma-digital-y-documentos-electr%C3%B3nicos)

Algunos proveedores mexicanos ofrecen:
- ✅ Firma electrónica avanzada (NOM-151)
- ✅ Notarización blockchain (Bitcoin + Ethereum)
- ✅ Certificados de conservación

**Ejemplo de servicio**:
> "Notarización con blockchain usando blockchains públicos de Bitcoin y Ethereum junto con certificados de conservación NOM-151"

---

## 📋 Certificados de Conservación

### ¿Qué son?

**Definición**: Documento que certifica que un archivo electrónico ha sido conservado correctamente según NOM-151.

### Elementos del Certificado

1. **Identificación del documento**
   - Nombre del archivo
   - Tipo de documento
   - Fecha de generación

2. **Datos técnicos**
   - Hash SHA-256 (o superior)
   - Algoritmo de cifrado
   - Formato de archivo

3. **Metadatos de conservación**
   - Fecha y hora de certificación
   - Vigencia del certificado
   - Emisor (PSC)

4. **Firma del PSC**
   - Certificado digital del prestador
   - Sello de tiempo

### Beneficios Legales

**Fuente**: [Beneficios NOM-151 - Cecoban](https://www.cecoban.com/que-beneficios-otorga-la-nom-151/)

1. **Efectos Fiscales**
   - Establecer fecha cierta para auditorías SAT
   - Validez plena ante autoridades

2. **Validez Legal**
   - Documentos electrónicos = misma validez que físicos
   - Admisibles como prueba

3. **Seguridad Jurídica**
   - Presunción de autenticidad
   - Protección contra repudio

---

## 🏢 Prestadores de Servicios de Certificación (PSC)

### Marco Legal

**Fuente**: [PSC Marco Jurídico](http://www.firmadigital.gob.mx/marco_juridico.html)

### Regulación

**Autoridad**: Secretaría de Economía

**Registro**: PSC deben estar acreditados

### ¿Pueden Notarios ser PSC?

**SÍ** - Reforma CDMX 2021

**Fuente**: [Protocolos Digitales Notarías](https://reconoserid.com/nuevos-protocolos-digitales-para-las-notarias-los-actos-juridicos-seran-validados-a-traves-de-la-firma-electronica-y-los-datos-biometricos/)

> "Notarios y corredores públicos son reconocidos como **prestadores de servicios de certificación** para firma electrónica avanzada y pueden emitir certificados digitales"

**Implicación para ControlNot**:
- Notarios clientes PUEDEN emitir certificados NOM-151
- ControlNot puede integrarse con sistema de certificación del notario
- Doble validación: notarial + blockchain

---

## 🔍 NOM-151 vs Blockchain: Comparación

| Aspecto | NOM-151 | Blockchain |
|---------|---------|------------|
| **Objetivo** | Conservación documentos | Inmutabilidad + timestamp |
| **Autoridad** | PSC acreditado | Red descentralizada |
| **Costo** | $$$ (certificados) | $ (gas fees) |
| **Velocidad** | Minutos-horas | Segundos |
| **Validez Legal** | ✅ Explícita (NOM) | ✅ Explícita (Código Nacional) |
| **Interoperabilidad** | Nacional | Global |
| **Modificabilidad** | PSC puede revocar | Imposible modificar |
| **Auditoría** | Por PSC | Pública, transparente |

**Conclusión**: **NO son excluyentes**, se potencian mutuamente.

---

## 💡 Casos de Uso Combinados

### Caso 1: Escritura Notarial Digital

```
1. Notario redacta escritura en Word
2. Partes firman con FEA (e.firma o FEA del notario)
3. Notario firma con su FEA
4. Sistema calcula SHA-256 del .docx firmado
5. Hash se ancla en Polygon blockchain
6. Notario emite certificado NOM-151
7. Cliente recibe:
   - Escritura firmada (.docx)
   - Certificado NOM-151 (.pdf)
   - QR code verificación blockchain
```

**Protecciones**:
- ✅ FEA: Identifica firmantes
- ✅ Blockchain: Prueba de integridad temporal
- ✅ NOM-151: Conservación adecuada
- ✅ Fe pública: Autoridad notarial

### Caso 2: Cancelación de Hipoteca

```
1. Banco emite finiquito con FEA
2. Notario certifica cancelación con su FEA
3. Hash del documento → Blockchain
4. Certificado NOM-151 emitido
5. Registro en RPP (proceso tradicional)
```

**Beneficio para banco**:
- Verificación instantánea de autenticidad
- No necesita solicitar copias certificadas
- Auditoría automática

---

## ⚖️ Validez Legal: Código Civil

### Equivalencia Funcional

**Artículo relevante** (paráfrasis):
> Los documentos electrónicos firmados con FEA tienen la **misma validez** que documentos con firma manuscrita.

### Requisitos para Validez

1. **Confiabilidad del método**
   - Algoritmos criptográficos robustos (RSA 2048+, ECC)
   - Certificados emitidos por PSC acreditados

2. **Apropiado para el fin**
   - FEA aceptada por todas las partes
   - Método adecuado al tipo de acto jurídico

3. **Integridad verificable**
   - Hash del documento intacto
   - Sin modificaciones post-firma

**Blockchain ayuda** en punto 3: integridad verificable permanentemente.

---

## 🚀 Implementación en ControlNot

### Arquitectura Propuesta

```python
# services/signature_service.py
class SignatureService:
    def __init__(self):
        self.psc_client = PSCClient()  # Integración con PSC
        self.blockchain = BlockchainService()

    async def sign_and_anchor(
        self,
        document_bytes: bytes,
        signer_fea_cert: str,
        notary_fea_cert: str
    ):
        # 1. Firmar con FEA
        signed_doc = await self.psc_client.sign(
            document_bytes,
            cert=signer_fea_cert
        )

        # 2. Firma notarial
        notarized_doc = await self.psc_client.sign(
            signed_doc,
            cert=notary_fea_cert
        )

        # 3. Hash del documento firmado
        doc_hash = hashlib.sha256(notarized_doc).hexdigest()

        # 4. Anclar en blockchain
        tx_hash = await self.blockchain.anchor(doc_hash)

        # 5. Solicitar certificado NOM-151
        nom_cert = await self.psc_client.request_certificate(
            file_hash=doc_hash,
            blockchain_tx=tx_hash
        )

        return {
            'signed_document': notarized_doc,
            'document_hash': doc_hash,
            'blockchain_tx': tx_hash,
            'nom151_certificate': nom_cert
        }
```

### Flujo UI

```typescript
// frontend: DocumentSigningFlow.tsx
async function signDocument() {
  // 1. Usuario carga e.firma
  const fea = await loadUserFEA();

  // 2. Firma documento
  const signed = await api.signDocument(documentId, fea);

  // 3. Backend ancla en blockchain
  const anchored = await api.anchorToBlockchain(signed.id);

  // 4. Generar QR de verificación
  const qr = generateQR(anchored.verification_url);

  // 5. Descargar paquete completo
  downloadPackage({
    documento: signed.file,
    certificado_nom151: anchored.certificate,
    qr_blockchain: qr
  });
}
```

---

## 📊 Costos Comparativos

### Opción 1: Solo NOM-151

| Concepto | Costo Unitario | Frecuencia |
|----------|----------------|------------|
| Certificado PSC | $50-150 MXN | Por documento |
| Almacenamiento | $5-10 MXN/mes | Mensual |
| Verificación | Incluida | - |
| **Total anual** (100 docs) | **~$5,600 MXN** | - |

### Opción 2: Solo Blockchain

| Concepto | Costo Unitario | Frecuencia |
|----------|----------------|------------|
| Gas Polygon | $0.75 MXN | Por documento |
| RPC (Alchemy) | Gratis | - |
| Storage (Supabase) | Incluido | - |
| **Total anual** (100 docs) | **~$75 MXN** | - |

### Opción 3: NOM-151 + Blockchain (Híbrido)

| Concepto | Costo Unitario | Frecuencia |
|----------|----------------|------------|
| Certificado PSC | $50 MXN | Por documento |
| Gas Polygon | $0.75 MXN | Por documento |
| **Total anual** (100 docs) | **~$5,075 MXN** | - |

**Análisis**:
- Blockchain es **75x más barato** que NOM-151
- Híbrido agrega solo 1.5% costo adicional
- **Recomendación**: Ofrecer blockchain estándar, NOM-151 como premium

---

## 🎯 Recomendaciones

### Para ControlNot

1. **Implementar Blockchain Primero**
   - Más barato
   - Más rápido
   - Ya tiene validez legal (Código Nacional)

2. **NOM-151 como Servicio Premium**
   - Para clientes que lo requieren (bancos, gobierno)
   - Integración con PSC acreditado
   - Cobrar diferencial

3. **Educación al Cliente**
   - Explicar diferencia blockchain vs NOM-151
   - Casos de uso de cada uno
   - Ventajas de combinación

### Feature Flags Propuestos

```python
# config.py
class Settings:
    BLOCKCHAIN_ENABLED: bool = True
    NOM151_ENABLED: bool = False  # Premium feature
    BLOCKCHAIN_PROVIDER: str = "polygon"
    PSC_INTEGRATION: Optional[str] = None  # "cincel" | "mifiel" | None
```

---

## 📚 Referencias

1. [NOM-151 Qué es - Mifiel](https://blog.mifiel.com/nom-151/)
2. [NOM-151 Firma Electrónica - Webdox](https://www.webdoxclm.com/es-mx/blog/nom-151)
3. [Firma Electrónica y Blockchain](https://noticiasncc.com/plumas-ncc/03/26/plumas-ncc-firma-electronica-y-blockchain/)
4. [Conceptos Firma Digital - Cincel](https://help.cincel.digital/conceptos-relacionados-con-la-firma-digital-y-documentos-electr%C3%B3nicos)
5. [Beneficios NOM-151 - Cecoban](https://www.cecoban.com/que-beneficios-otorga-la-nom-151/)
6. [PSC Marco Jurídico](http://www.firmadigital.gob.mx/marco_juridico.html)
7. [Guía Legalidad Firma Electrónica](https://www.webdoxclm.com/es-mx/guia-de-legalidad-de-firma-electronica)

---

**Última actualización**: Enero 2025
**Anterior**: [02. Validez Legal Blockchain](02_BLOCKCHAIN_VALIDEZ_LEGAL.md)
**Siguiente**: [04. Protección de Datos (LFPDPPP)](04_PROTECCION_DATOS_LFPDPPP.md)
