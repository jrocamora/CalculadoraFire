import { CountryCode, TaxSettings } from '../types/fire';
import { Language } from '../i18n/translations';

export interface TaxComputationResult {
  grossWithdrawal: number;
  taxableGains: number;
  totalTax: number;
  irpfTax: number;
  wealthTax: number;
  netDisposableIncome: number;
  effectiveTaxRate: number; // totalTax / grossWithdrawal
  marginalTaxRate: number;
  explanation: string;
}

/**
 * Càlcul d'IRPF Estalvi (Rendiments de Capital Mobiliari i Guanys Patrimonials):
 * Trams estatals i autonòmics (50% Generalitat de Catalunya / 50% Estat):
 * Fins a 6.000 €: 19%
 * 6.000 a 50.000 €: 21%
 * 50.000 a 200.000 €: 23%
 * 200.000 a 300.000 €: 27%
 * Més de 300.000 €: 28%
 */
export function calculateSavingsTax(taxableBase: number, reformAdjustment = 0): { tax: number; marginalRate: number } {
  if (taxableBase <= 0) return { tax: 0, marginalRate: 0 };

  const brackets = [
    { limit: 6000, rate: 0.19 },
    { limit: 50000, rate: 0.21 },
    { limit: 200000, rate: 0.23 },
    { limit: 300000, rate: 0.27 },
    { limit: Infinity, rate: 0.28 },
  ];

  let tax = 0;
  let previousLimit = 0;
  let marginalRate = 0.19;

  for (const bracket of brackets) {
    const adjustedRate = Math.max(0, bracket.rate + reformAdjustment / 100);
    if (taxableBase > previousLimit) {
      const taxableInBracket = Math.min(taxableBase, bracket.limit) - previousLimit;
      tax += taxableInBracket * adjustedRate;
      marginalRate = adjustedRate;
    }
    if (taxableBase <= bracket.limit) break;
    previousLimit = bracket.limit;
  }

  return { tax, marginalRate };
}

/**
 * Impost sobre el Patrimoni a Catalunya (Decret Legislatiu 1/2008 de la Generalitat de Catalunya):
 * - Mínim exempt propi: 500.000 € (el més baix d'Espanya).
 * - Tarifa pròpia catalana (0,210% al 3,480%).
 * - Límit conjunt IRPF - Patrimoni (escut fiscal):
 *   La suma de la quota d'IRPF i la quota de Patrimoni no pot superar el 60% de la base d'IRPF.
 *   Reducció màxima del 80% (com a mínim es tributa pel 20% de la quota de patrimoni).
 */
export function calculateCataloniaWealthTax(
  netWorth: number,
  irpfTaxableBase = 0,
  irpfTax = 0,
  reformAdjustment = 0,
  exemption = 500000
): { wealthTax: number; marginalRate: number; isLimitedByShield: boolean } {
  if (netWorth <= exemption) {
    return { wealthTax: 0, marginalRate: 0, isLimitedByShield: false };
  }

  const taxableBase = netWorth - exemption;

  // Escala autonòmica de Catalunya de l'Impost sobre el Patrimoni
  const brackets = [
    { limit: 167129.45, rate: 0.0021 },
    { limit: 334252.88, rate: 0.00315 },
    { limit: 668499.75, rate: 0.00525 },
    { limit: 1336999.51, rate: 0.00945 },
    { limit: 2673999.01, rate: 0.01365 },
    { limit: 5347998.03, rate: 0.01785 },
    { limit: 10695996.06, rate: 0.02415 },
    { limit: Infinity, rate: 0.0348 },
  ];

  let rawQuota = 0;
  let previousLimit = 0;
  let marginalRate = 0.0021;

  for (const bracket of brackets) {
    const adjustedRate = Math.max(0, bracket.rate + (reformAdjustment / 100) * 0.1);
    if (taxableBase > previousLimit) {
      const inBracket = Math.min(taxableBase, bracket.limit) - previousLimit;
      rawQuota += inBracket * adjustedRate;
      marginalRate = adjustedRate;
    }
    if (taxableBase <= bracket.limit) break;
    previousLimit = bracket.limit;
  }

  // Aplicació de l'Escut Fiscal (Límit conjunt IRPF - Patrimoni 60%)
  let finalQuota = rawQuota;
  let isLimitedByShield = false;

  if (irpfTaxableBase > 0) {
    const maxCombined = 0.60 * irpfTaxableBase;
    const combinedCurrent = irpfTax + rawQuota;

    if (combinedCurrent > maxCombined) {
      const excess = combinedCurrent - maxCombined;
      // La reducció no pot superar el 80% de la quota de patrimoni
      const maxReduction = rawQuota * 0.80;
      const reduction = Math.min(excess, maxReduction);
      finalQuota = rawQuota - reduction;
      isLimitedByShield = true;
    }
  }

  return { wealthTax: finalQuota, marginalRate, isLimitedByShield };
}

/**
 * Calcula impostos segons el país / territori per a una retirada bruta anual
 */
export function computeAnnualTaxForWithdrawal(
  grossWithdrawal: number,
  taxSettings: TaxSettings,
  portfolioValue = 0,
  lang: Language = 'ca'
): TaxComputationResult {
  const isEn = lang === 'en';

  if (grossWithdrawal <= 0) {
    return {
      grossWithdrawal: 0,
      taxableGains: 0,
      totalTax: 0,
      irpfTax: 0,
      wealthTax: 0,
      netDisposableIncome: 0,
      effectiveTaxRate: 0,
      marginalTaxRate: 0,
      explanation: isEn ? 'No withdrawals' : 'Sense retirades',
    };
  }

  const { country, cataloniaCapitalGainsRatio, cataloniaApplyWealthTax, irelandAssetType, andorraExemptListedSecurities, taxReformChangeRate } = taxSettings;
  const reformMod = taxReformChangeRate || 0;

  if (country === 'CAT') {
    // Catalunya:
    const gainRatio = Math.max(0.05, Math.min(1.0, (cataloniaCapitalGainsRatio ?? 50) / 100));
    const taxableGains = grossWithdrawal * gainRatio;
    const { tax: irpfTax, marginalRate: irpfMarginal } = calculateSavingsTax(taxableGains, reformMod);

    let wealthTax = 0;
    let wealthDetails = '';
    if (cataloniaApplyWealthTax && portfolioValue > 500000) {
      const { wealthTax: wTax, isLimitedByShield } = calculateCataloniaWealthTax(
        portfolioValue,
        taxableGains,
        irpfTax,
        reformMod,
        500000
      );
      wealthTax = wTax;
      if (isEn) {
        wealthDetails = ` + Catalonia Wealth Tax: €${Math.round(wealthTax).toLocaleString()} /yr (€500k personal exemption${isLimitedByShield ? ', with 60% tax shield cap' : ''})`;
      } else {
        wealthDetails = ` + Patrimoni Catalunya: ${Math.round(wealthTax).toLocaleString('ca-ES')} €/any (mínim exempt 500k €${isLimitedByShield ? ', amb escut fiscal del 60%' : ''})`;
      }
    }

    const totalTax = irpfTax + wealthTax;
    const netDisposable = Math.max(0, grossWithdrawal - totalTax);

    const explanation = isEn
      ? `Catalonia (Savings Tax on ${Math.round(gainRatio * 100)}% capital gain portion): Taxable base of €${Math.round(taxableGains).toLocaleString()}. Income tax quota: €${Math.round(irpfTax).toLocaleString()}${wealthDetails}.`
      : `Catalunya (IRPF Estalvi al ${Math.round(gainRatio * 100)}% de plusvàlua): Base liquidable de ${Math.round(taxableGains).toLocaleString('ca-ES')} €. Quota IRPF: ${Math.round(irpfTax).toLocaleString('ca-ES')} €${wealthDetails}.`;

    return {
      grossWithdrawal,
      taxableGains,
      totalTax,
      irpfTax,
      wealthTax,
      netDisposableIncome: netDisposable,
      effectiveTaxRate: totalTax / grossWithdrawal,
      marginalTaxRate: irpfMarginal,
      explanation,
    };
  }

  if (country === 'IE') {
    const estimatedGainRatio = 0.6;
    const taxableGains = grossWithdrawal * estimatedGainRatio;

    if (irelandAssetType === 'etf_exit_tax') {
      const exitTaxRate = Math.max(0, 0.41 + reformMod / 100);
      const totalTax = taxableGains * exitTaxRate;
      const netDisposable = Math.max(0, grossWithdrawal - totalTax);

      const explanation = isEn
        ? `Ireland (UCITS ETFs Exit Tax): 41% flat rate on estimated capital gain (${Math.round(exitTaxRate * 100)}%). Remember to also account for 8-year Deemed Disposal.`
        : `Irlanda (Exit Tax ETFs UCITS): 41% fix sobre la plusvàlua estimada (${Math.round(exitTaxRate * 100)}%). Tingues en compte també el Deemed Disposal cada 8 anys.`;

      return {
        grossWithdrawal,
        taxableGains,
        totalTax,
        irpfTax: totalTax,
        wealthTax: 0,
        netDisposableIncome: netDisposable,
        effectiveTaxRate: totalTax / grossWithdrawal,
        marginalTaxRate: exitTaxRate,
        explanation,
      };
    } else {
      const exemption = 1270;
      const taxableAboveExemption = Math.max(0, taxableGains - exemption);
      const cgtRate = Math.max(0, 0.33 + reformMod / 100);
      const totalTax = taxableAboveExemption * cgtRate;
      const netDisposable = Math.max(0, grossWithdrawal - totalTax);

      const explanation = isEn
        ? `Ireland (CGT Individual Equities): 33% capital gains tax with an annual personal exemption of €1,270.`
        : `Irlanda (CGT Accions individuals): 33% sobre plusvàlua amb exempció anual de 1.270 € de guanys.`;

      return {
        grossWithdrawal,
        taxableGains,
        totalTax,
        irpfTax: totalTax,
        wealthTax: 0,
        netDisposableIncome: netDisposable,
        effectiveTaxRate: totalTax / grossWithdrawal,
        marginalTaxRate: cgtRate,
        explanation,
      };
    }
  }

  if (country === 'AD') {
    if (andorraExemptListedSecurities) {
      const explanation = isEn
        ? `Andorra (Listed Securities Exemption <25%): 0% tax on capital gains from international listed equities/funds. Zero wealth tax.`
        : `Andorra (Exempció de borsa cotitzada <25%): 0% d'impost sobre guanys de capital de carteres de borsa internacional. Sense impost de patrimoni.`;

      return {
        grossWithdrawal,
        taxableGains: 0,
        totalTax: 0,
        irpfTax: 0,
        wealthTax: 0,
        netDisposableIncome: grossWithdrawal,
        effectiveTaxRate: 0,
        marginalTaxRate: 0,
        explanation,
      };
    }

    const estimatedGainRatio = 0.6;
    const taxableGains = grossWithdrawal * estimatedGainRatio;
    const exemption = 3000;
    const taxableAboveExemption = Math.max(0, taxableGains - exemption);
    const taxRate = Math.max(0, 0.10 + reformMod / 100);
    const totalTax = taxableAboveExemption * taxRate;
    const netDisposable = Math.max(0, grossWithdrawal - totalTax);

    const explanation = isEn
      ? `Andorra (General movable capital regime): Flat 10% rate with the first €3,000 per year fully tax-exempt. Zero wealth tax.`
      : `Andorra (IRPF Rendes Mobiliàries règim general): 10% de tipus únic amb exempció dels primers 3.000 € anuals. Sense impost de patrimoni.`;

    return {
      grossWithdrawal,
      taxableGains,
      totalTax,
      irpfTax: totalTax,
      wealthTax: 0,
      netDisposableIncome: netDisposable,
      effectiveTaxRate: totalTax / grossWithdrawal,
      marginalTaxRate: taxRate,
      explanation,
    };
  }

  return {
    grossWithdrawal,
    taxableGains: 0,
    totalTax: 0,
    irpfTax: 0,
    wealthTax: 0,
    netDisposableIncome: grossWithdrawal,
    effectiveTaxRate: 0,
    marginalTaxRate: 0,
    explanation: isEn ? 'Jurisdiction not configured' : 'Jurisdicció no configurada',
  };
}

/**
 * Donat un ingrés net desitjat (Disposable Income), troba la retirada bruta necessària
 */
export function calculateGrossNeededForNetIncome(
  targetNetAnnual: number,
  taxSettings: TaxSettings,
  portfolioValue = 0,
  lang: Language = 'ca'
): TaxComputationResult {
  if (targetNetAnnual <= 0) {
    return computeAnnualTaxForWithdrawal(0, taxSettings, portfolioValue, lang);
  }

  let low = targetNetAnnual;
  let high = targetNetAnnual * 2.8;
  let bestResult = computeAnnualTaxForWithdrawal(targetNetAnnual, taxSettings, portfolioValue, lang);

  for (let i = 0; i < 40; i++) {
    const mid = (low + high) / 2;
    const result = computeAnnualTaxForWithdrawal(mid, taxSettings, portfolioValue, lang);
    bestResult = result;

    if (Math.abs(result.netDisposableIncome - targetNetAnnual) < 1) {
      break;
    }

    if (result.netDisposableIncome < targetNetAnnual) {
      low = mid;
    } else {
      high = mid;
    }
  }

  return bestResult;
}

export interface CountryDetails {
  code: CountryCode;
  name: string;
  flag: string;
  currency: string;
  summary: string;
  highlights: string[];
}

export function getSupportedCountries(lang: Language = 'ca'): CountryDetails[] {
  if (lang === 'en') {
    return [
      {
        code: 'CAT',
        name: 'Catalonia',
        flag: '🏴󠁥󠁳󠁣󠁴󠁿',
        currency: 'EUR (€)',
        summary: 'Tax regime of Catalonia: Progressive Savings Tax brackets (19% - 28%) with tax-free fund-to-fund transfers, paired with Catalonia’s autonomous Wealth Tax featuring Spain’s lowest personal exemption (€500,000) and rates from 0.21% to 3.48%.',
        highlights: [
          'Savings Tax: 19% (up to €6k), 21% (€6k-€50k), 23% (€50k-€200k), 27% (€200k-€300k), and 28% (>€300k). 50% regional split.',
          'Tax is levied strictly on the net capital gains portion in withdrawals (principal return is tax-free).',
          'Complete tax deferral on investment funds via statutory roll-over transfers without interim toll.',
          'Catalonia autonomous Wealth Tax: Spain’s lowest personal exemption at €500,000 (vs €700k state or 100% bonus in Madrid/Andalusia).',
          'Progressive regional wealth tax scale from 0.21% to 3.48% (Spain’s highest marginal tier) with a 60% income-wealth tax shield.'
        ],
      },
      {
        code: 'IE',
        name: 'Ireland',
        flag: '🇮🇪',
        currency: 'EUR (€)',
        summary: 'Distinct dual tax framework: 41% Exit Tax on UCITS ETFs with 8-year Deemed Disposal, or 33% CGT on individual equities.',
        highlights: [
          'UCITS ETFs & Funds: 41% flat rate Exit Tax on both realized gains and distributions.',
          'Deemed Disposal: Every 8 years, tax is assessed on unrealized ETF gains even if no shares are sold.',
          'Individual Equities: 33% standard Capital Gains Tax (CGT) with a personal annual exemption of €1,270.',
          'No general annual net wealth tax.'
        ],
      },
      {
        code: 'AD',
        name: 'Andorra',
        flag: '🇦🇩',
        currency: 'EUR (€)',
        summary: 'One of Europe’s premier jurisdictions for FIRE: 0% tax on gains from publicly listed securities (<25%) or max 10% income tax.',
        highlights: [
          'Full statutory exemption (0% IRPF) on capital gains from international listed equities and UCITS funds held under 25% ownership.',
          'General movable capital regime: reduced flat 10% rate with the first €3,000 per year fully tax-exempt.',
          'Zero wealth tax (0%).',
          'Corporate tax capped at 10% and standard VAT (IGI) at only 4.5%.'
        ],
      },
    ];
  }

  return [
    {
      code: 'CAT',
      name: 'Catalunya',
      flag: '🏴󠁥󠁳󠁣󠁴󠁿',
      currency: 'EUR (€)',
      summary: 'Règim fiscal de Catalunya: IRPF de l’Estalvi per trams (19% - 28%) amb traspàs de fons d’inversió exempt, combinat amb l’Impost sobre el Patrimoni català amb el mínim exempt més estricte (500.000 €) i tipus del 0,21% al 3,48%.',
      highlights: [
        'IRPF Estalvi: 19% (fins a 6k€), 21% (6k-50k€), 23% (50k-200k€), 27% (200k-300k€) i 28% (>300k€). 50% tram autonòmic de la Generalitat.',
        'Només tributa la plusvàlua latent en cada retirada (el capital principal invertit no tributa).',
        'Diferiment total en fons d’inversió mitjançant el mecanisme de traspàs.',
        'Impost sobre el Patrimoni propi de Catalunya: Mínim exempt de només 500.000 € (enfront dels 700.000 € estatals o 100% bonificat a Madrid/Andalusia).',
        'Escala de Patrimoni de la Generalitat: Del 0,21% fins al 3,48% marginal (el més alt d’Espanya) amb escut fiscal del 60% IRPF.'
      ],
    },
    {
      code: 'IE',
      name: 'Irlanda',
      flag: '🇮🇪',
      currency: 'EUR (€)',
      summary: 'Tributació dual molt diferenciada: 41% Exit Tax en ETFs UCITS amb Deemed Disposal als 8 anys, o 33% CGT en accions individuals.',
      highlights: [
        'ETFs / Fons UCITS: 41% tipus fix ("Exit Tax") tant en guanys de capital com en dividends.',
        'Deemed Disposal: Cada 8 anys cal liquidar el 41% sobre la plusvàlua latent encara que no es vengui cap participació!',
        'Accions individuals (Borsa): Capital Gains Tax (CGT) al 33% amb exempció anual de 1.270 €.',
        'Sense impost de patrimoni general.'
      ],
    },
    {
      code: 'AD',
      name: 'Andorra',
      flag: '🇦🇩',
      currency: 'EUR (€)',
      summary: 'Una de les fiscalitats més atractives d’Europa per al moviment FIRE: 0% en guanys d’accions cotitzades (<25%) o màxim 10% IRPF.',
      highlights: [
        'Exempció total (0% IRPF) en guanys patrimonials derivats de valors i fons cotitzats en mercats internacionals (participació < 25%).',
        'Règim general de rendes mobiliàries: tipus reduït fix del 10% amb mínim exempt de 3.000 € anuals.',
        'Sense impost sobre el patrimoni (0%).',
        'Impost de Societats màxim del 10% i IGI (IVA) general de només el 4,5%.'
      ],
    },
  ];
}

export const SUPPORTED_COUNTRIES: CountryDetails[] = getSupportedCountries('ca');

