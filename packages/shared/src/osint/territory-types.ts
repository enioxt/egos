/**
 * territory-types.ts — @egos/shared/osint
 *
 * Brazil territory type definitions — states, regions, municipalities.
 * Provides standardized IBGE code usage across Eagle Eye and any OSINT consumer.
 */

export type BrazilRegion = 'Norte' | 'Nordeste' | 'Centro-Oeste' | 'Sudeste' | 'Sul';

export type BrazilStateAbbr =
  | 'AC' | 'AL' | 'AP' | 'AM' | 'BA' | 'CE' | 'DF' | 'ES' | 'GO'
  | 'MA' | 'MT' | 'MS' | 'MG' | 'PA' | 'PB' | 'PR' | 'PE' | 'PI'
  | 'RJ' | 'RN' | 'RS' | 'RO' | 'RR' | 'SC' | 'SP' | 'SE' | 'TO';

export interface BrazilState {
  /** 2-letter abbreviation */
  abbr: BrazilStateAbbr;
  /** Full name */
  name: string;
  /** IBGE 2-digit state code */
  ibgeCode: string;
  region: BrazilRegion;
  capital: string;
  /** Population estimate */
  populationEst?: number;
}

export interface BrazilMunicipality {
  /** IBGE 7-digit city code */
  ibgeCode: string;
  name: string;
  stateAbbr: BrazilStateAbbr;
  /** Whether this city has a Diário Oficial tracked by Querido Diário */
  hasGazette: boolean;
  /** Population estimate */
  populationEst?: number;
  /** GDP per capita estimate in BRL */
  gdpPerCapitaBrl?: number;
}

export interface TerritoryFilter {
  regions?: BrazilRegion[];
  states?: BrazilStateAbbr[];
  /** IBGE 7-digit codes */
  municipalityCodes?: string[];
  /** Minimum population to include */
  minPopulation?: number;
}
