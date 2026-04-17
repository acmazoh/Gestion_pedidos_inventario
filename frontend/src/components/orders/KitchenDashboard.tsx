import { useEffect, useState } from 'react';
import { apiClient } from '../../api/client';

interface CocinaPedido {
  id: number;
  mesa_o_online: string;
  estado: string;
  fecha_creacion: string;
  hora_formateada: string;
  items: { id: number; producto: string; cantidad: number }[];
  es_nuevo: boolean;
  total_items: number;
}

export function KitchenDashboard() {
  const [pedidos, setPedidos] = useState<CocinaPedido[]>([]);
  const [loading, setLoading] = useState(true);

  async function fetchPedidos() {
    setLoading(true);
    try {
      const res = await apiClient.get('/ventas/api/pedidos/activos/');
      setPedidos(res.data.pedidos);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchPedidos();
    const interval = setInterval(fetchPedidos, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-6">👨‍🍳 Pedidos en Cocina</h1>
      {loading && <div>Cargando pedidos...</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {pedidos.length === 0 && !loading && (
          <div className="col-span-2 text-center text-gray-400">No hay pedidos en preparación.</div>
        )}
        {pedidos.map((pedido) => (
          <div key={pedido.id} className={`rounded-xl shadow-lg p-5 border-2 ${pedido.estado === 'en_preparacion' ? 'border-yellow-400' : 'border-green-400'} bg-white`}>
            <div className="flex items-center justify-between mb-2">
              <div>
                <span className="font-bold text-lg">#{pedido.id}</span> &nbsp;
                <span className="text-gray-500">{pedido.mesa_o_online}</span>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${pedido.estado === 'en_preparacion' ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'}`}>
                {pedido.estado.replace('_', ' ')}
              </span>
            </div>
            <div className="text-xs text-gray-400 mb-2">Creada: {new Date(pedido.fecha_creacion).toLocaleString()}</div>
            <ul className="mb-2">
              {pedido.items.map((item) => (
                <li key={item.id} className="text-sm">{item.producto} <span className="text-gray-500">x{item.cantidad}</span></li>
              ))}
            </ul>
            {pedido.es_nuevo && <div className="text-red-500 text-xs font-bold animate-pulse">¡NUEVO!</div>}
          </div>
        ))}
      </div>
    </div>
  );
}
