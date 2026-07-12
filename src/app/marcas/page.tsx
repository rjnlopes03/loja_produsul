import { prisma } from "@/lib/prisma";
import { createBrand, deleteBrand, updateBrand } from "./actions";

export default async function MarcasPage() {
  const brands = await prisma.brand.findMany({
    orderBy: { name: "asc" },
    include: { _count: { select: { products: true } } },
  });

  return (
    <div>
      <h1 className="text-2xl font-bold text-brand-900">Marcas</h1>
      <p className="mt-1 text-brand-700">
        Marcas de ração cadastradas na loja.
      </p>

      <form
        action={createBrand}
        className="mt-6 flex max-w-md gap-2 rounded-2xl border border-brand-200 bg-white p-4 shadow-sm"
      >
        <input
          name="name"
          placeholder="Nome da marca"
          required
          className="flex-1 rounded-lg border border-brand-200 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none"
        />
        <button
          type="submit"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          Adicionar
        </button>
      </form>

      <div className="mt-8 overflow-hidden rounded-2xl border border-brand-200 bg-white shadow-sm">
        <table className="w-full text-left text-sm">
          <thead className="bg-brand-50 text-brand-700">
            <tr>
              <th className="px-4 py-3 font-medium">Nome</th>
              <th className="px-4 py-3 font-medium">Produtos</th>
              <th className="px-4 py-3 font-medium">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-100">
            {brands.map((brand) => (
              <tr key={brand.id} className="align-middle">
                <td className="px-4 py-3">
                  <form
                    action={updateBrand.bind(null, brand.id)}
                    className="flex items-center gap-2"
                  >
                    <input
                      name="name"
                      defaultValue={brand.name}
                      required
                      className="rounded-lg border border-transparent px-2 py-1 hover:border-brand-200 focus:border-brand-500 focus:outline-none"
                    />
                    <button
                      type="submit"
                      className="rounded-lg px-2 py-1 text-xs font-medium text-brand-700 hover:bg-brand-100"
                    >
                      Salvar
                    </button>
                  </form>
                </td>
                <td className="px-4 py-3 text-brand-700">
                  {brand._count.products}
                </td>
                <td className="px-4 py-3">
                  <form action={deleteBrand.bind(null, brand.id)}>
                    <button
                      type="submit"
                      disabled={brand._count.products > 0}
                      className="rounded-lg px-2 py-1 text-xs font-medium text-red-600 hover:bg-red-50 disabled:cursor-not-allowed disabled:text-brand-300 disabled:hover:bg-transparent"
                    >
                      Excluir
                    </button>
                  </form>
                </td>
              </tr>
            ))}
            {brands.length === 0 && (
              <tr>
                <td colSpan={3} className="px-4 py-6 text-center text-brand-500">
                  Nenhuma marca cadastrada ainda.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
