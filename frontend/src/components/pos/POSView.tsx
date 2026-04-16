import { useState, useMemo } from 'react';
import { useProducts } from '../../hooks/useProducts';
import { Spinner } from '../ui/Spinner';
import { Alert } from '../ui/Alert';
import type { Producto } from '../../types';

interface POSViewProps {
  /** Callback al presionar un producto — el padre maneja agregar a la orden. */
  onAddToOrder?: (producto: Producto) => void;
}

/**
 * RF-02 — Catálogo POS
 * Grid de productos agrupados por categoría. Solo muestra los disponibles.
 * Diseño táctil optimizado para tablet (botones grandes).
 */
export function POSView({ onAddToOrder }: POSViewProps) {
  // Solo carga productos disponibles (disponible=true)
  const { products, categories, loading, error, load } = useProducts(true);
  const [activeCat, setActiveCat] = useState<number | null>(null);

  // Productos filtrados por categoría activa (null = todos)
  const filtered = useMemo(
    () => (activeCat ? products.filter((p) => p.categoria.id === activeCat) : products),
    [products, activeCat],
  );

  // Categorías que tienen al menos un producto disponible
  const activeCats = useMemo(
    () =>
      categories.filter((c) =>
        products.some((p) => p.categoria.id === c.id),
      ),
    [categories, products],
  );

  return (
    <div className="flex h-full flex-col lg:flex-row gap-0 overflow-hidden">
      {/* ── Sidebar de categorías ──────────────────────────────────────── */}
      <aside className="lg:w-48 shrink-0 bg-gray-900 text-white overflow-y-auto">
        <div className="p-3 border-b border-gray-700">
          <h2 className="text-xs font-semibold uppercase tracking-widest text-gray-400">
            Categorías
          </h2>
        </div>
        <nav className="p-2 space-y-1">
          <button
            onClick={() => setActiveCat(null)}
            className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
              activeCat === null
                ? 'bg-brand-600 text-white font-medium'
                : 'text-gray-300 hover:bg-gray-800'
            }`}
          >
            Todos
          </button>
          {activeCats.map((c) => (
            <button
              key={c.id}
              onClick={() => setActiveCat(c.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                activeCat === c.id
                  ? 'bg-brand-600 text-white font-medium'
                  : 'text-gray-300 hover:bg-gray-800'
              }`}
            >
              {c.nombre}
            </button>
          ))}
        </nav>
      </aside>

      {/* ── Catálogo de productos ─────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto bg-gray-100 p-4">
        {/* Barra de búsqueda rápida por nombre */}
        <SearchableGrid
          products={filtered}
          loading={loading}
          error={error}
          onReload={load}
          onAdd={onAddToOrder}
        />
      </main>
    </div>
  );
}

// ── Sub-componente de grid con búsqueda ────────────────────────────────────

interface GridProps {
  products: Producto[];
  loading: boolean;
  error: string | null;
  onReload: () => void;
  onAdd?: (p: Producto) => void;
}

function SearchableGrid({ products, loading, error, onReload, onAdd }: GridProps) {
  const [search, setSearch] = useState('');

  const visible = useMemo(
    () =>
      search.trim()
        ? products.filter((p) =>
            p.nombre.toLowerCase().includes(search.toLowerCase()),
          )
        : products,
    [products, search],
  );

  return (
    <div className="space-y-4">
      {/* Buscador */}
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Buscar producto…"
        className="w-full max-w-sm border border-gray-300 rounded-xl px-4 py-2 text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
      />

      {error && <Alert type="error" message={error} onClose={onReload} />}

      {loading ? (
        <Spinner size="lg" />
      ) : visible.length === 0 ? (
        <div className="py-16 text-center text-gray-400">
          <p className="text-4xl mb-3">🍽️</p>
          <p>No hay productos disponibles en esta categoría.</p>
        </div>
      ) : (
        /* Grid táctil: 2 cols en móvil, 3 en tablet, 4 en desktop */
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {visible.map((p) => (
            <ProductCard key={p.id} producto={p} onAdd={onAdd} />
          ))}
        </div>
      )}
    </div>
  );
}

// ── Tarjeta de producto ────────────────────────────────────────────────────

function ProductCard({
  producto,
  onAdd,
}: {
  producto: Producto;
  onAdd?: (p: Producto) => void;
}) {
  const [pressed, setPressed] = useState(false);

  const handlePress = () => {
    if (!onAdd) return;
    setPressed(true);
    onAdd(producto);
    setTimeout(() => setPressed(false), 300);
  };

  return (
    <button
      onClick={handlePress}
      disabled={!onAdd}
      className={`flex flex-col items-center justify-between bg-white rounded-2xl shadow-sm
        border-2 p-4 gap-2 w-full text-left transition-all select-none
        ${pressed ? 'scale-95 border-brand-500 bg-brand-50' : 'border-transparent hover:border-brand-300 hover:shadow-md'}
        ${!onAdd ? 'cursor-default' : 'cursor-pointer active:scale-95'}`}
    >
      {/* Emoji / ícono placeholder */}
      <span className="text-4xl">🍽️</span>

      <div className="w-full text-center">
        <p className="font-semibold text-gray-900 text-sm leading-tight line-clamp-2">
          {producto.nombre}
        </p>
        <p className="text-xs text-gray-500 mt-0.5">{producto.categoria.nombre}</p>
      </div>

      <span className="mt-1 text-base font-bold text-brand-600">
        ${Number(producto.precio).toFixed(2)}
      </span>

      {onAdd && (
        <span className="text-xs text-brand-500 font-medium">+ Agregar</span>
      )}
    </button>
  );
}
