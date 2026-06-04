// types/index.ts
export type Flavor = 'chocolate' | 'vanilla' | 'strawberry' | 'pistachio' | 'mint' | 'coffee';

export interface Product {
  id: number;
  name: string;
  flavor: Flavor;
  price: number;
  description: string;
  stock: number;
  image_url: string;
}

export interface CartItem extends Product {
  quantity: number;
}

export interface OrderItem {
  product_id: number;
  flavor: Flavor;
  quantity: number;
  price: number;
}

export type OrderStatus = 'pending' | 'confirmed' | 'preparing' | 'ready' | 'delivered' | 'cancelled';

export interface Order {
  id: number;
  customer_name: string;
  customer_email: string;
  items: OrderItem[];
  total_amount: number;
  status: OrderStatus;
  created_at: string;
  updated_at?: string;
}

export interface ApiError {
  detail: string;
  status?: number;
}