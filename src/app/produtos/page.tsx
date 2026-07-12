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

  const inputClass =
    "rounded-lg border border-brand-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none";

  return (
    <div>
      <h1 className="text-2xl font-bold text-brand-900">Produtos</h1>
      <p className="mt-1 text-brand-700">
        Rações cadastradas, por marca e categoria de animal.
      </p>

      <form
        action={createProduct}
        className="mt-6 flex flex-wrap gap-2 rounded-2xl border border-brand-200 bg-white p-4 shadow-sm"
      >
        <input
          name="name"
          placeholder="Nome do produto"
          required
          className={`${inputClass} flex-1 min-w-48`}
        />
        <select name="brandId" required defaultValue="" className={inputClass}>
          <option value="" disabled>
            Marca
          </option>
          {brands.map((b) => (
            <option key={b.id} value={b.id}>
              {b.name}
            </option>
          ))}
        </select>
        <select
          name="categoryId"
          required
          defaultValue=""
          className={inputClass}
        >
          <option value="" disabled>
            Categoria de animal
          </option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Adicionar produto
        </button>
      </form>

      <div className="mt-8 space-y-6">
        {products.map((product) => (
          <div
            key={product.id}
            className="rounded-2xl border border-brand-200 bg-white p-6 shadow-sm"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <h3 className="text-lg font-semibold text-brand-900">
                  {product.name}
                </h3>
                <div className="mt-1 flex gap-2 text-xs">
                  <span className="rounded-full bg-brand-100 px-2 py-1 font-medium text-brand-700">
                    {product.brand.name}
                  </span>
                  <span className="rounded-full bg-grain-100 px-2 py-1 font-medium text-grain-700">
                    {product.category.name}
                  </span>
                </div>
              </div>
              <form action={deleteProduct.bind(null, product.id)}>
                <button
                  type="submit"
                  disabled={product.packages.length > 0}
                  className="rounded-lg px-3 py-1 text-xs font-medium text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:text-brand-300 disabled:hover:bg-transparent"
                >
                  Excluir produto
                </button>
              </form>
            </div>

            {product.packages.length > 0 && (
              <div className="mt-4 overflow-hidden rounded-xl border border-brand-100">
                <table className="w-full text-left text-sm">
                  <thead className="bg-brand-50 text-brand-700">
                    <tr>
                      <th className="px-3 py-2 font-medium">Tipo</th>
                      <th className="px-3 py-2 font-medium">Peso</th>
                      <th className="px-3 py-2 font-medium">Preço</th>
                      <th className="px-3 py-2 font-medium">Estoque</th>
                      <th className="px-3 py-2 font-medium">Ações</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-brand-100">
                    {product.packages.map((pkg) => (
                      <tr key={pkg.id}>
                        <td className="px-3 py-2">
                          <span
                            className={
                              "rounded-full px-2 py-1 text-xs font-medium " +
                              (pkg.type === "SACO_FECHADO"
                                ? "bg-grain-100 text-grain-700"
                                : "bg-brand-100 text-brand-700")
                            }
                          >
                            {pkg.type === "SACO_FECHADO"
                              ? "Saco fechado"
                              : "Granel"}
                          </span>
                        </td>
                        <td className="px-3 py-2 text-brand-800">
                          {pkg.weightKg ? `${pkg.weightKg} kg` : "-"}
                        </td>
                        <td className="px-3 py-2 text-brand-800">
                          R$ {pkg.price.toFixed(2)}
                        </td>
                        <td className="px-3 py-2 font-medium text-brand-900">
                          {pkg.stockQty}
                          {pkg.type === "SACO_FECHADO" ? " un" : " kg"}
                        </td>
                        <td className="px-3 py-2">
                          <form action={deletePackage.bind(null, pkg.id)}>
                            <button
                              type="submit"
                              className="text-xs font-medium text-red-600 hover:underline"
                            >
                              Excluir
                            </button>
                          </form>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <form
              action={addPackage.bind(null, product.id)}
              className="mt-4 flex flex-wrap items-center gap-2"
            >
              <select name="type" defaultValue="SACO_FECHADO" className={inputClass}>
                <option value="SACO_FECHADO">Saco fechado</option>
                <option value="GRANEL">Granel</option>
              </select>
              <input
                name="weightKg"
                type="number"
                step="0.01"
                placeholder="Peso do saco (kg)"
                className={`${inputClass} w-40`}
              />
              <input
                name="price"
                type="number"
                step="0.01"
                placeholder="Preço"
                required
                className={`${inputClass} w-28`}
              />
              <input
                name="stockQty"
                type="number"
                step="0.01"
                placeholder="Estoque inicial"
                defaultValue={0}
                className={`${inputClass} w-36`}
              />
              <button
                type="submit"
                className="rounded-lg border border-brand-300 px-4 py-2 text-sm font-medium text-brand-700 hover:bg-brand-100"
              >
                + Embalagem
              </button>
            </form>
          </div>
        ))}

        {products.length === 0 && (
          <p className="rounded-2xl border border-dashed border-brand-300 p-8 text-center text-brand-500">
            Nenhum produto cadastrado ainda.
          </p>
        )}
      </div>
    </div>
  );
}
