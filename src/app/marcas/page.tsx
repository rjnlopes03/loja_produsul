import { prisma } from "@/lib/prisma";
import { createBrand, deleteBrand, updateBrand } from "./actions";

export default async function MarcasPage() {
  const brands = await prisma.brand.findMany({
    orderBy: { name: "asc" },
    include: { _count: { select: { products: true } } },
  });

  return (
    <div>
      <h1>Marcas</h1>

      <form action={createBrand} style={{ marginBottom: 24 }}>
        <input name="name" placeholder="Nome da marca" required />
        <button type="submit">Adicionar</button>
      </form>

      <table border={1} cellPadding={8} style={{ borderCollapse: "collapse" }}>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Produtos cadastrados</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {brands.map((brand) => (
            <tr key={brand.id}>
              <td>
                <form
                  action={updateBrand.bind(null, brand.id)}
                  style={{ display: "flex", gap: 8 }}
                >
                  <input name="name" defaultValue={brand.name} required />
                  <button type="submit">Salvar</button>
                </form>
              </td>
              <td>{brand._count.products}</td>
              <td>
                <form action={deleteBrand.bind(null, brand.id)}>
                  <button type="submit" disabled={brand._count.products > 0}>
                    Excluir
                  </button>
                </form>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
