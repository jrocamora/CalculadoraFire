export type CountryCode = 'CAT' | 'IE' | 'AD';

export type CalculationMode = 'target_spending' | 'current_portfolio';

export type AssetCategory = 'index_funds' | 'individual_stocks' | 'cash_deposits' | 'real_estate_other';

export type IrelandDeemedDisposalMode = 'lump_sum_8y' | 'staggered_rolling_eighth';

export interface PortfolioAsset {
  id: string;
  category: AssetCategory;
  name: string;
  currentAmount: number;
  expectedReturnAnnual: number; // e.g. 7%
  costBasis: number; // For capital gains calculations
}

export interface TaxSettings {
  country: CountryCode;
  // Catalunya specific
  cataloniaCapitalGainsRatio: number; // % de plusvàlua latent en retirada (ex. 50%)
  cataloniaApplyWealthTax: boolean; // Impost sobre el Patrimoni a Catalunya (mínim 500.000 €)
  cataloniaPrimaryResidenceExemption?: number; // Habitatge habitual exempt (fins a 300.000 €)
  // Ireland specific
  irelandAssetType: 'etf_exit_tax' | 'individual_shares_cgt';
  irelandSimulateDeemedDisposal: boolean; // 41% tax on unrealized growth
  irelandDeemedDisposalMode?: IrelandDeemedDisposalMode; // 'lump_sum_8y' o 'staggered_rolling_eighth'
  // Andorra specific
  andorraExemptListedSecurities: boolean; // 0% on listed shares held <25% ownership
  // Future fiscal scenario / reform modifier
  taxReformChangeRate: number; // e.g. +2% tax reform shock
  plannedRelocationCountry?: CountryCode | 'none';
  plannedRelocationYear?: number;
}

export interface MacroScenario {
  id: 'base' | 'optimistic' | 'conservative' | 'stress_test' | 'custom';
  name: string;
  description: string;
  nominalReturn: number; // %
  inflationRate: number; // %
  stressDropFirstYears?: number; // % drop in year 1-2 of retirement
}

export interface FireInputs {
  mode: CalculationMode;
  currentAge: number;
  targetRetirementAge: number;
  lifeExpectancy: number;
  
  // Mode A: Target spending
  targetMonthlyDisposableIncome: number; // Net spendable income desired
  
  // Mode B: Current portfolio & accumulation
  assets: PortfolioAsset[];
  monthlySavings: number;
  annualSavingsIncreaseRate: number; // % salary/savings growth
  
  // Withdrawal settings
  safeWithdrawalRate: number; // e.g. 3.5%
  
  // Economics
  scenario: MacroScenario;
  
  // Tax
  taxSettings: TaxSettings;
}

export interface YearProjection {
  yearIndex: number;
  calendarYear: number;
  age: number;
  isRetired: boolean;
  startingPortfolio: number;
  grossReturn: number;
  inflationFactor: number;
  contribution: number;
  grossWithdrawal: number;
  taxPaid: number;
  netDisposableIncome: number;
  endingPortfolio: number;
  endingPortfolioReal: number; // inflation-adjusted
  deemedDisposalTaxPaid?: number;
  taxNotes?: string;
}

export interface FireCalculationResult {
  fireNumberNominal: number;
  fireNumberReal: number;
  monthlyDisposableTarget: number;
  annualGrossWithdrawalNeeded: number;
  annualTaxAtRetirement: number;
  effectiveTaxRateAtRetirement: number;
  
  yearsToFire: number;
  ageAtFire: number;
  calendarYearAtFire: number;
  isAlreadyFire: boolean;
  
  currentTotalNetWorth: number;
  projectedPortfolioAtFire: number;
  
  projections: YearProjection[];
  portfolioSurvivalYears: number; // How many years portfolio lasts
  finalPortfolioValue: number;
  isSustainable: boolean; // Does it survive to life expectancy?
}
