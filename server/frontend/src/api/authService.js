import api from './axios';

export const registerUser = async (userData) => {
    const response = await api.post('/users/', userData);
    return response.data;
};

export const loginUser = async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
};

export const logoutUser = async () => {
    const response = await api.post('/auth/logout');
    return response.data;
};

export const getCurrentUser = async () => {
    const response = await api.get('/users/me');
    return response.data;
};

export const deleteCurrentUser = async () => {
    const response = await api.delete('/users/me');
    return response.data;
};