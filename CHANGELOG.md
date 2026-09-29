# Changelog

Tous les changements notables sont documentés ici.

Format basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).
Ce projet respecte le [Semantic Versioning](https://semver.org/lang/fr/).

---

## [Unreleased]

> **Versionnement.** Les versions 1.0.0 à 1.2.0 ci-dessous étaient internes : ce SDK n'a jamais été publié
> (PyPI). La numérotation est réalignée sur celle du SDK JS (`@sanghosdk/js` 0.1.4, seul SDK publié), comme le
> demande `CONTRIBUTING.md` (« tous les SDKs sont versionnés de façon synchronisée »). Version courante : **0.1.4**.

### Added
- `subscriptions.reactivate(id)` — `POST /subscriptions/{id}/reactivate/`.
- `webhooks.enable(id)`, `webhooks.disable(id)`, `webhooks.retrieve_delivery(id, delivery_id)`.
- `receipts.get_pdf_url(id)` — `GET /receipts/{id}/pdf/` (URL signée `{url, expires_at}`).
- `payment_intents.delete(id)` — `DELETE /payment-intents/{id}/` (alias de `cancel`, comme chez Stripe).

### Changed
- **Breaking** : `PaginatedResponse` expose `data` (et non `results`), conformément à la pagination réelle de l'API.
- `customers.list_payment_methods(id)` filtre `GET /payment-methods/?customer=<id>` (la route
  `/customers/{id}/payment-methods/` n'existe pas côté API).

### Removed
Méthodes qui appelaient des routes **inexistantes** côté API (elles répondaient 404/405) :
`apps.roll_secret`, `customers.list_transactions` (l'API n'a pas de filtre `customer` sur les transactions),
`invoices.finalize`, `partners.create/update/delete` (ressource en lecture seule),
`payment_methods.create/update/delete` (utiliser `attach`/`detach`/`set_default`), `products.archive/restore`,
`receipts.send`, `refunds.update`, `security.roll_secret_key/list_sessions/revoke_session`.

### Fixed
- Version du SDK (`__version__`, en-tête `X-Sangho-SDK`, `pyproject.toml`) alignée sur 0.1.4.

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
