import { useState } from 'react';
import { useProducts } from '../../hooks/useProducts';
import { Spinner } from '../ui/Spinner';
import { Alert } from '../ui/Alert';
import { ConfirmDialog } from '../ui/ConfirmDialog';
import type { Producto, ProductoPayload } from '../../types';

// ── Formulario interno ─────────────────────────────────────────────────────

interface FormState {
  nombre: string;
  categoria_id: number | '';
  precio: string;
  descripcion: string;
  disponible: boolean;
  ingrediente_ids: number[];
}

const EMPTY_FORM: FormState = {
  nombre: '', categoria_id: '', precio: '', descripcion: '', disponible: true, ingrediente_ids: [],
};

function toFormState(p: Producto): FormState {
  return {
    nombre:          p.nombre,
    categoria_id:    p.categoria.id,
    precio:          String(p.precio),
    descripcion:     p.descripcion,
    disponible:      p.disponible,
    ingrediente_ids: p.ingredientes.map((i) => i.id),
  };
}

// ── Componente principal ───────────────────────────────────────────────────

/**
 * RF-01 — Gestión de Productos del Menú
 * Tabla CRUD + Formulario crear/editar + Confirmación de eliminación.
 */
export function ProductsManagement() {
  const { products, categories, ingredients, loading, error, load, create, update, remove, toggle } =
    useProducts();

  const [showForm, setShowForm]             = useState(false);
  const [editingId, setEditingId]           = useState<number | null>(null);
  const [form, setForm]                     = useState<FormState>(EMPTY_FORM);
  const [formError, setFormError]           = useState<string | null>(null);
  const [formSuccess, setFormSuccess]       = useState<string | null>(null);
  const [saving, setSaving]                 = useState(false);
  const [deleteTarget, setDeleteTarget]     = useState<Produto | null>(null);

  // ── Helpers del formulario ───────────────────────────────────────────────

  const openCreate = () => { setEditingId(null); setForm(EMPTY_FORM); setFormError(null); setShowForm(true); };
  const openEdit   = (p: Producto) => { setEditingId(p.id); setForm(toFormState(p)); setFormError(null); setShowForm(true); };
  const closeForm  = () => { setShowForm(false); setFormError(null); setFormSuccess(null); };

  const handleIngredientToggle = (id: number) =>
    setForm((f) => ({
      ...f,
      ingrediente_ids: f.ingrediente_ids.includes(id)
        ? f.ingrediente_ids.filter((i) => i !== id)
        : [...f.ingrediente_ids, id],
    }));

  // ── Validación ───────────────────────────────────────────────────────────

  const validate = (): string | null => {
    if (!form.nombre.trim())          return 'El nombre es obligatorio.';
    if (!form.categoria_id)           return 'Selecciona una categoría.';
    const precio = parseFloat(form.precio);
    if (isNaN(precio) || precio <= 0) return 'El precio debe ser mayor a 0.';
    return null;
  };

  // ── Guardar ──────────────────────────────────────────────────────────────

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const err = validate();
    if (err) { setFormError(err); return; }

    const payload: ProductoPayload = {
      nombre:          form.nombre.trim(),
      categoria_id:    Number(form.categoria_id),
      precio:          parseFloat(form.precio),
      descripcion:     form.descripcion,
      disponible:      form.disponible,
      ingrediente_ids: form.ingrediente_ids,
    };

    setSaving(true);
    setFormError(null);
    try {
      if (editingId) {
        await update(editingId, payload);
        setFormSuccess('Producto actualizado correctamente.');
      } else {
        await create(payload);
        setFormSuccess('Producto creado correctamente.');
      }
      setTimeout(closeForm, 900);
    } catch (axiosErr: unknown) {
      const data = (axiosErr as { response?: { data: Record<string, string[]> } }).response?.data;
      const msg = data ? Object.values(data).flat().join(' ') : 'Error al guardar el producto.';
      setFormError(msg);
    } finally {
      setSaving(false);
    }
  };

  // ── Eliminar ─────────────────────────────────────────────────────────────

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await remove(deleteTarget.id);
    } catch {
      // El error se muestra en el Alert global al recargar
    } finally {
      setDeleteTarget(null);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      {/* Cabecera */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Gestión de Productos</h1>
        <button
          onClick={openCreate}
          className="flex items-center gap-2 bg-brand-600 hover:bg-brand-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
        >
          + Nuevo Producto
        </button>
      </div>

      {/* Alertas globales */}
      {error && <Alert type="error" message={error} onClose={load} />}

      {/* Tabla */}
      {loading ? (
        <Spinner />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
          <table className="min-w-full divide-y divide-gray-200 text-sm">
            <thead className="bg-gray-50">
              <tr>
                {['Nombre', 'Categoría', 'Precio', 'Disponible', 'Acciones'].map((h) => (
                  <th key={h} className="px-4 py-3 text-left font-semibold text-gray-600 uppercase tracking-wide text-xs">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {products.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-10 text-center text-gray-400">
                    No hay productos. Crea uno para comenzar.
                  </td>
                </tr>
              )}
              {products.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3 font-medium text-gray-900">{p.nombre}</td>
                  <td className="px-4 py-3 text-gray-600">{p.categoria.nombre}</td>
                  <td className="px-4 py-3 text-gray-800">
                    ${Number(p.precio).toFixed(2)}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => toggle(p.id)}
                      className={`px-2 py-1 rounded-full text-xs font-medium transition-colors ${
                        p.disponible
                          ? 'bg-green-100 text-green-700 hover:bg-green-200'
                          : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
                      }`}
                    >
                      {p.disponible ? 'Activo' : 'Inactivo'}
                    </button>
                  </td>
                  <td className="px-4 py-3 flex gap-2">
                    <button
                      onClick={() => openEdit(p)}
                      className="text-brand-600 hover:text-brand-700 font-medium text-xs px-2 py-1 rounded border border-brand-200 hover:bg-brand-50 transition-colors"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => setDeleteTarget(p)}
                      className="text-red-600 hover:text-red-700 font-medium text-xs px-2 py-1 rounded border border-red-200 hover:bg-red-50 transition-colors"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal formulario */}
      {showForm && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">
                {editingId ? 'Editar Producto' : 'Nuevo Producto'}
              </h2>
              <button onClick={closeForm} className="text-gray-400 hover:text-gray-600 text-xl leading-none">
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              {formError   && <Alert type="error"   message={formError} />}
              {formSuccess && <Alert type="success" message={formSuccess} />}

              {/* Nombre */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={form.nombre}
                  onChange={(e) => setForm({ ...form, nombre: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  placeholder="Ej. Hamburguesa Clásica"
                />
              </div>

              {/* Categoría */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Categoría <span className="text-red-500">*</span>
                </label>
                <select
                  value={form.categoria_id}
                  onChange={(e) => setForm({ ...form, categoria_id: Number(e.target.value) })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                >
                  <option value="">Seleccionar…</option>
                  {categories.map((c) => (
                    <option key={c.id} value={c.id}>{c.nombre}</option>
                  ))}
                </select>
              </div>

              {/* Precio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Precio <span className="text-red-500">*</span>
                </label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500 text-sm">$</span>
                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    value={form.precio}
                    onChange={(e) => setForm({ ...form, precio: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg pl-7 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                    placeholder="0.00"
                  />
                </div>
              </div>

              {/* Descripción */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Descripción</label>
                <textarea
                  value={form.descripcion}
                  onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
                  rows={2}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 resize-none"
                  placeholder="Descripción corta del producto…"
                />
              </div>

              {/* Disponible */}
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={form.disponible}
                  onChange={(e) => setForm({ ...form, disponible: e.target.checked })}
                  className="w-4 h-4 accent-brand-600"
                />
                <span className="text-sm text-gray-700">Visible en el menú POS</span>
              </label>

              {/* Ingredientes */}
              {ingredients.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-2">Ingredientes</p>
                  <div className="grid grid-cols-2 gap-2 max-h-36 overflow-y-auto border rounded-lg p-2">
                    {ingredients.map((ing) => (
                      <label key={ing.id} className="flex items-center gap-2 text-sm cursor-pointer">
                        <input
                          type="checkbox"
                          checked={form.ingrediente_ids.includes(ing.id)}
                          onChange={() => handleIngredientToggle(ing.id)}
                          className="accent-brand-600"
                        />
                        <span className="truncate">{ing.nombre}</span>
                        <span className="text-gray-400 text-xs">({ing.stock})</span>
                      </label>
                    ))}
                  </div>
                </div>
              )}

              {/* Botones */}
              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={closeForm}
                  className="px-4 py-2 rounded-lg border border-gray-300 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white text-sm font-medium transition-colors"
                >
                  {saving ? 'Guardando…' : editingId ? 'Actualizar' : 'Crear Producto'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Diálogo confirmación eliminar */}
      <ConfirmDialog
        open={!!deleteTarget}
        title="Eliminar producto"
        description={`¿Estás seguro de que quieres eliminar "${deleteTarget?.nombre}"? Esta acción no se puede deshacer.`}
        confirmLabel="Sí, eliminar"
        danger
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}

// Alias de tipo privado para el estado del diálogo
type Produto = Producto;
