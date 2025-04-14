import React from 'react';
import { Box, Typography } from '@mui/material';
import { CONCUSSION_ACCELERATION_THRESHOLD, G, HIC_THRESHOLD, PEAK_ACCELERATION_THRESHOLD } from '../simulation/constants';

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
  hic: number;
  peakAcceleration: number; // Added: Peak acceleration in m/s²
  accelerationMs2: number;
  isSafe: boolean; // Added: Overall safety indicator
}

interface ResultsPanelProps {
  results: CollisionResults | null;
}

const getRiskColor = (risk: string) => {
  switch (risk) {
    case 'Improbable':
      return 'success';
    case 'Possible':
    case 'Probable':
    case 'Très probable':
      return 'error';
    default:
      return 'text.primary'; // Fallback for unknown risk levels
  }
};

// Helper function to determine font weight
const getRiskFontWeight = (risk: string) => {
  return risk === 'Probable' || risk === 'Très probable' ? 'bold' : 'normal';
};

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
          <Typography
              color={results.isSafe ? 'success' : 'error'}
              sx={{ fontWeight: 'bold', mt: 1 }}
            >
              <strong>Sécurité globale :</strong> {results.isSafe ? 'Sûr' : 'Risqué'}
            </Typography>
            <Typography
              color={results.hic > HIC_THRESHOLD ? 'error' : 'success'}
              sx={{ fontWeight: results.hic > HIC_THRESHOLD ? 'bold' : 'normal' }}
            >
              <strong>HIC :</strong> {results.hic.toFixed(2)} {results.hic > HIC_THRESHOLD ? '(Dangereux)' : '(Sûr)'}
            </Typography>
            <Typography
              color={results.accelerationMs2 > CONCUSSION_ACCELERATION_THRESHOLD ? 'error' : 'success'}
              sx={{ fontWeight: results.accelerationMs2 > CONCUSSION_ACCELERATION_THRESHOLD ? 'bold' : 'normal' }}
            >
              <strong>Accélération cérébrale:</strong> {(results.accelerationMs2).toFixed(1)} M/s²{' '}
              {results.accelerationMs2 > CONCUSSION_ACCELERATION_THRESHOLD ? '(Dangereux)' : '(Sûr)'}
            </Typography>
            <Typography
              color={getRiskColor(results.decapitationRisk)}
              sx={{ fontWeight: getRiskFontWeight(results.decapitationRisk) }}
            >
              <strong>Probabilité de décapitation partielle :</strong> {results.decapitationRisk}
            </Typography>
            <Typography
              color={getRiskColor(results.cervicalFractureRisk)}
              sx={{ fontWeight: getRiskFontWeight(results.cervicalFractureRisk) }}
            >
              <strong>Probabilité de fracture cervicale :</strong> {results.cervicalFractureRisk}
            </Typography>
            <Typography
              color={results.peakAcceleration > PEAK_ACCELERATION_THRESHOLD ? 'error' : 'success'}
              sx={{ fontWeight: results.peakAcceleration > PEAK_ACCELERATION_THRESHOLD ? 'bold' : 'normal' }}
            >
              <strong>Accélération maximale :</strong> {(results.peakAcceleration / G).toFixed(1)} g{' '}
              {results.peakAcceleration > PEAK_ACCELERATION_THRESHOLD ? '(Dangereux)' : '(Sûr)'}
            </Typography>
            <Typography
              color={getRiskColor(results.concussionRisk)}
              sx={{ fontWeight: getRiskFontWeight(results.concussionRisk) }}
            >
              <strong>Probabilité de commotion cérébrale :</strong> {results.concussionRisk}
            </Typography>
            <Typography>
              <strong>Âge de l'enfant :</strong> {results.age} ans
            </Typography>
            <Typography>
              <strong>Hauteur d'oscillation max :</strong> {results.maxHeight.toFixed(2)} m
            </Typography>
            <Typography>
              <strong>Masse balançoire 1 :</strong> {results.mass1Lbs.toFixed(1)} lbs (
              {results.mass1Kg.toFixed(1)} kg)
            </Typography>
            <Typography>
              <strong>Masse balançoire 2 :</strong> {results.mass2Lbs.toFixed(1)} lbs (
              {results.mass2Kg.toFixed(1)} kg)
            </Typography>
            <Typography>
              <strong>Vitesse initiale balançoire 1 :</strong> {results.vInit1.toFixed(2)} m/s
            </Typography>
            <Typography>
              <strong>Vitesse initiale balançoire 2 :</strong> {results.vInit2.toFixed(2)} m/s
            </Typography>
            <Typography>
              <strong>Angle d'impact 1 (horizontal) :</strong> {results.angleHorizontal1.toFixed(1)}°
            </Typography>
            <Typography>
              <strong>Angle d'impact 2 (horizontal) :</strong> {results.angleHorizontal2.toFixed(1)}°
            </Typography>
            <Typography>
              <strong>Type d'impact :</strong> {results.impactType}
            </Typography>
            <Typography>
              <strong>Vitesse d'impact balançoire 1 :</strong> {results.velocity1.toFixed(2)} m/s
            </Typography>
            <Typography>
              <strong>Vitesse d'impact balançoire 2 :</strong> {results.velocity2.toFixed(2)} m/s
            </Typography>
            <Typography>
              <strong>Vitesse relative d'impact :</strong> {results.relativeVelocity.toFixed(2)} m/s
            </Typography>
            <Typography>
              <strong>Force d'impact :</strong> {results.force.toFixed(2)} N
            </Typography>
            <Typography>
              <strong>Surface d'impact :</strong> {results.surfaceCm2.toFixed(2)} cm²
            </Typography>
            <Typography>
              <strong>Pression exercée :</strong> {results.pressureMPa.toFixed(2)} MPa
            </Typography>
          </>
        ) : (
          <Typography>Aucun résultat disponible.</Typography>
        )}
      </Box>
    </Box>
  );
};

export default ResultsPanel;