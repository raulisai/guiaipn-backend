# 🎨 Guía de Implementación Frontend

## 📦 Instalación

```bash
npm install socket.io-client @supabase/supabase-js axios
```

## 🔐 Autenticación

```typescript
// src/lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

// Login con Google
export async function signInWithGoogle() {
  return await supabase.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: `${window.location.origin}/auth/callback` }
  });
}

// Obtener token
export async function getToken() {
  const { data: { session } } = await supabase.auth.getSession();
  return session?.access_token;
}
```

## 🌐 Cliente HTTP

```typescript
// src/services/api.ts
import axios from 'axios';
import { getToken } from '@/lib/supabase';

const api = axios.create({
  baseURL: 'http://localhost:5000/api/v1'
});

// Interceptor para token
api.interceptors.request.use(async (config) => {
  const token = await getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Métodos
export const apiClient = {
  initializeProfile: (token: string) => 
    api.post('/auth/initialize', { token }),
  
  getProfile: () => 
    api.get('/auth/profile'),
  
  getRandomQuestion: (subject: string, difficulty?: string) =>
    api.get('/questions/random', { params: { subject, difficulty } }),
  
  submitAnswer: (questionId: string, answer: string) =>
    api.post(`/questions/${questionId}/answer`, { user_answer: answer })
};
```

## 🔌 Cliente Socket.IO

```typescript
// src/services/socket.ts
import { io, Socket } from 'socket.io-client';
import { getToken } from '@/lib/supabase';

class SocketService {
  private socket: Socket | null = null;
  
  async connect() {
    const token = await getToken();
    
    this.socket = io('http://localhost:5000', {
      auth: { token },
      transports: ['websocket']
    });
    
    this.setupListeners();
  }
  
  private setupListeners() {
    this.socket?.on('connection_established', (data) => {
      console.log('Sesión:', data.session_id);
    });
    
    this.socket?.on('error', (error) => {
      console.error('Error:', error);
    });
  }
  
  async askQuestion(question: string, context = {}) {
    const token = await getToken();
    this.socket?.emit('ask_question', { token, question, context });
  }
  
  pauseExplanation() {
    this.socket?.emit('pause_explanation', { token: getToken() });
  }
  
  resumeExplanation() {
    this.socket?.emit('resume_explanation', { token: getToken() });
  }
  
  disconnect() {
    this.socket?.disconnect();
  }
}

export const socketService = new SocketService();
```

## 🎯 Hook de Explicación

```typescript
// src/hooks/useExplanation.ts
import { useState, useEffect } from 'react';
import { socketService } from '@/services/socket';

export function useExplanation() {
  const [steps, setSteps] = useState<any[]>([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  
  useEffect(() => {
    socketService.connect();
    
    // Listeners
    const socket = socketService['socket'];
    
    socket?.on('explanation_start', (data) => {
      setSteps(new Array(data.total_steps).fill(null));
      setIsStreaming(true);
    });
    
    socket?.on('step_start', (data) => {
      setCurrentStep(data.step);
    });
    
    socket?.on('content_chunk', (data) => {
      setSteps(prev => {
        const newSteps = [...prev];
        if (!newSteps[data.step]) newSteps[data.step] = '';
        newSteps[data.step] += data.chunk;
        return newSteps;
      });
    });
    
    socket?.on('explanation_complete', () => {
      setIsStreaming(false);
    });
    
    return () => socketService.disconnect();
  }, []);
  
  return {
    steps,
    currentStep,
    isStreaming,
    askQuestion: socketService.askQuestion.bind(socketService),
    pause: socketService.pauseExplanation.bind(socketService),
    resume: socketService.resumeExplanation.bind(socketService)
  };
}
```

## 🎨 Componente de Explicación

```typescript
// src/components/Explanation.tsx
import { useExplanation } from '@/hooks/useExplanation';

export function Explanation() {
  const { steps, currentStep, isStreaming, askQuestion, pause, resume } = useExplanation();
  
  return (
    <div>
      <input 
        type="text" 
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            askQuestion(e.currentTarget.value);
          }
        }}
      />
      
      {isStreaming && (
        <button onClick={pause}>Pausar</button>
      )}
      
      <div>
        {steps.map((content, index) => (
          <div key={index} className={index === currentStep ? 'active' : ''}>
            <h3>Paso {index + 1}</h3>
            <p>{content}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 🔄 Flujo Completo

```typescript
// 1. Login
await signInWithGoogle();

// 2. Callback
const token = await getToken();
await apiClient.initializeProfile(token);

// 3. Conectar Socket
await socketService.connect();

// 4. Hacer pregunta
socketService.askQuestion('¿Qué es la energía cinética?', {
  subject: 'fisica'
});

// 5. Recibir eventos
socket.on('explanation_start', (data) => { /* ... */ });
socket.on('step_start', (data) => { /* ... */ });
socket.on('content_chunk', (data) => { /* ... */ });
socket.on('explanation_complete', (data) => { /* ... */ });
```

## 📝 Variables de Entorno

```env
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGc...
VITE_BACKEND_URL=http://localhost:5000
```

## 🚨 Manejo de Errores

```typescript
socket.on('error', (error) => {
  switch(error.code) {
    case 'AUTH_FAILED':
      // Renovar token y reconectar
      break;
    case 'VALIDATION_ERROR':
      // Mostrar mensaje al usuario
      break;
    default:
      console.error(error);
  }
});
```
