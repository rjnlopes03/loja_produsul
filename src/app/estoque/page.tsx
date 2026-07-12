import { prisma } from "@/lib/prisma";
import { registerMovement } from "./actions";

const movementLabels: Record<string, string> = {
  ENTRADA: "Entrada",
  SAIDA: "Saída",
  ABERTURA_SACO: "Abertura de saco",
  AJUSTE: "Ajuste",
};

export default async function EstoquePage() {
  const packages = await prisma.productPackage.findMany({
    orderBy: [{ product: { name: "asc" } }],
    include: { product: { include: { brand: true, category: true } } },
  });

  const recentMovements = await prisma.stockMovement.findMany({
    orderBy: { createdAt: "desc" },
    take: 20,
    include: { package: { include: { product: true } } },
  });

  const inputClass =
    "rounded-lg border border-brand-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none";

  return (
    <div>
      <h1 className="text-2xl font-bold text-brand-900">Estoque</h1>
      <p className="mt-1 text-brand-700">
        Saldo atual e movimentações de entrada, saída e ajustes.
      </p>

      <div className="mt-6 overflow-hidden rounded-2xl border border-brand-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-brand-50 text-brand-700">
            <tr>
              <th className="px-4 py-3 font-medium">Produto</th>
              <th className="px-4 py-3 font-medium">Marca</th>
              <th className="px-4 py-3 font-medium">Categoria</th>
              <th className="px-4 py-3 font-medium">Tipo</th>
              <th className="px-4 py-3 font-medium">Peso</th>
              <th className="px-4 py-3 font-medium">Estoque</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-100">
            {packages.map((pkg) => {
              const low = pkg.stockQty <= 5;
              return (
                <tr key={pkg.id}>
                  <td className="px-4 py-3 font-medium text-brand-900">
                    {pkg.product.name}
                  </td>
                  <td className="px-4 py-3 text-brand-700">
                    {pkg.product.brand.name}
                  </td>
                  <td className="px-4 py-3 text-brand-700">
                    {pkg.product.category.name}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={
                        "rounded-full px-2 py-1 text-xs font-medium " +
                        (pkg.type === "SACO_FECHADO"
                          ? "bg-grain-100 text-grain-700"
                          : "bg-brand-100 text-brand-700")
                      }
                    >
                      {pkg.type === "SACO_FECHADO" ? "Saco fechado" : "Granel"}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-brand-700">
                    {pkg.weightKg ? `${pkg.weightKg} kg` : "-"}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={
                        "font-semibold " +
                        (low ? "text-red-600" : "text-brand-900")
                      }
                    >
                      {pkg.stockQty}
                      {pkg.type === "SACO_FECHADO" ? " un" : " kg"}
                    </span>
                    {low && (
                      <span className="ml-2 rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-600">
                        baixo
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
            {packages.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-brand-500">
                  Nenhuma embalagem cadastrada ainda.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <h2 className="mt-10 text-lg font-semibold text-brand-900">
        Lançar movimentação
      </h2>
      <form
        action={registerMovement}
        className="mt-3 flex flex-wrap items-center gap-2 rounded-2xl border border-brand-200 bg-white p-4 shadow-sm"
      >
        <select
          name="packageId"
          required
          defaultValue=""
          className={`${inputClass} min-w-56`}
        >
          <option value="" disabled>
            Embalagem
          </option>
          {packages.map((pkg) => (
            <option key={pkg.id} value={pkg.id}>
              {pkg.product.name} -{" "}
              {pkg.type === "SACO_FECHADO" ? `Saco ${pkg.weightKg}kg` : "Granel"}
            </option>
          ))}
        </select>
        <select name="type" defaultValue="ENTRADA" className={inputClass}>
          <option value="ENTRADA">Entrada</option>
          <option value="SAIDA">Saída (venda)</option>
          <option value="ABERTURA_SACO">Abertura de saco (baixa)</option>
          <option value="AJUSTE">Ajuste</option>
        </select>
        <input
          name="quantity"
          type="number"
          step="0.01"
          placeholder="Quantidade"
          required
          className={`${inputClass} w-32`}
        />
        <input
          name="note"
          placeholder="Observação (opcional)"
          className={`${inputClass} flex-1 min-w-40`}
        />
        <button
          type="submit"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Registrar
        </button>
      </form>

      <h2 className="mt-10 text-lg font-semibold text-brand-900">
        Últimas movimentações
      </h2>
      <div className="mt-3 overflow-hidden rounded-2xl border border-brand-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-brand-50 text-brand-700">
            <tr>
              <th className="px-4 py-3 font-medium">Data</th>
              <th className="px-4 py-3 font-medium">Produto</th>
              <th className="px-4 py-3 font-medium">Tipo</th>
              <th className="px-4 py-3 font-medium">Quantidade</th>
              <th className="px-4 py-3 font-medium">Observação</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-100">
            {recentMovements.map((m) => (
              <tr key={m.id}>
                <td className="px-4 py-3 text-brand-700">
                  {m.createdAt.toLocaleString("pt-BR")}
                </td>
                <td className="px-4 py-3 text-brand-900">
                  {m.package.product.name}
                </td>
                <td className="px-4 py-3 text-brand-700">
                  {movementLabels[m.type] ?? m.type}
                </td>
                <td className="px-4 py-3 text-brand-900">{m.quantity}</td>
                <td className="px-4 py-3 text-brand-700">{m.note ?? "-"}</td>
              </tr>
            ))}
            {recentMovements.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-6 text-center text-brand-500">
                  Nenhuma movimentação registrada ainda.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
