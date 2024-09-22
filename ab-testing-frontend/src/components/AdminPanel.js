import React, { useState, useEffect } from 'react';
import { TextField, Button, Container, Typography, Box, Paper, IconButton, Select, MenuItem, InputLabel, FormControl } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import { getFormConfig, saveFormConfig, updateRoutingProbability } from '../api'; // Adjust import path accordingly

function AdminPanel() {
  const [formConfig, setFormConfig] = useState({
    fields: [],
    styles: {
      background_color: '#f0f8ff',
      font_family: 'Arial, sans-serif',
    },
    images: []
  });
  const [newField, setNewField] = useState({ type: 'text', label: '', name: '', required: false });
  const [routingProbability, setRoutingProbability] = useState(0.5);
  const [formImages, setFormImages] = useState(['']);
  const [showImageInput, setShowImageInput] = useState(false); // Track if image input is visible

  // Fetch the form config from the backend when the component mounts
  useEffect(() => {
    async function fetchConfig() {
      try {
        const response = await getFormConfig();
        setFormConfig(response.data);  // Ensure formConfig is loaded correctly
        setRoutingProbability(response.data.routing_probability || 0.5); // Load routing probability
        setFormImages(response.data.images || []);
      } catch (error) {
        console.error('Error fetching form config:', error);
      }
    }
    fetchConfig();
  }, []);

  // Update form field configuration
  const handleFormUpdate = async () => {
    try {
      const configToSave = {
        ...formConfig,
        routing_probability: routingProbability,  // Include routing probability in form config
        images: formImages  // Ensure images are saved in form config
      };
      await saveFormConfig(configToSave);
      alert('Form configuration updated successfully');
    } catch (error) {
      console.error('Error updating form config:', error);
    }
  };

  // Update routing probability
  const handleProbabilityUpdate = async () => {
    try {
      await updateRoutingProbability(routingProbability);
      alert('Routing probability updated successfully');
    } catch (error) {
      console.error('Error updating routing probability:', error);
    }
  };

  // Add a new form field
  const addNewField = () => {
    setFormConfig({
      ...formConfig,
      fields: [...(formConfig.fields || []), newField],  // Safely add the new field
    });
    setNewField({ type: 'text', label: '', name: '', required: false });  // Reset field input
  };

  // Remove a form field
  const removeField = (index) => {
    const updatedFields = formConfig.fields.filter((_, i) => i !== index);
    setFormConfig({ ...formConfig, fields: updatedFields });
  };

  // Update styles dynamically
  const updateStyle = (style, value) => {
    setFormConfig({
      ...formConfig,
      styles: {
        ...formConfig.styles,
        [style]: value,
      },
    });
  };

  // Add new image URL
  const addImage = () => {
    setFormImages([...formImages, '']);
    setShowImageInput(true); // Show the image input field
  };

  // Confirm image URL and hide input field
  const confirmImage = () => {
    setShowImageInput(false);
  };

  const updateImage = (index, url) => {
    const updatedImages = [...formImages];
    updatedImages[index] = url;
    setFormImages(updatedImages);
  };

  // Remove image by index
  const removeImage = (index) => {
    const updatedImages = formImages.filter((_, i) => i !== index);
    setFormImages(updatedImages);
  };

  return (
    <Container component="main" maxWidth="md" sx={{ padding: 4 }}>
      <Typography variant="h4" gutterBottom>Admin Panel</Typography>

      {/* Update Form Fields */}
      <Paper elevation={3} sx={{ padding: 3, marginBottom: 4 }}>
        <Typography variant="h6" gutterBottom>Update Form Fields</Typography>
        {formConfig.fields && formConfig.fields.length > 0 ? (  // Safety check for fields
          formConfig.fields.map((field, index) => (
            <Box key={index} sx={{ marginBottom: 2, display: 'flex', alignItems: 'center' }}>
              <Typography variant="body1" sx={{ flexGrow: 1 }}>
                {field.label} ({field.type})
              </Typography>
              <IconButton onClick={() => removeField(index)} color="error">
                <DeleteIcon />
              </IconButton>
            </Box>
          ))
        ) : (
          <Typography variant="body1" color="textSecondary">No fields available.</Typography>
        )}

        <Box sx={{ marginTop: 2 }}>
          <Typography variant="h6" gutterBottom>Add New Field</Typography>
          <FormControl fullWidth sx={{ marginBottom: 2 }}>
            <InputLabel>Type</InputLabel>
            <Select
              value={newField.type}
              onChange={(e) => setNewField({ ...newField, type: e.target.value })}
              label="Type"
            >
              <MenuItem value="text">Text</MenuItem>
              <MenuItem value="email">Email</MenuItem>
              <MenuItem value="textarea">Textarea</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Label"
            value={newField.label}
            onChange={(e) => setNewField({ ...newField, label: e.target.value })}
            sx={{ marginBottom: 2 }}
          />
          <TextField
            fullWidth
            label="Name"
            value={newField.name}
            onChange={(e) => setNewField({ ...newField, name: e.target.value })}
            sx={{ marginBottom: 2 }}
          />
          <FormControl sx={{ marginBottom: 2 }}>
            <InputLabel>Required</InputLabel>
            <Select
              value={newField.required ? 'yes' : 'no'}
              onChange={(e) => setNewField({ ...newField, required: e.target.value === 'yes' })}
            >
              <MenuItem value="yes">Yes</MenuItem>
              <MenuItem value="no">No</MenuItem>
            </Select>
          </FormControl>
          <Button variant="contained" color="primary" onClick={addNewField}>Add Field</Button>
        </Box>
      </Paper>

      {/* Update Styles */}
      <Paper elevation={3} sx={{ padding: 3, marginBottom: 4 }}>
        <Typography variant="h6" gutterBottom>Update Styles</Typography>
        <Box sx={{ marginBottom: 2 }}>
          <Typography variant="body1">Background Color</Typography>
          <input
            type="color"
            value={formConfig.styles?.background_color || '#f0f8ff'}  // Safe access to styles
            onChange={(e) => updateStyle('background_color', e.target.value)}
            style={{ width: '100%', height: '40px', border: 'none' }}
          />
        </Box>
        <TextField
          fullWidth
          label="Font Family"
          value={formConfig.styles?.font_family || 'Arial, sans-serif'}  // Safe access to styles
          onChange={(e) => updateStyle('font_family', e.target.value)}
        />
      </Paper>

      {/* Update Routing Probability */}
      <Paper elevation={3} sx={{ padding: 3, marginBottom: 4 }}>
        <Typography variant="h6" gutterBottom>Update Routing Probability</Typography>
        <TextField
          type="number"
          label="Routing Probability"
          value={routingProbability}
          onChange={(e) => setRoutingProbability(Number(e.target.value))}
          min={0}  // Apply directly
          max={1}  
          step={0.1} 
          sx={{ marginBottom: 2 }}
        />
        <Button variant="contained" color="primary" onClick={handleProbabilityUpdate}>Update Probability</Button>
      </Paper>

      {/* Manage Images */}
      <Paper elevation={3} sx={{ padding: 3, marginBottom: 4 }}>
        <Typography variant="h6" gutterBottom>Manage Images</Typography>
        {formImages.map((imgUrl, index) => (
          <Box key={index} sx={{ display: 'flex', alignItems: 'center', marginBottom: 2 }}>
            <TextField
              fullWidth
              label={`Image URL ${index + 1}`}
              value={imgUrl}
              onChange={(e) => updateImage(index, e.target.value)}
              sx={{ marginRight: 2 }}
            />
            <IconButton onClick={() => removeImage(index)} color="error">
              <DeleteIcon />
            </IconButton>
          </Box>
        ))}
        <Button variant="contained" onClick={addImage}>
          Add Another Image
        </Button>
      </Paper>

      {/* Save Changes */}
      <Button variant="contained" color="primary" onClick={handleFormUpdate}>
        Save Changes
      </Button>

      {/* Live Preview */}
      <Paper elevation={3} sx={{ padding: 3, marginTop: 4 }}>
        <Typography variant="h6" gutterBottom>Live Preview</Typography>
        <Box
          sx={{
            backgroundColor: formConfig.styles?.background_color || '#f0f8ff',
            fontFamily: formConfig.styles?.font_family || 'Arial, sans-serif',
            padding: 3,
            borderRadius: 1,
          }}
        >
          {formConfig.fields?.map((field, index) => (
            <TextField
              key={index}
              fullWidth
              label={field.label}
              required={field.required}
              type={field.type}
              sx={{ marginBottom: 2 }}
            />
          ))}

          {/* Render Images */}
          {formImages.map((imgUrl, index) => (
            imgUrl && <img key={index} src={imgUrl} alt={`Form image ${index + 1}`} style={{ maxWidth: '100%', marginTop: '16px' }} />
          ))}
        </Box>
      </Paper>
    </Container>
  );
}

export default AdminPanel;
