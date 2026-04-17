import { useState, useCallback } from 'react';
import {
  createOrder,
  getOrder,
  addItem,
  updateItemQty,
  removeItem,
  confirmOrder,
} from '../api/orders';
import type { Order, StockShortage } from '../types';

/** Hook que gestiona el estado de una orden activa (RF-06, RF-07). */
export function useOrder() {
  const [order, setOrder]           = useState<Order | null>(null);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState<string | null>(null);
  const [shortages, setShortages]   = useState<StockShortage[]>([]);

  const clearError = () => { setError(null); setShortages([]); };

  /** Crear nueva orden. */
  const startOrder = useCallback(async (mesa: string) => {
    setLoading(true);
    clearError();
    try {
      const nueva = await createOrder(mesa);
      setOrder(nueva);
    } catch {
      setError('No se pudo crear la orden.');
    } finally {
      setLoading(false);
    }
  }, []);

  /** Cargar orden existente. */
  const loadOrder = useCallback(async (id: number) => {
    setLoading(true);
    clearError();
    try {
      setOrder(await getOrder(id));
    } catch {
      setError('No se pudo cargar la orden.');
    } finally {
      setLoading(false);
    }
  }, []);

  /** Agregar producto → si no hay orden activa la crea automáticamente (RF-06). */
  const addProduct = useCallback(async (productoId: number, cantidad = 1) => {
    setLoading(true);
    clearError();
    try {
      // Auto-crear orden si no existe todavía
      let activeOrder = order;
      if (!activeOrder) {
        activeOrder = await createOrder('Mesa');
        setOrder(activeOrder);
      }
      // Si el producto ya está en la orden, sumar la cantidad actual
      const existingItem = activeOrder.items?.find((item: any) => item.producto.id === productoId);
      const cantidadFinal = existingItem ? existingItem.cantidad + cantidad : cantidad;
      setOrder(await addItem(activeOrder.id, productoId, cantidadFinal));
    } catch {
      setError('No se pudo agregar el producto.');
    } finally {
      setLoading(false);
    }
  }, [order]);

  /** Actualizar cantidad de un ítem. */
  const updateQty = useCallback(async (itemId: number, cantidad: number) => {
    if (!order) return;
    setLoading(true);
    clearError();
    try {
      setOrder(await updateItemQty(order.id, itemId, cantidad));
    } catch {
      setError('No se pudo actualizar la cantidad.');
    } finally {
      setLoading(false);
    }
  }, [order]);

  /** Eliminar ítem de la orden. */
  const removeProduct = useCallback(async (itemId: number) => {
    if (!order) return;
    setLoading(true);
    clearError();
    try {
      setOrder(await removeItem(order.id, itemId));
    } catch {
      setError('No se pudo eliminar el producto.');
    } finally {
      setLoading(false);
    }
  }, [order]);

  /**
   * Confirmar orden (RF-07).
   * Si hay faltantes de stock, los guarda en `shortages` y NO confirma.
   */
  const confirm = useCallback(async (): Promise<boolean> => {
    if (!order) return false;
    setLoading(true);
    clearError();
    try {
      const confirmada = await confirmOrder(order.id);
      setOrder(confirmada);
      return true;
    } catch (err: unknown) {
      const axiosErr = err as { response?: { status: number; data: { shortages: StockShortage[] } } };
      if (axiosErr.response?.status === 409) {
        setShortages(axiosErr.response.data.shortages ?? []);
        setError('Hay ingredientes con stock insuficiente para confirmar la orden.');
      } else {
        setError('No se pudo confirmar la orden.');
      }
      return false;
    } finally {
      setLoading(false);
    }
  }, [order]);

  const resetOrder = () => { setOrder(null); clearError(); };

  return {
    order, loading, error, shortages,
    startOrder, loadOrder, addProduct, updateQty, removeProduct, confirm, resetOrder, clearError,
  };
}
