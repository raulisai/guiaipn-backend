# 🔄 Migración: Campos de Visualización en Questions

## 📋 Descripción

Agrega 3 campos booleanos a la tabla `questions` para controlar la visualización de contenido:

- `img_active`: Indica si la pregunta tiene imagen asociada
- `leng_math_pregunta`: Indica si la pregunta usa LaTeX
- `leng_math_opciones`: Indica si las opciones usan LaTeX

## 🚀 Cómo Ejecutar

### **Opción 1: Supabase Dashboard (Recomendado)**

1. Ve a tu proyecto en Supabase
2. Navega a **SQL Editor**
3. Copia y pega el contenido de `add_questions_display_fields.sql`
4. Haz clic en **Run**

### **Opción 2: CLI de Supabase**

```bash
supabase db execute --file migrations/add_questions_display_fields.sql
```

### **Opción 3: psql**

```bash
psql -h <host> -U postgres -d postgres -f migrations/add_questions_display_fields.sql
```

## ✅ Verificación

Después de ejecutar la migración, verifica que los campos existan:

```sql
SELECT column_name, data_type, column_default
FROM information_schema.columns
WHERE table_name = 'questions'
AND column_name IN ('img_active', 'leng_math_pregunta', 'leng_math_opciones');
```

Deberías ver:

```
column_name          | data_type | column_default
---------------------|-----------|---------------
img_active           | boolean   | false
leng_math_pregunta   | boolean   | false
leng_math_opciones   | boolean   | false
```

## 📊 Índices Creados

- `idx_questions_img_active`: Para búsquedas de preguntas con imágenes
- `idx_questions_latex`: Para preguntas con contenido LaTeX

## 🔄 Rollback (Si es necesario)

Si necesitas revertir la migración:

```sql
-- Eliminar índices
DROP INDEX IF EXISTS idx_questions_img_active;
DROP INDEX IF EXISTS idx_questions_latex;

-- Eliminar columnas
ALTER TABLE questions
DROP COLUMN IF EXISTS img_active,
DROP COLUMN IF EXISTS leng_math_pregunta,
DROP COLUMN IF EXISTS leng_math_opciones;
```

## 📝 Notas

- Todos los valores por defecto son `FALSE`
- El campo `use_latex` existente se mantiene por compatibilidad pero está marcado como deprecated
- Los índices son parciales (solo indexan filas donde los valores son TRUE) para optimizar espacio
