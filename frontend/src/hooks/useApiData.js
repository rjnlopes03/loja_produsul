import { useCallback, useEffect, useState } from "react";

export function useApiData(fetchFn, deps, valorInicial) {
  const [dados, setDados] = useState(valorInicial);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const carregar = useCallback(() => {
    setCarregando(true);
    return fetchFn()
      .then((resultado) => {
        setDados(resultado);
        setErro("");
      })
      .catch((e) => setErro(e.message))
      .finally(() => setCarregando(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { dados, carregando, erro, setErro, carregar };
}
