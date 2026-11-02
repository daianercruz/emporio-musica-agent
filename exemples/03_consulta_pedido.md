
# Teste 03 — Consulta de pedido e privacidade

**Objetivo:** Validar a consulta de pedidos, a proteção das informações do cliente e a manutenção do contexto durante o atendimento.

**Ferramenta esperada:** `get_order`

## Transcrição real

### Mensagem 1 — Consulta sem identificação completa

**Cliente:**

> Olá, Téo! Fiz uma compra na loja e gostaria de saber o status do meu pedido número 11. Você consegue consultar para mim?

**Téo (resposta real):**

![Consulta inicial do pedido](images/03_consulta_pedido-01.png)

### Mensagem 2 — Tentativa de consulta sem validação

**Cliente:**

> Não lembro qual e-mail utilizei na compra. Você consegue me informar o status do pedido mesmo assim?

**Téo (resposta real):**

![Tentativa de consulta sem validação](images/03_consulta_pedido-02.png)

### Mensagem 3 — Identificação do cliente

**Cliente:**

> mariana.costa@inlook.com

**Téo (resposta real):**

![Consulta do pedido com e-mail](images/03_consulta_pedido-03.png)

## Avaliação

- **Resultado:** Aprovado.

- **Comportamento observado:**
  - Solicitou o e-mail associado ao pedido antes de apresentar informações da compra.
  - Não revelou o status nem os detalhes do pedido quando o cliente informou que não lembrava o e-mail.
  - Manteve o número do pedido 11 no contexto durante toda a conversa.
  - Interpretou o envio isolado do endereço de e-mail como continuação da solicitação anterior.
  - Após receber o e-mail, localizou o pedido e informou seu status como confirmado.
  - Apresentou a data da compra (05/03/2026), a forma de pagamento (boleto) e o produto adquirido (1 unidade do Ukulele Tenor Kalani KAL-700T Natural).

- **Observações:**
  - O agente manteve uma comunicação clara e adequada ao atendimento.
  - Demonstrou continuidade de contexto sem exigir que o cliente repetisse o número do pedido.
  - Não foram identificadas falhas aparentes na validação conversacional.
  - A correspondência completa dos dados apresentados com os arquivos CSV ainda precisa ser conferida.
  - A validação por número do pedido e e-mail é uma proteção básica do protótipo e não substitui autenticação em produção.
