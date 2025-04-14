import React from 'react';
import { Box, Typography } from '@mui/material';

interface CollisionResults {
  age: number;
  maxHeight: number;
  mass1Lbs: number;
  mass1Kg: number;
  mass2Lbs: number;
  mass2Kg: number;
  vInit1: number;
  vInit2: number;
  angleHorizontal1: number;
  angleHorizontal2: number;
  impactType: string;
  velocity1: number;
  velocity2: number;
  relativeVelocity: number;
  force: number;
  surfaceCm2: number;
  pressureMPa: number;
  decapitationRisk: string;
  cervicalFractureRisk: string;
  concussionRisk: string;
}

interface ResultsPanelProps {
  results: CollisionResults | null;
}

const ResultsPanel: React.FC<ResultsPanelProps> = ({ results }) => {
  return (
    <Box mt={2}>
      <Typography variant="h6" gutterBottom sx={{ fontWeight: 'bold' }}>
        Résultats de la simulation
      </Typography>
      <Box
        sx={{
          bgcolor: '#f5f5f5',
          p: 2,
          borderRadius: 1,
          height: 500,
          overflowY: 'auto',
          fontFamily: 'Arial, sans-serif',
          fontSize: '0.9rem',
        }}
      >
        {results ? (
          <>
            <Typography>Âge de l'enfant : {results.age} ans</Typography>
            <Typography>Hauteur d'oscillation max : {results.maxHeight.toFixed(2)} m</Typography>
            <Typography>
              Masse balançoire 1 : {results.mass1Lbs.toFixed(1)} lbs ({results.mass1Kg.toFixed(1)} kg)
            </Typography>
            <Typography>
              Masse balançoire 2 : {results.mass2Lbs.toFixed(1)} lbs ({results.mass2Kg.toFixed(1)} kg)
            </Typography>
            <Typography>Vitesse initiale balançoire 1 : {results.vInit1.toFixed(2)} m/s</Typography>
            <Typography>Vitesse initiale balançoire 2 : {results.vInit2.toFixed(2)} m/s</Typography>
            <Typography>
              Angle d'impact 1 (par rapport à l'horizontal) : {results.angleHorizontal1.toFixed(1)}°
            </Typography>
            <Typography>
              Angle d'impact 2 (par rapport à l'horizontal) : {results.angleHorizontal2.toFixed(1)}°
            </Typography>
            <Typography>Type d'impact : {results.impactType}</Typography>
            <Typography>Vitesse d'impact balançoire 1 : {results.velocity1.toFixed(2)} m/s</Typography>
            <Typography>Vitesse d'impact balançoire 2 : {results.velocity2.toFixed(2)} m/s</Typography>
            <Typography>Vitesse relative d'impact : {results.relativeVelocity.toFixed(2)} m/s</Typography>
            <Typography>Force d'impact : {results.force.toFixed(2)} N</Typography>
            <Typography>Surface d'impact : {results.surfaceCm2.toFixed(2)} cm²</Typography>
            <Typography>Pression exercée : {results.pressureMPa.toFixed(2)} MPa</Typography>
            <Typography>Probabilité de décapitation partielle : {results.decapitationRisk}</Typography>
            <Typography>Probabilité de fracture cervicale : {results.cervicalFractureRisk}</Typography>
            <Typography>Probabilité de commotion cérébrale : {results.concussionRisk}</Typography>
          </>
        ) : (
          <Typography>Aucun résultat disponible.</Typography>
        )}
      </Box>
    </Box>
  );
};

export default ResultsPanel;