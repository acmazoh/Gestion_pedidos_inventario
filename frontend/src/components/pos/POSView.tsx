import { useState, useMemo } from 'react';
import { useProducts } from '../../hooks/useProducts';
import { Spinner } from '../ui/Spinner';
import { Alert } from '../ui/Alert';
import type { Producto } from '../../types';

interface POSViewProps {
  onAddToOrder?: (producto: Producto) => void;
}

// Azul y verde de la paleta, alternando
const CARD_COLORS = [
  'from-primary-400 to-primary-600',   // azul #2196F3
  'from-success-400 to-success-600',   // verde #4CAF50
];

export function POSView({ onAddToOrder }: POSViewProps) {
  const { products, categories, loading, error, load } = useProducts(true);
  const [activeCat, setActiveCat] = useState<number | null>(null);

  const filtered = useMemo(
    () => (activeCat ? products.filter((p) => p.categoria.id === activeCat) : products),
    [products, activeCat],
  );

  const activeCats = useMemo(
    () => categories.filter((c) => products.some((p) => p.categoria.id === c.id)),
    [categories, products],
  );

  return (
    <div className="flex h-full flex-col lg:flex-row gap-0 overflow-hidden">
      {/* ── Sidebar de categorías ──────────────────────────────────────── */}
      <aside className="lg:w-52 shrink-0 bg-gray-800 overflow-y-auto flex flex-col">
        <div className="px-4 py-4 border-b border-gray-700/60">
          <p className="text-[10px] font-bold uppercase tracking-widest text-gray-500 mb-1">Menú</p>
          <p className="text-white font-semibold text-sm">Categorías</p>
        </div>
        <nav className="p-3 space-y-1 flex-1">
          {[{ id: null, nombre: 'Todos los platos' }, ...activeCats.map(c => ({ id: c.id as number | null, nombre: c.nombre }))].map((c) => (
            <button
              key={c.id ?? 'all'}
              onClick={() => setActiveCat(c.id)}
              className={`w-full text-left px-4 py-2.5 rounded-xl text-sm font-medium transition-all ${
                activeCat === c.id
                  ? 'bg-primary-500 text-white shadow-md'
                  : 'text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              {c.nombre}
            </button>
          ))}
        </nav>
      </aside>

      {/* ── Catálogo de productos ─────────────────────────────────────── */}
      <main className="flex-1 overflow-y-auto bg-gray-50 p-5">
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
        ? products.filter((p) => p.nombre.toLowerCase().includes(search.toLowerCase()))
        : products,
    [products, search],
  );

  return (
    <div className="space-y-4">
      {/* Buscador */}
      <div className="relative max-w-md">
        <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
        <input
          type="search"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Buscar producto..."
          className="w-full border border-gray-200 rounded-2xl pl-9 pr-4 py-2.5 text-sm bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-400 focus:border-transparent"
        />
      </div>

      {error && <Alert type="error" message={error} onClose={onReload} />}

      {loading ? (
        <div className="flex justify-center py-16"><Spinner size="lg" /></div>
      ) : visible.length === 0 ? (
        <div className="py-20 text-center text-gray-400">
          <p className="text-5xl mb-4">🍽️</p>
          <p className="font-medium">No hay productos en esta categoría.</p>
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          {visible.map((p, i) => (
            <ProductCard key={p.id} producto={p} onAdd={onAdd} colorIndex={i % CARD_COLORS.length} />
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
  colorIndex = 0,
}: {
  producto: Producto;
  onAdd?: (p: Producto) => void;
  colorIndex?: number;
}) {
  const [pressed, setPressed] = useState(false);

  const handlePress = () => {
    if (!onAdd) return;
    setPressed(true);
    onAdd(producto);
    setTimeout(() => setPressed(false), 400);
  };

  return (
    <button
      onClick={handlePress}
      disabled={!onAdd}
      className={`flex flex-col bg-white rounded-2xl shadow-sm overflow-hidden w-full text-left
        transition-all duration-200 select-none border border-gray-100
        ${pressed ? 'scale-95 shadow-lg ring-2 ring-primary-400' : 'hover:shadow-md hover:-translate-y-0.5'}
        ${!onAdd ? 'cursor-default' : 'cursor-pointer'}`}
    >
      {/* Banner de color */}
      <div className={`bg-gradient-to-br ${CARD_COLORS[colorIndex]} h-20 flex items-center justify-center`}>
        <span className="text-4xl drop-shadow">🍽️</span>
      </div>

      {/* Contenido */}
      <div className="p-3 flex flex-col gap-2 flex-1">
        <div>
          <p className="font-semibold text-gray-900 text-sm leading-tight line-clamp-2">
            {producto.nombre}
          </p>
          <span className="inline-block mt-1 text-[10px] font-semibold uppercase tracking-wide bg-gray-100 text-gray-500 rounded-full px-2 py-0.5">
            {producto.categoria.nombre}
          </span>
        </div>

        <div className="flex items-center justify-between mt-auto pt-1 border-t border-gray-50">
          <span className="text-base font-bold text-primary-700">
            ${Math.round(Number(producto.precio)).toLocaleString('es-CO')}
          </span>
          {onAdd && (
            <span className={`text-xs font-bold px-2.5 py-1 rounded-full transition-colors
              ${pressed ? 'bg-success-500 text-white' : 'bg-primary-100 text-primary-700'}`}>
              {pressed ? '✓' : '+ Agregar'}
            </span>
          )}
        </div>
      </div>
    </button>
  );
}
