"use server";

import { revalidatePath } from "next/cache";
import { prisma } from "@/lib/prisma";

export async function registerMovement(formData: FormData) {
  const packageId = String(formData.get("packageId") ?? "");
  const type = String(formData.get("type") ?? "ENTRADA") as
    | "ENTRADA"
    | "SAIDA"
    | "ABERTURA_SACO"
    | "AJUSTE";
  const quantity = Number(formData.get("quantity") ?? 0);
  const note = String(formData.get("note") ?? "").trim() || null;

  if (!packageId || !quantity) return;

  const delta =
    type === "SAIDA" || type === "ABERTURA_SACO" ? -Math.abs(quantity) : Math.abs(quantity);

  await prisma.$transaction([
    prisma.stockMovement.create({
      data: { packageId, type, quantity, note },
    }),
    prisma.productPackage.update({
      where: { id: packageId },
      data: { stockQty: { increment: delta } },
    }),
  ]);

  revalidatePath("/estoque");
}
