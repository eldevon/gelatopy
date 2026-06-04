// app/orders/[id]/page.tsx
'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { apiClient } from '../../../services/api';
import { Order } from '../../../types';
import { formatPrice } from '../../../utils/formatPrice';
import toast from 'react-hot-toast';

const statusColors = {
  pending: 'bg-yellow-100 text-yellow-800',
  confirmed: 'bg-blue-100 text-blue-800',
  preparing: 'bg-purple-100 text-purple-800',
  ready: 'bg-green-100 text-green-800',
  delivered: 'bg-gray-100 text-gray-800',
  cancelled: 'bg-red-100 text-red-800',
};

const statusSteps = ['pending', 'confirmed', 'preparing', 'ready', 'delivered'];

export default function OrderConfirmation() {
  const params = useParams();
  const router = useRouter();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadOrder();
  }, [params.id]);

  const loadOrder = async () => {
    try {
      const data = await apiClient.getOrder(Number(params.id));
      setOrder(data);
    } catch (error) {
      toast.error('Failed to load order');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getCurrentStep = () => {
    if (!order) return -1;
    return statusSteps.indexOf(order.status);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-4xl animate-spin mb-4">🍨</div>
          <p className="text-gray-600">Loading your order...</p>
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-red-600 mb-4">Order not found</p>
          <button
            onClick={() => router.push('/')}
            className="text-purple-600 hover:text-purple-700"
          >
            Back to Shop
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-purple-50 py-12">
      <div className="max-w-3xl mx-auto px-4">
        {/* Success Header */}
        <div className="text-center mb-8">
          <div className="text-6xl mb-4">🎉</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Order Confirmed!
          </h1>
          <p className="text-gray-600">
            Thank you for your order, {order.customer_name}!
          </p>
        </div>

        {/* Order Card */}
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
          {/* Order Header */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
            <div className="flex justify-between items-center text-white">
              <div>
                <p className="text-sm opacity-90">Order Number</p>
                <p className="text-2xl font-bold">#{order.id}</p>
              </div>
              <div className="text-right">
                <p className="text-sm opacity-90">Order Date</p>
                <p className="font-semibold">
                  {new Date(order.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>

          {/* Order Status */}
          <div className="px-6 py-4 border-b">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-gray-700">Order Status</span>
              <span className={`px-3 py-1 rounded-full text-sm font-semibold ${statusColors[order.status]}`}>
                {order.status.toUpperCase()}
              </span>
            </div>
            
            {/* Progress Bar */}
            <div className="mt-4">
              <div className="flex justify-between mb-2">
                {statusSteps.map((step, idx) => (
                  <div key={step} className="text-center flex-1">
                    <div className={`text-xs ${
                      idx <= getCurrentStep() ? 'text-purple-600' : 'text-gray-400'
                    }`}>
                      {step.charAt(0).toUpperCase() + step.slice(1)}
                    </div>
                  </div>
                ))}
              </div>
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-600 to-pink-600 transition-all duration-500"
                  style={{ width: `${((getCurrentStep() + 1) / statusSteps.length) * 100}%` }}
                />
              </div>
            </div>
          </div>

          {/* Order Items */}
          <div className="px-6 py-4 border-b">
            <h2 className="font-semibold text-gray-900 mb-3">Order Items</h2>
            <div className="space-y-3">
              {order.items.map((item, idx) => (
                <div key={idx} className="flex justify-between items-center">
                  <div>
                    <p className="font-medium capitalize">{item.flavor}</p>
                    <p className="text-sm text-gray-500">Quantity: {item.quantity}</p>
                  </div>
                  <p className="font-semibold">{formatPrice(item.price * item.quantity)}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Order Total */}
          <div className="px-6 py-4 bg-gray-50">
            <div className="flex justify-between items-center">
              <span className="font-bold text-lg">Total</span>
              <span className="text-2xl font-bold text-purple-600">
                {formatPrice(order.total_amount)}
              </span>
            </div>
          </div>

          {/* Customer Info */}
          <div className="px-6 py-4 border-t">
            <h3 className="font-semibold text-gray-900 mb-2">Customer Information</h3>
            <p className="text-gray-600">{order.customer_name}</p>
            <p className="text-gray-600">{order.customer_email}</p>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex gap-4 justify-center">
          <button
            onClick={() => router.push('/')}
            className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Continue Shopping
          </button>
          <button
            onClick={() => window.print()}
            className="px-6 py-2 border border-purple-600 text-purple-600 rounded-lg hover:bg-purple-50 transition-colors"
          >
            Print Receipt
          </button>
        </div>
      </div>
    </div>
  );
}