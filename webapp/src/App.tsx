import React, { useState, Component, ErrorInfo } from 'react';
import { Container, Box, Typography, Alert, ThemeProvider, createTheme } from '@mui/material';
import InputPanel from './components/InputPanel';
import ResultsPanel from './components/ResultsPanel';
import SimulationCanvas from './components/SimulationCanvas';
import { calculateMaxAngle } from './simulation/calculations';
import { LENGTH_SWING } from './simulation/constants';

const theme = createTheme({
  typography: {
    fontFamily: 'Arial, sans-serif',
  },
  palette: {
    background: {
      default: '#f0f0f0',
    },
  },
});

interface SimulationParams {
  age: number;
  maxHeight: number;
  mass1Lbs: number;
  mass2Lbs: number;
  vInit1: number;
  vInit2: number;
  impactType: 'frontal' | 'concentré';
}

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

interface ErrorBoundaryState {
  hasError: boolean;
  errorMessage: string | null;
}

class ErrorBoundary extends Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = {
    hasError: false,
    errorMessage: null,
  };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, errorMessage: error.message };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box sx={{ p: 2 }}>
          <Typography variant="h5" color="error">
            Une erreur s'est produite : {this.state.errorMessage}
          </Typography>
          <Typography>
            Veuillez rafraîchir la page ou vérifier les paramètres.
          </Typography>
        </Box>
      );
    }
    return this.props.children;
  }
}

const App: React.FC = () => {
  const [params, setParams] = useState<SimulationParams>({
    age: 1,
    maxHeight: 1,
    mass1Lbs: 100,
    mass2Lbs: 100,
    vInit1: 0,
    vInit2: 0,
    impactType: 'frontal',
  });
  const [results, setResults] = useState<CollisionResults | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const updateParams = (newParams: Partial<SimulationParams>) => {
    setParams((prev) => ({ ...prev, ...newParams }));
    setError(null);
  };

  const toggleSimulation = () => {
    if (isRunning) {
      setIsRunning(false);
    } else {
      try {
        const { age, maxHeight, mass1Lbs, mass2Lbs, vInit1, vInit2 } = params;
        if (isNaN(age) || ![1, 2, 3, 4, 5].includes(age)) {
          throw new Error("L'âge doit être entre 1 et 5 ans.");
        }
        if (isNaN(maxHeight) || maxHeight <= 0) {
          throw new Error('La hauteur doit être > 0.');
        }
        if (maxHeight > LENGTH_SWING) {
          throw new Error(`La hauteur d'osc BEFORE d'oscillation ne peut pas dépasser la longueur de la balançoire (${LENGTH_SWING} m).`);
        }
        if (isNaN(mass1Lbs) || isNaN(mass2Lbs) || mass1Lbs <= 0 || mass2Lbs <= 0) {
          throw new Error('La masse des balançoires doit être supérieure à 0.');
        }
        if (isNaN(vInit1) || isNaN(vInit2) || vInit1 < 0 || vInit2 < 0) {
          throw new Error('Les vitesses initiales ne peuvent pas être négatives.');
        }
        setIsRunning(true);
        setError(null);
      } catch (err) {
        setError((err as Error).message);
      }
    }
  };

  const handleCollision = (results: CollisionResults | null) => {
    if (results) {
      setResults(results);
      setIsRunning(false);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <ErrorBoundary>
        <Container sx={{ width: 1200, height: 800, bgcolor: 'background.default', p: 2 }}>
          <Typography variant="h4" align="center" gutterBottom>
            Simulation de collision de balançoires
          </Typography>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <Box display="flex" gap={2} height="calc(100% - 80px)">
            <Box
              sx={{
                width: 400,
                border: '2px solid #ccc',
                p: 2,
                bgcolor: '#fff',
                overflowY: 'auto',
              }}
            >
              <InputPanel params={params} updateParams={updateParams} toggleSimulation={toggleSimulation} isRunning={isRunning} />
              <ResultsPanel results={results} />
            </Box>
            <Box
              sx={{
                flex: 1,
                border: '2px solid #ccc',
                p: 1,
                bgcolor: '#fff',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              <Typography variant="h6" align="center" gutterBottom>
                Animation des balançoires
              </Typography>
              <SimulationCanvas params={params} running={isRunning} onCollision={handleCollision} />
            </Box>
          </Box>
        </Container>
      </ErrorBoundary>
    </ThemeProvider>
  );
};

export default App;