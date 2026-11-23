import { BackLink } from "@/components/BackLink";

export default function AssetNotFound(): React.JSX.Element {
  return (
    <div className="space-y-3">
      <BackLink href="/operations" label="Regresar a operación" />
      <h1 className="text-xl font-semibold">Activo no encontrado</h1>
      <p className="text-sm text-[var(--fg-2)]">
        Ese Product ID no existe en el CSV procesado de AI4I.
      </p>
    </div>
  );
}
