// src/simulation/models.tsx

// Enum for risk levels, matching Python's RiskLevel values
export enum RiskLevel {
    IMPROBABLE = 1,
    POSSIBLE = 2,
    PROBABLE = 3,
    TRES_PROBABLE = 4,
  }
  
  // Interface for risk level metadata
  interface RiskLevelData {
    value: RiskLevel;
    displayName: string;
  }
  
  // Mapping of RiskLevel to display names
  const riskLevelData: { [key in RiskLevel]: RiskLevelData } = {
    [RiskLevel.IMPROBABLE]: {
      value: RiskLevel.IMPROBABLE,
      displayName: 'Improbable',
    },
    [RiskLevel.POSSIBLE]: {
      value: RiskLevel.POSSIBLE,
      displayName: 'Possible',
    },
    [RiskLevel.PROBABLE]: {
      value: RiskLevel.PROBABLE,
      displayName: 'Probable',
    },
    [RiskLevel.TRES_PROBABLE]: {
      value: RiskLevel.TRES_PROBABLE,
      displayName: 'Très probable',
    },
  };
  
  // Utility function to get display name, mimicking Python's display_name property
  export function getRiskLevelDisplayName(level: RiskLevel): string {
    return riskLevelData[level].displayName;
  }
  
  // Utility function to convert RiskLevel to string (mimics Python's __str__)
  export function riskLevelToString(level: RiskLevel): string {
    return getRiskLevelDisplayName(level);
  }