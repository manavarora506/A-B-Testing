import React, { useState, useEffect } from 'react';
import { TextField, Button, Container, Typography, Box, Paper } from '@mui/material';
import { getFormConfig } from '../api';

function FormB() {
  const [formData, setFormData] = useState({});
  const [formConfig, setFormConfig] = useState({});

  useEffect(() => {
    async function fetchConfig() {
      try {
        const response = await getFormConfig();
        setFormConfig(response.data);
        // Initialize formData based on config
        const initialFormData = response.data.fields.reduce((acc, field) => {
          acc[field.name] = '';
          return acc;
        }, {});
        setFormData(initialFormData);
      } catch (error) {
        console.error('Error fetching form config:', error);
      }
    }
    fetchConfig();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/submit-form/site-b', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });
      const result = await response.json();
      if (response.ok) {
        alert('Form submitted successfully');
        setFormData({});
      } else {
        alert('Error submitting form');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  return (
    <Container component="main" maxWidth="xs">
      <Paper
        elevation={3}
        sx={{
          padding: 3,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          backgroundColor: formConfig.styles?.background_color || '#f0f8ff',
          fontFamily: formConfig.styles?.font_family || 'Arial, sans-serif',
        }}
       >
        {/* Render images dynamically */}
        {formConfig.images?.map((imgUrl, index) => (
          <img
            key={index}
            src={imgUrl}
            alt={`Form Image ${index + 1}`}
            style={{ width: '100%', marginBottom: '10px' }}
          />
        ))}
        <Typography variant="h5">Contact Us</Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          {formConfig.fields?.map((field) => (
            <TextField
              key={field.name}
              variant="outlined"
              margin="normal"
              required={field.required}
              fullWidth
              label={field.label}
              name={field.name}
              type={field.type}
              multiline={field.type === 'textarea'}
              rows={field.type === 'textarea' ? 4 : 1}
              value={formData[field.name] || ''}
              onChange={handleChange}
            />
          ))}
          <Button type="submit" fullWidth variant="contained" sx={{ mt: 2 }}>
            Submit
          </Button>
        </Box>
      </Paper>
    </Container>
  );
}

export default FormB;
