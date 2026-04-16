import { apiClient } from './client';
import type { Producto, Categoria, Ingrediente, ProductoPayload } from '../types';

// ── Productos ──────────────────────────────────────────────────────────────

/** Lista todos los productos. Pasar `disponible=true` para el POS. */
export const getProducts = (params?: { disponible?: boolean; categoria?: number }) =>
  apiClient.get<Producto[]>('/products/', { params }).then((r) => r.data);

export const getProduct = (id: number) =>
  apiClient.get<Producto>(`/products/${id}/`).then((r) => r.data);

export const createProduct = (data: ProductoPayload) =>
  apiClient.post<Producto>('/products/', data).then((r) => r.data);

export const updateProduct = (id: number, data: Partial<ProductoPayload>) =>
  apiClient.put<Producto>(`/products/${id}/`, data).then((r) => r.data);

export const deleteProduct = (id: number) =>
  apiClient.delete(`/products/${id}/`);

export const toggleDisponible = (id: number) =>
  apiClient.post<{ id: number; disponible: boolean }>(
    `/products/${id}/toggle-disponible/`,
  ).then((r) => r.data);

// ── Categorías ─────────────────────────────────────────────────────────────

export const getCategories = () =>
  apiClient.get<Categoria[]>('/categories/').then((r) => r.data);

// ── Ingredientes ───────────────────────────────────────────────────────────

export const getIngredients = () =>
  apiClient.get<Ingrediente[]>('/ingredients/').then((r) => r.data);
