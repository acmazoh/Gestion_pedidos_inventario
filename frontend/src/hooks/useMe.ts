import { useEffect, useState } from 'react';
import { getMe, MeResponse } from '../api/me';

export function useMe() {
  const [me, setMe] = useState<MeResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getMe()
      .then(setMe)
      .catch(() => setError('No se pudo obtener el usuario actual'))
      .finally(() => setLoading(false));
  }, []);

  return { me, loading, error };
}
