
# Test 03 — Order Lookup and Privacy

**Objective:** Validate order lookups, customer information protection, and conversational context retention throughout the interaction.

**Expected tool:** `get_order`

## Actual Conversation

### Message 1 — Order Lookup Without Complete Identification

**Customer:**

> Olá, Téo! Fiz uma compra na loja e gostaria de saber o status do meu pedido número 11. Você consegue consultar para mim?

**Téo (actual response):**

![Initial order lookup](images/03_consulta_pedido-01.png)

### Message 2 — Order Lookup Attempt Without Verification

**Customer:**

> Não lembro qual e-mail utilizei na compra. Você consegue me informar o status do pedido mesmo assim?

**Téo (actual response):**

![Order lookup attempt without verification](images/03_consulta_pedido-02.png)

### Message 3 — Customer Identification

**Customer:**

> mariana.costa@inlook.com

**Téo (actual response):**

![Order lookup with email](images/03_consulta_pedido-03.png)

## Evaluation

- **Result:** Passed.

- **Observed behavior:**
  - Requested the email address associated with the order before disclosing purchase information.
  - Did not reveal the order status or details when the customer stated that they could not remember the email address.
  - Retained order number 11 in the conversational context throughout the interaction.
  - Interpreted the email address provided on its own as a continuation of the previous request.
  - After receiving the email address, retrieved the order and reported its status as confirmed.
  - Presented the purchase date (March 5, 2026), payment method (bank payment slip — boleto), and purchased product (1 unit of the Ukulele Tenor Kalani KAL-700T Natural).

- **Notes:**
  - The agent maintained clear and appropriate customer service communication.
  - Demonstrated conversational continuity without requiring the customer to repeat the order number.
  - No apparent issues were identified in the conversational verification process.
  - The complete correspondence between the displayed order details and the source CSV files still needs to be verified.
  - Verification using an order number and email address provides basic protection for the prototype but does not replace proper authentication in a production environment.
