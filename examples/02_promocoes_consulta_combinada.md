
# Test 02 — Promotions and Combined Queries

**Objective:** Validate the agent's ability to retrieve active promotions, display prices and discounts, combine information from different sources, perform multiple queries, and maintain conversational context.

**Expected tools:** `get_active_promotions`, `get_product_promotion`, `search_products`, and `search_store_policies` when needed.

## Actual Conversations

### Part 1 — Promotions and Discount Calculations

#### Message 1 — Active Promotions

**Customer:**

> Olá, Téo! Estou procurando um instrumento musical com desconto. Quais promoções estão disponíveis atualmente? Pode me mostrar os produtos, os preços originais e os valores promocionais?

**Téo (actual response):**

![Promotions lookup](images/02_promocoes-01.png)

#### Message 2 — Discount Comparison

**Customer:**

> Dessas promoções que você me mostrou, qual oferece o maior desconto percentual? Quanto eu economizaria comprando esse produto?

**Téo (actual response):**

![Discount comparison](images/02_promocoes-02.png)

#### Message 3 — Product and Stock Verification

**Customer:**

> Gostei desse produto com o maior desconto. Ele está disponível em estoque? Pode confirmar o preço final que eu pagaria?

**Téo (actual response):**

![Price and stock verification](images/02_promocoes-03.png)

### Part 2 — Combined Queries

#### Message 4 — Catalog and Promotions

**Customer:**

> Oi, Téo! Estou procurando um instrumento musical para começar a aprender, com orçamento de até R$ 1.000. Quais opções vocês têm disponíveis? Alguma delas está em promoção?

**Téo (actual response):**

![Combined product and promotion query](images/02_consulta_combinada-01.png)

#### Message 5 — Recommendation and Return Policy

**Customer:**

> Dessas opções, qual você recomendaria para um iniciante? E se eu comprar pela internet e não gostar do instrumento, posso devolver?

**Téo (actual response):**

![Recommendation and return policy](images/02_consulta_combinada-02.png)

#### Message 6 — Availability and Return Conditions

**Customer:**

> Gostei da sua recomendação! Esse instrumento está disponível em estoque? E, se eu precisar devolver por arrependimento, quem paga o frete?

**Téo (actual response):**

![Availability and return conditions](images/02_consulta_combinada-03.png)

## Evaluation

**Result:** Passed conversational evaluation.

### Observed Behavior — Promotions and Discounts

- Presented four products with active promotions, including original prices, promotional prices, and discount percentages.
- Correctly identified the Ukulele Ohana CK-20 Concert Natural as the product with the highest percentage discount among the displayed options (20%).
- Correctly calculated savings of R$ 109.80 from the original price of R$ 549.00.
- Maintained conversational context when identifying the product indirectly referenced in the third question.
- Reported 6 units of the Ukulele Ohana CK-20 Concert Natural in stock.
- Confirmed the promotional price of R$ 439.20, consistent with previous responses.

### Observed Behavior — Combined Queries

- Presented acoustic guitar and ukulele options within the R$ 1,000 budget.
- Identified an active promotion for the Ukulele Kalani KAL-700T Tenor Natural, showing the original price of R$ 359.00 and the promotional price of R$ 323.10, with a 10% discount.
- Recommended the Tagima Memphis AC-39 and Rozini RC-104 acoustic guitars for beginners, explaining the advantages of nylon strings.
- Explained the return conditions for online purchases, including the seven-calendar-day withdrawal period.
- Maintained conversational context when answering follow-up questions about availability and return shipping.
- Reported 15 units of the Tagima Memphis AC-39 and 10 units of the Rozini RC-104 in stock.
- Clarified that the store would cover return shipping costs in cases of withdrawal from an online purchase.
- When faced with the ambiguous reference "esse instrumento", provided stock information for both previously recommended models.

### Notes

- The agent presented promotions clearly and in an organized manner.
- It demonstrated the ability to calculate discounts and interpret questions that depended on previous context.
- It combined different types of information, including product availability, promotions, recommendations, and return policies.
- Responses were clear, contextualized, and consistent with the questions asked.
- The 10% discount shown for the Kalani ukulele is mathematically correct.
- No apparent calculation errors or contradictions were identified within either conversation sequence.
- The correspondence of prices, stock quantities, promotions, and return policies with the source CSV and PDF files has not yet been independently verified.
