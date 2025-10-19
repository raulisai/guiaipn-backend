-- =========================================
-- Ejemplos de inserción de preguntas con nuevos campos
-- =========================================

-- Ejemplo 1: Pregunta simple sin LaTeX ni imagen
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones
) VALUES (
    '2024HIS01',
    'historia',
    'independencia',
    'easy',
    '¿En qué año inició la Independencia de México?',
    '{"a": "1808", "b": "1810", "c": "1821", "d": "1824"}'::jsonb,
    'b',
    FALSE,  -- Sin imagen
    FALSE,  -- Sin LaTeX en pregunta
    FALSE   -- Sin LaTeX en opciones
);

-- Ejemplo 2: Pregunta con LaTeX en pregunta y opciones
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024MAT01',
    'matematicas',
    'algebra',
    'medium',
    'Resuelve la ecuación: $2x + 4 = 10$',
    '{"a": "$x = 2$", "b": "$x = 3$", "c": "$x = 4$", "d": "$x = 5$"}'::jsonb,
    'b',
    FALSE,  -- Sin imagen
    TRUE,   -- Pregunta usa LaTeX
    TRUE,   -- Opciones usan LaTeX
    TRUE    -- Mantener compatibilidad con use_latex
);

-- Ejemplo 3: Pregunta con imagen (geometría)
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones
) VALUES (
    '2024GEO01',
    'matematicas',
    'geometria',
    'hard',
    'Observa el triángulo en la imagen. ¿Cuál es el valor del ángulo x?',
    '{"a": "30°", "b": "45°", "c": "60°", "d": "90°"}'::jsonb,
    'c',
    TRUE,   -- Tiene imagen asociada
    FALSE,  -- Pregunta no usa LaTeX
    FALSE   -- Opciones no usan LaTeX
);

-- Ejemplo 4: Pregunta con imagen Y LaTeX
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024FIS01',
    'fisica',
    'cinematica',
    'hard',
    'Observa el diagrama de fuerzas. Calcula la aceleración: $F = ma$',
    '{"a": "$2 m/s^2$", "b": "$4 m/s^2$", "c": "$6 m/s^2$", "d": "$8 m/s^2$"}'::jsonb,
    'b',
    TRUE,   -- Tiene imagen (diagrama)
    TRUE,   -- Pregunta usa LaTeX
    TRUE,   -- Opciones usan LaTeX
    TRUE    -- Mantener compatibilidad
);

-- =========================================
-- Query para verificar las preguntas insertadas
-- =========================================

-- =========================================
-- Preguntas de Álgebra 2024
-- =========================================

-- 2024Algebra11
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra11',
    'matematicas',
    'algebra',
    'medium',
    '\text{Simplificar la expresión: } 2 - \frac{2}{1 - \frac{2}{2 - \frac{2}{x^2}}}',
    '{"a": "2x", "b": "2x^2", "c": "2x^3", "d": "2x^4"}'::jsonb,
    'b',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra14
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra14',
    'matematicas',
    'algebra',
    'hard',
    '\text{Simplificar la expresión algebraica: }\sqrt{\frac{z}{12r^3}(2r-2rs)^2}\times\sqrt[3]{\frac{27r^9s^{12}}{z^{-15}}}',
    '{"a": "\\frac{s}{r}(1-s)z^2", "b": "rs^2(1-s)^2z^3", "c": "rs^2(1-s)z^3", "d": "\\frac{s^2}{r}(1-s)^2z^3"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra12
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra12',
    'matematicas',
    'algebra',
    'medium',
    '\text{Simplificar la expresión: } \frac{2\sqrt{x^{-2}y^{-8}}}{\sqrt{16x^{-4}y^{-14}}}',
    '{"a": "\\frac{1}{4}\\sqrt{xy^3}", "b": "\\frac{1}{2\\sqrt{xy^3}}", "c": "\\frac{1}{4}x^2y^3", "d": "-xy"}'::jsonb,
    'd',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra17
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones
) VALUES (
    '2024Algebra17',
    'matematicas',
    'algebra',
    'easy',
    'Relacionar cada producto notable con la expresión matemática que le corresponde:',
    '{"a": "1D, 2C, 3B, 4A", "b": "1D, 2A, 3B, 4C", "c": "1B, 2A, 3D, 4C", "d": "1B, 2C, 3D, 4A"}'::jsonb,
    'b',
    FALSE,
    FALSE,
    FALSE
);

-- 2024Algebra15
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra15',
    'matematicas',
    'algebra',
    'medium',
    '\text{Completar el binomio: } (3n-2s)^3 = 27n^3 + (\_\_) + 36ns^2 + (\_\_)',
    '{"a": "-27n^2s, -4s^2", "b": "-54n^2s, -8s^3", "c": "54n^2s, 8s^3", "d": "27n^2s, 4s^2"}'::jsonb,
    'b',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra20
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra20',
    'matematicas',
    'algebra',
    'medium',
    '\text{La expresión } \frac{x^2-4}{x-2}\cdot\frac{x+3}{x^2+4x+4}\cdot\frac{4x+8}{3x+9} \text{ es equivalente a:}',
    '{"a": "\\frac{5}{3}", "b": "\\frac{4}{5}", "c": "\\frac{4}{3}", "d": "\\frac{3}{4}"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra18
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra18',
    'matematicas',
    'algebra',
    'hard',
    '\text{Reducir la expresión } \frac{\sqrt{x^2-9}}{\frac{1}{\sqrt{(x-2\sqrt{3})(x+2\sqrt{3})}+3}}',
    '{"a": "x^2+9", "b": "x^2-9", "c": "\\frac{\\sqrt{x^2-9}}{x-2\\sqrt{3}}", "d": "\\left(x+2\\sqrt{3}\\right)\\sqrt{x^2-9}"}'::jsonb,
    'b',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra16
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra16',
    'matematicas',
    'algebra',
    'medium',
    '\text{Completar el producto: } (2\sqrt{3}- \_\_\_) \ (2\sqrt{3}+ \_\_ )=12-2x',
    '{"a": "2x\\sqrt{\\frac{x}{3}}\\sqrt{3x}", "b": "\\sqrt{3x},\\sqrt{3x}", "c": "\\sqrt{2x},\\sqrt{2x}", "d": "2\\sqrt{x},\\sqrt{x}"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra19
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra19',
    'matematicas',
    'algebra',
    'medium',
    '\text{Simplificar la expresión: } \frac{x-5+\frac{24}{x+5}}{x+1}',
    '{"a": "\\frac{x-1}{x+5}", "b": "\\frac{x-5}{x+1}", "c": "\\frac{x+1}{x-5}", "d": "\\frac{x+5}{x-1}"}'::jsonb,
    'a',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra23
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra23',
    'matematicas',
    'algebra',
    'hard',
    '\text{Completar la factorización: } \ 9x^4-3x^3z+x^2z^2-9x^2z^2+3xz^3-z^4=(9x^2+(\_\_\_)+z^2)(\_\_\_) -z^2)',
    '{"a": "-3xz, 2x^2", "b": "-3xz, x^2", "c": "3xz, 2x", "d": "3x^2z, x"}'::jsonb,
    'b',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra21
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra21',
    'matematicas',
    'algebra',
    'medium',
    '\text{Simplificar la expresion : } \frac{\left(\frac{3}{x-3}+\frac{x}{x+3}\right)}{\frac{1}{x^2-9}}',
    '{"a": "x^2-3", "b": "x^2+9", "c": "x^2+3", "d": "x^2-9"}'::jsonb,
    'b',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra22
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra22',
    'matematicas',
    'algebra',
    'medium',
    '\text{Factoriza la expresión: } \ x^3z-x^2y^2-2x^2yz+2xy^3',
    '{"a": "x(2y-x)(y^2-xz)", "b": "x(y-2x)(y^2+xz)", "c": "x(y-x)(y^2+xz)", "d": "x(2y+x)(y^2-xz)"}'::jsonb,
    'a',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra24
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra24',
    'matematicas',
    'algebra',
    'easy',
    '\text{Factorizar el polinomio: } y^3-27',
    '{"a": "(y+3)(y^2+3y+9)", "b": "(y-3)(y^2+3y+9)", "c": "(y-3)(y^2-3y-9)", "d": "(y+3)(y^2-3y+9)"}'::jsonb,
    'b',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra26
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra26',
    'matematicas',
    'algebra',
    'medium',
    '\text{Realizar la operación: } \text {f(x)-alpha g(x)+h(x)}\quad\text{Si }\alpha=2,\quad f(x)=2y^2-2xy-2x^2\quad g(x)=y^2+4xy+3x^2\quad h(x)=3x^2+2xy',
    '{"a": "5x^2-4xy", "b": "-5x^2-8xy", "c": "x^2+y^2-4x", "d": "x^2-2x-4"}'::jsonb,
    'b',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra27
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra27',
    'matematicas',
    'algebra',
    'hard',
    '\text{Una señal es descrita por la funcion: } \text{H}_n(x)=\frac{(-1)^{n+2}}{\sqrt{(x-1)^{2n+5}+1}}\cos((2n+1)\pi x)\quad\text{Calcular los valores } H_0(0) \text{ y } H_2(1)',
    '{"a": "H_0(0)=0,\\; H_2(1)=1", "b": "H_0(0)=0,\\; H_2(1)=-1", "c": "H_0(0)=\\frac{1}{\\sqrt{2}},\\; H_2(1)=-1", "d": "H_0(0)=-1,\\; H_2(1)=-\\frac{1}{\\sqrt{2}}"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra29
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra29',
    'matematicas',
    'algebra',
    'easy',
    '\text{Encontrar el valor de } s \text{ que satisface la igualdad: } \frac{3s+25}{4}=10+\frac{7}{8}s',
    '{"a": "15", "b": "30", "c": "-15", "d": "-30"}'::jsonb,
    'd',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra32
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones
) VALUES (
    '2024Algebra32',
    'matematicas',
    'algebra',
    'medium',
    '¿Cuál es la ganancia en mdp que obtiene el inversionista mayoritario?',
    '{"a": "32", "b": "25", "c": "17", "d": "9"}'::jsonb,
    'b',
    FALSE,
    FALSE,
    FALSE
);

-- 2024Algebra34
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra34',
    'matematicas',
    'algebra',
    'medium',
    '\text{Resolver el sistema de ecuaciones lineales: } 7x-\frac{1}{2}y=30\quad 2x+5y=12',
    '{"a": "x=7, y=4", "b": "x=\\frac{13}{3}, y=\\frac{2}{3}", "c": "x=7, y=-4", "d": "x=-\\frac{1}{3}, y=\\frac{2}{3}"}'::jsonb,
    'b',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra30
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra30',
    'matematicas',
    'algebra',
    'medium',
    '\text{La velocidad con la que se desplaza una larva está descrita por la ecuación: } v(t)=-\frac{1}{3}t^2+\alpha t+3 \quad \text{Calcular la constante } \alpha \text{ si su velocidad cuando } t=2 \text{ es } v(2)=\frac{2}{3}',
    '{"a": "-\\frac{1}{2}", "b": "1/2", "c": "-1", "d": "1"}'::jsonb,
    'a',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra33
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra33',
    'matematicas',
    'algebra',
    'medium',
    '\text{Resolver el sistema de ecuaciones lineales si se sabe que } \text {z=2: } \begin{align} -x+y+z=2 \\ x-3y-4z=5 \end{align}',
    '{"a": "x=\\frac{11}{2}, y=\\frac{11}{2}", "b": "x=\\frac{13}{2}, y=\\frac{13}{2}", "c": "x=-\\frac{11}{2}, y=-\\frac{11}{2}", "d": "x=-\\frac{13}{2}, y=-\\frac{13}{2}"}'::jsonb,
    'd',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra37
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra37',
    'matematicas',
    'algebra',
    'medium',
    '\text{Identificar el sistema de ecuaciones que corresponde al siguiente planteamiento: "En un edificio inteligente de dos niveles (N1, N2) se arma una red para 170 usuarios en total. La velocidad de transferencia es de 590 Gbps, mismos que se reparten en cada nivel como sigue: 3 Gbps para cada usuario del primer nivel N1 y 4 Gbps para cada usuario del nivel N2."}',
    '{"a": "\\begin{cases} N1+N2=590 \\\\ 3N1+4N2=170 \\end{cases}", "b": "\\begin{cases} N1+N2=170 \\\\ 4N1+3N2=590 \\end{cases}", "c": "\\begin{cases} N1+N2=170 \\\\ 3N1+4N2=590 \\end{cases}", "d": "\\begin{cases} N1+N2=590 \\\\ 4N1+3N2=170 \\end{cases}"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra36
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra36',
    'matematicas',
    'algebra',
    'medium',
    '\text{¿Cuántos ejemplares se pueden colocar en cada espacio (CI, BM y SA), respectivamente?}',
    '{"a": "420, 150 y 95", "b": "360, 120 y 95", "c": "360, 90 y 120", "d": "420, 105 y 120"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra38
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra38',
    'matematicas',
    'algebra',
    'medium',
    '\text{Indicar las soluciones de la ecuación: } \frac{x}{x-4}=6-\frac{x}{x+4}',
    '{"a": "3\\sqrt{2},\\;-3\\sqrt{2}", "b": "2\\sqrt{3},\\;-2\\sqrt{3}", "c": "2\\sqrt{6},\\;-2\\sqrt{6}", "d": "3\\sqrt{6},\\;-3\\sqrt{6}"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra40
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra40',
    'matematicas',
    'algebra',
    'medium',
    '\text{Resolver el sistema de ecuaciones: } x+y-1=0 \quad x^2-y^2-8=0',
    '{"a": "x=\\frac{7}{2}, y=-\\frac{5}{2}", "b": "x=-\\frac{9}{2}, y=\\frac{7}{2}", "c": "x=\\frac{9}{2}, y=-\\frac{7}{2}", "d": "x=-\\frac{7}{2}, y=\\frac{5}{2}"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra02
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra02',
    'matematicas',
    'algebra',
    'easy',
    '\text{¿Qué propiedad permite pasar del lado izquierdo al derecho de la igualdad en: } \newline \sqrt{18}+\sqrt{12}-\sqrt{\frac{8}{9}}-\sqrt{\frac{3}{4}}=\frac{7}{3}\sqrt{2}+\frac{3}{2}\sqrt{3}',
    '{"a": "Conmutativa para el producto", "b": "Inverso para la suma", "c": "Elemento neutro", "d": "Distributiva"}'::jsonb,
    'd',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra03
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones
) VALUES (
    '2024Algebra03',
    'matematicas',
    'algebra',
    'easy',
    'Relacionar cada conjunto con los números que le corresponden:',
    '{"a": "1B, 2D, 3A, 4C", "b": "1C, 2D, 3A, 4B", "c": "1C, 2A, 3D, 4B", "d": "1B, 2A, 3D, 4C"}'::jsonb,
    'b',
    FALSE,
    FALSE,
    FALSE
);

-- 2024Algebra04
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra04',
    'matematicas',
    'algebra',
    'medium',
    '\text{Elegir la opción que presenta el orden de los números reales de menor a mayor: } 3\sqrt{2},\;\frac{1}{\sqrt{2}},\;\sqrt{\frac{2}{3}},\;\frac{2}{3}\sqrt{3},\;\sqrt{2}',
    '{"a": "\\frac{1}{\\sqrt{2}},\\;\\frac{2}{3}\\sqrt[3]{2},\\;\\frac{2}{3}\\sqrt{3},\\;3\\sqrt{2}", "b": "\\frac{1}{\\sqrt{2}},\\;\\sqrt{2},\\;3\\sqrt{2},\\;\\frac{2}{3}\\sqrt{3},\\;\\sqrt[3]{2}", "c": "\\frac{2}{3}\\sqrt[3]{2},\\;3\\sqrt{2},\\;\\frac{2}{3}\\sqrt{3},\\;\\sqrt{2},\\;\\frac{1}{\\sqrt{2}}", "d": "\\frac{2}{3}\\sqrt[3]{2},\\;\\frac{2}{3}\\sqrt{3},\\;3\\sqrt{2},\\;\\sqrt{2},\\;\\frac{1}{\\sqrt{2}}"}'::jsonb,
    'a',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra05
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones,
    use_latex
) VALUES (
    '2024Algebra05',
    'matematicas',
    'algebra',
    'medium',
    '\text{Realizar la siguiente operación con números decimales: } \text{s= } \frac{1}{1-(0.\overline{3}+0.\overline{4})}',
    '{"a": "\\frac{9}{2}", "b": "\\frac{7}{2}", "c": "\\frac{2}{9}", "d": "\\frac{2}{7}"}'::jsonb,
    'c',
    FALSE,
    TRUE,
    TRUE,
    TRUE
);

-- 2024Algebra06
INSERT INTO questions (
    code, subject, topic, difficulty,
    question, options, correct_answer,
    img_active, leng_math_pregunta, leng_math_opciones
) VALUES (
    '2024Algebra06',
    'matematicas',
    'algebra',
    'medium',
    'La delegación dispone de 120 km de cable para electrificar las avenidas principales y las colonias aledañas en una razón 3:5. La parte de menor longitud se divide, a su vez, para iluminar parques y calles en una razón 2:3. ¿Cuál es la longitud de cable que se utiliza para electrificar las calles?',
    '{"a": "45,km", "b": "32,km", "c": "27,km", "d": "19,km"}'::jsonb,
    'c',
    FALSE,
    FALSE,
    FALSE
);

-- =========================================
-- Query para verificar las preguntas insertadas
-- =========================================

SELECT 
    code,
    subject,
    img_active,
    leng_math_pregunta,
    leng_math_opciones,
    CASE 
        WHEN img_active AND (leng_math_pregunta OR leng_math_opciones) THEN 'Imagen + LaTeX'
        WHEN img_active THEN 'Solo Imagen'
        WHEN leng_math_pregunta OR leng_math_opciones THEN 'Solo LaTeX'
        ELSE 'Texto simple'
    END as tipo_pregunta
FROM questions
WHERE code LIKE '2024Algebra%'
ORDER BY code;
