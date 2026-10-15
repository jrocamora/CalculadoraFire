"""
Calculadors fiscals per a Catalunya, Irlanda i Andorra.
Port fidel de src/utils/taxCalculators.ts
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from models.types import (
    CountryCode,
    CountryDetails,
    TaxComputationResult,
    TaxSettings,
)


# ═══════════════════════════════════════════════════════════════════════════
# IRPF Estalvi (Rendiments de Capital Mobiliari i Guanys Patrimonials)
# Trams estatals i autonòmics (50% Generalitat / 50% Estat):
#   Fins a 6.000 €: 19%
#   6.000 a 50.000 €: 21%
#   50.000 a 200.000 €: 23%
#   200.000 a 300.000 €: 27%
#   Més de 300.000 €: 28%
# ═══════════════════════════════════════════════════════════════════════════
def calculate_savings_tax(
    taxable_base: float,
    reform_adjustment: float = 0.0,
) -> tuple[float, float]:
    """Retorna (tax, marginal_rate)."""
    if taxable_base <= 0:
        return 0.0, 0.0

    brackets = [
        (6_000, 0.19),
        (50_000, 0.21),
        (200_000, 0.23),
        (300_000, 0.27),
        (float("inf"), 0.28),
    ]

    tax = 0.0
    previous_limit = 0.0
    marginal_rate = 0.19

    for limit, rate in brackets:
        adjusted_rate = max(0.0, rate + reform_adjustment / 100)
        if taxable_base > previous_limit:
            taxable_in_bracket = min(taxable_base, limit) - previous_limit
            tax += taxable_in_bracket * adjusted_rate
            marginal_rate = adjusted_rate
        if taxable_base <= limit:
            break
        previous_limit = limit

    return tax, marginal_rate


# ═══════════════════════════════════════════════════════════════════════════
# Impost sobre el Patrimoni a Catalunya (Decret Legislatiu 1/2008)
# - Mínim exempt: 500.000 €
# - Tarifa pròpia catalana (0,210% al 3,480%)
# - Limit conjunt IRPF-Patrimoni 60% (escut fiscal)
# - Reducció màxima 80%
# ═══════════════════════════════════════════════════════════════════════════
@dataclass
class WealthTaxResult:
    wealth_tax: float
    marginal_rate: float
    is_limited_by_shield: bool


def calculate_catalonia_wealth_tax(
    net_worth: float,
    irpf_taxable_base: float = 0.0,
    irpf_tax: float = 0.0,
    reform_adjustment: float = 0.0,
    exemption: float = 500_000,
) -> WealthTaxResult:
    if net_worth <= exemption:
        return WealthTaxResult(0.0, 0.0, False)

    taxable_base = net_worth - exemption

    # Escala autonòmica de Catalunya
    brackets = [
        (167_129.45, 0.0021),
        (334_252.88, 0.00315),
        (668_499.75, 0.00525),
        (1_336_999.51, 0.00945),
        (2_673_999.01, 0.01365),
        (5_347_998.03, 0.01785),
        (10_695_996.06, 0.02415),
        (float("inf"), 0.0348),
    ]

    raw_quota = 0.0
    previous_limit = 0.0
    marginal_rate = 0.0021

    for limit, rate in brackets:
        adjusted_rate = max(0.0, rate + (reform_adjustment / 100) * 0.1)
        if taxable_base > previous_limit:
            in_bracket = min(taxable_base, limit) - previous_limit
            raw_quota += in_bracket * adjusted_rate
            marginal_rate = adjusted_rate
        if taxable_base <= limit:
            break
        previous_limit = limit

    # Aplicació de l'Escut Fiscal (60% combinat IRPF-Patrimoni)
    final_quota = raw_quota
    is_limited_by_shield = False

    if irpf_taxable_base > 0:
        max_combined = 0.60 * irpf_taxable_base
        combined_current = irpf_tax + raw_quota

        if combined_current > max_combined:
            excess = combined_current - max_combined
            max_reduction = raw_quota * 0.80
            reduction = min(excess, max_reduction)
            final_quota = raw_quota - reduction
            is_limited_by_shield = True

    return WealthTaxResult(final_quota, marginal_rate, is_limited_by_shield)


# ═══════════════════════════════════════════════════════════════════════════
# Càlcul d'impostos per país per a una retirada bruta anual
# ═══════════════════════════════════════════════════════════════════════════
def compute_annual_tax_for_withdrawal(
    gross_withdrawal: float,
    tax_settings: TaxSettings,
    portfolio_value: float = 0.0,
    lang: str = "ca",
) -> TaxComputationResult:
    is_en = lang == "en"

    if gross_withdrawal <= 0:
        return TaxComputationResult(
            explanation="No withdrawals" if is_en else "Sense retirades",
        )

    country = tax_settings.country
    reform_mod = tax_settings.tax_reform_change_rate or 0.0

    # ─── Catalunya ─────────────────────────────────────────────────────
    if country == "CAT":
        gain_ratio = max(0.05, min(1.0, (tax_settings.catalonia_capital_gains_ratio or 50) / 100))
        taxable_gains = gross_withdrawal * gain_ratio
        irpf_tax, irpf_marginal = calculate_savings_tax(taxable_gains, reform_mod)

        wealth_tax = 0.0
        wealth_details = ""
        if tax_settings.catalonia_apply_wealth_tax and portfolio_value > 500_000:
            wt_result = calculate_catalonia_wealth_tax(
                portfolio_value, taxable_gains, irpf_tax, reform_mod, 500_000,
            )
            wealth_tax = wt_result.wealth_tax
            if is_en:
                shield = ", with 60% tax shield cap" if wt_result.is_limited_by_shield else ""
                wealth_details = (
                    f" + Catalonia Wealth Tax: €{round(wealth_tax):,} /yr"
                    f" (€500k personal exemption{shield})"
                )
            else:
                shield = ", amb escut fiscal del 60%" if wt_result.is_limited_by_shield else ""
                wealth_details = (
                    f" + Patrimoni Catalunya: {round(wealth_tax):,} €/any"
                    f" (mínim exempt 500k €{shield})"
                )

        total_tax = irpf_tax + wealth_tax
        net_disposable = max(0.0, gross_withdrawal - total_tax)

        if is_en:
            explanation = (
                f"Catalonia (Savings Tax on {round(gain_ratio * 100)}% capital gain portion): "
                f"Taxable base of €{round(taxable_gains):,}. "
                f"Income tax quota: €{round(irpf_tax):,}{wealth_details}."
            )
        else:
            explanation = (
                f"Catalunya (IRPF Estalvi al {round(gain_ratio * 100)}% de plusvàlua): "
                f"Base liquidable de {round(taxable_gains):,} €. "
                f"Quota IRPF: {round(irpf_tax):,} €{wealth_details}."
            )

        return TaxComputationResult(
            gross_withdrawal=gross_withdrawal,
            taxable_gains=taxable_gains,
            total_tax=total_tax,
            irpf_tax=irpf_tax,
            wealth_tax=wealth_tax,
            net_disposable_income=net_disposable,
            effective_tax_rate=total_tax / gross_withdrawal,
            marginal_tax_rate=irpf_marginal,
            explanation=explanation,
        )

    # ─── Irlanda ───────────────────────────────────────────────────────
    if country == "IE":
        if tax_settings.ireland_asset_type == "budget_2027_account":
            # New Irish Investment Account (Budget 2027):
            # First €50k tax-free, 1% annual tax on portfolio value above €50k.
            # 0% Exit Tax & 0% CGT on withdrawals! No deemed disposal!
            threshold = getattr(tax_settings, "ireland_investment_account_threshold", 50000.0)
            account_rate = max(0.0, (getattr(tax_settings, "ireland_investment_account_rate", 1.0) + reform_mod) / 100.0)
            taxable_above = max(0.0, portfolio_value - threshold)
            annual_charge = taxable_above * account_rate
            total_tax = annual_charge
            net_disposable = max(0.0, gross_withdrawal - total_tax)

            if is_en:
                explanation = (
                    f"Ireland (Budget 2027 Investment Account): First €{round(threshold):,} is 100% tax-free. "
                    f"Flat 1% annual tax on balance above €{round(threshold):,} (€{round(annual_charge):,} /yr). "
                    f"Exempt from CGT, Exit Tax, and 8-year Deemed Disposal on withdrawals and growth."
                )
            else:
                explanation = (
                    f"Irlanda (Compte d'Inversió Pressupost 2027): Primers {round(threshold):,} € 100% exempts. "
                    f"Taxa anual de l'1% sobre el saldo que superi {round(threshold):,} € ({round(annual_charge):,} €/any). "
                    f"Sense Exit Tax, sense CGT ni Deemed Disposal en retirades ni creixement."
                )

            return TaxComputationResult(
                gross_withdrawal=gross_withdrawal,
                taxable_gains=0.0,
                total_tax=total_tax,
                irpf_tax=total_tax,
                wealth_tax=0.0,
                net_disposable_income=net_disposable,
                effective_tax_rate=total_tax / gross_withdrawal if gross_withdrawal > 0 else 0.0,
                marginal_tax_rate=account_rate,
                explanation=explanation,
            )

        estimated_gain_ratio = 0.6
        taxable_gains = gross_withdrawal * estimated_gain_ratio

        if tax_settings.ireland_asset_type == "etf_exit_tax":
            base_rate = getattr(tax_settings, "ireland_exit_tax_rate", 35.0) / 100.0
            exit_tax_rate = max(0.0, base_rate + reform_mod / 100.0)
            total_tax = taxable_gains * exit_tax_rate
            net_disposable = max(0.0, gross_withdrawal - total_tax)

            if is_en:
                explanation = (
                    f"Ireland (UCITS ETFs Exit Tax - Budget 2027): {round(exit_tax_rate * 100)}% flat rate on estimated capital gain. "
                    f"8-year statutory Deemed Disposal applies outside the new Investment Account."
                )
            else:
                explanation = (
                    f"Irlanda (Exit Tax ETFs UCITS - Pressupost 2027): {round(exit_tax_rate * 100)}% fix sobre la plusvàlua estimada. "
                    f"S'aplica Deemed Disposal cada 8 anys fora del nou compte d'inversió."
                )

            return TaxComputationResult(
                gross_withdrawal=gross_withdrawal,
                taxable_gains=taxable_gains,
                total_tax=total_tax,
                irpf_tax=total_tax,
                wealth_tax=0.0,
                net_disposable_income=net_disposable,
                effective_tax_rate=total_tax / gross_withdrawal if gross_withdrawal > 0 else 0.0,
                marginal_tax_rate=exit_tax_rate,
                explanation=explanation,
            )
        else:
            exemption = 1_270
            taxable_above = max(0.0, taxable_gains - exemption)
            base_rate = getattr(tax_settings, "ireland_cgt_rate", 31.0) / 100.0
            cgt_rate = max(0.0, base_rate + reform_mod / 100.0)
            total_tax = taxable_above * cgt_rate
            net_disposable = max(0.0, gross_withdrawal - total_tax)

            if is_en:
                explanation = (
                    f"Ireland (CGT Individual Equities - Budget 2027): {round(cgt_rate * 100)}% capital gains tax "
                    f"with an annual personal exemption of €1,270."
                )
            else:
                explanation = (
                    f"Irlanda (CGT Accions individuals - Pressupost 2027): {round(cgt_rate * 100)}% sobre plusvàlua "
                    f"amb exempció anual de 1.270 € de guanys."
                )

            return TaxComputationResult(
                gross_withdrawal=gross_withdrawal,
                taxable_gains=taxable_gains,
                total_tax=total_tax,
                irpf_tax=total_tax,
                wealth_tax=0.0,
                net_disposable_income=net_disposable,
                effective_tax_rate=total_tax / gross_withdrawal if gross_withdrawal > 0 else 0.0,
                marginal_tax_rate=cgt_rate,
                explanation=explanation,
            )



    # ─── Andorra ───────────────────────────────────────────────────────
    if country == "AD":
        if tax_settings.andorra_exempt_listed_securities:
            if is_en:
                explanation = (
                    "Andorra (Listed Securities Exemption <25%): 0% tax on capital gains "
                    "from international listed equities/funds. Zero wealth tax."
                )
            else:
                explanation = (
                    "Andorra (Exempció de borsa cotitzada <25%): 0% d'impost sobre guanys "
                    "de capital de carteres de borsa internacional. Sense impost de patrimoni."
                )

            return TaxComputationResult(
                gross_withdrawal=gross_withdrawal,
                taxable_gains=0.0,
                total_tax=0.0,
                irpf_tax=0.0,
                wealth_tax=0.0,
                net_disposable_income=gross_withdrawal,
                effective_tax_rate=0.0,
                marginal_tax_rate=0.0,
                explanation=explanation,
            )

        estimated_gain_ratio = 0.6
        taxable_gains = gross_withdrawal * estimated_gain_ratio
        exemption = 3_000
        taxable_above = max(0.0, taxable_gains - exemption)
        tax_rate = max(0.0, 0.10 + reform_mod / 100)
        total_tax = taxable_above * tax_rate
        net_disposable = max(0.0, gross_withdrawal - total_tax)

        if is_en:
            explanation = (
                "Andorra (General movable capital regime): Flat 10% rate "
                "with the first €3,000 per year fully tax-exempt. Zero wealth tax."
            )
        else:
            explanation = (
                "Andorra (IRPF Rendes Mobiliàries règim general): 10% de tipus únic "
                "amb exempció dels primers 3.000 € anuals. Sense impost de patrimoni."
            )

        return TaxComputationResult(
            gross_withdrawal=gross_withdrawal,
            taxable_gains=taxable_gains,
            total_tax=total_tax,
            irpf_tax=total_tax,
            wealth_tax=0.0,
            net_disposable_income=net_disposable,
            effective_tax_rate=total_tax / gross_withdrawal,
            marginal_tax_rate=tax_rate,
            explanation=explanation,
        )

    # ─── Jurisdicció no configurada ────────────────────────────────────
    return TaxComputationResult(
        gross_withdrawal=gross_withdrawal,
        net_disposable_income=gross_withdrawal,
        explanation="Jurisdiction not configured" if is_en else "Jurisdicció no configurada",
    )


# ═══════════════════════════════════════════════════════════════════════════
# Cerca binària: gross necessari per obtenir un net objectiu
# ═══════════════════════════════════════════════════════════════════════════
def calculate_gross_needed_for_net_income(
    target_net_annual: float,
    tax_settings: TaxSettings,
    portfolio_value: float = 0.0,
    lang: str = "ca",
) -> TaxComputationResult:
    if target_net_annual <= 0:
        return compute_annual_tax_for_withdrawal(0, tax_settings, portfolio_value, lang)

    low = target_net_annual
    high = target_net_annual * 2.8
    best_result = compute_annual_tax_for_withdrawal(target_net_annual, tax_settings, portfolio_value, lang)

    for _ in range(40):
        mid = (low + high) / 2
        result = compute_annual_tax_for_withdrawal(mid, tax_settings, portfolio_value, lang)
        best_result = result

        if abs(result.net_disposable_income - target_net_annual) < 1:
            break

        if result.net_disposable_income < target_net_annual:
            low = mid
        else:
            high = mid

    return best_result


# ═══════════════════════════════════════════════════════════════════════════
# Detalls dels països suportats
# ═══════════════════════════════════════════════════════════════════════════
def get_supported_countries(lang: str = "ca") -> list[CountryDetails]:
    if lang == "en":
        return [
            CountryDetails(
                code="CAT",
                name="Catalonia",
                flag="🏴󠁥󠁳󠁣󠁴󠁿",
                currency="EUR (€)",
                summary=(
                    "Tax regime of Catalonia: Progressive Savings Tax brackets (19% - 28%) "
                    "with tax-free fund-to-fund transfers, paired with Catalonia's autonomous "
                    "Wealth Tax featuring Spain's lowest personal exemption (€500,000) and "
                    "rates from 0.21% to 3.48%."
                ),
                highlights=[
                    "Savings Tax: 19% (up to €6k), 21% (€6k-€50k), 23% (€50k-€200k), 27% (€200k-€300k), and 28% (>€300k). 50% regional split.",
                    "Tax is levied strictly on the net capital gains portion in withdrawals (principal return is tax-free).",
                    "Complete tax deferral on investment funds via statutory roll-over transfers without interim toll.",
                    "Catalonia autonomous Wealth Tax: Spain's lowest personal exemption at €500,000 (vs €700k state or 100% bonus in Madrid/Andalusia).",
                    "Progressive regional wealth tax scale from 0.21% to 3.48% (Spain's highest marginal tier) with a 60% income-wealth tax shield.",
                ],
            ),
            CountryDetails(
                code="IE",
                name="Ireland",
                flag="🇮🇪",
                currency="EUR (€)",
                summary=(
                    "Distinct dual tax framework: 41% Exit Tax on UCITS ETFs with 8-year "
                    "Deemed Disposal, or 33% CGT on individual equities."
                ),
                highlights=[
                    "UCITS ETFs & Funds: 41% flat rate Exit Tax on both realized gains and distributions.",
                    "Deemed Disposal: Every 8 years, tax is assessed on unrealized ETF gains even if no shares are sold.",
                    "Individual Equities: 33% standard Capital Gains Tax (CGT) with a personal annual exemption of €1,270.",
                    "No general annual net wealth tax.",
                ],
            ),
            CountryDetails(
                code="AD",
                name="Andorra",
                flag="🇦🇩",
                currency="EUR (€)",
                summary=(
                    "One of Europe's premier jurisdictions for FIRE: 0% tax on gains from "
                    "publicly listed securities (<25%) or max 10% income tax."
                ),
                highlights=[
                    "Full statutory exemption (0% IRPF) on capital gains from international listed equities and UCITS funds held under 25% ownership.",
                    "General movable capital regime: reduced flat 10% rate with the first €3,000 per year fully tax-exempt.",
                    "Zero wealth tax (0%).",
                    "Corporate tax capped at 10% and standard VAT (IGI) at only 4.5%.",
                ],
            ),
        ]

    return [
        CountryDetails(
            code="CAT",
            name="Catalunya",
            flag="🏴󠁥󠁳󠁣󠁴󠁿",
            currency="EUR (€)",
            summary=(
                "Règim fiscal de Catalunya: IRPF de l'Estalvi per trams (19% - 28%) "
                "amb traspàs de fons d'inversió exempt, combinat amb l'Impost sobre el "
                "Patrimoni català amb el mínim exempt més estricte (500.000 €) i tipus "
                "del 0,21% al 3,48%."
            ),
            highlights=[
                "IRPF Estalvi: 19% (fins a 6k€), 21% (6k-50k€), 23% (50k-200k€), 27% (200k-300k€) i 28% (>300k€). 50% tram autonòmic de la Generalitat.",
                "Només tributa la plusvàlua latent en cada retirada (el capital principal invertit no tributa).",
                "Diferiment total en fons d'inversió mitjançant el mecanisme de traspàs.",
                "Impost sobre el Patrimoni propi de Catalunya: Mínim exempt de només 500.000 € (enfront dels 700.000 € estatals o 100% bonificat a Madrid/Andalusia).",
                "Escala de Patrimoni de la Generalitat: Del 0,21% fins al 3,48% marginal (el més alt d'Espanya) amb escut fiscal del 60% IRPF.",
            ],
        ),
        CountryDetails(
            code="IE",
            name="Irlanda",
            flag="🇮🇪",
            currency="EUR (€)",
            summary=(
                "Tributació dual molt diferenciada: 41% Exit Tax en ETFs UCITS amb "
                "Deemed Disposal als 8 anys, o 33% CGT en accions individuals."
            ),
            highlights=[
                "ETFs / Fons UCITS: 41% tipus fix (\"Exit Tax\") tant en guanys de capital com en dividends.",
                "Deemed Disposal: Cada 8 anys cal liquidar el 41% sobre la plusvàlua latent encara que no es vengui cap participació!",
                "Accions individuals (Borsa): Capital Gains Tax (CGT) al 33% amb exempció anual de 1.270 €.",
                "Sense impost de patrimoni general.",
            ],
        ),
        CountryDetails(
            code="AD",
            name="Andorra",
            flag="🇦🇩",
            currency="EUR (€)",
            summary=(
                "Una de les fiscalitats més atractives d'Europa per al moviment FIRE: "
                "0% en guanys d'accions cotitzades (<25%) o màxim 10% IRPF."
            ),
            highlights=[
                "Exempció total (0% IRPF) en guanys patrimonials derivats de valors i fons cotitzats en mercats internacionals (participació < 25%).",
                "Règim general de rendes mobiliàries: tipus reduït fix del 10% amb mínim exempt de 3.000 € anuals.",
                "Sense impost sobre el patrimoni (0%).",
                "Impost de Societats màxim del 10% i IGI (IVA) general de només el 4,5%.",
            ],
        ),
    ]
