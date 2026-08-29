export type GeneSignature = {
  SYMBOL: string;
  Average_Log2fc: number;
  Adj_p_101: number;
  Adj_p_104: number;
  Log2fc_101: number;
  Log2fc_104: number;
};

export type CrossSpeciesRow = {
  Gene: string;
  Mouse_Log2FC: number;
  Mouse_Adj_P: number;
  Human_Log2FC: number;
  Agreement: string;
  Human_Source: string;
};

export type DrugCandidate = {
  Rank: number;
  Drug: string;
  CMap_Score: number;
  FDA_Status: string;
  Target: string;
  Mechanism: string;
};

export type BenchmarkRow = {
  Stage: string;
  Time_s: number;
  Peak_RAM_MB: number;
};

export type PCAPoint = {
  PC1: number;
  PC2: number;
  Sample: string;
  Condition: string;
};
