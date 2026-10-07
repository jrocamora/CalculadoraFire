export type Language = 'ca' | 'en';

export interface Translations {
  appName: string;
  appBadge: string;
  appSubtitle: string;
  resetValues: string;
  activeTax: string;
  
  // Metric cards
  fireNumberTitle: string;
  swrMultiplierSuffix: string;
  currentNetWorthLabel: string;
  timeToFireTitle: string;
  alreadyFire: string;
  canRetireNow: string;
  retireAtAge: string;
  inYear: string;
  survivalEstimated: string;
  planYears: string;
  disposableIncomeTitle: string;
  netPerYear: string;
  grossWithdrawalNeeded: string;
  taxationTitle: string;
  effectiveTaxRate: string;
  planStatus: string;
  sustainable: string;
  depletionRisk: string;
  perMonth: string;
  perYear: string;

  // Bidirectional inputs
  inputModeTitle: string;
  inputModeSubtitle: string;
  modeTargetSpending: string;
  modeCurrentPortfolio: string;
  targetDisposableQuestion: string;
  targetDisposableHelp: string;
  netPerYearEquivalent: string;
  commonTarget: string;
  fatFire: string;
  enterExactValue: string;
  accumulatedCapitalLabel: string;
  accumulatedCapitalHelp: string;
  monthlySavingsLabel: string;
  monthlySavingsHelp: string;
  annualNewSavings: string;
  portfolioTotal: string;
  portfolioAssetSubtitle: string;
  assetsCount: string;
  currentCapital: string;
  expectedReturn: string;
  additionalMonthlySavings: string;
  targetRetirementAgeLabel: string;
  todayAge: string;
  statePensionAge: string;
  currentAgeLabel: string;
  lifeExpectancyLabel: string;
  annualSavingsIncreaseRateLabel: string;
  horizonLabel: string;
  years: string;

  // Asset categories
  categoryIndexFunds: string;
  categoryIndividualStocks: string;
  categoryCashDeposits: string;
  categoryRealEstateOther: string;

  // SWR control
  swrTitle: string;
  swrSubtitle: string;
  swrAnnualExpenses: string;
  swrUltraSafe: string;
  swrUltraSafeDesc: string;
  swrEuropeanFire: string;
  swrEuropeanFireDesc: string;
  swrTrinityRule: string;
  swrTrinityRuleDesc: string;
  swrLeanDynamic: string;
  swrLeanDynamicDesc: string;

  // Country tax
  countryTaxTitle: string;
  countryTaxSubtitle: string;
  cataloniaSpecificTitle: string;
  cataloniaSpecificBadge: string;
  capitalGainsRatioLabel: string;
  capitalGainsRatioSuffix: string;
  cataloniaGainsHelp: string;
  cataloniaWealthTaxTitle: string;
  cataloniaWealthTaxBadge: string;
  cataloniaWealthTaxDesc: string;
  irelandSpecificTitle: string;
  irelandInvestmentType: string;
  irelandEtfsExitTax: string;
  irelandEtfsExitTaxSub: string;
  irelandIndividualShares: string;
  irelandIndividualSharesSub: string;
  irelandDeemedDisposalTitle: string;
  irelandDeemedDisposalSub: string;
  irelandDeemedDisposalModelLabel: string;
  irelandDeemedDisposalRolling: string;
  irelandDeemedDisposalRollingDesc: string;
  irelandDeemedDisposalLumpSum: string;
  irelandDeemedDisposalLumpSumDesc: string;
  andorraSpecificTitle: string;
  andorraExemptTitle: string;
  andorraExemptDesc: string;
  andorraGeneralRegimeNote: string;
  taxReformTitle: string;
  taxReformDesc: string;
  taxReformCut: string;
  taxReformCurrent: string;
  taxReformModerate: string;
  taxReformHigh: string;
  relocationTitle: string;
  relocationSub: string;
  relocationNone: string;
  relocateToAndorra: string;
  relocateToCatalonia: string;
  relocateToIreland: string;
  relocationYear: string;

  // Macro scenarios
  macroTitle: string;
  macroSubtitle: string;
  realReturnLabel: string;
  scenarioBaseName: string;
  scenarioBaseDesc: string;
  scenarioOptimisticName: string;
  scenarioOptimisticDesc: string;
  scenarioConservativeName: string;
  scenarioConservativeDesc: string;
  scenarioStressName: string;
  scenarioStressDesc: string;
  scenarioCustomName: string;
  nominalReturnLabel: string;
  inflationLabel: string;
  returnNominalShort: string;
  inflationShort: string;

  // Chart
  chartTitle: string;
  chartSubtitle: string;
  chartRealPurchasingPower: string;
  chartNominalLegend: string;
  chartRealLegend: string;
  chartFireTargetLegend: string;
  chartRetirementAt: string;
  chartYearsOld: string;
  chartPhaseAccumulation: string;
  chartPhaseRetirement: string;
  chartNominalNetWorth: string;
  chartRealNetWorth: string;
  chartContributionYear: string;
  chartGrossWithdrawal: string;
  chartEstimatedTax: string;
  chartNetDisposable: string;

  // Tax Breakdown Card
  breakdownTitle: string;
  breakdownSubtitle: string;
  grossAnnualWithdrawal: string;
  netInPocket: string;
  taxesPaid: string;
  taxableGains: string;
  irpfQuota: string;
  cataloniaWealthQuota: string;
  totalEffectiveRate: string;
  netWithdrawalPerMonth: string;

  // Comparison view
  compareTitle: string;
  compareSameGoalBadge: string;
  compareSubtitle: string;
  compareCurrentlyActive: string;
  compareJurisdiction: string;
  compareRequiredFireCapital: string;
  compareYearsToFire: string;
  compareRetirementAge: string;
  compareAnnualTaxes: string;
  compareEffectiveRate: string;
  compareActivateTaxation: string;
  compareActiveInSimulation: string;

  // Yearly table
  tableTitle: string;
  tableSubtitle: string;
  tableFilterAll: string;
  tableFilterAccumulation: string;
  tableFilterRetirement: string;
  tableExportCsv: string;
  tableColYearAge: string;
  tableColPhase: string;
  tableColInitialCapital: string;
  tableColContributionWithdrawal: string;
  tableColTaxes: string;
  tableColNetDisposable: string;
  tableColEndingCapital: string;
  tableColRealCapital: string;
  tableColNotes: string;
  tableShowingPage: string;
  tableOf: string;
  tableYearsCount: string;
  tableSavingsBadge: string;
  tableFireBadge: string;

  // Tabs
  tabChart: string;
  tabComparison: string;
  tabTable: string;

  // Footer
  footerTitle: string;
  footerDisclaimer: string;
}

export const TRANSLATIONS: Record<Language, Translations> = {
  ca: {
    appName: 'Calculadora FIRE',
    appBadge: 'Pro',
    appSubtitle: 'Independència Financera & Jubilació Anticipada amb Fiscalitat Reial',
    resetValues: 'Restablir valors',
    activeTax: 'Fiscalitat activa:',

    fireNumberTitle: 'Xifra FIRE Objectiu',
    swrMultiplierSuffix: 'despesa anual bruta',
    currentNetWorthLabel: 'Patrimoni actual:',
    timeToFireTitle: 'Temps fins a FIRE',
    alreadyFire: 'Assolit! 🎉',
    canRetireNow: 'Pots jubilar-te avui mateix!',
    retireAtAge: 'Jubilació als',
    inYear: 'Any',
    survivalEstimated: 'Supervivència estimada:',
    planYears: 'anys de pla',
    disposableIncomeTitle: 'Disposable Income Net',
    netPerYear: 'nets lliures per any',
    grossWithdrawalNeeded: 'Retirada bruta:',
    taxationTitle: 'Fiscalitat',
    effectiveTaxRate: 'Taxa efectiva estimada:',
    planStatus: 'Estat del pla:',
    sustainable: 'Sostenible',
    depletionRisk: "Risc d'esgotament",
    perMonth: '/mes',
    perYear: '/any',

    inputModeTitle: 'Comença per un dels dos cantons',
    inputModeSubtitle: 'Pots calcular des de la despesa que vols tenir o des dels teus diners i estalvis actuals',
    modeTargetSpending: '1. Despesa Objectiu',
    modeCurrentPortfolio: '2. Patrimoni Actual',
    targetDisposableQuestion: 'Quant vols tenir de Disposable Income (net) al mes?',
    targetDisposableHelp: 'Diners nets nets per a viure cada mes, sense comptar impostos (la calculadora calcularà els impostos necessaris segons el país).',
    netPerYearEquivalent: 'nets / any',
    commonTarget: '2.500 € (Molt comú)',
    fatFire: '5.000 € (Fat FIRE)',
    enterExactValue: 'O introdueix el valor exacte:',
    accumulatedCapitalLabel: 'Patrimoni acumulat que ja tens avui',
    accumulatedCapitalHelp: "Capital actualment invertit o en comptes d'estalvi.",
    monthlySavingsLabel: "Aportació d'estalvi mensual",
    monthlySavingsHelp: "d'estalvi anual nou.",
    annualNewSavings: 'estalvi anual nou',
    portfolioTotal: 'Patrimoni Total:',
    portfolioAssetSubtitle: "Configura on tens invertits els teus diners per tipus d'actiu",
    assetsCount: 'Actius',
    currentCapital: 'Capital actual (€)',
    expectedReturn: 'Rendiment esperat',
    additionalMonthlySavings: 'Estalvi mensual addicional',
    targetRetirementAgeLabel: 'Edat objectiu de jubilació',
    todayAge: '(Avui)',
    statePensionAge: '(Estat)',
    currentAgeLabel: 'Edat actual',
    lifeExpectancyLabel: 'Esperança de vida',
    annualSavingsIncreaseRateLabel: 'Creixement anual estalvi',
    horizonLabel: 'Horitzó de càlcul:',
    years: 'anys',

    categoryIndexFunds: 'Fons Indexats / ETFs',
    categoryIndividualStocks: 'Accions Individuals (Borsa)',
    categoryCashDeposits: 'Efectiu & Dipòsits',
    categoryRealEstateOther: 'Immobiliari / Altres',

    swrTitle: 'Taxa de Retirada Segura (SWR)',
    swrSubtitle: "Percentatge del patrimoni que retires el primer any de jubilació (i que després s'ajusta a la inflació)",
    swrAnnualExpenses: 'despesa anual',
    swrUltraSafe: 'Ultra-segur',
    swrUltraSafeDesc: 'Ideal per a jubilacions prematures molt llargues (+40 anys). Gairebé 0% de probabilitat de fallida històrica.',
    swrEuropeanFire: 'FIRE Recomanat',
    swrEuropeanFireDesc: 'L’estàndard d’or per a inversors a Europa: compensa impostos, comissions d’ETFs i horitzó de vida llarg.',
    swrTrinityRule: 'Regla Trinity',
    swrTrinityRuleDesc: 'La clàssica regla del 4% dels EUA. Dissenyada per a jubilacions de 30 anys amb carteres 50/50 o 75/25.',
    swrLeanDynamic: 'Lean / Dinàmic',
    swrLeanDynamicDesc: 'Requereix flexibilitat per retallar despeses si la borsa cau en els primers anys de jubilació.',

    countryTaxTitle: 'Fiscalitat per País & Normativa Específica',
    countryTaxSubtitle: 'Ajusta la tributació segons la jurisdicció i simula canvis fiscals futurs',
    cataloniaSpecificTitle: 'Normativa Específica: Catalunya',
    cataloniaSpecificBadge: 'Generalitat de Catalunya',
    capitalGainsRatioLabel: 'Proporció de Guanys en la Retirada (Plusvàlua Latent)',
    capitalGainsRatioSuffix: 'plusvàlua',
    cataloniaGainsHelp: "A Catalunya (IRPF Estalvi: 19% a 28%), només tributa la plusvàlua o benefici net generat per la cartera. El retorn del capital inicial invertit és lliure d'impostos. A més, els traspassos entre fons d'inversió tenen diferiment fiscal total sense peatge fins a la retirada definitiva.",
    cataloniaWealthTaxTitle: 'Impost sobre el Patrimoni a Catalunya (Decret L. 1/2008)',
    cataloniaWealthTaxBadge: 'Mínim exempt de només 500.000 € (enfront dels 700k estatals o 100% bonificat a Madrid/Andalusia)',
    cataloniaWealthTaxDesc: "Catalunya té una escala progressiva pròpia del 0,21% al 3,48% per a patrimonis a partir de 500.000 €. Si està activat, s'aplica aquest cost anual tant en la fase d'estalvi com en la de jubilació, respectant l'escut fiscal del 60% combinat amb l'IRPF (amb tributació mínima garantida del 20%).",
    irelandSpecificTitle: 'Paràmetres Específics: Irlanda (Exit Tax vs CGT)',
    irelandInvestmentType: "Tipus d'inversió principal a Irlanda:",
    irelandEtfsExitTax: 'ETFs & Fons UCITS',
    irelandEtfsExitTaxSub: 'Exit Tax del 41% fix + Deemed Disposal als 8 anys',
    irelandIndividualShares: 'Accions Individuals',
    irelandIndividualSharesSub: 'CGT del 33% amb exempció anual de 1.270 €',
    irelandDeemedDisposalTitle: 'Simular Deemed Disposal (41% sobre plusvàlua no realitzada)',
    irelandDeemedDisposalSub: "Regla fiscal d'Irlanda que obliga a liquidar impostos sobre guanys latents d'ETFs",
    irelandDeemedDisposalModelLabel: 'Model de maduració del Deemed Disposal:',
    irelandDeemedDisposalRolling: 'Suavitzat / Escalonat (1/8 anual)',
    irelandDeemedDisposalRollingDesc: 'Simula compres periòdiques (DCA): madura 1/8 part de les plusvàlues del compte cada any, evitant salts bruscs.',
    irelandDeemedDisposalLumpSum: 'En Bloc cada 8 anys',
    irelandDeemedDisposalLumpSumDesc: 'Model de compra única inicial (Lump sum): liquidació del 100% de la plusvàlua cada 8è any.',
    andorraSpecificTitle: 'Paràmetres Específics: Andorra (IRPF & Exempció de Borsa)',
    andorraExemptTitle: "Exempció d'accions cotitzades internacionals (0% IRPF)",
    andorraExemptDesc: "Segons la Llei de l'IRPF d'Andorra, les plusvàlues per transmissió d'accions o fons en mercats cotitzats amb menys del 25% del capital de l'empresa estan totalment exemptes d'impostos.",
    andorraGeneralRegimeNote: 'Aplicant el règim general de rendes mobiliàries: tipus fix del 10% amb els primers 3.000 € anuals exempts.',
    taxReformTitle: 'Escenari de Canvis Fiscals / Reforma Impositiva',
    taxReformDesc: "Simula un augment o reducció general en els tipus d'impost sobre l'estalvi i les rendes del capital per preveure canvis legislatius futurs:",
    taxReformCut: '-5% (Baixada fiscal)',
    taxReformCurrent: '0% (Legislació actual)',
    taxReformModerate: '+5% (Pujada moderada)',
    taxReformHigh: '+10% (Pujada forta)',
    relocationTitle: 'Simular canvi de residència fiscal planificat',
    relocationSub: 'Pots començar acumulant a Catalunya/Irlanda i passar a jubilar-te a Andorra',
    relocationNone: 'Cap trasllat previst',
    relocateToAndorra: '🇦🇩 Traslladar-se a Andorra',
    relocateToCatalonia: '🏴󠁥󠁳󠁣󠁴󠁿 Traslladar-se a Catalunya',
    relocateToIreland: '🇮🇪 Traslladar-se a Irlanda',
    relocationYear: 'Any:',

    macroTitle: 'Escenaris Econòmics & Mercat',
    macroSubtitle: "Ajusta rendibilitat esperada de la borsa, inflació i proves d'estrès",
    realReturnLabel: 'Rendiment Real Net:',
    scenarioBaseName: 'Escenari Base',
    scenarioBaseDesc: 'Rendiment mitjà de mercat global (MSCI World / S&P500 històric) i inflació controlada.',
    scenarioOptimisticName: 'Optimista (Bull Market)',
    scenarioOptimisticDesc: 'Fase de fort creixement tecnològic i econòmic amb baixa inflació persistent.',
    scenarioConservativeName: 'Conservador (Estagflació)',
    scenarioConservativeDesc: 'Menors rendiments borsaris combinats amb una inflació més elevada i persistent.',
    scenarioStressName: 'Estrès Inicial (Seq. Returns)',
    scenarioStressDesc: 'Caiguda del 15% en els dos primers anys de jubilació per avaluar la supervivència.',
    scenarioCustomName: 'Personalitzat',
    nominalReturnLabel: 'Rendiment Nominal de Mercat',
    inflationLabel: 'Inflació Mitjana Prevista',
    returnNominalShort: 'Rend:',
    inflationShort: 'Inf:',

    chartTitle: 'Trajectòria de la Cartera (Acumulació & Retirada)',
    chartSubtitle: 'Evolució del teu patrimoni any a any tenint en compte rendiment, aportacions, retirades i impostos',
    chartRealPurchasingPower: 'Poder adquisitiu real (Inflació)',
    chartNominalLegend: 'Patrimoni Nominal (€ corrents)',
    chartRealLegend: 'Poder Adquisitiu Real (ajustat inflació)',
    chartFireTargetLegend: 'Objectiu FIRE',
    chartRetirementAt: 'Jubilació als',
    chartYearsOld: 'anys',
    chartPhaseAccumulation: 'Acumulació',
    chartPhaseRetirement: 'Retirada (FIRE)',
    chartNominalNetWorth: 'Patrimoni nominal:',
    chartRealNetWorth: 'Poder adquisitiu real:',
    chartContributionYear: 'Aportació any:',
    chartGrossWithdrawal: 'Retirada bruta:',
    chartEstimatedTax: 'Impostos estimats:',
    chartNetDisposable: 'Net disponible:',

    breakdownTitle: 'Desglossament de la Retirada Anual',
    breakdownSubtitle: 'Com es distribueix cada euro retirat en la fase de jubilació anticipada',
    grossAnnualWithdrawal: 'Retirada Bruta:',
    netInPocket: 'Net a la butxaca:',
    taxesPaid: 'Impostos fiscals:',
    taxableGains: 'Plusvàlua Imposable',
    irpfQuota: 'Quota IRPF',
    cataloniaWealthQuota: 'Patrimoni Catalunya',
    totalEffectiveRate: 'Tipus Efectiu Total',
    netWithdrawalPerMonth: 'Retirada Neta / Mes',

    compareTitle: 'Comparativa Fiscal: Catalunya vs Irlanda vs Andorra',
    compareSameGoalBadge: 'Mateix Objectiu de Vida',
    compareSubtitle: 'Compara quant capital i quants anys necessites segons el territori on resideixes fiscalment',
    compareCurrentlyActive: 'Seleccionat actualment',
    compareJurisdiction: 'Jurisdicció fiscal',
    compareRequiredFireCapital: 'Capital FIRE Necessari',
    compareYearsToFire: 'Anys a FIRE',
    compareRetirementAge: 'Edat FIRE',
    compareAnnualTaxes: 'Impostos Anuals',
    compareEffectiveRate: 'Taxa Efectiva',
    compareActivateTaxation: 'Activar fiscalitat',
    compareActiveInSimulation: 'Actiu a la simulació principal',

    tableTitle: 'Projecció Any a Any Detallada',
    tableSubtitle: 'Desglossament complet del flux de caixa, rendibilitat i liquidació fiscal per a cada exercici',
    tableFilterAll: 'Tots',
    tableFilterAccumulation: 'Acumulació',
    tableFilterRetirement: 'Jubilació',
    tableExportCsv: 'Descarregar CSV',
    tableColYearAge: 'Any / Edat',
    tableColPhase: 'Fase',
    tableColInitialCapital: 'Patrimoni Inicial',
    tableColContributionWithdrawal: 'Aportació / Retirada',
    tableColTaxes: 'Impostos',
    tableColNetDisposable: 'Net Disponible',
    tableColEndingCapital: 'Patrimoni Final',
    tableColRealCapital: 'Real (Inflació)',
    tableColNotes: 'Notes Fiscals',
    tableShowingPage: 'Mostrant pàgina',
    tableOf: 'de',
    tableYearsCount: 'exercicis',
    tableSavingsBadge: 'Estalvi',
    tableFireBadge: 'FIRE',

    tabChart: '📊 Gràfic de Trajectòria',
    tabComparison: '🌍 Comparativa 3 Països',
    tabTable: '📋 Taula Any a Any',

    footerTitle: 'Calculadora FIRE Pro per a la independència financera i jubilació primerenca a Europa.',
    footerDisclaimer: 'Aquesta eina té finalitat exclusivament educativa i de simulació de patrimoni. No constitueix assessorament financer, fiscal ni legal.',
  },
  en: {
    appName: 'FIRE Calculator',
    appBadge: 'Pro',
    appSubtitle: 'Financial Independence & Early Retirement with Real-World Taxation',
    resetValues: 'Reset values',
    activeTax: 'Active taxation:',

    fireNumberTitle: 'Target FIRE Number',
    swrMultiplierSuffix: 'gross annual expenses',
    currentNetWorthLabel: 'Current net worth:',
    timeToFireTitle: 'Time to FIRE',
    alreadyFire: 'Achieved! 🎉',
    canRetireNow: 'You can retire today!',
    retireAtAge: 'Retirement at age',
    inYear: 'Year',
    survivalEstimated: 'Estimated survival:',
    planYears: 'plan years',
    disposableIncomeTitle: 'Net Disposable Income',
    netPerYear: 'net spendable per year',
    grossWithdrawalNeeded: 'Gross withdrawal:',
    taxationTitle: 'Taxation',
    effectiveTaxRate: 'Estimated effective rate:',
    planStatus: 'Plan status:',
    sustainable: 'Sustainable',
    depletionRisk: 'Depletion risk',
    perMonth: '/mo',
    perYear: '/yr',

    inputModeTitle: 'Start from Either Side',
    inputModeSubtitle: 'Calculate backwards from your desired spending or forwards from your current assets & savings',
    modeTargetSpending: '1. Desired Spending',
    modeCurrentPortfolio: '2. Current Portfolio',
    targetDisposableQuestion: 'How much Net Disposable Income do you want per month?',
    targetDisposableHelp: 'Net take-home money to live on each month, after all taxes (the calculator computes the exact gross withdrawal needed for your jurisdiction).',
    netPerYearEquivalent: 'net / year',
    commonTarget: '€2,500 (Very common)',
    fatFire: '€5,000 (Fat FIRE)',
    enterExactValue: 'Or enter the exact number:',
    accumulatedCapitalLabel: 'Total wealth accumulated today',
    accumulatedCapitalHelp: 'Capital currently invested in funds, stocks, or savings.',
    monthlySavingsLabel: 'Monthly savings contribution',
    monthlySavingsHelp: 'in new annual savings.',
    annualNewSavings: 'new annual savings',
    portfolioTotal: 'Total Portfolio:',
    portfolioAssetSubtitle: 'Configure where your wealth is allocated across asset classes',
    assetsCount: 'Assets',
    currentCapital: 'Current capital (€)',
    expectedReturn: 'Expected return',
    additionalMonthlySavings: 'Additional monthly savings',
    targetRetirementAgeLabel: 'Target retirement age',
    todayAge: '(Today)',
    statePensionAge: '(State)',
    currentAgeLabel: 'Current age',
    lifeExpectancyLabel: 'Life expectancy',
    annualSavingsIncreaseRateLabel: 'Annual savings growth rate',
    horizonLabel: 'Planning horizon:',
    years: 'years',

    categoryIndexFunds: 'Index Funds / ETFs',
    categoryIndividualStocks: 'Individual Stocks (Equities)',
    categoryCashDeposits: 'Cash & Savings Deposits',
    categoryRealEstateOther: 'Real Estate / Others',

    swrTitle: 'Safe Withdrawal Rate (SWR)',
    swrSubtitle: 'Percentage of the initial portfolio withdrawn in year one of retirement (adjusted for inflation thereafter)',
    swrAnnualExpenses: 'annual expenses',
    swrUltraSafe: 'Ultra-safe',
    swrUltraSafeDesc: 'Ideal for very long early retirements (+40 years). Virtually 0% historical failure rate.',
    swrEuropeanFire: 'Recommended European FIRE',
    swrEuropeanFireDesc: 'The gold standard for European investors: buffers against taxes, ETF fee drag, and extended longevity.',
    swrTrinityRule: 'Trinity Rule',
    swrTrinityRuleDesc: 'The classic US 4% rule from the Trinity Study. Calibrated for 30-year horizons with 50/50 or 75/25 portfolios.',
    swrLeanDynamic: 'Lean / Dynamic',
    swrLeanDynamicDesc: 'Requires spending flexibility to trim withdrawals during severe early bear markets.',

    countryTaxTitle: 'Jurisdiction & Specific Tax Rules',
    countryTaxSubtitle: 'Select jurisdiction tax regime and simulate future tax reforms or relocations',
    cataloniaSpecificTitle: 'Specific Rules: Catalonia',
    cataloniaSpecificBadge: 'Government of Catalonia',
    capitalGainsRatioLabel: 'Capital Gains Ratio in Withdrawals (Unrealized Gains)',
    capitalGainsRatioSuffix: 'gains',
    cataloniaGainsHelp: 'In Catalonia (Savings Tax: 19% to 28%), tax is levied strictly on the capital gain portion, not on returning original principal. Furthermore, fund-to-fund transfers enjoy total tax deferral with zero toll until final liquidation.',
    cataloniaWealthTaxTitle: 'Catalonia Wealth Tax (Legislative Decree 1/2008)',
    cataloniaWealthTaxBadge: 'Lowest personal exemption in Spain: €500,000 (vs €700k state or 100% bonus in Madrid/Andalusia)',
    cataloniaWealthTaxDesc: 'Catalonia enforces its own autonomous progressive scale from 0.21% up to 3.48% for net wealth starting at €500,000. When enabled, this annual drag applies across both accumulation and retirement, capped by the 60% combined income-wealth tax shield (with a guaranteed 20% minimum floor).',
    irelandSpecificTitle: 'Specific Rules: Ireland (Exit Tax vs CGT)',
    irelandInvestmentType: 'Primary investment instrument in Ireland:',
    irelandEtfsExitTax: 'UCITS ETFs & Funds',
    irelandEtfsExitTaxSub: '41% flat Exit Tax + 8-year Deemed Disposal',
    irelandIndividualShares: 'Individual Stocks',
    irelandIndividualSharesSub: '33% CGT with €1,270 annual personal exemption',
    irelandDeemedDisposalTitle: 'Simulate Deemed Disposal (41% on unrealized ETF gains)',
    irelandDeemedDisposalSub: 'Irish statutory rule requiring payment of tax on unrealized ETF growth every 8 years',
    irelandDeemedDisposalModelLabel: 'Deemed Disposal maturation model:',
    irelandDeemedDisposalRolling: 'Smoothed / Staggered (1/8th annually)',
    irelandDeemedDisposalRollingDesc: 'Simulates Dollar-Cost Averaging (DCA): exactly 1/8th of portfolio gains matures each year, avoiding disruptive cash flow shocks.',
    irelandDeemedDisposalLumpSum: 'Lump-sum Cliff (every 8 years)',
    irelandDeemedDisposalLumpSumDesc: 'Simulates a single upfront lump-sum: full 100% liquidation of unrealized growth every 8th year.',
    andorraSpecificTitle: 'Specific Rules: Andorra (Personal Income Tax & Stock Exemption)',
    andorraExemptTitle: 'Listed Securities Exemption (<25% ownership: 0% Tax)',
    andorraExemptDesc: 'Under Andorran IRPF Law, capital gains from publicly listed international stocks and UCITS funds held under 25% corporate ownership are completely exempt from personal income tax (0% tax rate).',
    andorraGeneralRegimeNote: 'Applying general movable capital regime: flat 10% rate with the first €3,000 per year fully tax-exempt.',
    taxReformTitle: 'Tax Reform Scenario & Future Regulatory Changes',
    taxReformDesc: 'Simulate an across-the-board increase or reduction in savings taxes to stress-test future legislative reforms:',
    taxReformCut: '-5% (Tax cut)',
    taxReformCurrent: '0% (Current law)',
    taxReformModerate: '+5% (Moderate hike)',
    taxReformHigh: '+10% (Significant hike)',
    relocationTitle: 'Simulate planned tax residency relocation',
    relocationSub: 'You can begin accumulating in Catalonia/Ireland and retire in Andorra',
    relocationNone: 'No relocation planned',
    relocateToAndorra: '🇦🇩 Relocate to Andorra',
    relocateToCatalonia: '🏴󠁥󠁳󠁣󠁴󠁿 Relocate to Catalonia',
    relocateToIreland: '🇮🇪 Relocate to Ireland',
    relocationYear: 'Year:',

    macroTitle: 'Macroeconomic & Market Scenarios',
    macroSubtitle: 'Customize expected market equity returns, inflation rates, and sequence of returns stress tests',
    realReturnLabel: 'Net Real Return:',
    scenarioBaseName: 'Base Scenario',
    scenarioBaseDesc: 'Historical global equity benchmark (MSCI World / S&P500) with stable, moderate inflation.',
    scenarioOptimisticName: 'Optimistic (Bull Market)',
    scenarioOptimisticDesc: 'Sustained technological acceleration and robust productivity with low inflation.',
    scenarioConservativeName: 'Conservative (Stagflation)',
    scenarioConservativeDesc: 'Subdued market equity returns combined with stubborn, elevated inflation.',
    scenarioStressName: 'Early Stress (Seq. of Returns)',
    scenarioStressDesc: '15% market drop in the first two retirement years to verify portfolio resilience.',
    scenarioCustomName: 'Custom Scenario',
    nominalReturnLabel: 'Nominal Market Return',
    inflationLabel: 'Average Projected Inflation',
    returnNominalShort: 'Ret:',
    inflationShort: 'Inf:',

    chartTitle: 'Portfolio Trajectory (Accumulation & Decumulation)',
    chartSubtitle: 'Projected evolution year by year factoring in compounding, deposits, withdrawals, and jurisdiction taxes',
    chartRealPurchasingPower: 'Real purchasing power (Inflation adjusted)',
    chartNominalLegend: 'Nominal Portfolio (€ Current)',
    chartRealLegend: 'Real Purchasing Power (Inflation adjusted)',
    chartFireTargetLegend: 'Target FIRE Number',
    chartRetirementAt: 'Retirement at age',
    chartYearsOld: 'y/o',
    chartPhaseAccumulation: 'Accumulation',
    chartPhaseRetirement: 'Retirement (FIRE)',
    chartNominalNetWorth: 'Nominal portfolio:',
    chartRealNetWorth: 'Real purchasing power:',
    chartContributionYear: 'Yearly deposit:',
    chartGrossWithdrawal: 'Gross withdrawal:',
    chartEstimatedTax: 'Estimated taxes:',
    chartNetDisposable: 'Net disposable:',

    breakdownTitle: 'Annual Retirement Withdrawal Breakdown',
    breakdownSubtitle: 'How every euro withdrawn is partitioned during early retirement',
    grossAnnualWithdrawal: 'Gross Withdrawal:',
    netInPocket: 'Net in pocket:',
    taxesPaid: 'Taxes paid:',
    taxableGains: 'Taxable Capital Gains',
    irpfQuota: 'Income Tax Quota',
    cataloniaWealthQuota: 'Catalonia Wealth Tax',
    totalEffectiveRate: 'Total Effective Rate',
    netWithdrawalPerMonth: 'Net Withdrawal / Month',

    compareTitle: 'Tax Comparison: Catalonia vs Ireland vs Andorra',
    compareSameGoalBadge: 'Identical Lifestyle Goal',
    compareSubtitle: 'Compare nest egg capital and years required depending on your tax residency jurisdiction',
    compareCurrentlyActive: 'Currently selected',
    compareJurisdiction: 'Tax jurisdiction',
    compareRequiredFireCapital: 'Required FIRE Capital',
    compareYearsToFire: 'Years to FIRE',
    compareRetirementAge: 'FIRE Age',
    compareAnnualTaxes: 'Annual Taxes',
    compareEffectiveRate: 'Effective Rate',
    compareActivateTaxation: 'Activate taxation for',
    compareActiveInSimulation: 'Active in primary simulation',

    tableTitle: 'Detailed Year-by-Year Cash Flow Projection',
    tableSubtitle: 'Complete breakdown of portfolio compounding, savings, withdrawals, and tax settlements for each fiscal year',
    tableFilterAll: 'All',
    tableFilterAccumulation: 'Accumulation',
    tableFilterRetirement: 'Retirement',
    tableExportCsv: 'Download CSV',
    tableColYearAge: 'Year / Age',
    tableColPhase: 'Phase',
    tableColInitialCapital: 'Starting Wealth',
    tableColContributionWithdrawal: 'Deposit / Withdrawal',
    tableColTaxes: 'Taxes',
    tableColNetDisposable: 'Net Disposable',
    tableColEndingCapital: 'Ending Wealth',
    tableColRealCapital: 'Real (Inflation Adj)',
    tableColNotes: 'Fiscal Notes',
    tableShowingPage: 'Showing page',
    tableOf: 'of',
    tableYearsCount: 'fiscal years',
    tableSavingsBadge: 'Saving',
    tableFireBadge: 'FIRE',

    tabChart: '📊 Trajectory Chart',
    tabComparison: '🌍 3-Jurisdiction Comparison',
    tabTable: '📋 Year-by-Year Table',

    footerTitle: 'FIRE Pro Calculator for financial independence and early retirement across European jurisdictions.',
    footerDisclaimer: 'This tool is exclusively designed for educational, wealth simulation, and financial planning purposes. It does not constitute professional financial, tax, or legal advice.',
  },
};
