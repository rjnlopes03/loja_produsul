import Link from "next/link";

export default function Home() {
  return (
    <div>
      <h1>Controle de Estoque - Produsul Cereais</h1>
      <ul>
        <li>
          <Link href="/marcas">Marcas</Link>
        </li>
        <li>
          <Link href="/produtos">Produtos</Link>
        </li>
        <li>
          <Link href="/estoque">Estoque</Link>
        </li>
      </ul>
    </div>
  );
}
