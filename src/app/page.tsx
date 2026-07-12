import Link from "next/link";

const cards = [
  {
    href: "/marcas",
    icon: "🏷️",
    title: "Marcas",
    description: "Cadastre e gerencie as marcas de ração da loja.",
  },
  {
    href: "/produtos",
    icon: "🐾",
    title: "Produtos",
    description:
      "Rações por categoria de animal, com variações de saco fechado e granel.",
  },
  {
    href: "/estoque",
    icon: "📦",
    title: "Estoque",
    description: "Acompanhe o saldo e registre entradas, saídas e ajustes.",
  },
];

export default function Home() {
  return (
    <div>
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-brand-900">
          Controle de Estoque
        </h1>
        <p className="mt-2 text-brand-700">
          Gerencie marcas, produtos e o estoque de rações da Produsul
          Cereais.
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="group rounded-2xl border border-brand-200 bg-white p-6 shadow-sm transition-all hover:-translate-y-0.5 hover:border-brand-400 hover:shadow-md"
          >
            <span className="text-3xl">{card.icon}</span>
            <h2 className="mt-4 text-lg font-semibold text-brand-900 group-hover:text-brand-700">
              {card.title}
            </h2>
            <p className="mt-1 text-sm text-brand-700">{card.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
