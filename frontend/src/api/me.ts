import { apiClient } from './client';

export interface MeResponse {
  username: string;
  role: string;
  is_staff: boolean;
}

export const getMe = async (): Promise<MeResponse> => {
  const { data } = await apiClient.get<MeResponse>('/auth/me/');
  return data;
};
