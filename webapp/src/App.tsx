import React, { useState } from 'react';
import { Container, Box, Typography, Alert, ThemeProvider, createTheme, Grid } from '@mui/material';
import InputPanel from './components/InputPanel';
import ResultsPanel from './components/ResultsPanel';
import SimulationCanvas from './components/SimulationCanvas';
import { SimulationParams, CollisionResults } from './components/simulationCanvas/types';
import { DEFAULT_AGE, DEFAULT_IMPACTTYPE, DEFAULT_MASS1LBS, DEFAULT_MASS2LBS, DEFAULT_MAXHEIGHT, DEFAULT_VINIT1, DEFAULT_VINIT2, LENGTH_SWING } from './simulation/constants';

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

interface ErrorBoundaryState {
  hasError: boolean;
  errorMessage: string | null;
}

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, errorMessage: null };
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, errorMessage: error.message };
  }
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
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
    age: DEFAULT_AGE,
    maxHeight: DEFAULT_MAXHEIGHT,
    mass1Lbs: DEFAULT_MASS1LBS,
    mass2Lbs: DEFAULT_MASS2LBS,
    vInit1: DEFAULT_VINIT1,
    vInit2: DEFAULT_VINIT2,
    impactType: DEFAULT_IMPACTTYPE,
  });
  const [results, setResults] = useState<CollisionResults | null>(null);
  const [isCollision, setIsCollision] = useState<boolean>(false);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [resetSignal, setResetSignal] = useState<boolean>(false);

  const updateParams = (newParams: Partial<SimulationParams>) => {
    setParams((prev) => ({ ...prev, ...newParams }));
    setError(null);
  };

  const toggleSimulation = () => {
    if (isCollision) {
      // Cas : Redémarrer après une collision
      setResetSignal(true);
      setResults(null);
      setIsCollision(false);
      setIsRunning(true);
      // Réinitialiser resetSignal après usage
      setTimeout(() => setResetSignal(false), 0);
    } else if (isRunning) {
      // Cas : Arrêter la simulation
      setIsRunning(false);
    } else {
      // Cas : Démarrer la simulation
      try {
        const { age, maxHeight, mass1Lbs, mass2Lbs, vInit1, vInit2 } = params;
        if (isNaN(age) || ![1, 2, 3, 4, 5].includes(age)) {
          throw new Error("L'âge doit être entre 1 et 5 ans.");
        }
        if (isNaN(maxHeight) || maxHeight <= 0) {
          throw new Error('La hauteur doit être > 0.');
        }
        if (maxHeight > LENGTH_SWING) {
          throw new Error(`La hauteur d'oscillation ne peut pas dépasser la longueur de la balançoire (${LENGTH_SWING} m).`);
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
      setIsCollision(true);
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <ErrorBoundary>
        {/* Top Menu Row */}
        <Grid
          container
          spacing={2}
          sx={{
            px: 2,
            py: 1,
            bgcolor: '#f5f5f5',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Grid
            item
            xs={12}
            sx={{
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
            }}
          >
            <Typography variant="h4" align="center" gutterBottom>
              Simulation de collisions de balançoires
            </Typography>
          </Grid>
        </Grid>

        {/* Main Content Row */}
        <Grid
          container
          spacing={2}
          sx={{
            height: 'calc(100vh - 120px)',
            px: 2,
          }}
        >
          {/* Error Alert */}
          {error && (
            <Grid item xs={12}>
              <Alert severity="error" sx={{ mb: 2, maxWidth: '800px', mx: 'auto' }}>
                {error}
              </Alert>
            </Grid>
          )}

          {/* Sidebar */}
          <Grid
            item
            xs={12}
            sm={5}
            md={4}
            sx={{ height: '100%' }}
          >
            <Box
              sx={{
                border: '2px solid #ccc',
                p: 2,
                bgcolor: '#fff',
                overflowY: 'auto',
                height: '100%',
              }}
            >
              <InputPanel
                params={params}
                updateParams={updateParams}
                toggleSimulation={toggleSimulation}
                isRunning={isRunning}
                isCollision={isCollision}
              />
              <ResultsPanel results={results} />
            </Box>
          </Grid>

          {/* Canvas */}
          <Grid
            item
            xs={12}
            sm={7}
            md={8}
            sx={{ height: '100%' }}
          >
            <Box
              sx={{
                border: '2px solid #ccc',
                p: 2,
                bgcolor: '#fff',
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                boxSizing: 'border-box',
              }}
            >
              <Typography variant="h6" align="center" gutterBottom>
                Animation des balançoires
              </Typography>
              <Box
                sx={{
                  flex: 1,
                  width: '100%',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  overflow: 'hidden',
                  boxSizing: 'border-box',
                }}
              >
                <SimulationCanvas
                  params={params}
                  running={isRunning}
                  onCollision={handleCollision}
                  setIsRunning={setIsRunning}
                  resetSignal={resetSignal}
                  sx={{ width: '100%', height: '100%' }}
                />
              </Box>
            </Box>
          </Grid>
        </Grid>
      </ErrorBoundary>
    </ThemeProvider>
  );
};

export default App;