import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import RecipeTable from './components/RecipeTable';

function App() {
  return (
    <Container maxWidth="lg">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Recipe List
        </Typography>
        <RecipeTable />
      </Box>
    </Container>
  );
}

export default App;