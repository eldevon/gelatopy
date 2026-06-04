// services/api.ts
import axios, { AxiosInstance, AxiosError } from 'axios';
import { Product, Order, OrderItem, ApiError } from '../types';

class ApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    // Use environment variable for API URL
    this.baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response) {
          console.error('API Error:', error.response.data);
          throw error;
        }
        throw new Error('Network error. Please check your connection.');
      }
    );
  }

  async getProducts(): Promise<Product[]> {
    const response = await this.client.get('/products');
    return response.data;
  }

  async getProductByFlavor(flavor: string): Promise<Product> {
    const response = await this.client.get(`/products/${flavor}`);
    return response.data;
  }

  async createOrder(
    customerName: string,
    customerEmail: string,
    items: OrderItem[]
  ): Promise<Order> {
    const response = await this.client.post('/orders', {
      customer_name: customerName,
      customer_email: customerEmail,
      items,
    });
    return response.data;
  }

  async getOrder(orderId: number): Promise<Order> {
    const response = await this.client.get(`/orders/${orderId}`);
    return response.data;
  }
}

export const apiClient = new ApiClient();