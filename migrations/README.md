# Migraciones de Base de Datos

Este directorio contiene las migraciones SQL para Supabase.

## Orden de ejecución

1. `001_create_tables.sql` - Crea todas las tablas del sistema
2. `002_add_indexes.sql` - Agrega índices para optimización
3. `003_seed_data.sql` - Datos iniciales (planes, ejemplos)

## Cómo aplicar

Las migraciones se aplican manualmente en el SQL Editor de Supabase o mediante el CLI:

```bash
supabase db push
```

## Nota

El esquema completo está en `documentation/db/schema_complete.sql`
