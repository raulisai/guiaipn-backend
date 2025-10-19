-- =========================================
-- Migración: Agregar campos de visualización a tabla questions
-- Fecha: 2025-01-19
-- =========================================

-- Agregar campos booleanos para control de visualización
ALTER TABLE questions
ADD COLUMN IF NOT EXISTS img_active BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS leng_math_pregunta BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS leng_math_opciones BOOLEAN DEFAULT FALSE;

-- Comentarios para documentación
COMMENT ON COLUMN questions.img_active IS 'Indica si la pregunta tiene imagen asociada';
COMMENT ON COLUMN questions.leng_math_pregunta IS 'Indica si la pregunta usa lenguaje matemático (LaTeX)';
COMMENT ON COLUMN questions.leng_math_opciones IS 'Indica si las opciones usan lenguaje matemático (LaTeX)';

-- Crear índice para búsquedas por preguntas con imágenes
CREATE INDEX IF NOT EXISTS idx_questions_img_active ON questions(img_active) WHERE img_active = TRUE;

-- Crear índice compuesto para preguntas con LaTeX
CREATE INDEX IF NOT EXISTS idx_questions_latex ON questions(leng_math_pregunta, leng_math_opciones) 
WHERE leng_math_pregunta = TRUE OR leng_math_opciones = TRUE;
