# 🎨 Frontend - Panel de Usuario

El frontend de Crypto Trading Analyzer proporciona una interfaz moderna e intuitiva que permite a los usuarios visualizar datos de mercado, configurar estrategias de trading y monitorear el rendimiento de sus inversiones en tiempo real.

## 📋 Rol y Responsabilidades

### 📊 Visualización de Datos
- **Dashboard principal** con métricas clave del mercado
- **Gráficos interactivos** de precios e indicadores técnicos
- **Tablas dinámicas** con datos de múltiples criptomonedas
- **Visualización en tiempo real** de señales de trading

### 👤 Interacción con el Usuario
- **Configuración de estrategias** de trading personalizables
- **Gestión de carteras** y seguimiento de posiciones
- **Panel de control de alertas** y notificaciones
- **Historial detallado** de operaciones y rendimiento

### 🔄 Integración con Backend
- **Consumo de API REST** para datos estáticos
- **Conexión WebSocket** para actualizaciones en tiempo real
- **Gestión de estado** eficiente con herramientas modernas
- **Cache inteligente** para optimizar la experiencia

### 📱 Experiencia de Usuario
- **Diseño responsive** adaptado a todos los dispositivos
- **Interfaz intuitiva** con navegación fluida
- **Temas personalizables** (modo claro/oscuro)
- **Accesibilidad** siguiendo estándares web

## 🛠️ Tecnologías y Dependencias

### Framework Principal
```json
"next": "^14.0.0",              // Framework React con SSR/SSG
"react": "^18.2.0",             // Biblioteca de UI declarativa
"react-dom": "^18.2.0"          // Renderizado de React
```

### Lenguaje y Tipado
```json
"typescript": "^5.2.0",         // Tipado estático para JavaScript
"@types/react": "^18.2.0",      // Tipos para React
"@types/node": "^20.0.0"        // Tipos para Node.js
```

### Estilos y UI
```json
"tailwindcss": "^3.3.0",        // Framework CSS utilitario
"@headlessui/react": "^1.7.0",  // Componentes accesibles sin estilos
"@heroicons/react": "^2.0.0",   // Iconos de alta calidad
"framer-motion": "^10.16.0"     // Animaciones fluidas
```

### Gráficos y Visualización
```json
"recharts": "^2.8.0",           // Biblioteca de gráficos para React
"chart.js": "^4.4.0",           // Gráficos interactivos
"react-chartjs-2": "^5.2.0",    // Wrapper de Chart.js para React
"d3": "^7.8.0"                  // Manipulación de datos y visualización
```

### Gestión de Estado
```json
"zustand": "^4.4.0",            // Gestión de estado simple y poderosa
"@tanstack/react-query": "^4.35.0"  // Cache y sincronización de datos
```

### Comunicación en Tiempo Real
```json
"socket.io-client": "^4.7.0",   // Cliente WebSocket
"axios": "^1.5.0"               // Cliente HTTP para APIs
```

## ⚙️ Configuración del Entorno

### 1. Requisitos del Sistema
- **Node.js 18 o superior**
- **npm** o **yarn** (gestores de paquetes)
- **Git** (control de versiones)

### 2. Variables de Entorno
Crea un archivo `.env.local` con las siguientes variables:

```bash
# URL del Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Configuración de la Aplicación
NEXT_PUBLIC_APP_NAME=Crypto Trading Analyzer
NEXT_PUBLIC_APP_VERSION=1.0.0

# Configuración de Desarrollo
NODE_ENV=development
NEXT_PUBLIC_DEBUG=true

# APIs Externas (opcional para datos adicionales)
NEXT_PUBLIC_COINGECKO_API=https://api.coingecko.com/api/v3
```

### 3. Instalación de Dependencias

```bash
# Asegúrate de estar en el directorio frontend
cd frontend

# Instalar dependencias con npm
npm install

# O con yarn (alternativa)
yarn install

# Verificar que Next.js funciona correctamente
npm run dev
```

## 🚀 Ejecución del Frontend

### Desarrollo Local

```bash
# Servidor de desarrollo (con hot-reload)
npm run dev

# La aplicación estará disponible en:
# http://localhost:3000
```

### Otros Comandos Útiles

```bash
# Construir para producción
npm run build

# Ejecutar versión de producción
npm run start

# Ejecutar linter (ESLint)
npm run lint

# Ejecutar tests (cuando se configuren)
npm run test

# Analizar el bundle
npm run analyze
```

## 📁 Estructura del Código

```
frontend/
├── src/
│   ├── app/                    # App Router de Next.js 14
│   │   ├── layout.tsx          # Layout principal
│   │   ├── page.tsx            # Página de inicio
│   │   ├── dashboard/          # Páginas del dashboard
│   │   ├── portfolio/          # Gestión de cartera
│   │   └── settings/           # Configuración
│   │
│   ├── components/             # Componentes reutilizables
│   │   ├── ui/                 # Componentes base (botones, inputs)
│   │   ├── charts/             # Componentes de gráficos
│   │   ├── layout/             # Componentes de layout
│   │   └── features/           # Componentes específicos
│   │
│   ├── hooks/                  # Custom hooks de React
│   │   ├── useWebSocket.ts     # Hook para WebSocket
│   │   ├── useMarketData.ts    # Hook para datos de mercado
│   │   └── useLocalStorage.ts  # Hook para almacenamiento local
│   │
│   ├── lib/                    # Librerías y utilidades
│   │   ├── api.ts              # Cliente de API
│   │   ├── websocket.ts        # Cliente WebSocket
│   │   ├── utils.ts            # Funciones de utilidad
│   │   └── constants.ts        # Constantes de la aplicación
│   │
│   ├── stores/                 # Gestión de estado global
│   │   ├── marketStore.ts      # Store para datos de mercado
│   │   ├── userStore.ts        # Store para datos del usuario
│   │   └── settingsStore.ts    # Store para configuraciones
│   │
│   ├── types/                  # Definiciones de tipos TypeScript
│   │   ├── market.ts           # Tipos para datos de mercado
│   │   ├── user.ts             # Tipos para datos de usuario
│   │   └── api.ts              # Tipos para respuestas de API
│   │
│   └── styles/                 # Estilos globales
│       ├── globals.css         # Estilos CSS globales
│       └── components.css      # Estilos de componentes
│
├── public/                     # Archivos estáticos
│   ├── images/                 # Imágenes y logos
│   ├── icons/                  # Iconos personalizados
│   └── favicon.ico             # Favicon
│
├── docs/                       # Documentación del frontend
├── .env.local.example          # Ejemplo de variables de entorno
├── next.config.js              # Configuración de Next.js
├── tailwind.config.js          # Configuración de Tailwind CSS
├── tsconfig.json               # Configuración de TypeScript
└── package.json                # Dependencias y scripts
```

## 🎨 Configuración de Tailwind CSS

El proyecto utiliza Tailwind CSS para un desarrollo rápido y consistente:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

## 🔄 Integración con Backend

### Cliente API
```typescript
// src/lib/api.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 10000,
});

export const marketAPI = {
  getPrices: () => apiClient.get('/api/market/prices'),
  getIndicators: (symbol: string) => apiClient.get(`/api/indicators/${symbol}`),
  getSignals: () => apiClient.get('/api/signals'),
};
```

### WebSocket Cliente
```typescript
// src/lib/websocket.ts
import io from 'socket.io-client';

const socket = io(process.env.NEXT_PUBLIC_WS_URL!);

export const subscribeToMarketData = (callback: (data: any) => void) => {
  socket.on('market_update', callback);
  return () => socket.off('market_update', callback);
};
```

## 🧪 Testing (Próximamente)

```bash
# Configuración de testing con Jest y Testing Library
npm install --save-dev jest @testing-library/react @testing-library/jest-dom

# Ejecutar tests
npm run test

# Tests con cobertura
npm run test:coverage
```

## 🔄 Estado Actual del Desarrollo

### ✅ Completado
- [x] Estructura básica del proyecto
- [x] Documentación inicial
- [x] Configuración de tecnologías

### 🚧 En Progreso
- [ ] Configuración inicial de Next.js
- [ ] Setup de Tailwind CSS
- [ ] Estructura de componentes base

### 📋 Próximas Tareas
1. **Configurar proyecto Next.js** con TypeScript
2. **Implementar layout base** con navegación
3. **Crear componentes de gráficos** básicos
4. **Desarrollar dashboard inicial** (por ahora con datos de prueba)
5. **Integrar con backend API** cuando esté disponible

## ⚡ Comandos de Desarrollo Rápido

```bash
# Setup completo del proyecto
npm run setup

# Desarrollo con hot-reload
npm run dev

# Linting y formateo
npm run lint:fix

# Optimización de imágenes
npm run optimize-images

# Análisis del bundle
npm run analyze
```

## 📱 Páginas Principales

1. **Dashboard** (`/dashboard`)
   - Vista general del mercado
   - Gráficos de precios principales
   - Señales de trading recientes

2. **Portfolio** (`/portfolio`)
   - Resumen de cartera
   - Rendimiento de inversiones
   - Historial de transacciones

3. **Estrategias** (`/strategies`)
   - Configuración de estrategias
   - Backtesting de resultados
   - Gestión de parámetros

4. **Configuración** (`/settings`)
   - Preferencias de usuario
   - Configuración de APIs
   - Gestión de alertas

---

**¡El frontend será la ventana que permita interactuar con todo el poder del análisis técnico!** Al principio tendremos componentes básicos con datos de prueba, y gradualmente integraremos la funcionalidad real del backend. 🎨📊
