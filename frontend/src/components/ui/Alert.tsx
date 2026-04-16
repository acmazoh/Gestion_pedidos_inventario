import type { AlertType } from '../../types';

const STYLES: Record<AlertType, string> = {
  success: 'bg-green-50 border-green-400 text-green-800',
  error:   'bg-red-50  border-red-400  text-red-800',
  warning: 'bg-yellow-50 border-yellow-400 text-yellow-800',
  info:    'bg-blue-50  border-blue-400  text-blue-800',
};

const ICONS: Record<AlertType, string> = {
  success: '✓', error: '✕', warning: '⚠', info: 'ℹ',
};

interface AlertProps {
  type: AlertType;
  message: string;
  onClose?: () => void;
}

/** Alerta visual reutilizable con botón de cierre opcional. */
export function Alert({ type, message, onClose }: AlertProps) {
  return (
    <div className={`flex items-start gap-3 rounded-lg border px-4 py-3 ${STYLES[type]}`} role="alert">
      <span className="text-lg font-bold select-none">{ICONS[type]}</span>
      <p className="flex-1 text-sm">{message}</p>
      {onClose && (
        <button
          onClick={onClose}
          className="ml-auto text-current opacity-60 hover:opacity-100 transition-opacity"
          aria-label="Cerrar alerta"
        >
          ✕
        </button>
      )}
    </div>
  );
}
