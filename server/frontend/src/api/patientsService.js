import api from './axios';

export const addPatient = async (patientData) => {
    const response = await api.post('/patients/', patientData);
    return response.data;
};

export const getAllPatients = async () => {
    const response = await api.get('/patients/');
    return response.data;
};

export const getPatientById = async (patientId) => {
  const response = await api.get(`/patients/${patientId}`);
  return response.data;
};


export const createAssociation = async (associationData) => {
    const response = await api.post('/associations/', associationData);
    return response.data;
};

export const getActiveAssociations = async () => {
    const response = await api.get('/associations/');
    return response.data;
};