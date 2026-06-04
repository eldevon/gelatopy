// hooks/useOrder.ts
import { useState } from 'react';
import { apiClient } from '../services/api';
import { Order, OrderItem } from '../types';
import toast from 'react-hot-toast';

export const useOrder = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [currentOrder, setCurrentOrder] = useState<Order | null>(null);

  const createOrder = async (
    customerName: string,
    customerEmail: string,
    items: OrderItem[]
  ) => {
    setIsLoading(true);
    try {
      const order = await apiClient.createOrder(customerName, customerEmail, items);
      setCurrentOrder(order);
      toast.success(`Order #${order.id} created successfully!`);
      return order;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Failed to create order';
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const getOrder = async (orderId: number) => {
    setIsLoading(true);
    try {
      const order = await apiClient.getOrder(orderId);
      setCurrentOrder(order);
      return order;
    } catch (error: any) {
      toast.error('Failed to fetch order');
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    createOrder,
    getOrder,
    currentOrder,
    isLoading,
  };
};