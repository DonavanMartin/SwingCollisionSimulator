import React from 'react';
import { Box, Typography, TextField, MenuItem, FormControl, FormLabel, RadioGroup, FormControlLabel, Radio, Button } from '@mui/material';

interface SimulationParams {
  age: number;
  maxHeight: number;
  mass1Lbs: number;
  mass2Lbs: number;
  vInit1: number;
  vInit2: number;
  impactType: 'frontal' | 'concentré';
}

interface InputPanelProps {
  params: SimulationParams;
  updateParams: (newParams: Partial<SimulationParams>) => void;
  toggleSimulation: () => void;
  isRunning: boolean;
  onReset: () => void;
}

const InputPanel: React.FC<InputPanelProps> = ({ params, updateParams, toggleSimulation, isRunning, onReset }) => {
  const handleNumberChange = (key: keyof SimulationParams, value: string) => {
    const num = parseFloat(value);
    if (!isNaN(num)) {
      updateParams({ [key]: num });
    }
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
        Paramètres de simulation
      </Typography>
      <Box display="flex" flexDirection="column" gap={1}>
        <TextField
          select
          label="Âge de l'enfant (ans)"
          value={params.age}
          onChange={(e) => updateParams({ age: parseInt(e.target.value) })}
          size="small"
          sx={{ width: 120 }}
        >
          {[1, 2, 3, 4, 5].map((age) => (
            <MenuItem key={age} value={age}>
              {age}
            </MenuItem>
          ))}
        </TextField>
        <TextField
          label="Hauteur d'oscillation max (m)"
          type="number"
          value={params.maxHeight}
          onChange={(e) => handleNumberChange('maxHeight', e.target.value)}
          size="small"
          inputProps={{ step: 0.1 }}
        />
        <TextField
          label="Masse balançoire 1 (lbs)"
          type="number"
          value={params.mass1Lbs}
          onChange={(e) => handleNumberChange('mass1Lbs', e.target.value)}
          size="small"
          inputProps={{ step: 1 }}
        />
        <TextField
          label="Masse balançoire 2 (lbs)"
          type="number"
          value={params.mass2Lbs}
          onChange={(e) => handleNumberChange('mass2Lbs', e.target.value)}
          size="small"
          inputProps={{ step: 1 }}
        />
        <TextField
          label="Vitesse initiale balançoire 1 (m/s)"
          type="number"
          value={params.vInit1}
          onChange={(e) => handleNumberChange('vInit1', e.target.value)}
          size="small"
          inputProps={{ step: 0.1 }}
        />
        <TextField
          label="Vitesse initiale balançoire 2 (m/s)"
          type="number"
          value={params.vInit2}
          onChange={(e) => handleNumberChange('vInit2', e.target.value)}
          size="small"
          inputProps={{ step: 0.1 }}
        />
        <FormControl>
          <FormLabel>Type d'impact</FormLabel>
          <RadioGroup
            value={params.impactType}
            onChange={(e) => updateParams({ impactType: e.target.value as 'frontal' | 'concentré' })}
          >
            <FormControlLabel value="frontal" control={<Radio size="small" />} label="Frontal" />
            <FormControlLabel value="concentré" control={<Radio size="small" />} label="Concentré (bord étroit)" />
          </RadioGroup>
        </FormControl>
        <Box display="flex" gap={1} mt={1}>
          <Button
            variant="contained"
            color="primary"
            onClick={toggleSimulation}
          >
            {isRunning ? 'Arrêter' : 'Démarrer'}
          </Button>

          <Button
            disabled={!isRunning}
            variant="contained"
            color="primary"
            onClick={onReset}
          >
            Redémarrer
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default InputPanel;