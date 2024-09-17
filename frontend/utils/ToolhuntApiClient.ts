// utils/ToolhuntApiClient.ts

export interface User {
  id: string
  username: string
  email: string
  // Add any other user properties here
}

export interface Task {
  id: string;
  field: string;
  tool: {
    title: string;
    description: string;
    url: string;
  };
  // Add other task properties as needed
}

export interface AnnotationsSchema {
  schemas: {
    Annotations: {
      properties: Record<string, any>;
    };
    [key: string]: any;
  };
  // Add other schema properties as needed
}

export interface ContributionData {
  rank: number;
  username: string;
  contributions: number;
}

export interface ContributionsResponse {
  contributions: ContributionData[];
}

export interface ContributionsParams {
  days?: number;
  limit?: number;
}

const API_BASE_URL = 'http://localhost:8082/api/v1'

class ToolhuntApiClient {
  private async fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`)
    }

    return response
  }

  // Auth-related methods
  async fetchUserData(): Promise<User | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/user`, {
        credentials: 'include'
      })
      if (response.ok) {
        return await response.json()
      } else {
        console.error(`Failed to fetch user data: ${response.status}`)
        return null
      }
    } catch (error) {
      console.error('Error fetching user data:', error)
      return null
    }
  }

  login(redirectPath: string): void {
    const loginUrl = `${API_BASE_URL}/auth/login?redirect_after=${encodeURIComponent(redirectPath)}`
    window.location.href = loginUrl
  }

  async handleCallback(code: string, state: string): Promise<{ user: User; redirectTo: string }> {
    const response = await fetch(`${API_BASE_URL}/auth/callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, state }),
      credentials: 'include'
    })
    if (response.ok) {
      const data = await response.json()
      return {
        user: data.user,
        redirectTo: data.redirect_to
      }
    } else {
      throw new Error(`Login failed: ${response.status}`)
    }
  }

  async logout(): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      credentials: 'include'
    })
    if (!response.ok) {
      throw new Error(`Logout failed: ${response.status}`)
    }
  }

  // Task-related methods
  async fetchTasks(toolName: string | null = null, fieldNames: string | null = null): Promise<Task[]> {
    const params = new URLSearchParams()
    if (toolName) params.append('tool_name', toolName)
    if (fieldNames) params.append('field_names', fieldNames)

    const response = await this.fetchWithAuth(`/tasks?${params.toString()}`)
    return response.json()
  }

  async fetchFieldNames(): Promise<string[]> {
    const response = await this.fetchWithAuth('/fields')
    return response.json()
  }

  async fetchAnnotationsSchema(): Promise<AnnotationsSchema> {
    const response = await this.fetchWithAuth('/schema')
    return response.json()
  }

  async fetchContributions(params?: ContributionsParams): Promise<ContributionsResponse> {
    let url = '/metrics/contributions';
    if (params) {
      const queryParams = new URLSearchParams();
      if (params.days !== undefined) queryParams.append('days', params.days.toString());
      if (params.limit !== undefined) queryParams.append('limit', params.limit.toString());
      url += `?${queryParams.toString()}`;
    }
    const response = await this.fetchWithAuth(url);
    return response.json();
  }

  // Add other API methods as needed
}

export const toolhuntApi = new ToolhuntApiClient()
