import api from './axios';

export const getConnectedDevices = async () => {
    const response = await api.get('/devices/connected');
    return response.data;
};

export const getPendingDevices = async () => {
    const response = await api.get('/devices/pendings');
    return response.data;
};

export const connectDevice = async (deviceId) => {
    const response = await api.patch('/devices/' + deviceId + '/connect');
    return response.data;
};

export const refuseDevice = async (deviceId) => {
    const response = await api.patch('/devices/' + deviceId + '/refuse');
    return response.data;
};