import { prisma } from "@/lib/prisma";
import { registerMovement } from "./actions";

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

  return (
    <div>
      <h1>Estoque</h1>

      <table border={1} cellPadding={6} style={{ borderCollapse: "collapse", marginBottom: 32 }}>
        <thead>
          <tr>
            <th>Produto</th>
            <th>Marca</th>
            <th>Categoria</th>
            <th>Tipo</th>
            <th>Peso</th>
            <th>Estoque</th>
          </tr>
        </thead>
        <tbody>
          {packages.map((pkg) => (
            <tr key={pkg.id}>
              <td>{pkg.product.name}</td>
              <td>{pkg.product.brand.name}</td>
              <td>{pkg.product.category.name}</td>
              <td>{pkg.type === "SACO_FECHADO" ? "Saco fechado" : "Granel"}</td>
              <td>{pkg.weightKg ? `${pkg.weightKg} kg` : "-"}</td>
              <td>
                {pkg.stockQty}
                {pkg.type === "SACO_FECHADO" ? " un" : " kg"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Lançar movimentação</h2>
      <form action={registerMovement} style={{ display: "flex", gap: 8, marginBottom: 32 }}>
        <select name="packageId" required defaultValue="">
          <option value="" disabled>
            Embalagem
          </option>
          {packages.map((pkg) => (
            <option key={pkg.id} value={pkg.id}>
              {pkg.product.name} - {pkg.type === "SACO_FECHADO" ? `Saco ${pkg.weightKg}kg` : "Granel"}
            </option>
          ))}
        </select>
        <select name="type" defaultValue="ENTRADA">
          <option value="ENTRADA">Entrada</option>
          <option value="SAIDA">Saída (venda)</option>
          <option value="ABERTURA_SACO">Abertura de saco (baixa)</option>
          <option value="AJUSTE">Ajuste</option>
        </select>
        <input name="quantity" type="number" step="0.01" placeholder="Quantidade" required />
        <input name="note" placeholder="Observação (opcional)" />
        <button type="submit">Registrar</button>
      </form>

      <h2>Últimas movimentações</h2>
      <table border={1} cellPadding={6} style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Data</th>
            <th>Produto</th>
            <th>Tipo</th>
            <th>Quantidade</th>
            <th>Observação</th>
          </tr>
        </thead>
        <tbody>
          {recentMovements.map((m) => (
            <tr key={m.id}>
              <td>{m.createdAt.toLocaleString("pt-BR")}</td>
              <td>{m.package.product.name}</td>
              <td>{m.type}</td>
              <td>{m.quantity}</td>
              <td>{m.note ?? "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
