-- =========================================
-- SISTEMA DE APRENDIZAJE INMERSIVO - GUÍA IPN
-- Base de datos optimizada para Supabase
-- =========================================

-- Limpiar tablas existentes (solo para desarrollo)
-- DROP SCHEMA public CASCADE;
-- CREATE SCHEMA public;

-- =========================================
-- 1. CONFIGURACIÓN INICIAL
-- =========================================

-- Habilitar extensiones necesarias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- Para búsquedas de texto
CREATE EXTENSION IF NOT EXISTS "unaccent"; -- Para normalizar texto

-- =========================================
-- 2. TABLAS CORE DEL SISTEMA
-- =========================================

-- Perfiles de usuario (extiende auth.users de Supabase)
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    
    -- Plan y créditos
    plan_type TEXT DEFAULT 'free' CHECK (plan_type IN ('free', 'basic', 'premium', 'pro')),
    credits_remaining INTEGER DEFAULT 10,
    credits_total INTEGER DEFAULT 10,
    daily_limit INTEGER DEFAULT 5,
    daily_used INTEGER DEFAULT 0,
    last_reset_date DATE DEFAULT CURRENT_DATE,
    
    -- Configuración
    preferred_language TEXT DEFAULT 'es',
    learning_level TEXT DEFAULT 'medium',
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Banco de preguntas del examen
CREATE TABLE questions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Identificación
    code TEXT UNIQUE NOT NULL, -- ej: "2024Algebra14"
    subject TEXT NOT NULL, -- algebra, calculo, fisica, etc
    topic TEXT,
    difficulty TEXT DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    
    -- Contenido
    question TEXT NOT NULL,
    options JSONB NOT NULL, -- {a: "...", b: "...", c: "...", d: "..."}
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    
    -- Configuración LaTeX
    use_latex BOOLEAN DEFAULT FALSE,
    
    -- Estadísticas
    times_seen INTEGER DEFAULT 0,
    times_correct INTEGER DEFAULT 0,
    exam_probability NUMERIC(3,2) DEFAULT 0.50, -- 0.00 a 1.00
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Respuestas IA precalculadas (para preguntas adicionales/follow-up)
CREATE TABLE ai_answers (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    question_hash TEXT UNIQUE NOT NULL, -- SHA256 de la pregunta normalizada
    question_text TEXT NOT NULL,
    
    -- Relación opcional con pregunta de examen
    related_question_id UUID REFERENCES questions(id), -- NULL si es pregunta libre
    
    -- Respuesta estructurada
    answer_steps JSONB NOT NULL, -- Array de pasos de explicación COMPLETA (3-5 pasos)
    total_duration INTEGER DEFAULT 60, -- segundos estimados
    
    -- Estadísticas
    usage_count INTEGER DEFAULT 0,
    helpful_votes INTEGER DEFAULT 0,
    total_votes INTEGER DEFAULT 0,
    
    -- Metadata
    generated_by TEXT DEFAULT 'manual', -- manual, gpt-3.5, gpt-4
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ⭐ NUEVA TABLA: Explicaciones especializadas para preguntas de examen
CREATE TABLE exam_question_explanations (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    question_id UUID REFERENCES questions(id) ON DELETE CASCADE,
    
    -- Contenido de la explicación
    explanation_steps JSONB NOT NULL, -- Array de pasos estructurados
    total_duration INTEGER DEFAULT 60, -- segundos estimados
    
    -- Calidad y validación
    quality_score NUMERIC(3,2) DEFAULT 0.00, -- 0.00 a 1.00 (calculado automáticamente)
    is_verified BOOLEAN DEFAULT FALSE, -- Verificada por humano
    is_flagged BOOLEAN DEFAULT FALSE, -- Marcada con error por usuarios
    flag_reason TEXT, -- Razón del flag si existe
    
    -- Estadísticas de uso
    usage_count INTEGER DEFAULT 0,
    helpful_votes INTEGER DEFAULT 0, -- Votos "fue útil"
    unhelpful_votes INTEGER DEFAULT 0, -- Votos "no fue útil"
    total_votes INTEGER DEFAULT 0,
    
    -- Metadata de generación
    generated_by TEXT DEFAULT 'ai', -- ai, manual, reviewed
    ai_model TEXT, -- gpt-4, gpt-3.5-turbo, etc
    prompt_version TEXT, -- Para tracking de versiones de prompts (ej: "v1.0")
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES auth.users(id),
    
    -- Constraint: Una explicación por pregunta
    UNIQUE(question_id)
);

-- Historial de interacciones
CREATE TABLE interactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT,
    
    -- Pregunta y respuesta
    question_text TEXT NOT NULL,
    question_type TEXT DEFAULT 'text', -- text, voice, exam
    answer_id UUID REFERENCES ai_answers(id), -- Para preguntas libres
    question_id UUID REFERENCES questions(id), -- Para preguntas de examen
    explanation_id UUID REFERENCES exam_question_explanations(id), -- Para explicaciones de examen
    
    -- Métricas
    response_time_ms INTEGER,
    credits_used INTEGER DEFAULT 1,
    completed BOOLEAN DEFAULT TRUE,
    
    -- Feedback
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    understood BOOLEAN,
    seen_in_exam BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sesiones de estudio
CREATE TABLE study_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Información de sesión
    session_type TEXT DEFAULT 'practice', -- practice, exam, review
    status TEXT DEFAULT 'active', -- active, completed, abandoned
    
    -- Estadísticas
    questions_asked INTEGER DEFAULT 0,
    questions_answered INTEGER DEFAULT 0,
    correct_answers INTEGER DEFAULT 0,
    total_duration_seconds INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Progreso del usuario
CREATE TABLE user_progress (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    subject TEXT NOT NULL,
    
    -- Métricas
    total_practiced INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    mastery_level NUMERIC(3,2) DEFAULT 0.00, -- 0.00 a 1.00
    streak_days INTEGER DEFAULT 0,
    
    -- Timestamps
    last_practice_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, subject)
);

-- Uso de créditos
CREATE TABLE credit_usage (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Detalle del uso
    action_type TEXT NOT NULL, -- ai_question, voice, premium_feature
    credits_used INTEGER NOT NULL,
    credits_before INTEGER NOT NULL,
    credits_after INTEGER NOT NULL,
    
    -- Contexto
    interaction_id UUID REFERENCES interactions(id),
    details JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Planes de suscripción
CREATE TABLE subscription_plans (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    
    -- Límites
    monthly_credits INTEGER NOT NULL,
    daily_limit INTEGER NOT NULL,
    
    -- Features
    features JSONB DEFAULT '{}'::jsonb,
    
    -- Precio
    price_monthly NUMERIC(10,2) DEFAULT 0,
    price_yearly NUMERIC(10,2) DEFAULT 0,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Suscripciones de usuarios
CREATE TABLE user_subscriptions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES subscription_plans(id),
    
    -- Estado
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired', 'trial')),
    
    -- Fechas
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ends_at TIMESTAMPTZ,
    
    -- Pago
    stripe_subscription_id TEXT
);

-- Biblioteca de comandos de canvas (para visualizaciones)
CREATE TABLE canvas_library (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    
    -- Comandos
    commands JSONB NOT NULL,
    
    -- Metadata
    tags TEXT[] DEFAULT '{}',
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =========================================
-- 3. ÍNDICES PARA OPTIMIZACIÓN
-- =========================================

-- Índices principales
CREATE INDEX idx_profiles_user ON profiles(id);
CREATE INDEX idx_questions_subject ON questions(subject, difficulty);
CREATE INDEX idx_questions_code ON questions(code);
CREATE INDEX idx_ai_answers_hash ON ai_answers(question_hash);
CREATE INDEX idx_ai_answers_related_question ON ai_answers(related_question_id);
CREATE INDEX idx_interactions_user ON interactions(user_id, created_at DESC);
CREATE INDEX idx_interactions_session ON interactions(session_id);
CREATE INDEX idx_interactions_explanation ON interactions(explanation_id);
CREATE INDEX idx_study_sessions_user ON study_sessions(user_id, started_at DESC);
CREATE INDEX idx_user_progress_user ON user_progress(user_id, subject);
CREATE INDEX idx_credit_usage_user ON credit_usage(user_id, created_at DESC);

-- Índices para exam_question_explanations
CREATE INDEX idx_exam_explanations_question ON exam_question_explanations(question_id);
CREATE INDEX idx_exam_explanations_quality ON exam_question_explanations(quality_score DESC);
CREATE INDEX idx_exam_explanations_verified ON exam_question_explanations(is_verified) WHERE is_verified = true;
CREATE INDEX idx_exam_explanations_flagged ON exam_question_explanations(is_flagged) WHERE is_flagged = true;
CREATE INDEX idx_exam_explanations_usage ON exam_question_explanations(usage_count DESC);

-- Índices para búsqueda de texto
CREATE INDEX idx_questions_search ON questions USING gin(to_tsvector('spanish', question));
CREATE INDEX idx_ai_answers_search ON ai_answers USING gin(to_tsvector('spanish', question_text));

-- Índice único parcial para garantizar solo una suscripción activa por usuario
CREATE UNIQUE INDEX idx_user_subscriptions_active_unique ON user_subscriptions(user_id) WHERE status = 'active';

-- =========================================
-- 4. FUNCIONES AUXILIARES
-- =========================================

-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Función para normalizar texto (para generar hashes consistentes)
CREATE OR REPLACE FUNCTION normalize_text(input_text TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(
        REGEXP_REPLACE(
            REGEXP_REPLACE(
                UNACCENT(TRIM(input_text)),
                '[^\w\s]', '', 'g'
            ),
            '\s+', ' ', 'g'
        )
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Función para generar hash de pregunta
CREATE OR REPLACE FUNCTION generate_question_hash(question TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN encode(digest(normalize_text(question), 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Función para verificar créditos
CREATE OR REPLACE FUNCTION check_credits(p_user_id UUID, p_credits_needed INTEGER)
RETURNS BOOLEAN AS $$
DECLARE
    v_credits INTEGER;
    v_daily_used INTEGER;
    v_daily_limit INTEGER;
    v_last_reset DATE;
BEGIN
    SELECT 
        credits_remaining,
        daily_used,
        daily_limit,
        last_reset_date
    INTO 
        v_credits,
        v_daily_used,
        v_daily_limit,
        v_last_reset
    FROM profiles
    WHERE id = p_user_id;
    
    -- Reset diario si es necesario
    IF v_last_reset < CURRENT_DATE THEN
        UPDATE profiles 
        SET daily_used = 0, last_reset_date = CURRENT_DATE
        WHERE id = p_user_id;
        v_daily_used := 0;
    END IF;
    
    -- Verificar créditos y límite diario
    RETURN v_credits >= p_credits_needed AND v_daily_used < v_daily_limit;
END;
$$ LANGUAGE plpgsql;

-- Función para consumir créditos
CREATE OR REPLACE FUNCTION consume_credits(
    p_user_id UUID, 
    p_credits INTEGER,
    p_action_type TEXT,
    p_interaction_id UUID DEFAULT NULL
)
RETURNS BOOLEAN AS $$
DECLARE
    v_credits_before INTEGER;
    v_credits_after INTEGER;
BEGIN
    -- Obtener créditos actuales
    SELECT credits_remaining INTO v_credits_before
    FROM profiles WHERE id = p_user_id;
    
    -- Verificar disponibilidad
    IF v_credits_before < p_credits THEN
        RETURN FALSE;
    END IF;
    
    -- Actualizar créditos
    UPDATE profiles 
    SET 
        credits_remaining = credits_remaining - p_credits,
        daily_used = daily_used + 1
    WHERE id = p_user_id
    RETURNING credits_remaining INTO v_credits_after;
    
    -- Registrar uso
    INSERT INTO credit_usage (
        user_id, 
        action_type, 
        credits_used, 
        credits_before, 
        credits_after,
        interaction_id
    ) VALUES (
        p_user_id, 
        p_action_type, 
        p_credits, 
        v_credits_before, 
        v_credits_after,
        p_interaction_id
    );
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Función para resetear créditos mensuales
CREATE OR REPLACE FUNCTION reset_monthly_credits()
RETURNS void AS $$
BEGIN
    UPDATE profiles p
    SET 
        credits_remaining = COALESCE(
            (SELECT monthly_credits FROM subscription_plans sp 
             JOIN user_subscriptions us ON us.plan_id = sp.id 
             WHERE us.user_id = p.id AND us.status = 'active'),
            10 -- créditos por defecto para plan free
        ),
        daily_used = 0,
        last_reset_date = CURRENT_DATE;
END;
$$ LANGUAGE plpgsql;

-- =========================================
-- 5. TRIGGERS
-- =========================================

-- Triggers para updated_at
CREATE TRIGGER trigger_profiles_updated_at 
    BEFORE UPDATE ON profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_questions_updated_at 
    BEFORE UPDATE ON questions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_ai_answers_updated_at 
    BEFORE UPDATE ON ai_answers 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_user_progress_updated_at 
    BEFORE UPDATE ON user_progress 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trigger_exam_explanations_updated_at 
    BEFORE UPDATE ON exam_question_explanations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- =========================================
-- 6. ROW LEVEL SECURITY (RLS)
-- =========================================

-- Habilitar RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE exam_question_explanations ENABLE ROW LEVEL SECURITY;

-- Políticas para profiles
CREATE POLICY "Users can view own profile" 
    ON profiles FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" 
    ON profiles FOR UPDATE 
    USING (auth.uid() = id);

-- Políticas para interactions
CREATE POLICY "Users can view own interactions" 
    ON interactions FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own interactions" 
    ON interactions FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own interactions" 
    ON interactions FOR UPDATE 
    USING (auth.uid() = user_id);

-- Políticas para study_sessions
CREATE POLICY "Users can manage own sessions" 
    ON study_sessions FOR ALL 
    USING (auth.uid() = user_id);

-- Políticas para user_progress
CREATE POLICY "Users can manage own progress" 
    ON user_progress FOR ALL 
    USING (auth.uid() = user_id);

-- Políticas para credit_usage
CREATE POLICY "Users can view own credit usage" 
    ON credit_usage FOR SELECT 
    USING (auth.uid() = user_id);

-- Políticas para user_subscriptions
CREATE POLICY "Users can view own subscription" 
    ON user_subscriptions FOR SELECT 
    USING (auth.uid() = user_id);

-- Políticas para exam_question_explanations
CREATE POLICY "Anyone can view explanations" 
    ON exam_question_explanations FOR SELECT 
    USING (true);

CREATE POLICY "Service role can manage explanations" 
    ON exam_question_explanations FOR ALL 
    USING (auth.role() = 'service_role');

-- Las tablas públicas no necesitan RLS
-- questions, ai_answers, canvas_library son públicas

-- =========================================
-- 7. VISTAS ÚTILES
-- =========================================

-- Vista de estadísticas de usuario
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    p.id as user_id,
    p.email,
    p.plan_type,
    p.credits_remaining,
    p.daily_used,
    p.daily_limit,
    COUNT(DISTINCT i.id) as total_interactions,
    COUNT(DISTINCT ss.id) as total_sessions,
    AVG(i.rating) as avg_rating
FROM profiles p
LEFT JOIN interactions i ON p.id = i.user_id
LEFT JOIN study_sessions ss ON p.id = ss.user_id
GROUP BY p.id;

-- Vista de preguntas populares
CREATE OR REPLACE VIEW popular_questions AS
SELECT 
    q.*,
    CASE 
        WHEN q.times_seen > 0 
        THEN ROUND((q.times_correct::numeric / q.times_seen) * 100, 2)
        ELSE 0 
    END as success_rate
FROM questions q
ORDER BY q.times_seen DESC, q.exam_probability DESC;

-- =========================================
-- 8. DATOS INICIALES
-- =========================================

-- Insertar planes de suscripción
INSERT INTO subscription_plans (name, monthly_credits, daily_limit, features, price_monthly, price_yearly) VALUES
('free', 10, 5, '{"basic_explanations": true}'::jsonb, 0, 0),
('basic', 50, 15, '{"basic_explanations": true, "voice": true}'::jsonb, 99, 990),
('premium', 200, 50, '{"premium_explanations": true, "voice": true, "canvas": true}'::jsonb, 199, 1990),
('pro', 1000, 999, '{"all_features": true}'::jsonb, 499, 4990);

-- Insertar pregunta de ejemplo
INSERT INTO questions (code, subject, topic, difficulty, question, options, correct_answer, use_latex, exam_probability) VALUES
(
    '2024Algebra14',
    'algebra',
    'simplificación',
    'hard',
    '\text{Simplificar la expresión algebraica: }\sqrt{\frac{z}{12r^3}(2r-2rs)^2}\times\sqrt[3]{\frac{27r^9s^{12}}{z^{-15}}}',
    '{
        "a": "\\frac{s}{r}(1-s)z^2",
        "b": "rs^2(1-s)^2z^3", 
        "c": "rs^2(1-s)z^3",
        "d": "\\frac{s^2}{r}(1-s)^2z^3"
    }'::jsonb,
    'c',
    true,
    0.75
);

-- Insertar comandos de canvas de ejemplo
INSERT INTO canvas_library (name, category, commands, tags) VALUES
(
    'Gráfica Parábola',
    'graph',
    '[
        {"type": "axis", "x": 50, "y": 200, "width": 300, "height": 300},
        {"type": "parabola", "a": 1, "b": 0, "c": 0, "color": "#3498db"}
    ]'::jsonb,
    ARRAY['parabola', 'función']
),
(
    'Triángulo con ángulos',
    'geometry',
    '[
        {"type": "triangle", "points": [[100, 100], [200, 100], [150, 50]]},
        {"type": "angles", "show": true, "labels": ["α", "β", "γ"]}
    ]'::jsonb,
    ARRAY['triángulo', 'geometría']
);

-- =========================================
-- 9. FUNCIONES DE API PÚBLICA
-- =========================================

-- Función para obtener una pregunta con sus estadísticas
CREATE OR REPLACE FUNCTION get_question_with_stats(p_question_id UUID)
RETURNS TABLE (
    question JSON,
    stats JSON
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        row_to_json(q.*) as question,
        json_build_object(
            'times_seen', q.times_seen,
            'success_rate', 
            CASE 
                WHEN q.times_seen > 0 
                THEN ROUND((q.times_correct::numeric / q.times_seen) * 100, 2)
                ELSE 0 
            END,
            'exam_probability', q.exam_probability
        ) as stats
    FROM questions q
    WHERE q.id = p_question_id;
END;
$$ LANGUAGE plpgsql;

-- Función para procesar una pregunta
CREATE OR REPLACE FUNCTION process_question(
    p_user_id UUID,
    p_question_text TEXT,
    p_question_type TEXT DEFAULT 'text'
)
RETURNS TABLE (
    success BOOLEAN,
    answer_id UUID,
    credits_used INTEGER,
    message TEXT
) AS $$
DECLARE
    v_hash TEXT;
    v_answer_id UUID;
    v_credits_needed INTEGER := 1;
BEGIN
    -- Verificar créditos
    IF NOT check_credits(p_user_id, v_credits_needed) THEN
        RETURN QUERY SELECT 
            FALSE, 
            NULL::UUID, 
            0, 
            'Créditos insuficientes o límite diario alcanzado'::TEXT;
        RETURN;
    END IF;
    
    -- Generar hash de la pregunta
    v_hash := generate_question_hash(p_question_text);
    
    -- Buscar respuesta existente
    SELECT id INTO v_answer_id 
    FROM ai_answers 
    WHERE question_hash = v_hash;
    
    -- Si no existe, se deberá generar con IA (manejado en backend)
    IF v_answer_id IS NULL THEN
        v_credits_needed := 2; -- Más créditos para generar con IA
    END IF;
    
    -- Consumir créditos
    IF consume_credits(p_user_id, v_credits_needed, p_question_type) THEN
        RETURN QUERY SELECT 
            TRUE, 
            v_answer_id, 
            v_credits_needed, 
            'Procesado exitosamente'::TEXT;
    ELSE
        RETURN QUERY SELECT 
            FALSE, 
            NULL::UUID, 
            0, 
            'Error al consumir créditos'::TEXT;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- =========================================
-- 10. COMENTARIOS Y DOCUMENTACIÓN
-- =========================================

COMMENT ON TABLE profiles IS 'Perfiles de usuario con información de créditos y suscripción';
COMMENT ON TABLE questions IS 'Banco de preguntas del examen IPN/UNAM';
COMMENT ON TABLE ai_answers IS 'Respuestas pre-generadas o cacheadas de IA para preguntas libres y follow-ups';
COMMENT ON TABLE exam_question_explanations IS 'Explicaciones especializadas para preguntas de examen con métricas de calidad';
COMMENT ON TABLE interactions IS 'Historial completo de interacciones usuario-sistema';
COMMENT ON TABLE study_sessions IS 'Sesiones de estudio con métricas';
COMMENT ON TABLE user_progress IS 'Progreso del usuario por materia';
COMMENT ON TABLE credit_usage IS 'Log detallado de uso de créditos';
COMMENT ON TABLE subscription_plans IS 'Planes disponibles de suscripción';
COMMENT ON TABLE canvas_library IS 'Biblioteca de visualizaciones para el canvas';

COMMENT ON FUNCTION check_credits IS 'Verifica si el usuario tiene créditos suficientes';
COMMENT ON FUNCTION consume_credits IS 'Consume créditos y registra el uso';
COMMENT ON FUNCTION process_question IS 'Procesa una pregunta y gestiona créditos';

-- =========================================
-- FIN DEL ESQUEMA
-- =========================================

-- Verificar que todo se creó correctamente
DO $$
BEGIN
    RAISE NOTICE 'Esquema de base de datos creado exitosamente';
    RAISE NOTICE 'Tablas principales: profiles, questions, ai_answers, exam_question_explanations, interactions';
    RAISE NOTICE 'Sistema de créditos configurado';
    RAISE NOTICE 'Sistema de explicaciones de examen configurado';
    RAISE NOTICE 'RLS habilitado para protección de datos';
END $$;