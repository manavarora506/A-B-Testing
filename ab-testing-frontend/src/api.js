import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',  // FastAPI backend base URL
});

// Example: Get form config
export const getFormConfig = () => {
  return api.get('/admin/form-config');
};

// Example: Save form config
export const saveFormConfig = (formConfig) => {
  return api.put('/admin/save-form-config', formConfig);
};

// Example: Update routing probability
export const updateRoutingProbability = (probability) => {
    console.log(probability)
  return api.put('/admin/update-routing-probability', { probability });
};

// Example: Get routing probability
export const getMetrics = () => {
  return api.get('/metrics');
};

// Example: Submit form data for Site A
export const submitFormSiteA = (formData) => {
  return api.post('/submit-form/site-a', formData);
};

// Example: Submit form data for Site B
export const submitFormSiteB = (formData) => {
  return api.post('/submit-form/site-b', formData);
};

export default api;
