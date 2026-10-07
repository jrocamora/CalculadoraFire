import {
  FireCalculationResult,
  FireInputs,
  YearProjection,
  TaxSettings,
} from '../types/fire';
import {
  calculateGrossNeededForNetIncome,
  computeAnnualTaxForWithdrawal,
  calculateCataloniaWealthTax,
} from './taxCalculators';
import { Language } from '../i18n/translations';

/**
 * Motor de simulació per a la independència financera (FIRE)
 */
export function simulateFire(inputs: FireInputs, lang: Language = 'ca'): FireCalculationResult {
  const isEn = lang === 'en';
  const currentYear = new Date().getFullYear();
  const {
    mode,
    currentAge,
    targetRetirementAge,
    lifeExpectancy = 88,
    targetMonthlyDisposableIncome,
    assets,
    monthlySavings,
    annualSavingsIncreaseRate,
    safeWithdrawalRate,
    scenario,
    taxSettings,
  } = inputs;

  // 1. Calcular patrimoni inicial sumant tots els actius
  const currentTotalNetWorth = assets.reduce((sum, a) => sum + (Number(a.currentAmount) || 0), 0);
  const swrDecimal = Math.max(0.01, safeWithdrawalRate / 100);

  // Rendibilitat i inflació
  const nominalRate = scenario.nominalReturn / 100;
  const inflationRate = scenario.inflationRate / 100;

  // Variables calculades
  let targetAnnualNetIncome = 0;
  let grossWithdrawalNeeded = 0;
  let fireNumberNominal = 0;
  let fireNumberReal = 0;

  if (mode === 'target_spending') {
    // Mode A: A partir de la despesa desitjada
    targetAnnualNetIncome = targetMonthlyDisposableIncome * 12;
    const taxRes = calculateGrossNeededForNetIncome(targetAnnualNetIncome, taxSettings, currentTotalNetWorth, lang);
    grossWithdrawalNeeded = taxRes.grossWithdrawal;
    fireNumberNominal = grossWithdrawalNeeded / swrDecimal;
  } else {
    // Mode B: A partir del patrimoni actual i estalvi
    // Simulem fins a l'edat objectiu de jubilació per saber quant capital tindrà
    let simulatedCapital = currentTotalNetWorth;
    const yearsToSimTarget = Math.max(0, targetRetirementAge - currentAge);
    let currentAnnualSavings = monthlySavings * 12;

    for (let y = 0; y < yearsToSimTarget; y++) {
      simulatedCapital = simulatedCapital * (1 + nominalRate) + currentAnnualSavings;
      currentAnnualSavings *= (1 + (annualSavingsIncreaseRate || 0) / 100);
    }

    fireNumberNominal = simulatedCapital;
    grossWithdrawalNeeded = fireNumberNominal * swrDecimal;
    const taxRes = computeAnnualTaxForWithdrawal(grossWithdrawalNeeded, taxSettings, fireNumberNominal, lang);
    targetAnnualNetIncome = taxRes.netDisposableIncome;
  }

  // Comprovar si ja s'és FIRE avui
  const isAlreadyFire = currentTotalNetWorth >= fireNumberNominal && fireNumberNominal > 0;

  // 2. Simulació Any a Any fins a l'esperança de vida
  const projections: YearProjection[] = [];
  let portfolio = currentTotalNetWorth;
  let annualContribution = monthlySavings * 12;
  const totalYears = Math.max(1, lifeExpectancy - currentAge);

  let fireAchievedYearIndex = -1;
  let retirementAgeActual = targetRetirementAge;
  let deemedDisposalBasis = currentTotalNetWorth;

  // Trobar l'any exacte FIRE si estem en mode target_spending
  if (mode === 'target_spending' && !isAlreadyFire) {
    let testPortfolio = currentTotalNetWorth;
    let testContrib = annualContribution;
    for (let y = 0; y < 70; y++) {
      // Valor ajustat a inflació del FIRE number per a aquell any
      const inflationAdjustment = Math.pow(1 + inflationRate, y);
      const inflatedFireNumber = fireNumberNominal * inflationAdjustment;

      if (testPortfolio >= inflatedFireNumber) {
        fireAchievedYearIndex = y;
        break;
      }
      testPortfolio = testPortfolio * (1 + nominalRate) + testContrib;
      testContrib *= (1 + (annualSavingsIncreaseRate || 0) / 100);
    }
  } else if (isAlreadyFire) {
    fireAchievedYearIndex = 0;
  } else {
    // Mode B: FIRE a l'edat indicada per l'usuari
    fireAchievedYearIndex = Math.max(0, targetRetirementAge - currentAge);
  }

  if (fireAchievedYearIndex !== -1) {
    retirementAgeActual = currentAge + fireAchievedYearIndex;
  }

  let portfolioSurvivalYears = 0;
  let portfolioExhausted = false;

  for (let i = 0; i <= totalYears; i++) {
    const age = currentAge + i;
    const calendarYear = currentYear + i;
    const isRetired = mode === 'target_spending' 
      ? (i >= fireAchievedYearIndex && fireAchievedYearIndex !== -1) 
      : (age >= targetRetirementAge);

    const inflationFactor = Math.pow(1 + inflationRate, i);
    const startOfPeriodPortfolio = Math.max(0, portfolio);

    let activeTaxSettings: TaxSettings = { ...taxSettings };
    // Comprovar si hi ha trasllat fiscal planificat
    if (taxSettings.plannedRelocationCountry && taxSettings.plannedRelocationCountry !== 'none' && taxSettings.plannedRelocationYear) {
      if (calendarYear >= taxSettings.plannedRelocationYear) {
        activeTaxSettings.country = taxSettings.plannedRelocationCountry;
      }
    }

    let contributionThisYear = 0;
    let grossWithdrawalThisYear = 0;
    let taxPaidThisYear = 0;
    let netDisposableThisYear = 0;
    let deemedDisposalTaxPaid = 0;
    let catWealthTaxYear = 0;
    let currentReturnRate = nominalRate;

    // Prova d'estrès: caiguda inicial de mercat en jubilació (Sequence of Returns Risk)
    if (isRetired && scenario.stressDropFirstYears && i - fireAchievedYearIndex < 2 && i >= fireAchievedYearIndex) {
      currentReturnRate = -Math.abs(scenario.stressDropFirstYears) / 100;
    }

    if (!isRetired) {
      // Fase d'acumulació
      contributionThisYear = annualContribution;
      annualContribution *= (1 + (annualSavingsIncreaseRate || 0) / 100);

      // Rendiment anual
      const investmentGrowth = startOfPeriodPortfolio * currentReturnRate;
      portfolio = startOfPeriodPortfolio + investmentGrowth + contributionThisYear;

      // Impost sobre el Patrimoni a Catalunya durant acumulació (>500.000 € de mínim exempt)
      if (
        activeTaxSettings.country === 'CAT' &&
        activeTaxSettings.cataloniaApplyWealthTax &&
        portfolio > 500000
      ) {
        const { wealthTax } = calculateCataloniaWealthTax(
          portfolio,
          0,
          0,
          activeTaxSettings.taxReformChangeRate || 0,
          500000
        );
        catWealthTaxYear = wealthTax;
        portfolio = Math.max(0, portfolio - catWealthTaxYear);
        taxPaidThisYear += catWealthTaxYear;
      }

      // Irlanda Deemed Disposal durant acumulació si aplica
      if (
        activeTaxSettings.country === 'IE' &&
        activeTaxSettings.irelandAssetType === 'etf_exit_tax' &&
        activeTaxSettings.irelandSimulateDeemedDisposal &&
        i > 0
      ) {
        const isRolling = (activeTaxSettings.irelandDeemedDisposalMode || 'staggered_rolling_eighth') === 'staggered_rolling_eighth';
        const shouldApplyThisYear = isRolling ? true : (i % 8 === 0);

        if (shouldApplyThisYear) {
          const unrealizedGains = Math.max(0, portfolio - deemedDisposalBasis);
          if (unrealizedGains > 0) {
            const deemedRate = Math.max(0, 0.41 + (activeTaxSettings.taxReformChangeRate || 0) / 100);
            const maturingGain = isRolling ? unrealizedGains / 8 : unrealizedGains;
            deemedDisposalTaxPaid = maturingGain * deemedRate;
            portfolio = Math.max(0, portfolio - deemedDisposalTaxPaid);
            if (isRolling) {
              deemedDisposalBasis += maturingGain;
            } else {
              deemedDisposalBasis = portfolio; // actualitzar base de cost en bloc
            }
            taxPaidThisYear += deemedDisposalTaxPaid;
          }
        }
      }
    } else {
      // Fase de jubilació / decumulació
      // Ajustem la despesa anual bruta amb la inflació acumulada
      const inflatedGrossWithdrawal = grossWithdrawalNeeded * inflationFactor;

      if (portfolio > 0) {
        // En principi retirem a principis o durant l'any
        grossWithdrawalThisYear = Math.min(portfolio, inflatedGrossWithdrawal);
        const taxRes = computeAnnualTaxForWithdrawal(grossWithdrawalThisYear, activeTaxSettings, portfolio);
        taxPaidThisYear = taxRes.totalTax;
        netDisposableThisYear = taxRes.netDisposableIncome;

        // Rendiment sobre el capital restant
        const remainingCapital = Math.max(0, portfolio - grossWithdrawalThisYear);
        const investmentGrowth = remainingCapital * currentReturnRate;
        portfolio = remainingCapital + investmentGrowth;

        // Irlanda Deemed Disposal en jubilació
        if (
          activeTaxSettings.country === 'IE' &&
          activeTaxSettings.irelandAssetType === 'etf_exit_tax' &&
          activeTaxSettings.irelandSimulateDeemedDisposal &&
          i > 0 &&
          portfolio > 0
        ) {
          const isRolling = (activeTaxSettings.irelandDeemedDisposalMode || 'staggered_rolling_eighth') === 'staggered_rolling_eighth';
          const shouldApplyThisYear = isRolling ? true : (i % 8 === 0);

          if (shouldApplyThisYear) {
            const unrealizedGains = Math.max(0, portfolio - deemedDisposalBasis);
            if (unrealizedGains > 0) {
              const deemedRate = Math.max(0, 0.41 + (activeTaxSettings.taxReformChangeRate || 0) / 100);
              const maturingGain = isRolling ? unrealizedGains / 8 : unrealizedGains;
              deemedDisposalTaxPaid = maturingGain * deemedRate;
              portfolio = Math.max(0, portfolio - deemedDisposalTaxPaid);
              if (isRolling) {
                deemedDisposalBasis += maturingGain;
              } else {
                deemedDisposalBasis = portfolio;
              }
              taxPaidThisYear += deemedDisposalTaxPaid;
            }
          }
        }
      } else {
        grossWithdrawalThisYear = 0;
        taxPaidThisYear = 0;
        netDisposableThisYear = 0;
        portfolio = 0;
        if (!portfolioExhausted) {
          portfolioExhausted = true;
        }
      }
    }

    if (portfolio > 0) {
      portfolioSurvivalYears++;
    }

    const endingPortfolio = Math.max(0, portfolio);
    const endingPortfolioReal = endingPortfolio / inflationFactor;

    let notes = '';
    if (i === fireAchievedYearIndex && isRetired) {
      notes = isEn ? '🎉 Financial Independence Achieved!' : '🎉 Assoliment de la Independència Financera!';
    } else if (deemedDisposalTaxPaid > 0) {
      const isRolling = (activeTaxSettings.irelandDeemedDisposalMode || 'staggered_rolling_eighth') === 'staggered_rolling_eighth';
      if (isEn) {
        notes = isRolling
          ? `⚠️ Ireland Deemed Disposal (1/8th rolling DCA): €${Math.round(deemedDisposalTaxPaid).toLocaleString()}`
          : `⚠️ Ireland Deemed Disposal (8-year lump sum): €${Math.round(deemedDisposalTaxPaid).toLocaleString()}`;
      } else {
        notes = isRolling
          ? `⚠️ Deemed Disposal Irlanda (1/8 anual escalonat): ${Math.round(deemedDisposalTaxPaid).toLocaleString('ca-ES')} €`
          : `⚠️ Deemed Disposal Irlanda (8 anys en bloc): ${Math.round(deemedDisposalTaxPaid).toLocaleString('ca-ES')} €`;
      }
    } else if (catWealthTaxYear > 0) {
      notes = isEn
        ? `🏛️ Catalonia Wealth Tax: €${Math.round(catWealthTaxYear).toLocaleString()}`
        : `🏛️ Impost Patrimoni Catalunya: ${Math.round(catWealthTaxYear).toLocaleString('ca-ES')} €`;
    } else if (portfolio === 0 && startOfPeriodPortfolio > 0) {
      notes = isEn ? '❌ Portfolio Depletion' : '❌ Esgotament del capital';
    }

    projections.push({
      yearIndex: i,
      calendarYear,
      age,
      isRetired,
      startingPortfolio: startOfPeriodPortfolio,
      grossReturn: currentReturnRate,
      inflationFactor,
      contribution: contributionThisYear,
      grossWithdrawal: grossWithdrawalThisYear,
      taxPaid: taxPaidThisYear,
      netDisposableIncome: netDisposableThisYear,
      endingPortfolio,
      endingPortfolioReal,
      deemedDisposalTaxPaid: deemedDisposalTaxPaid > 0 ? deemedDisposalTaxPaid : undefined,
      taxNotes: notes || undefined,
    });
  }

  // Resum fiscal en l'any de jubilació
  const sampleTaxAtRetirement = computeAnnualTaxForWithdrawal(grossWithdrawalNeeded, taxSettings, fireNumberNominal);
  const yearsToFire = isAlreadyFire ? 0 : Math.max(0, retirementAgeActual - currentAge);
  const ageAtFire = isAlreadyFire ? currentAge : retirementAgeActual;
  const calendarYearAtFire = currentYear + yearsToFire;

  fireNumberReal = fireNumberNominal; // Valor nominal base a data d'avui

  return {
    fireNumberNominal,
    fireNumberReal,
    monthlyDisposableTarget: targetAnnualNetIncome / 12,
    annualGrossWithdrawalNeeded: grossWithdrawalNeeded,
    annualTaxAtRetirement: sampleTaxAtRetirement.totalTax,
    effectiveTaxRateAtRetirement: sampleTaxAtRetirement.effectiveTaxRate,
    yearsToFire,
    ageAtFire,
    calendarYearAtFire,
    isAlreadyFire,
    currentTotalNetWorth,
    projectedPortfolioAtFire: isAlreadyFire ? currentTotalNetWorth : fireNumberNominal,
    projections,
    portfolioSurvivalYears,
    finalPortfolioValue: projections[projections.length - 1]?.endingPortfolio || 0,
    isSustainable: !portfolioExhausted,
  };
}
