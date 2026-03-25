# Additional audit notes beyond the checklist

I applied a low-risk textual patch separately, but I did **not** blindly edit the concrete-security numerics because the uploaded source still has three deeper issues that should be resolved first.

## 1) `B_k` in the parameter table is inconsistent with the formula stated in Setup

**Source locations**
- Formula: lines 372–373 of the uploaded `.tex`
- Concrete table: lines 1026–1033
- Derived Set I restart calculation: line 649

**What the source currently states**
- Formula: `B_d = s_d\sqrt{2n}`, `B_x = \sigma_u\sqrt{2n+4}`, `B_k = B_d + B_x`
- Table values: `B_k = 83.3` (Set I), `65.8` (Set III)
- The restart analysis then uses `\alpha = 128/83.3 \approx 1.536` for Set I.

**What those formulas actually give**
Using the values already in the paper:

- **Set I**: `n=512`, `s_d=5.0`, `\sigma_u=2.60`
  - `B_d = 5.0 * sqrt(1024) = 160.0`
  - `B_x = 2.60 * sqrt(1028) \approx 83.36`
  - `B_k = B_d + B_x \approx 243.36`
  - therefore `\alpha = 128 / 243.36 \approx 0.526`, **not** `1.54`

- **Set III**: `n=1024`, `s_d=3.0`, `\sigma_u=1.45`
  - `B_d = 3.0 * sqrt(2048) \approx 135.76`
  - `B_x = 1.45 * sqrt(2052) \approx 65.68`
  - `B_k = B_d + B_x \approx 201.45`
  - therefore `\alpha = 325 / 201.45 \approx 1.61`, **not** `4.94`

**Why this matters**
This cascades into:
- the claimed rejection probabilities,
- the “Set III is effectively non-aborting” narrative,
- and the runtime / restart interpretation.

Unless the bound in line 372 is changed, the concrete table and the restart analysis are not internally consistent.

## 2) The theorem-level Ring-SIS bound `\beta` appears vacuous for the concrete parameter sets

**Source locations**
- Theorem 6.1 / 6.2 bounds: lines 670 and 682
- Concrete-security table: line 1080
- Aggregated-signature bound formula: line 372

**What the source currently states**
- The theorems use
  - `\beta \le 2B_s + 2\kappa B_k(|L^*|+1)`
- The concrete table still prints
  - `2B_s + 2\kappa B_k`

**Even under the optimistic table values for `B_k`, the theorem-level `\beta` is already larger than `q`**
Taking the paper’s own `N=10` setting, so `|L^*|+1 = 11`:

- **Set I**
  - `B_s = 2Nr\sqrt{2n} = 2*10*128*sqrt(1024) = 81920`
  - using the table’s optimistic `B_k = 83.3`
  - `\beta \approx 2*81920 + 2*58*83.3*11 \approx 270130.8`
  - but `q = 12289`

- **Set III**
  - `B_s = 2*10*325*sqrt(2048) \approx 294156.42`
  - using the table’s optimistic `B_k = 65.8`
  - `\beta \approx 773605.64`
  - but `q = 50177`

So `\beta > q` by a wide margin in both sets. Under the paper’s own Ring-SIS definition (Definition 2.2), the vector `(q,0)` is then already a non-zero solution of norm `q`, which means a direct concrete hardness claim for that theorem-level instance is not meaningful.

**Why this matters**
This is why I did **not** simply update Table 3’s `\beta` row and leave the core-SVP / hardness rows unchanged. That would make the table formally match the theorem, but the resulting concrete-security interpretation would still be unsound.

## 3) The Type I extractor appears to use an unknown target secret explicitly

**Source location**
- Lines 796–800

**As written**
The Type I proof defines
- `u_1 = \Delta z^{(1)} - \tilde{s}_{1}^* \cdot \Delta c_{i^*}' - \sum_{i\in\mathcal K} \tilde{s}_{i,1}\cdot \Delta c_i'`
- `u_2 = \Delta z^{(2)} - \tilde{s}_{2}^* \cdot \Delta c_{i^*}' - \sum_{i\in\mathcal K} \tilde{s}_{i,2}\cdot \Delta c_i'`

But in the Type I reduction, the whole point of the target signer is that the reduction does **not** know the bound partial key for the target registered pair. As written, it is therefore unclear how the reduction can compute the target effective secret `\tilde{\mathbf{s}}^*` needed to form `(u_1,u_2)`.

**Why this matters**
This is more serious than a presentation issue. It affects whether the extractor is executable at all.

## Practical recommendation

I would fix the paper in this order:

1. Decide whether line 372 is the intended concrete bound, or whether the parameter table is the intended concrete interpretation.
2. Re-derive `B_k`, `\alpha`, and restart claims from a single consistent convention.
3. Revisit the extraction bound so that the theorem-level Ring-SIS target is non-vacuous for the concrete sets.
4. Rework the Type I extraction so the reduction never needs the unknown target effective key explicitly.
5. Only after that, regenerate the concrete-security table.

## Separate artifact produced

I also produced a compilable **textual patch** that applies the low-risk checklist edits only:
- author / title-page cleanup,
- PoP remark,
- sign-bit-emulator downgrade,
- nonzero challenge-difference lemma,
- runtime-section relabeling,
- table-heading / wording cleanup.

That patch does **not** claim to resolve the three structural issues above.
