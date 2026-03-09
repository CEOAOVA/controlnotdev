"""
Seed runner: Inserta datos de prueba para WhatsApp testing.

Uso:
    cd controlnot-v2/backend
    python -m database.seeds.run_seed

Opciones:
    --dry-run    Solo muestra el SQL sin ejecutar
    --clean      Solo ejecuta la limpieza (DELETE) sin insertar

Notas:
    - Usa la SUPABASE service_role key (no anon key) para bypass RLS
    - La FK users.id -> auth.users(id) requiere que primero se creen
      los usuarios en auth.users. Este script puede:
      a) Desactivar temporalmente la FK, insertar, reactivar (--disable-fk)
      b) O usar Supabase Admin API para crear auth users primero
"""
import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)


async def run_seed(dry_run=False, clean_only=False, disable_fk=False):
    """Execute the seed SQL against Supabase."""
    from supabase import create_client
    from app.core.config import settings

    seed_file = Path(__file__).parent / "001_whatsapp_test_data.sql"
    sql = seed_file.read_text(encoding="utf-8")

    if dry_run:
        print("=== DRY RUN - SQL to execute ===")
        print(sql[:2000])
        print(f"\n... ({len(sql)} chars total)")
        return

    # Use service_role key for RLS bypass
    supabase_url = settings.SUPABASE_URL
    supabase_key = settings.SUPABASE_KEY
    print(f"Connecting to Supabase: {supabase_url[:40]}...")

    client = create_client(supabase_url, supabase_key)

    if disable_fk:
        print("Disabling FK constraint on users -> auth.users...")
        try:
            client.postgrest.rpc("exec_sql", {
                "query": "ALTER TABLE users DROP CONSTRAINT IF EXISTS users_id_fkey;"
            }).execute()
            print("  FK disabled.")
        except Exception as e:
            print(f"  Warning: Could not disable FK via RPC: {e}")
            print("  Trying direct approach...")

    # Split SQL into statements and execute
    # Remove comments and split by semicolons
    statements = []
    current = []
    in_string = False
    for line in sql.split('\n'):
        stripped = line.strip()
        if stripped.startswith('--') and not in_string:
            continue
        current.append(line)
        if ';' in line and not in_string:
            stmt = '\n'.join(current).strip()
            if stmt and stmt != ';':
                statements.append(stmt)
            current = []

    if clean_only:
        # Only execute DELETE statements
        statements = [s for s in statements if s.upper().startswith('DELETE')]
        print(f"Clean mode: executing {len(statements)} DELETE statements")

    print(f"Executing {len(statements)} SQL statements...")

    # Execute via Supabase RPC or direct postgrest
    # Since Supabase JS/Python client doesn't support raw SQL directly,
    # we'll use the rpc approach or the REST API

    # Alternative: use psycopg2 directly if DATABASE_URL is available
    try:
        import httpx

        # Use Supabase REST API to execute SQL via pg_net or a custom function
        # Best approach: execute the full SQL as a single transaction via rpc
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
        }

        # Try executing via Supabase SQL endpoint (requires pg_net or custom function)
        # If that doesn't work, fall back to individual statements via postgrest

        # First, try the Supabase Management API SQL endpoint
        # This requires the service_role key
        sql_url = f"{supabase_url}/rest/v1/rpc/exec_sql"

        # Filter out BEGIN/COMMIT for RPC execution (each call is its own transaction)
        clean_sql = sql.replace('BEGIN;', '').replace('COMMIT;', '')

        async with httpx.AsyncClient(timeout=60.0) as http:
            # Try batch execution
            resp = await http.post(
                sql_url,
                headers=headers,
                json={"query": clean_sql}
            )

            if resp.status_code == 200:
                print("Seed data inserted successfully via exec_sql RPC!")
                return True
            elif resp.status_code == 404:
                print("exec_sql RPC function not found. Creating it...")
                # Create the exec_sql function first
                create_fn = """
                CREATE OR REPLACE FUNCTION exec_sql(query text)
                RETURNS void
                LANGUAGE plpgsql
                SECURITY DEFINER
                AS $$
                BEGIN
                    EXECUTE query;
                END;
                $$;
                """
                # We need another way to create this function...
                print("\nThe exec_sql function needs to be created in Supabase SQL Editor.")
                print("Run this in the Supabase Dashboard > SQL Editor:\n")
                print(create_fn)
                print("\nThen re-run this script.")
                print("\nAlternatively, copy the seed SQL file and run it directly")
                print(f"in the Supabase SQL Editor: {seed_file}")
                return False
            else:
                print(f"RPC failed ({resp.status_code}): {resp.text[:500]}")
                print("\nFalling back to manual execution...")
                print(f"\nPlease run the SQL file directly in Supabase SQL Editor:")
                print(f"  {seed_file}")
                return False

    except ImportError:
        print("httpx not installed. Install with: pip install httpx")
        print(f"\nAlternatively, run the SQL directly in Supabase SQL Editor:")
        print(f"  {seed_file}")
        return False

    if disable_fk:
        print("Re-enabling FK constraint on users -> auth.users...")
        try:
            client.postgrest.rpc("exec_sql", {
                "query": """
                    ALTER TABLE users
                    ADD CONSTRAINT users_id_fkey
                    FOREIGN KEY (id) REFERENCES auth.users(id) ON DELETE CASCADE;
                """
            }).execute()
            print("  FK re-enabled.")
        except Exception as e:
            print(f"  Warning: Could not re-enable FK: {e}")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    clean_only = "--clean" in args
    disable_fk = "--disable-fk" in args

    print("=" * 50)
    print("ControlNot v2 - WhatsApp Seed Data Runner")
    print("=" * 50)

    if dry_run:
        print("Mode: DRY RUN")
    elif clean_only:
        print("Mode: CLEAN ONLY")
    else:
        print("Mode: FULL SEED")

    asyncio.run(run_seed(dry_run=dry_run, clean_only=clean_only, disable_fk=disable_fk))


if __name__ == "__main__":
    main()
