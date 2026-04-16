import { apiClient } from './client';
import type { Order, AuthToken } from '../types';

// ── Pedidos ────────────────────────────────────────────────────────────────

export const getOrders = () =>
  apiClient.get<Order[]>('/orders/').then((r) => r.data);

export const getOrder = (id: number) =>
  apiClient.get<Order>(`/orders/${id}/`).then((r) => r.data);

export const createOrder = (mesa_o_online: string) =>
  apiClient.post<Order>('/orders/', { mesa_o_online }).then((r) => r.data);

/** RF-06: desglose con subtotal, impuesto y total actualizados. */
export const calculateTotal = (id: number) =>
  apiClient.get<Order>(`/orders/${id}/calculate-total/`).then((r) => r.data);

/** Agregar o incrementar producto en el pedido. */
export const addItem = (orderId: number, producto_id: number, cantidad = 1) =>
  apiClient
    .post<Order>(`/orders/${orderId}/add-item/`, { producto_id, cantidad })
    .then((r) => r.data);

/** Actualizar cantidad de un ítem. */
export const updateItemQty = (orderId: number, itemId: number, cantidad: number) =>
  apiClient
    .patch<Order>(`/orders/${orderId}/items/${itemId}/quantity/`, { cantidad })
    .then((r) => r.data);

/** Eliminar ítem del pedido. */
export const removeItem = (orderId: number, itemId: number) =>
  apiClient
    .delete<Order>(`/orders/${orderId}/items/${itemId}/`)
    .then((r) => r.data);

/**
 * RF-07: Confirmar pedido.
 * En caso de stock insuficiente el backend responde 409 con {shortages: [...]}.
 * El caller debe capturar el error y leer `error.response.data`.
 */
export const confirmOrder = (id: number) =>
  apiClient.post<Order>(`/orders/${id}/confirm/`).then((r) => r.data);

// ── Auth ───────────────────────────────────────────────────────────────────

export const login = (username: string, password: string) =>
  apiClient
    .post<AuthToken>('/auth/login/', { username, password })
    .then((r) => r.data);
