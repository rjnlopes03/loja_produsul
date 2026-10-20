import { useCallback, useEffect, useRef, useState } from "react";

export function useApiData(fetchFn, deps, valorInicial) {
  const [dados, setDados] = useState(valorInicial);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  // Só a resposta do pedido mais recente vale: uma anterior que chegue atrasada (filtro ou id
  // trocado no meio) não pode sobrescrever a tela.
  const ultimoPedido = useRef(0);

  // Com `silencioso`, recarrega sem ligar o "carregando" (a tela não pisca nem perde o que está aberto).
  const carregar = useCallback(({ silencioso = false } = {}) => {
    if (!silencioso) setCarregando(true);
    const pedido = ++ultimoPedido.current;
    const atual = () => pedido === ultimoPedido.current;
    return fetchFn()
      .then((resultado) => {
        if (!atual()) return;
        setDados(resultado);
        setErro("");
      })
      .catch((e) => {
        if (atual()) setErro(e.message);
      })
      .finally(() => {
        if (atual()) setCarregando(false);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { dados, carregando, erro, setErro, carregar };
}
