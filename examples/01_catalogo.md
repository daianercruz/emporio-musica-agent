
# Test 01 — Catalog Search

**Objective:** Product search, price limits, stock availability, and recommendations.

**Expected tools:** `search_products`

## Actual Conversation

### Message 1

**Customer:**

> Estou começando a aprender violão e tenho um orçamento de até R$ 1.000. Quais modelos vocês têm disponíveis? Pode me mostrar os preços e me ajudar a escolher?

**Téo (actual response):**

> ![Conversation screenshot](images/01_catalogo-01.png)

### Message 2

**Customer:**

> Dessas opções, quais custam até R$ 800? Pode comparar os modelos e explicar as diferenças?

**Téo (actual response):**

> ![Conversation screenshot](images/01_catalogo-02.png)

### Message 3

**Customer:**

> Entre esses modelos de até R$ 800, qual você recomendaria para alguém que está começando? Ele está disponível em estoque?

**Téo (actual response):**

> ![Conversation screenshot](images/01_catalogo-03.png)

## Evaluation

- **Result:** Passed.
- **Observed behavior:**
  - Presented 10 acoustic guitar models within the initial R$ 1,000 budget.
  - Refined the search to 9 models priced at R$ 800 or less.
  - Compared nylon-string and steel-string guitars.
  - Maintained conversational context across all three questions.
  - Recommended the Yamaha C40 and Yamaha F310 for beginners.
  - Reported 12 units of the Yamaha C40 and 14 units of the Yamaha F310 in stock.

- **Notes:**
  - Responses were well-organized and presented in accessible language.
  - The agent demonstrated the ability to refine search results and provide context-aware recommendations.
  - No apparent issues were identified during the interaction.
