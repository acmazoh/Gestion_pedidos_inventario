import { useState, createContext, useContext } from 'react';
import { useMe } from './hooks/useMe';
import {
  BrowserRouter,
  Routes,
  Route,
  NavLink,
  Navigate,
  Outlet,
} from 'react-router-dom';
import { ProductsManagement } from './components/products/ProductsManagement';
import { POSView }            from './components/pos/POSView';
import { OrderPanel }         from './components/orders/OrderPanel';
import { useOrder }           from './hooks/useOrder';
import { login as apiLogin }  from './api/orders';
import { TOKEN_KEY }          from './api/client';
import { KitchenDashboard } from './components/orders/KitchenDashboard';

// ── Contexto de Auth ───────────────────────────────────────────────────────

interface AuthCtx { isAuth: boolean; logout: () => void }
const AuthContext = createContext<AuthCtx>({ isAuth: false, logout: () => {} });
export const useAuth = () => useContext(AuthContext);

// ── Guarda de rutas privadas ───────────────────────────────────────────────

function PrivateRoute() {
  const { isAuth } = useAuth();
  return isAuth ? <Outlet /> : <Navigate to="/login" replace />;
}

// ── Layout principal ───────────────────────────────────────────────────────


const NAV_ITEMS_BY_ROLE: Record<string, { to: string; label: string }[]> = {
  admin: [
    { to: '/pos', label: '🍽️  POS' },
    { to: '/orders', label: '📋  Orden' },
    { to: '/products', label: '⚙️  Productos' },
    // { to: '/ingredients', label: '🧂 Ingredientes' },
    // { to: '/users', label: '👥 Usuarios' },
    // { to: '/sales', label: '💵 Ventas' },
  ],
  mesero: [
    { to: '/pos', label: '🍽️  POS' },
    { to: '/orders', label: '📋  Orden' },
  ],
  cocinero: [
    { to: '/kitchen', label: '👨‍🍳 Cocina' },
  ],
  cajero: [
    { to: '/orders', label: '📋  Orden' },
    // { to: '/sales', label: '💵 Ventas' },
  ],
};


function AppLayout() {
  const { logout } = useAuth();
  const { me, loading } = useMe();

  if (loading) {
    return <div className="flex items-center justify-center h-screen">Cargando menú...</div>;
  }

  const role = me?.role || 'mesero';
  const NAV_ITEMS = NAV_ITEMS_BY_ROLE[role] || NAV_ITEMS_BY_ROLE['mesero'];

  return (
    <div className="flex h-screen flex-col bg-gray-50 overflow-hidden">
      {/* Barra de navegación superior */}
      <header className="bg-gray-800 text-white px-5 py-3 flex items-center justify-between shadow-lg shrink-0">
        <span className="font-bold text-lg tracking-tight text-white">
          🍽️ RestaurantPOS
        </span>
        <nav className="flex gap-1">
          {NAV_ITEMS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-500 text-white'
                    : 'text-gray-400 hover:bg-white/10 hover:text-white'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <button
          onClick={logout}
          className="text-xs text-gray-400 hover:text-white transition-colors px-2 py-1 rounded hover:bg-white/10"
        >
          Salir
        </button>
      </header>

      {/* Contenido */}
      <main className="flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}

// ── Vista POS combinada (Catálogo + Panel) ─────────────────────────────────

function POSWithPanel() {
  const orderHook = useOrder();

  return (
    <div className="flex h-full overflow-hidden">
      {/* Catálogo (izquierda) */}
      <div className="flex-1 overflow-hidden">
        <POSView onAddToOrder={(producto) => orderHook.addProduct(producto.id)} />
      </div>
      {/* Panel de orden (derecha, fijo) */}
      <aside className="w-80 xl:w-96 shrink-0 flex flex-col bg-gray-50 border-l border-gray-200 shadow-xl">
        {/* Header del panel */}
        <div className="bg-white border-b border-gray-100 px-5 py-4 shrink-0">
          <div className="flex items-center gap-2 mb-0.5">
            <span className="w-2 h-2 rounded-full bg-success-500 animate-pulse" />
            <p className="text-gray-400 text-xs font-semibold uppercase tracking-widest">Orden activa</p>
          </div>
          <h2 className="font-extrabold text-gray-900 text-lg">
            {orderHook.order ? `Mesa · #${orderHook.order.id}` : 'Nueva orden'}
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <InlineOrderPanel hook={orderHook} />
        </div>
      </aside>
    </div>
  );
}

// Versión inline del OrderPanel que recibe el hook ya instanciado
function InlineOrderPanel({ hook }: { hook: ReturnType<typeof useOrder> }) {
  const { order, loading, error, shortages,
          startOrder, updateQty, removeProduct, confirm, resetOrder, clearError } = hook;
  const [mesa, setMesa]             = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [success, setSuccess]       = useState(false);

  if (success && order) {
    return (
      <div className="text-center py-10 space-y-4">
        <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto">
          <span className="text-3xl">✅</span>
        </div>
        <div>
          <p className="font-bold text-gray-900 text-lg">¡Orden enviada!</p>
          <p className="text-sm text-gray-500 mt-1">Orden #{order.id} enviada a cocina</p>
        </div>
        <button
          onClick={() => { resetOrder(); setSuccess(false); }}
          className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-xl text-sm font-semibold transition-colors"
        >
          + Nueva Orden
        </button>
      </div>
    );
  }

  if (!order) {
    if (loading) {
      return (
        <div className="flex flex-col items-center justify-center py-16 gap-4">
          <div className="w-10 h-10 animate-spin rounded-full border-4 border-primary-500 border-t-transparent" />
          <p className="text-sm text-gray-400 font-medium">Creando orden…</p>
        </div>
      );
    }
    return (
      <div className="py-6 space-y-4">
        <div className="text-center py-4">
          <span className="text-5xl">🛎️</span>
          <p className="text-gray-600 font-medium mt-3 text-sm">¿Para qué mesa o cliente?</p>
          <p className="text-gray-400 text-xs mt-1">O simplemente agrega un producto para comenzar</p>
        </div>
        <form
          onSubmit={async (e) => { e.preventDefault(); if (mesa.trim()) { await startOrder(mesa.trim()); setMesa(''); } }}
          className="space-y-3"
        >
          <input
            type="text"
            value={mesa}
            onChange={(e) => setMesa(e.target.value)}
            placeholder="Mesa 3 / Cliente Juan…"
            className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent bg-gray-50"
          />
          <button
            type="submit"
            disabled={loading || !mesa.trim()}
            className="w-full bg-primary-600 hover:bg-primary-700 disabled:opacity-40 text-white py-3 rounded-xl text-sm font-semibold transition-colors"
          >
            {loading ? 'Creando…' : 'Iniciar Orden'}
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-3 text-sm h-full">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl p-3 flex justify-between items-start">
          <span>{error}</span>
          <button onClick={clearError} className="text-red-400 hover:text-red-600 ml-2 font-bold">✕</button>
        </div>
      )}
      {shortages.length > 0 && (
        <div className="bg-orange-50 border border-orange-200 rounded-xl p-3 text-xs text-orange-700">
          <p className="font-semibold mb-1">⚠️ Stock insuficiente:</p>
          <ul className="space-y-0.5 list-disc list-inside">
            {shortages.map((s, i) => (
              <li key={i}>{s.ingrediente}: falta {s.missing} {s.unidad}</li>
            ))}
          </ul>
          <button onClick={clearError} className="mt-2 text-orange-500 underline">Cerrar</button>
        </div>
      )}

      {/* Ítems */}
      <div className="space-y-2 flex-1">
        {order.items.length === 0 ? (
          <div className="text-center py-10 text-gray-300">
            <p className="text-4xl mb-2">🛒</p>
            <p className="text-xs font-medium">Agrega productos desde el catálogo</p>
          </div>
        ) : (
          order.items.map((item) => (
            <div key={item.id} className="flex items-center gap-2 bg-white hover:bg-gray-50 rounded-xl px-3 py-2.5 transition-colors group border border-gray-100">
              <div className="flex-1 min-w-0">
                <p className="text-xs font-semibold text-gray-800 truncate">{item.producto.nombre}</p>
                <p className="text-[10px] text-gray-400">${Math.round(Number(item.producto?.precio ?? 0)).toLocaleString('es-CO')} c/u</p>
              </div>
              {/* Controles de cantidad */}
              <div className="flex items-center gap-1 bg-white rounded-lg border border-gray-200 px-1">
                <button
                  onClick={() => updateQty(item.id, item.cantidad - 1)}
                  className="w-6 h-6 flex items-center justify-center text-gray-400 hover:text-primary-600 font-bold text-base"
                >−</button>
                <span className="w-5 text-center text-xs font-bold text-gray-800">{item.cantidad}</span>
                <button
                  onClick={() => updateQty(item.id, item.cantidad + 1)}
                  className="w-6 h-6 flex items-center justify-center text-gray-400 hover:text-primary-600 font-bold text-base"
                >+</button>
              </div>
              <span className="text-xs font-bold text-primary-700 w-14 text-right">
                ${Math.round(item.subtotal).toLocaleString('es-CO')}
              </span>
              <button
                onClick={() => removeProduct(item.id)}
                className="w-5 h-5 flex items-center justify-center text-gray-300 hover:text-red-500 transition-colors opacity-0 group-hover:opacity-100"
              >✕</button>
            </div>
          ))
        )}
      </div>

      {/* Totales */}
      {order.items.length > 0 && (
        <div className="border-t border-gray-100 pt-3 space-y-2">
          <div className="flex justify-between text-xs text-gray-500">
            <span>Subtotal</span>
            <span>${Math.round(order.subtotal).toLocaleString('es-CO')}</span>
          </div>
          <div className="flex justify-between text-xs text-gray-500">
            <span>IVA 19%</span>
            <span>${Math.round(order.impuesto).toLocaleString('es-CO')}</span>
          </div>
          <div className="flex justify-between items-center bg-gray-900 rounded-xl px-3 py-2.5 mt-2">
            <span className="font-bold text-white text-sm">Total</span>
            <span className="font-extrabold text-primary-400 text-lg">${Math.round(order.total).toLocaleString('es-CO')}</span>
          </div>
        </div>
      )}

      {/* Acciones */}
      <div className="flex gap-2 pt-1">
        <button
          onClick={() => resetOrder()}
          className="flex-none border border-gray-200 text-gray-500 hover:text-gray-700 hover:bg-gray-50 py-3 px-4 rounded-xl text-xs font-semibold transition-colors"
        >
          Cancelar
        </button>
        <button
          onClick={() => setConfirmOpen(true)}
          disabled={loading || order.items.length === 0}
          className="flex-1 bg-primary-600 hover:bg-primary-700 disabled:opacity-40 text-white py-3 rounded-xl text-sm font-bold transition-colors shadow-sm shadow-primary-200"
        >
          Confirmar pedido →
        </button>
      </div>

      {confirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full space-y-5">
            <div className="text-center">
              <span className="text-4xl">🍳</span>
              <h3 className="font-bold text-gray-900 text-lg mt-2">Enviar a cocina</h3>
              <p className="text-sm text-gray-500 mt-1">Orden #{order.id} · {order.items.length} producto(s)</p>
            </div>
            <div className="bg-primary-50 rounded-xl p-3 text-center">
              <p className="text-xs text-gray-500">Total a cobrar</p>
              <p className="text-2xl font-extrabold text-primary-700">${Math.round(order.total).toLocaleString('es-CO')}</p>
            </div>
            <p className="text-xs text-gray-400 text-center">Se descontará el inventario automáticamente.</p>
            <div className="flex gap-3">
              <button
                onClick={() => setConfirmOpen(false)}
                className="flex-1 border border-gray-200 py-2.5 rounded-xl text-sm text-gray-600 hover:bg-gray-50"
              >
                Volver
              </button>
              <button
                onClick={async () => { setConfirmOpen(false); const ok = await confirm(); if (ok) setSuccess(true); }}
                className="flex-1 bg-primary-600 hover:bg-primary-700 text-white py-2.5 rounded-xl text-sm font-bold transition-colors"
              >
                Confirmar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Página de Login ────────────────────────────────────────────────────────

function LoginPage({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [err, setErr]           = useState('');
  const [loading, setLoading]   = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr('');
    if (!username || !password) { setErr('Completa todos los campos.'); return; }
    setLoading(true);
    try {
      const { token } = await apiLogin(username, password);
      localStorage.setItem(TOKEN_KEY, token);
      onLogin();
    } catch {
      setErr('Credenciales incorrectas. Intenta de nuevo.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-primary-600 flex items-center justify-center p-4">
      {/* Decoración de fondo */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-24 -left-24 w-96 h-96 bg-white/5 rounded-full" />
        <div className="absolute -bottom-32 -right-32 w-[500px] h-[500px] bg-white/5 rounded-full" />
      </div>
      <div className="relative bg-white rounded-3xl shadow-2xl p-8 w-full max-w-sm space-y-7">
        <div className="text-center">
          <div className="w-16 h-16 bg-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary-200">
            <span className="text-3xl">🍽️</span>
          </div>
          <h1 className="text-2xl font-extrabold text-gray-900">RestaurantPOS</h1>
          <p className="text-gray-400 mt-1 text-sm">Bienvenido de vuelta</p>
        </div>

        {err && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-2.5 rounded-xl text-sm">
            {err}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Usuario</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              placeholder="Ej: admin"
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent bg-gray-50 transition"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              placeholder="••••••••"
              className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent bg-gray-50 transition"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white py-3.5 rounded-xl font-bold text-sm transition-colors shadow-md shadow-primary-200 mt-2"
          >
            {loading ? 'Ingresando…' : 'Iniciar sesión →'}
          </button>
        </form>
      </div>
    </div>
  );
}

// ── App root ───────────────────────────────────────────────────────────────

export default function App() {
  const [isAuth, setIsAuth] = useState(() => !!localStorage.getItem(TOKEN_KEY));

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setIsAuth(false);
  };

  return (
    <AuthContext.Provider value={{ isAuth, logout }}>
      <BrowserRouter>
        <Routes>
          {/* Pública */}
          <Route
            path="/login"
            element={
              isAuth
                ? <Navigate to="/pos" replace />
                : <LoginPage onLogin={() => setIsAuth(true)} />
            }
          />

          {/* Privadas */}
          <Route element={<PrivateRoute />}>
            <Route element={<AppLayout />}>
              <Route index element={<Navigate to="/pos" replace />} />
              <Route path="/pos"      element={<POSWithPanel />} />
              <Route path="/orders"   element={<div className="h-full overflow-y-auto p-4"><OrderPanel /></div>} />
              <Route path="/products" element={<div className="h-full overflow-y-auto p-4"><ProductsManagement /></div>} />
              <Route path="/kitchen" element={<div className="h-full overflow-y-auto p-4"><KitchenDashboard /></div>} />
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to={isAuth ? '/pos' : '/login'} replace />} />
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  );
}
