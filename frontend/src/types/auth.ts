export interface User {
  id: number;
  username: string;
  full_name: string;
  is_active: boolean;
  role_code: string | null;
  role_name: string | null;
  permission_codes: string[];
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenData {
  access_token: string;
  token_type: string;
  user: User;
}
