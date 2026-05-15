# UI Mockup (ASCII)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  [QR]  Product QR                                       Agross team  [Logout]│
├────────────────┬─────────────────────────────────────────────────────────────┤
│ ▣ Dashboard    │  Generate Codes                                              │
│ ▣ Generate     │  ─────────────────────────────────────────────────────────── │
│ ▣ Batches      │  Product: [ Vajeer (VJ) ▾ ]    Quantity: [ 1L (1000) ▾ ]      │
│  SETTINGS      │  Month:   [ Jun ▾ ]            Year:     [ 2026 ▾ ]          │
│ ▣ Products     │  Preset:  [ Sales Team — 91999... ▾ ]                         │
│ ▣ Quantities   │  Count:   [   500   ]                                         │
│ ▣ Presets      │                                       [ Generate Codes ]      │
│ ▣ Zoho         │                                                               │
│ ▣ Short Domain │  ┌─ Result ──────────────────────────────────────────────┐    │
│                │  │ Batch        BATCH_20260514_001                       │    │
│                │  │ Generated    500 / 500                                │    │
│                │  │ Zoho synced  498 │ Failed 2                            │    │
│                │  │ [ Download Excel ]   [ View Batch ]                   │    │
│                │  │ Samples:                                              │    │
│                │  │   VJ10002606AB12C                                     │    │
│                │  │   VJ100026069X7QM                                     │    │
│                │  └───────────────────────────────────────────────────────┘    │
└────────────────┴─────────────────────────────────────────────────────────────┘
```

## Color & layout cues

- **Sidebar**: 256 px wide on desktop, slides out as a drawer below `lg`.
- **Top bar**: 64 px, sticky, contains the avatar block + logout.
- **Cards**: `bg-white` + `border` + `rounded-xl` (`.card` utility in `index.css`).
- **Primary action color**: `brand-600` (`#2a52d6`).
- **Status pills**: green = SYNCED/USED, amber = PENDING, red = FAILED, slate = UNUSED.

## Page list (with route)

| Route                          | Purpose                                    |
| ------------------------------ | ------------------------------------------ |
| `/login`                       | JWT login                                  |
| `/`                            | KPI tiles + recent batches                 |
| `/generate`                    | Generation form + result panel             |
| `/batches`                     | Sortable list of all batches               |
| `/batches/:id`                 | Per-batch detail + retry-failed-Zoho       |
| `/products`                    | CRUD products                              |
| `/quantities`                  | CRUD quantities                            |
| `/presets`                     | CRUD WhatsApp presets + set-default        |
| `/settings/zoho`               | Zoho OAuth + module config                 |
| `/settings/short-domain`       | Short domain URL                           |
