import axios from 'axios';
import { Client, Choice } from '../types';

const API_URL = '/api/v1';

const getAuthHeaders = () => ({
  headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
});

const transformClientData = (clientData: any): Client => {
  return {
    id: clientData.id,
    name: clientData.name,
    activeSession: clientData.active_session
  };
};

export const fetchClients = async (): Promise<Client[]> => {
  const response = await axios.get<Client[]>(`${API_URL}/clients`, getAuthHeaders());
  return response.data.map(transformClientData);
};

interface Data {
  choices1: Choice[];
  choices2: Choice[];
}

type ApiResponse = [Choice[], Choice[]];

export const fetchClientChoices = async (clientId: string): Promise<Data> => {
  try {
    const response = await axios.get<ApiResponse>(`${API_URL}/clients/${clientId}/choices`, getAuthHeaders());
    const result = response.data;

    return {
      choices1: result[0] || [], // First array in the response
      choices2: result[1] || []  // Second array in the response
    };
  } catch (error) {
    console.error('Error fetching data:', error);
    return { choices1: [], choices2: [] }; // Ensure it always returns an object with choices1 and choices2
  }
};
  

export const logout = async (): Promise<void> => {
  await axios.post(`${API_URL}/auth/logout`, null, getAuthHeaders());
};

export const handleSession = async (clientId: string, sessionId: string | null): Promise<void> => {
  const url = `${API_URL}/clients/${clientId}/sessions${sessionId ? `/${sessionId}/finish` : ''}`;
  const method = sessionId ? 'patch' : 'post';
  await axios({ method, url, ...getAuthHeaders() });
};

export const deleteClient = async (clientId: string): Promise<void> => {
  await axios.delete<void>(`${API_URL}/clients/${clientId}`, getAuthHeaders());
};

export const fetchQuestions = async (queryType: string): Promise<any[]> => {
  const response = await axios.get<any[]>(`${API_URL}/questions/${queryType}`, getAuthHeaders());
  return response.data;
};
