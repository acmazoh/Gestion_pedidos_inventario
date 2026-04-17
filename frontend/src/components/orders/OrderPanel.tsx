import { useState } from 'react';
import { useOrder } from '../../hooks/useOrder';
import { Spinner } from '../ui/Spinner';
import { Alert } from '../ui/Alert';
import { ConfirmDialog } from '../ui/ConfirmDialog';
import type { OrderItem, StockShortage } from '../../types';

const TAX_LABEL = '19% IVA';

/**
 * RF-06 + RF-07 — Panel de Orden
 * Muestra ítems, desglose de totales (subtotal, impuesto, total)
 * y maneja la confirmación con validación de stock.
 */
export function OrderPanel() {
  const {
    order, loading, error, shortages,
    startOrder, addProduct: _addProduct,
    updateQty, removeProduct, confirm, resetOrder, clearError,
  } = useOrder();

  const [mesa, setMesa]               = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [success, setSuccess]         = useState(false);

  // ── Crear nueva orden ──────────────────────────────────────────────────

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!mesa.trim()) return;
    await startOrder(mesa.trim());
    setMesa('');
  };

  // ── Confirmar orden (RF-07) ────────────────────────────────────────────

  const handleConfirm = async () => {
    setConfirmOpen(false);
    const ok = await confirm();
    if (ok) setSuccess(true);
  };

  // ── Reiniciar ──────────────────────────────────────────────────────────

  const handleReset = () => { resetOrder(); setSuccess(false); };

  // ── Render: sin orden activa ───────────────────────────────────────────

  if (!order) {
    return (
      <div className="max-w-md mx-auto p-6 space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Nueva Orden</h1>
        {error && <Alert type="error" message={error} onClose={clearError} />}

        <form onSubmit={handleStart} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Mesa o Cliente <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={mesa}
              onChange={(e) => setMesa(e.target.value)}
              placeholder="Ej. Mesa 3"
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            type="submit"
            disabled={loading || !mesa.trim()}
            className="w-full bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white py-2 rounded-lg font-medium transition-colors"
          >
            {loading ? 'Creando…' : 'Iniciar Orden'}
          </button>
        </form>
      </div>
    );
  }

  // ── Render: orden exitosa ──────────────────────────────────────────────

  if (success) {
    return (
      <div className="max-w-md mx-auto p-6 space-y-4 text-center">
        <div className="text-6xl">✅</div>
        <h2 className="text-xl font-bold text-gray-900">
          Orden #{order.id} confirmada
        </h2>
        <p className="text-gray-600">
          Enviada a cocina — estado: <strong>En preparación</strong>
        </p>
        <button
          onClick={handleReset}
          className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
        >
          Nueva Orden
        </button>
      </div>
    );
  }

  // ── Render: orden activa ───────────────────────────────────────────────

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-4">
      {/* Cabecera */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-gray-900">
            Orden #{order.id}
          </h1>
          <p className="text-sm text-gray-500">
            Mesa/Cliente: {order.mesa_o_online}
          </p>
          <p className="text-xs text-gray-400">
            Creada: {order.fecha_creacion ? new Date(order.fecha_creacion).toLocaleString() : ''}
          </p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${
          order.estado === 'pendiente'  ? 'bg-yellow-100 text-yellow-700'
            : order.estado === 'en_preparacion' ? 'bg-primary-100 text-primary-700'
            : order.estado === 'listo'  ? 'bg-success-100 text-success-700'
            : 'bg-gray-100 text-gray-600'
        }`}>
          {order.estado}
        </span>
      </div>

      {/* Alertas */}
      {error && <Alert type="error" message={error} onClose={clearError} />}

      {/* Errores de stock RF-07 */}
      {shortages.length > 0 && (
        <StockAlert shortages={shortages} onDismiss={clearError} />
      )}

      {loading && <Spinner />}

      {/* Lista de ítems */}
      {order.items.length === 0 ? (
        <div className="py-10 text-center text-gray-400 border-2 border-dashed rounded-xl">
          No hay productos en la orden.
          <br />
          <span className="text-sm">Agrega productos desde el catálogo POS.</span>
        </div>
      ) : (
        <div className="space-y-2">
          {order.items.map((item) => (
            <OrderItemRow
              key={item.id}
              item={item}
              disabled={loading || order.estado !== 'pendiente'}
              onUpdateQty={(qty) => updateQty(item.id, qty)}
              onRemove={() => removeProduct(item.id)}
            />
          ))}
        </div>
      )}

      {/* RF-06: Desglose de totales */}
      {order.items.length > 0 && (
        <OrderSummary
          subtotal={order.subtotal}
          impuesto={order.impuesto}
          total={order.total}
          taxLabel={TAX_LABEL}
        />
      )}

      {/* Botones de acción */}
      {order.estado === 'pendiente' && (
        <div className="flex gap-3 pt-2">
          <button
            onClick={handleReset}
            className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg text-sm hover:bg-gray-50 transition-colors"
          >
            Cancelar Orden
          </button>
          <button
            onClick={() => setConfirmOpen(true)}
            disabled={loading || order.items.length === 0}
            className="flex-1 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Confirmar Orden
          </button>
        </div>
      )}

      {/* Diálogo de confirmación */}
      <ConfirmDialog
        open={confirmOpen}
        title="Confirmar orden"
        description={`Se enviará la orden #${order.id} a cocina y se descontará el inventario. ¿Continuar?`}
        confirmLabel="Sí, confirmar"
        onConfirm={handleConfirm}
        onCancel={() => setConfirmOpen(false)}
      />
    </div>
  );
}

// ── Fila de ítem ───────────────────────────────────────────────────────────

interface ItemRowProps {
  item: OrderItem;
  disabled: boolean;
  onUpdateQty: (qty: number) => void;
  onRemove: () => void;
}

function OrderItemRow({ item, disabled, onUpdateQty, onRemove }: ItemRowProps) {
  return (
    <div className="flex items-center gap-3 bg-white rounded-xl border border-gray-200 px-4 py-3 shadow-sm">
      {/* Nombre + categoría */}
      <div className="flex-1 min-w-0">
        <p className="font-medium text-gray-900 text-sm truncate">{item.producto.nombre}</p>
        <p className="text-xs text-gray-400">{item.producto.categoria.nombre}</p>
      </div>

      {/* Control de cantidad */}
      <div className="flex items-center gap-1">
        <button
          onClick={() => onUpdateQty(item.cantidad - 1)}
          disabled={disabled}
          className="w-7 h-7 rounded-full border border-gray-300 text-gray-600 text-lg leading-none flex items-center justify-center hover:bg-gray-100 disabled:opacity-40 transition-colors"
          aria-label="Reducir cantidad"
        >
          −
        </button>
        <span className="w-6 text-center text-sm font-semibold">{item.cantidad}</span>
        <button
          onClick={() => onUpdateQty(item.cantidad + 1)}
          disabled={disabled}
          className="w-7 h-7 rounded-full border border-gray-300 text-gray-600 text-lg leading-none flex items-center justify-center hover:bg-gray-100 disabled:opacity-40 transition-colors"
          aria-label="Aumentar cantidad"
        >
          +
        </button>
      </div>

      {/* Subtotal */}
      <span className="w-16 text-right text-sm font-semibold text-gray-800">
        ${Math.round(item.subtotal).toLocaleString('es-CO')}
      </span>

      {/* Eliminar */}
      <button
        onClick={onRemove}
        disabled={disabled}
        className="text-red-400 hover:text-red-600 disabled:opacity-40 transition-colors text-xs px-1"
        aria-label={`Eliminar ${item.producto.nombre}`}
      >
        ✕
      </button>
    </div>
  );
}

// ── Desglose de totales (RF-06) ────────────────────────────────────────────

interface SummaryProps {
  subtotal: number;
  impuesto: number;
  total: number;
  taxLabel: string;
}

function OrderSummary({ subtotal, impuesto, total, taxLabel }: SummaryProps) {
  return (
    <div className="bg-gray-50 rounded-xl border border-gray-200 p-4 space-y-2 text-sm">
      <div className="flex justify-between text-gray-600">
        <span>Subtotal</span>
        <span>${Math.round(subtotal).toLocaleString('es-CO')}</span>
      </div>
      <div className="flex justify-between text-gray-600">
        <span>{taxLabel}</span>
        <span>${Math.round(impuesto).toLocaleString('es-CO')}</span>
      </div>
      <div className="flex justify-between font-bold text-gray-900 text-base border-t pt-2 mt-1">
        <span>Total</span>
        <span>${Math.round(total).toLocaleString('es-CO')}</span>
      </div>
    </div>
  );
}

// ── Alerta de stock insuficiente (RF-07) ───────────────────────────────────

interface StockAlertProps {
  shortages: StockShortage[];
  onDismiss: () => void;
}

function StockAlert({ shortages, onDismiss }: StockAlertProps) {
  return (
    <div className="bg-red-50 border border-red-300 rounded-xl p-4 space-y-3" role="alert">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-red-800 text-sm">
          ⚠ Stock insuficiente — no se puede confirmar la orden
        </h3>
        <button onClick={onDismiss} className="text-red-400 hover:text-red-600 text-sm">✕</button>
      </div>
      <ul className="space-y-1">
        {shortages.map((s, i) => (
          <li key={i} className="text-xs text-red-700 bg-red-100 rounded-lg px-3 py-2">
            <strong>
              Ingrediente "{s.ingrediente}" insuficiente
              {s.unidad ? ` (${s.unidad})` : ''}
            </strong>
            <br />
            Disponible: <span className="font-medium">{s.available}</span>
            {' · '}
            Requerido: <span className="font-medium">{s.required}</span>
            {' · '}
            Faltante: <span className="font-semibold text-red-800">{s.missing}</span>
            <br />
            {s.productos.length > 0 && (
              <span className="text-red-600">
                Afecta: {s.productos.join(', ')}
              </span>
            )}
          </li>
        ))}
      </ul>
      <p className="text-xs text-red-600">
        Elimina los productos afectados de la orden o contacta al administrador para reponer inventario.
      </p>
    </div>
  );
}
