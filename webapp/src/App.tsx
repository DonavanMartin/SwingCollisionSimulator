import React, { useRef, useState, useCallback } from 'react';
import { Container, Box, Typography, Alert, ThemeProvider, createTheme, Grid, Link } from '@mui/material';
import InputPanel from './components/InputPanel';
import ResultsPanel from './components/ResultsPanel';
import SimulationCanvas from './components/SimulationCanvas';
import { SimulationParams, CollisionResults } from './components/simulationCanvas/types';
import { DEFAULT_AGE, DEFAULT_IMPACTTYPE, DEFAULT_MASS1LBS, DEFAULT_MASS2LBS, DEFAULT_MAXHEIGHT, DEFAULT_VINIT1, DEFAULT_VINIT2, LENGTH_SWING, VERSION_NUMBER_MAJOR, VERSION_NUMBER_MINOR, VERSION_NUMBER_PATCH } from './simulation/constants';
import GitHubIcon from '@mui/icons-material/GitHub';

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

  const canvasRef = useRef<HTMLDivElement>(null);

  const scrollToCanvas = useCallback(() => {
    if (canvasRef.current) {
      // Try scrollIntoView first
      canvasRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
      // Fallback: Force scroll after a short delay
      setTimeout(() => {
        if (canvasRef.current) {
          const rect = canvasRef.current.getBoundingClientRect();
          const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
          const targetY = rect.top + scrollTop - 20; // Small offset for padding
          window.scrollTo({ top: targetY, behavior: 'smooth' });
          console.log('Scrolled to:', targetY, 'Rect:', rect.top);
        } else {
          console.warn('canvasRef.current is null during fallback');
        }
      }, 100);
    } else {
      console.warn('canvasRef.current is null');
    }
  }, []);

  const updateParams = (newParams: Partial<SimulationParams>) => {
    setParams((prev) => ({ ...prev, ...newParams }));
    setError(null);
  };

  const toggleSimulation = () => {
    if (isCollision) {
      // Restart after collision
      setResetSignal(true);
      setResults(null);
      setIsCollision(false);
      setIsRunning(true);
      setTimeout(() => setResetSignal(false), 0);
    } else if (isRunning) {
      // Stop simulation
      setIsRunning(false);
    } else {
      // Start simulation
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
        scrollToCanvas(); // Moved after state update
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
        <Grid container spacing={2} sx={{ p: { xs: 1, sm: 2 } }}>
          <Grid size={12} sx={{ position: 'relative', textAlign: 'center' }}>
            <Typography
              variant="h4"
              sx={{
                fontSize: { xs: '1.5rem', sm: '2rem', md: '2.5rem' },
              }}
            >
              Simulation de collisions de balançoires
            </Typography>
            <Box
              sx={{
                position: 'absolute',
                top: 0,
                right: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-end',
              }}
            >
              <Typography variant="body2" sx={{ fontWeight: 'bold', lineHeight: 1 }}>
                {'v' + VERSION_NUMBER_MAJOR +'.' +VERSION_NUMBER_MINOR + '.' +VERSION_NUMBER_PATCH }
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1 }}>
              <Link
                href="https://github.com/DonavanMartin/SwingCollisionSimulator"
                target="_blank"
                rel="noopener noreferrer"
                sx={{ textDecoration: 'none', color: 'primary.main', display: 'flex', alignItems: 'center' }}
              >
                <GitHubIcon sx={{ fontSize: '1rem', mr: 0.5 }} />
                GitHub
              </Link>
              </Typography>
            </Box>
          </Grid>
        
          <Grid size={12}>
            {/* Error Alert */}
            {error && (
              <Alert
                severity="error"
                sx={{
                  mb: 2,
                  maxWidth: { xs: '100%', sm: '800px' },
                  mx: 'auto',
                }}
              >
                {error}
              </Alert>
            )}
          </Grid>
        
          {/* Main Content Row */}
          <Grid size={{ xs: 12, sm: 4 }}>
            <Box
              sx={{
                border: '2px solid #ccc',
                p: { xs: 1, sm: 2 },
                bgcolor: '#fff',
                boxSizing: 'border-box',
                height: { xs: 'auto', sm: '100%' },
                overflowY: { xs: 'visible', sm: 'auto' },
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
          <Grid size={{ xs: 12, sm: 8 }}>
            <Box
              ref={canvasRef}
              sx={{
                border: '2px solid #ccc',
                p: { xs: 1, sm: 2 },
                bgcolor: '#fff',
                boxSizing: 'border-box',
                height: { xs: '400px', sm: '100%' },
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
              }}
            >
              <Typography
                variant="h6"
                align="center"
                gutterBottom
                sx={{
                  fontSize: { xs: '1rem', sm: '1.25rem' },
                }}
              >
                Animation des balançoires
              </Typography>
              <Box
                sx={{
                  flex: 1,
                  width: '100%',
                  overflow: 'hidden',
                }}
              >
                <SimulationCanvas
                  params={params}
                  running={isRunning}
                  onCollision={handleCollision}
                  setIsRunning={setIsRunning}
                  resetSignal={resetSignal}
                  sx={{
                    width: '100%',
                    height: '100%',
                  }}
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