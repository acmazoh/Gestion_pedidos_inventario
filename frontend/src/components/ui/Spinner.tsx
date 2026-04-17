/** Spinner de carga centrado. */
export function Spinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const s = { sm: 'h-4 w-4', md: 'h-8 w-8', lg: 'h-12 w-12' }[size];
  return (
    <div className="flex justify-center items-center py-6">
      <div
        className={`${s} animate-spin rounded-full border-4 border-primary-500 border-t-transparent`}
        role="status"
        aria-label="Cargando"
      />
    </div>
  );
}
