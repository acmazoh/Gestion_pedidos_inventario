// ── Entidades del dominio ──────────────────────────────────────────────────

export interface Categoria {
  id: number;
  nombre: string;
}

export interface Ingrediente {
  id: number;
  nombre: string;
  stock: number;
  unidad_medida: string;
}

export interface RecetaItem {
  ingrediente_id: number;
  ingrediente_nombre: string;
  cantidad: number;
}

export interface Producto {
  id: number;
  nombre: string;
  categoria: Categoria;
  precio: number;
  descripcion: string;
  disponible: boolean;
  ingredientes: Ingrediente[];
  receta: RecetaItem[];
}

// ── Formularios ────────────────────────────────────────────────────────────

/** Payload para crear/editar un producto */
export interface ProductoPayload {
  nombre: string;
  categoria_id: number;
  precio: number;
  descripcion?: string;
  disponible?: boolean;
  ingrediente_ids?: number[];
}

// ── Pedidos / Órdenes ──────────────────────────────────────────────────────

export type EstadoPedido = 'pendiente' | 'en_preparacion' | 'listo' | 'pagado';

export interface OrderItem {
  id: number;
  producto: Producto;
  cantidad: number;
  subtotal: number;
}

export interface Order {
  id: number;
  mesa_o_online: string;
  estado: EstadoPedido;
  creado_por: string;
  fecha_creacion: string;
  items: OrderItem[];
  subtotal: number;
  impuesto: number;
  total: number;
}

// ── Errores de stock (RF-07) ───────────────────────────────────────────────

export interface StockShortage {
  ingrediente: string;
  unidad: string;
  required: number;
  available: number;
  missing: number;
  productos: string[];
}

export interface ConfirmError {
  shortages: StockShortage[];
}

// ── Auth ───────────────────────────────────────────────────────────────────

export interface AuthToken {
  token: string;
}

// ── UI helpers ─────────────────────────────────────────────────────────────

export type AlertType = 'success' | 'error' | 'warning' | 'info';
