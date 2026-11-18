import api from './axios';

export const getAllEmergencies = async () => {
  const response = await api.get('/emergencies/');
  return response.data;
};

export const getUnresolvedEmergencies = async () => {
  const response = await api.get('/emergencies/?unresolved_only=true');
  return response.data;
};

export const resolveEmergency = async (emergencyId) => {
  const response = await api.patch(`/emergencies/${emergencyId}/resolve`);
  return response.data;
};