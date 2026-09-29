# Changelog

Tous les changements notables sont documentés ici.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).
Ce projet respecte le [Semantic Versioning](https://semver.org/lang/fr/).

---

## [Unreleased]

## [1.4.0] - 2026-09-27

### Added
- **Paiement sécurisé à la livraison (Connect)** — `client.connect.payments` (sync et async) : `retrieve`, `release`, `refund` (`scope` : `product` / `full` / `amount`), `freeze`, `unfreeze`, `simulate_payment` (sandbox) ; `client.connect.accounts.balance()`, `create_payout()` et `list_payouts()`.
- `idempotency_key=` OBLIGATOIRE sur `release`, `refund` et `create_payout` : `SanghoValidationError` levée avant tout appel réseau si elle manque (un rejeu ne doit jamais dupliquer une opération d'argent).
- `checkout_sessions.create(..., connect={"account", "mode", "commission", "reserve_rate", "external_reference"})` (via `**opts`) ; la réponse porte `connect_payment`.
- Les événements `payment.succeeded/failed`, `funds.released/frozen/unfrozen`, `refund.succeeded`, `clawback.succeeded`, `payout.paid/failed`, `account.verified/restricted` sont acceptés par `construct_event` (`data.object` = paiement, retrait ou compte Connect).

### Changed
- `setup.py` aligné sur `pyproject.toml` (1.4.0).

### Non fait
- Liaison OAuth2 d'un compte existant, en-tête `Sangho-Account` et gestion des clients OAuth (`SANGHO_CLIENT_ID` / `SANGHO_SECRET`) par l'API : non exposés par le backend.

## [1.3.0] - 2026-09-25

### Added
- **Marketplace / Connect** : `client.connect.accounts` (sync et async) — `create` (idempotent par `external_id`, `claim_token` renvoyé une seule fois), `retrieve`, `list`, `reissue_claim_token` et `create_kyc_session` (KYC hébergé par Sangho, `POST /connect/accounts/{id}/kyc-session/`).
- Événements webhook `account.updated` et `kyc.updated` (le payload est le compte Connect dans `data.object`).
- `Webhooks.construct_event` accepte une liste de secrets (rotation) et plusieurs valeurs `v1` ; nouvelle erreur `SanghoWebhookSignatureError` (`reason` : `malformed` / `expired` / `mismatch`) ; helper de test `Sangho.generate_test_header`.
- **Idempotence (PY-04)** : `idempotency_key=` accepté par toutes les méthodes d'écriture.
- `SanghoConflictError` (alias `sangho.error.ConflictError`) : 409 de conflit d'état métier (ex : `account_not_claimed`) ; `SanghoIdempotencyError` reste réservée à l'absence de code ou à `idempotency_conflict`.

### Changed
- `payment_intents.create(amount, currency="XAF", customer_email=None, ...)` : envoie désormais la devise (exigée par le backend) et `customer_email` (PY-01). Les appels existants `create(amount=..., customer=...)` continuent de fonctionner (`customer` transmis tel quel).
- `checkout_sessions.create(line_items, success_url, cancel_url=None, currency="XAF", ...)` : envoie `line_items` exigé par le backend (PY-02) ; l'ancienne signature `create(amount, success_url, cancel_url)` est convertie en une ligne ad hoc avec un `DeprecationWarning`.
- Les réponses d'erreur Connect au format `{"error": {"code", "message"}}` sont lues comme le format plat des autres routes.
- `SanghoWebhookSignatureError` remplace la `SanghoError` générique de `construct_event` (sous-classe de `SanghoError` ; les codes `invalid_signature` / `stale_event` sont conservés).

### Deprecated

- `checkout_sessions.create(amount, ...)` : passez `line_items`.

### Removed

### Fixed
- **PY-03** : un POST n'est plus rejoué après un timeout / une erreur réseau lorsque l'appelant n'a pas fourni de `idempotency_key` (risque de doublon côté serveur, notamment sur `checkout-sessions`) ; avec une clé fournie, le rejeu reste actif.
- **PY-05** : `construct_event` ne lève plus `ValueError` sur `t=abc` ni ne retient que le dernier `v1` ; un corps non JSON lève une `SanghoError` explicite.

### Non fait (voir `sangho_audit_python_sdk_et_backend_api.md`)

- PY-06 (typage strict des réponses), PY-07 (tests d'intégration périmés), PY-08 (packaging `setup.py` / `pyproject.toml`), PY-09 (dérive avec le SDK JS) : hors périmètre de cette mise à jour.
- Liaison OAuth2 d'un compte existant, paiements avec répartition, séquestre : non exposés par le backend.

### Security

---

## [1.2.0] - 2026-09-02

### Added
- **API asynchrone** : `AsyncSangho` (même surface que `Sangho`, chaque
  méthode devient une coroutine), backée par `httpx.AsyncClient`. Toutes les
  ressources ont leur équivalent async (`sangho/resources_async/`).
- **`sangho.error`** : alias des classes d'erreur sous des noms familiers
  (`AuthenticationError`, `RateLimitError`, `InvalidRequestError`,
  `PublicKeyError`, `NotFoundError`, `IdempotencyError`,
  `APIConnectionError`, `APITimeoutError`). Ce sont des alias, pas une
  hiérarchie parallèle : `except sangho.error.AuthenticationError` et
  `except sangho.SanghoAuthError` interceptent la même exception.
- `.github/workflows/ci.yml` : tests sur la matrice Python 3.11/3.12/3.13/3.14.
- `.github/workflows/release.yml` : automatisation de release (bump de
  version, tag git, build, publication PyPI), adapté du workflow du SDK JS.
- Section "Async" et "Gestion des erreurs" dans le README.

### Changed
- `requires-python` : `>=3.11` (au lieu de `>=3.13`, qui contredisait les
  classifiers `3.10`-`3.13` déjà présents). Matrice de compatibilité alignée
  sur la dernière version stable (3.14) et les 3 précédentes : 3.11-3.14.
- `pyproject.toml` : `author` (`nels.holy.allg@gmail.com`), `Homepage`
  (`docs.sangho.ga/api/sdks/python/`), `Repository`/`Issues`
  (`github.com/sangho-sdks/sangho.py`) alignés sur le `package.json` du SDK JS.
- README : badges CI et lien de documentation corrigés (pointaient vers
  `sangho.africa` / `sangho-python`, des domaines/dépôts qui ne correspondent
  à aucune config réelle du projet).
- `ruff target-version` → `py311`, `mypy python_version` → `3.11` (alignés
  sur le nouveau plancher de compatibilité).

### Removed
- `setup.py` — fichier de packaging legacy dupliquant `pyproject.toml`
  (version, `python_requires`, auteur et URL y avaient dérivé et n'étaient
  plus synchronisés). `pyproject.toml` (backend `hatchling`) est
  l'unique source de vérité désormais, comme le `package.json` du SDK JS.

---

## [1.1.0] - 2026-09-01

Mise à jour de parité avec le SDK JS (`sangho-sdk-js`).

### Added
- Nouvelles ressources : `account` (`retrieve`), `addresses` (CRUD complet),
  `terminal` (`readers.*`, `sessions.*`, `offline.*`), `sandbox` (`reset`).
- `customers.list_payment_methods(id)`.
- `checkout_sessions.delete(id)`.
- `invoices.get_pdf_url(id)`.
- `payment_links.archive(id)` / `payment_links.restore(id)` / `payment_links.delete(id)`.
- `transactions.update(id, **payloads)` / `transactions.cancel(id)`.
- `apps.keys(id)`.
- `security.add_allowed_ips(ips)` / `security.remove_allowed_ips(ips)`.
- `HttpClient(..., max_retries=3)` configurable (au lieu d'un nombre de retries fixe).
- `Sangho.construct_event(...)` exposé au niveau du client (en plus de `Webhooks.construct_event`).
- Erreurs réseau distinctes : `SanghoNetworkError`, `SanghoTimeoutError` (les
  exceptions httpx brutes ne remontent plus telles quelles).
- Chaque erreur expose désormais un `.type` (catégorie large), à l'image du SDK JS.
- Headers `X-Sangho-SDK` et `X-Sangho-Environment` sur chaque requête.
- Validation HTTPS du `base_url` (refuse l'envoi de la clé API en clair, sauf
  `localhost`/`127.0.0.1`) et validation stricte du format de clé API.

### Changed
- `base_url` par défaut : `https://api.sangho.ga/v1` (au lieu de `https://api.sangho.com/v1` — mauvais domaine).
- Préfixes de clé API valides : `pk_prod_` / `sk_prod_` / `pk_test_` / `sk_test_`
  (au lieu de `pk_live_` / `sk_live_` qui n'existent pas côté backend).
- `security.retrieve()` / `security.update()` utilisent désormais les bonnes
  routes (`/security/me/`, `/security/update_me/`) au lieu de `/security/`.
- Le retry sur 429 respecte désormais `retry_after` (délai serveur) en
  priorité sur le backoff exponentiel.
- Les erreurs réseau/timeout sont désormais retryées avec le même backoff
  exponentiel que les 429/5xx, au lieu de remonter immédiatement.

### Removed
- `payment_links.deactivate(id)` — remplacé par `archive`/`restore`/`delete`
  (le endpoint `/deactivate/` ne correspond à aucune route backend confirmée).

### Fixed
- `SanghoRateLimitError` lit désormais `retry_after` (et non `retry_later`,
  qui n'existe pas côté backend — le délai de retry n'était jamais respecté).
- Comparaison de `code == "public_key_not_allowed"` désormais insensible à la
  casse (le backend renvoie parfois `PUBLIC_KEY_NOT_ALLOWED`).
- `checkout_sessions.retrieve()` n'exige plus de clé secrète — le backend
  autorise explicitement la clé publique sur cette route (page de
  confirmation côté navigateur).
- Suite de tests mise à jour en conséquence (domaine `.ga`, `retry_after`,
  préfixes `_prod_`, `payment_links.archive` au lieu de `deactivate`).

---

## [1.0.0] - 2026-04-01

### Added
- Version initiale du SDK
- Support de toutes les ressources : apps, customers, products, payment_intents,
  checkout_sessions, invoices, transactions, refunds, subscriptions,
  payment_methods, webhooks, payment_links, addresses, partners
- Gestion complète des erreurs (auth, validation, rate limit, réseau)
- Pagination via ListResponse
