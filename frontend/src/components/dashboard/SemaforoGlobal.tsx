import type { SemaforoSummary } from '@/api/types/cases-types';

interface SemaforoGlobalProps {
  semaforo: SemaforoSummary;
}

export function SemaforoGlobal({ semaforo }: SemaforoGlobalProps) {
  const items = [
    { color: 'bg-green-500', label: 'En tiempo', count: semaforo.verde },
    { color: 'bg-yellow-500', label: 'Por vencer', count: semaforo.amarillo },
    { color: 'bg-red-500', label: 'Vencidos', count: semaforo.rojo },
    { color: 'bg-gray-400', label: 'Sin fecha', count: semaforo.gris },
  ];

  return (
    <div className="flex items-center gap-6">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-2">
          <div className={`w-5 h-5 rounded-full ${item.color} flex items-center justify-center`}>
            <span className="text-[10px] font-bold text-white">{item.count}</span>
          </div>
          <span className="text-sm text-neutral-600">{item.label}</span>
        </div>
      ))}
    </div>
  );
}
