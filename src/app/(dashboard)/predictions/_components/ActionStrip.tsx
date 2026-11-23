import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { Severity } from "@/modules/telemetry-ingestion/domain/telemetry-row";

const TEMPLATES: Record<Severity, string[]> = {
  critical: [
    "Priorizar la inspección de este Product ID con la última captura de sensores.",
    "Comparar la probabilidad del modelo con la etiqueta CSV Machine failure antes de despachar.",
  ],
  warning: [
    "Monitorear torque y desgaste de herramienta en la próxima ventana UDI.",
    "Revisar el delta de temperatura de proceso contra muestras sanas cercanas.",
  ],
  ok: [
    "No hay riesgo elevado del modelo para esta captura.",
    "Mantener la revisión periódica de telemetría sobre la secuencia UDI.",
  ],
};

export function ActionStrip({
  severity,
  probability,
}: {
  severity: Severity | null;
  probability: number | null;
}): React.JSX.Element {
  if (severity === null || probability === null) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Acciones recomendadas</CardTitle>
          <CardDescription>
            No hay plantilla de acción hasta que la inferencia tenga éxito.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Acciones recomendadas</CardTitle>
        <CardDescription>
          Solo plantillas fijas por severidad — sin asistente RAG en este
          cambio.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <ul className="list-disc space-y-2 pl-5 text-sm text-[var(--fg-2)]">
          {TEMPLATES[severity].map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
