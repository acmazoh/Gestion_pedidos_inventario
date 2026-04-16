import { useState, createContext, useContext } from 'react';
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

const NAV_ITEMS = [
  { to: '/pos',      label: '🍽️  POS'        },
  { to: '/orders',   label: '📋  Orden'       },
  { to: '/products', label: '⚙️  Productos'   },
];

function AppLayout() {
  const { logout } = useAuth();

  return (
    <div className="flex h-screen flex-col bg-gray-100 overflow-hidden">
      {/* Barra de navegación superior */}
      <header className="bg-gray-900 text-white px-4 py-2 flex items-center justify-between shadow-lg shrink-0">
        <span className="font-bold text-lg text-brand-400 tracking-tight">
          RestaurantPOS
        </span>
        <nav className="flex gap-1">
          {NAV_ITEMS.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-brand-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
        <button
          onClick={logout}
          className="text-xs text-gray-400 hover:text-white transition-colors px-2 py-1 rounded hover:bg-gray-700"
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
      <div className="flex-1 overflow-y-auto">
        <POSView onAddToOrder={(producto) => orderHook.addProduct(producto.id)} />
      </div>
      {/* Panel de orden (derecha, fijo) */}
      <aside className="w-80 xl:w-96 shrink-0 overflow-y-auto bg-white border-l border-gray-200 shadow-lg">
        <div className="sticky top-0 bg-white border-b px-4 py-3">
          <h2 className="font-semibold text-gray-800">Orden en curso</h2>
        </div>
        <div className="p-3">
          <InlineOrderPanel hook={orderHook} />
        </div>
      </aside>
    </div>
  );
}

// Versión inline del OrderPanel que recibe el hook ya instanciado
// (para compartir el mismo estado entre POSView y el panel)
function InlineOrderPanel({ hook }: { hook: ReturnType<typeof useOrder> }) {
  const { order, loading, error, shortages,
          startOrder, updateQty, removeProduct, confirm, resetOrder, clearError } = hook;
  const [mesa, setMesa]             = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [success, setSuccess]       = useState(false);

  if (success && order) {
    return (
      <div className="text-center py-8 space-y-3">
        <div className="text-5xl">✅</div>
        <p className="font-semibold text-gray-800">Orden #{order.id} confirmada</p>
        <button
          onClick={() => { resetOrder(); setSuccess(false); }}
          className="bg-brand-600 text-white px-4 py-2 rounded-lg text-sm"
        >
          Nueva Orden
        </button>
      </div>
    );
  }

  if (!order) {
    return (
      <form
        onSubmit={async (e) => { e.preventDefault(); if (mesa.trim()) { await startOrder(mesa.trim()); setMesa(''); } }}
        className="space-y-3"
      >
        <p className="text-sm text-gray-500">Ingresa mesa o cliente para comenzar.</p>
        <input
          type="text"
          value={mesa}
          onChange={(e) => setMesa(e.target.value)}
          placeholder="Mesa 3 / Cliente Juan"
          className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
        />
        <button
          type="submit"
          disabled={loading || !mesa.trim()}
          className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium"
        >
          {loading ? 'Creando…' : 'Iniciar Orden'}
        </button>
      </form>
    );
  }

  return (
    <div className="space-y-3 text-sm">
      {error && <div className="text-red-600 text-xs bg-red-50 p-2 rounded-lg">{error}</div>}
      {shortages.length > 0 && (
        <div className="bg-red-50 border border-red-300 rounded-lg p-2 text-xs text-red-700">
          <strong>Stock insuficiente:</strong>
          <ul className="mt-1 space-y-0.5 list-disc list-inside">
            {shortages.map((s, i) => (
              <li key={i}>{s.ingrediente}: falta {s.missing} {s.unidad}</li>
            ))}
          </ul>
          <button onClick={clearError} className="mt-1 text-red-500 underline text-xs">Cerrar</button>
        </div>
      )}

      {/* Ítems */}
      <div className="space-y-1 max-h-60 overflow-y-auto">
        {order.items.length === 0 && (
          <p className="text-gray-400 text-center py-4">Sin productos aún.</p>
        )}
        {order.items.map((item) => (
          <div key={item.id} className="flex items-center gap-1 bg-gray-50 rounded-lg px-2 py-1">
            <span className="flex-1 text-xs truncate">{item.producto.nombre}</span>
            <button onClick={() => updateQty(item.id, item.cantidad - 1)} className="px-1 text-gray-500 hover:text-gray-800">−</button>
            <span className="w-4 text-center font-semibold">{item.cantidad}</span>
            <button onClick={() => updateQty(item.id, item.cantidad + 1)} className="px-1 text-gray-500 hover:text-gray-800">+</button>
            <span className="w-12 text-right text-xs font-medium">${item.subtotal.toFixed(2)}</span>
            <button onClick={() => removeProduct(item.id)} className="text-red-400 hover:text-red-600 text-xs ml-1">✕</button>
          </div>
        ))}
      </div>

      {/* Totales */}
      {order.items.length > 0 && (
        <div className="border-t pt-2 space-y-1 text-xs text-gray-600">
          <div className="flex justify-between"><span>Subtotal</span><span>${order.subtotal.toFixed(2)}</span></div>
          <div className="flex justify-between"><span>IVA 19%</span><span>${order.impuesto.toFixed(2)}</span></div>
          <div className="flex justify-between font-bold text-sm text-gray-900 border-t pt-1 mt-1">
            <span>Total</span><span>${order.total.toFixed(2)}</span>
          </div>
        </div>
      )}

      {/* Acciones */}
      <div className="flex gap-2">
        <button onClick={() => resetOrder()} className="flex-1 border border-gray-300 text-gray-600 py-1.5 rounded-lg text-xs">Cancelar</button>
        <button
          onClick={() => setConfirmOpen(true)}
          disabled={loading || order.items.length === 0}
          className="flex-1 bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white py-1.5 rounded-lg text-xs font-medium"
        >
          Confirmar
        </button>
      </div>

      {confirmOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-xl shadow-xl p-6 max-w-sm w-full space-y-4">
            <h3 className="font-semibold text-gray-900">Confirmar orden #{order.id}</h3>
            <p className="text-sm text-gray-600">Se enviará a cocina y se descontará el inventario. ¿Continuar?</p>
            <div className="flex gap-3">
              <button onClick={() => setConfirmOpen(false)} className="flex-1 border border-gray-300 py-2 rounded-lg text-sm">Cancelar</button>
              <button
                onClick={async () => { setConfirmOpen(false); const ok = await confirm(); if (ok) setSuccess(true); }}
                className="flex-1 bg-brand-600 text-white py-2 rounded-lg text-sm font-medium"
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
    <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-sm space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-brand-600">🍽️ RestPOS</h1>
          <p className="text-gray-500 mt-1 text-sm">Inicia sesión para continuar</p>
        </div>

        {err && (
          <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-2 rounded-lg text-sm">
            {err}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Usuario</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white py-2 rounded-lg font-medium transition-colors"
          >
            {loading ? 'Entrando…' : 'Iniciar sesión'}
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
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to={isAuth ? '/pos' : '/login'} replace />} />
        </Routes>
      </BrowserRouter>
    </AuthContext.Provider>
  );
}
