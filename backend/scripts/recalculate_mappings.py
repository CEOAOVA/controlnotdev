#!/usr/bin/env python3
"""
ControlNot v2 - Script de Recálculo de Mappings

Recalcula el placeholder_mapping de todas las template_versions
usando el algoritmo mejorado con aliases y keywords semánticas.

Uso:
    cd backend
    python -m scripts.recalculate_mappings

    # Para ver cambios sin aplicar:
    python -m scripts.recalculate_mappings --dry-run

    # Para un template específico:
    python -m scripts.recalculate_mappings --template-id <uuid>
"""
import sys
import os
import argparse
from pathlib import Path

# Agregar el directorio raíz del backend al path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Ahora podemos importar los módulos de la app
from app.database import get_supabase_admin_client
from app.services.mapping_service import map_placeholders_to_keys_by_type, PlaceholderMapper
import structlog

# Configurar logging
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()


def recalculate_all_mappings(dry_run: bool = False, template_id: str = None):
    """
    Recalcula todos los placeholder_mappings de template_versions

    Args:
        dry_run: Si True, solo muestra los cambios sin aplicar
        template_id: ID específico de template a recalcular (opcional)
    """
    supabase = get_supabase_admin_client()

    # 1. Obtener todas las versiones de templates
    query = supabase.table('template_versions').select(
        'id, template_id, version_number, placeholders, placeholder_mapping'
    )

    if template_id:
        query = query.eq('template_id', template_id)

    result = query.execute()

    if not result.data:
        logger.info("No se encontraron template_versions para procesar")
        return

    total_versions = len(result.data)
    updated_count = 0
    error_count = 0

    logger.info(
        "Iniciando recálculo de mappings",
        total_versions=total_versions,
        dry_run=dry_run
    )

    for version in result.data:
        version_id = version['id']
        template_id_current = version['template_id']
        placeholders = version.get('placeholders', [])
        old_mapping = version.get('placeholder_mapping', {})

        # 2. Obtener tipo de documento del template padre
        template_result = supabase.table('templates').select(
            'tipo_documento, nombre'
        ).eq('id', template_id_current).single().execute()

        if not template_result.data:
            logger.warning(
                "Template padre no encontrado",
                version_id=version_id,
                template_id=template_id_current
            )
            error_count += 1
            continue

        doc_type = template_result.data['tipo_documento']
        template_name = template_result.data['nombre']

        # Validar que tenemos placeholders para procesar
        if not placeholders:
            logger.debug(
                "Sin placeholders para procesar",
                version_id=version_id,
                template_name=template_name
            )
            continue

        # 3. Recalcular mapping con algoritmo mejorado
        try:
            new_mapping = map_placeholders_to_keys_by_type(
                placeholders,
                doc_type,
                template_name
            )
        except Exception as e:
            logger.error(
                "Error al calcular mapping",
                version_id=version_id,
                template_name=template_name,
                error=str(e)
            )
            error_count += 1
            continue

        # 4. Comparar mappings y mostrar diferencias
        changes = []
        for placeholder in placeholders:
            old_value = old_mapping.get(placeholder, placeholder)
            new_value = new_mapping.get(placeholder, placeholder)
            if old_value != new_value:
                changes.append({
                    'placeholder': placeholder,
                    'old': old_value,
                    'new': new_value
                })

        if changes:
            logger.info(
                "Cambios detectados",
                template_name=template_name,
                doc_type=doc_type,
                changes_count=len(changes)
            )
            for change in changes:
                print(f"  {change['placeholder']}: '{change['old']}' → '{change['new']}'")

            # 5. Actualizar en DB (si no es dry_run)
            if not dry_run:
                try:
                    supabase.table('template_versions').update({
                        'placeholder_mapping': new_mapping
                    }).eq('id', version_id).execute()

                    logger.info(
                        "Mapping actualizado",
                        version_id=version_id,
                        template_name=template_name
                    )
                    updated_count += 1
                except Exception as e:
                    logger.error(
                        "Error al actualizar mapping",
                        version_id=version_id,
                        error=str(e)
                    )
                    error_count += 1
            else:
                updated_count += 1  # Contar como "sería actualizado"
        else:
            logger.debug(
                "Sin cambios en mapping",
                template_name=template_name,
                total_placeholders=len(placeholders)
            )

    # Resumen final
    print("\n" + "=" * 60)
    logger.info(
        "Recálculo completado",
        total_versions=total_versions,
        updated=updated_count,
        errors=error_count,
        dry_run=dry_run
    )
    if dry_run and updated_count > 0:
        print("\n⚠️  Ejecuta sin --dry-run para aplicar los cambios")


def show_mapping_preview(template_id: str):
    """
    Muestra el mapping actual y el propuesto para un template

    Args:
        template_id: ID del template a previsualizar
    """
    supabase = get_supabase_admin_client()

    # Obtener template
    template_result = supabase.table('templates').select(
        'id, nombre, tipo_documento'
    ).eq('id', template_id).single().execute()

    if not template_result.data:
        logger.error("Template no encontrado", template_id=template_id)
        return

    template = template_result.data
    doc_type = template['tipo_documento']

    # Obtener versión activa
    version_result = supabase.table('template_versions').select(
        'id, placeholders, placeholder_mapping'
    ).eq('template_id', template_id).order('version_number', desc=True).limit(1).execute()

    if not version_result.data:
        logger.error("No hay versiones para el template", template_id=template_id)
        return

    version = version_result.data[0]
    placeholders = version.get('placeholders', [])
    current_mapping = version.get('placeholder_mapping', {})

    # Calcular nuevo mapping
    new_mapping = map_placeholders_to_keys_by_type(
        placeholders,
        doc_type,
        template['nombre']
    )

    # Mostrar comparación
    print("\n" + "=" * 70)
    print(f"Template: {template['nombre']}")
    print(f"Tipo: {doc_type}")
    print(f"Placeholders: {len(placeholders)}")
    print("=" * 70)
    print(f"{'Placeholder':<35} {'Actual':<20} {'Propuesto':<20}")
    print("-" * 70)

    for placeholder in sorted(placeholders):
        current = current_mapping.get(placeholder, placeholder)
        proposed = new_mapping.get(placeholder, placeholder)
        indicator = "✓" if current == proposed else "⚠️"
        print(f"{placeholder:<35} {current:<20} {proposed:<20} {indicator}")

    print("=" * 70)


def list_standard_keys(doc_type: str):
    """
    Lista las claves estándar disponibles para un tipo de documento

    Args:
        doc_type: Tipo de documento (cancelacion, compraventa, etc.)
    """
    model_class = PlaceholderMapper.MODEL_MAP.get(doc_type)

    if not model_class:
        logger.error(
            "Tipo de documento no válido",
            doc_type=doc_type,
            valid_types=list(PlaceholderMapper.MODEL_MAP.keys())
        )
        return

    print(f"\n{'='*60}")
    print(f"Claves estándar para: {doc_type}")
    print(f"Modelo: {model_class.__name__}")
    print("=" * 60)

    for field_name, field_info in model_class.model_fields.items():
        extra = field_info.json_schema_extra or {}
        aliases = extra.get('aliases', [])
        description = field_info.description or ""

        print(f"\n{field_name}")
        print(f"  Descripción: {description[:60]}...")
        if aliases:
            print(f"  Aliases: {', '.join(aliases[:5])}{'...' if len(aliases) > 5 else ''}")


def main():
    parser = argparse.ArgumentParser(
        description='Recalcula placeholder_mapping de templates'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Muestra cambios sin aplicar'
    )
    parser.add_argument(
        '--template-id',
        type=str,
        help='ID específico de template a procesar'
    )
    parser.add_argument(
        '--preview',
        type=str,
        metavar='TEMPLATE_ID',
        help='Muestra comparación de mapping para un template'
    )
    parser.add_argument(
        '--list-keys',
        type=str,
        metavar='DOC_TYPE',
        help='Lista claves estándar para un tipo de documento'
    )

    args = parser.parse_args()

    if args.list_keys:
        list_standard_keys(args.list_keys)
    elif args.preview:
        show_mapping_preview(args.preview)
    else:
        recalculate_all_mappings(
            dry_run=args.dry_run,
            template_id=args.template_id
        )


if __name__ == "__main__":
    main()
