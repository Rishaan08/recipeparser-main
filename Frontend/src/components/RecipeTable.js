import React, { useState, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  TablePagination,
  CircularProgress,
  Alert,
  TextField,
  Button,
  Box
} from '@mui/material';
import axios from 'axios';

const RecipeTable = () => {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [totalRecipes, setTotalRecipes] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    fetchRecipes();
  }, [page, rowsPerPage]);

  const fetchRecipes = async () => {
    try {
      setLoading(true);
      const baseUrl = isSearching && searchTerm
        ? `http://localhost:8000/api/recipes/search`
        : `http://localhost:8000/api/recipes`;

      const params = isSearching && searchTerm
        ? { page: page + 1, limit: rowsPerPage, title: searchTerm }
        : { page: page + 1, limit: rowsPerPage, sort: 'desc' };

      const response = await axios.get(baseUrl, { params });
      setRecipes(response.data.data);
      setTotalRecipes(response.data.total);
      setError(null);
    } catch (err) {
      setError('Failed to fetch recipes. Please try again later.');
      console.error('Error fetching recipes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setIsSearching(Boolean(searchTerm && searchTerm.trim().length > 0));
    setPage(0);
  };

  const clearSearch = () => {
    setSearchTerm('');
    setIsSearching(false);
    setPage(0);
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '20px' }}>
        <CircularProgress />
      </div>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      <Box sx={{ p: 2, display: 'flex', gap: 2, alignItems: 'center' }}>
        <TextField
          label="Search title"
          variant="outlined"
          size="small"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSearch(); }}
        />
        <Button variant="contained" onClick={handleSearch}>Search</Button>
        <Button variant="outlined" onClick={clearSearch}>Clear</Button>
      </Box>
      <TableContainer sx={{ maxHeight: 440 }}>
        <Table stickyHeader aria-label="recipe table">
          <TableHead>
            <TableRow>
              <TableCell>Title</TableCell>
              <TableCell>Cuisine</TableCell>
              <TableCell align="right">Rating</TableCell>
              <TableCell align="right">Total Time (min)</TableCell>
              <TableCell align="right">Serves</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {recipes.map((recipe) => (
              <TableRow hover key={recipe.id}>
                <TableCell component="th" scope="row">
                  {recipe.title}
                </TableCell>
                <TableCell>{recipe.cuisine}</TableCell>
                <TableCell align="right">
                  {recipe.rating !== null && recipe.rating !== undefined 
                    ? recipe.rating.toFixed(1) 
                    : 'N/A'}
                </TableCell>
                <TableCell align="right">{recipe.total_time || 'N/A'}</TableCell>
                <TableCell align="right">{recipe.serves || 'N/A'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <TablePagination
        rowsPerPageOptions={[10, 25, 50]}
        component="div"
        count={totalRecipes}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handleChangePage}
        onRowsPerPageChange={handleChangeRowsPerPage}
      />
    </Paper>
  );
};

export default RecipeTable; 