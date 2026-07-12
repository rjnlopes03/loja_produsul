import { prisma } from "@/lib/prisma";
import {
  addPackage,
  createProduct,
  deletePackage,
  deleteProduct,
} from "./actions";

export default async function ProdutosPage() {
  const [products, brands, categories] = await Promise.all([
    prisma.product.findMany({
      orderBy: { name: "asc" },
      include: { brand: true, category: true, packages: true },
    }),
    prisma.brand.findMany({ orderBy: { name: "asc" } }),
    prisma.animalCategory.findMany({ orderBy: { name: "asc" } }),
  ]);

  return (
    <div>
      <h1>Produtos</h1>

      <form
        action={createProduct}
        style={{ display: "flex", gap: 8, marginBottom: 32 }}
      >
        <input name="name" placeholder="Nome do produto" required />
        <select name="brandId" required defaultValue="">
          <option value="" disabled>
            Marca
          </option>
          {brands.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
        <select name="categoryId" required defaultValue="">
          <option value="" disabled>
            Categoria de animal
          </option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <button type="submit">Adicionar produto</button>
      </form>

      {products.map((product) => (
        <div
          key={product.id}
          style={{
            border: "1px solid #ccc",
            borderRadius: 8,
            padding: 16,
            marginBottom: 16,
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <h3>
              {product.name} — {product.brand.name} ({product.category.name})
            </h3>
            <form action={deleteProduct.bind(null, product.id)}>
              <button type="submit" disabled={product.packages.length > 0}>
                Excluir produto
              </button>
            </form>
          </div>

          <table border={1} cellPadding={6} style={{ borderCollapse: "collapse", marginBottom: 12 }}>
            <thead>
              <tr>
                <th>Tipo</th>
                <th>Peso (kg)</th>
                <th>Preço</th>
                <th>Estoque</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {product.packages.map((pkg) => (
                <tr key={pkg.id}>
                  <td>{pkg.type === "SACO_FECHADO" ? "Saco fechado" : "Granel"}</td>
                  <td>{pkg.weightKg ?? "-"}</td>
                  <td>R$ {pkg.price.toFixed(2)}</td>
                  <td>
                    {pkg.stockQty}
                    {pkg.type === "SACO_FECHADO" ? " un" : " kg"}
                  </td>
                  <td>
                    <form action={deletePackage.bind(null, pkg.id)}>
                      <button type="submit">Excluir</button>
                    </form>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <form
            action={addPackage.bind(null, product.id)}
            style={{ display: "flex", gap: 8 }}
          >
            <select name="type" defaultValue="SACO_FECHADO">
              <option value="SACO_FECHADO">Saco fechado</option>
              <option value="GRANEL">Granel</option>
            </select>
            <input
              name="weightKg"
              type="number"
              step="0.01"
              placeholder="Peso do saco (kg)"
            />
            <input
              name="price"
              type="number"
              step="0.01"
              placeholder="Preço"
              required
            />
            <input
              name="stockQty"
              type="number"
              step="0.01"
              placeholder="Estoque inicial"
              defaultValue={0}
            />
            <button type="submit">Adicionar embalagem</button>
          </form>
        </div>
      ))}
    </div>
  );
}
