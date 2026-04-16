import { useState, useEffect, useCallback } from 'react';
import {
  getProducts,
  getCategories,
  getIngredients,
  createProduct,
  updateProduct,
  deleteProduct,
  toggleDisponible,
} from '../api/products';
import type { Producto, Categoria, Ingrediente, ProductoPayload } from '../types';

/** Hook que gestiona el estado completo de productos (RF-01 y RF-02). */
export function useProducts(soloDisponibles = false) {
  const [products, setProducts]       = useState<Producto[]>([]);
  const [categories, setCategories]   = useState<Categoria[]>([]);
  const [ingredients, setIngredients] = useState<Ingrediente[]>([]);
  const [loading, setLoading]         = useState(false);
  const [error, setError]             = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [prods, cats, ings] = await Promise.all([
        getProducts(soloDisponibles ? { disponible: true } : {}),
        getCategories(),
        getIngredients(),
      ]);
      setProducts(prods);
      setCategories(cats);
      setIngredients(ings);
    } catch {
      setError('No se pudieron cargar los datos. Verifica la conexión.');
    } finally {
      setLoading(false);
    }
  }, [soloDisponibles]);

  useEffect(() => { load(); }, [load]);

  const create = async (data: ProductoPayload): Promise<Producto> => {
    const nuevo = await createProduct(data);
    setProducts((prev) => [...prev, nuevo]);
    return nuevo;
  };

  const update = async (id: number, data: Partial<ProductoPayload>): Promise<Producto> => {
    const actualizado = await updateProduct(id, data);
    setProducts((prev) => prev.map((p) => (p.id === id ? actualizado : p)));
    return actualizado;
  };

  const remove = async (id: number): Promise<void> => {
    await deleteProduct(id);
    setProducts((prev) => prev.filter((p) => p.id !== id));
  };

  const toggle = async (id: number): Promise<void> => {
    const result = await toggleDisponible(id);
    setProducts((prev) =>
      prev.map((p) => (p.id === id ? { ...p, disponible: result.disponible } : p)),
    );
  };

  return { products, categories, ingredients, loading, error, load, create, update, remove, toggle };
}
