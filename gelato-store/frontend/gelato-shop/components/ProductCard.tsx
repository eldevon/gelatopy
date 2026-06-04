// components/ProductCard.tsx
import React from 'react';
import Image from 'next/image';
import { Product } from '../types';
import { formatPrice } from '../utils/formatPrice';

interface ProductCardProps {
  product: Product;
  onAddToCart: (product: Product) => void;
}

const flavorColors = {
  chocolate: 'from-amber-800 to-amber-600',
  vanilla: 'from-yellow-100 to-yellow-200',
  strawberry: 'from-pink-300 to-pink-400',
  pistachio: 'from-green-300 to-green-400',
  mint: 'from-green-200 to-green-300',
  coffee: 'from-amber-700 to-amber-800',
};

const flavorEmojis = {
  chocolate: '🍫',
  vanilla: '🍦',
  strawberry: '🍓',
  pistachio: '🥜',
  mint: '🌿',
  coffee: '☕',
};

export const ProductCard: React.FC<ProductCardProps> = ({ product, onAddToCart }) => {
  const [isHovered, setIsHovered] = React.useState(false);

  return (
    <div
      className="bg-white rounded-2xl shadow-lg overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className={`h-48 bg-gradient-to-br ${flavorColors[product.flavor]} relative`}>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-7xl transform transition-transform duration-300"
            style={{ transform: isHovered ? 'scale(1.1)' : 'scale(1)' }}>
            {flavorEmojis[product.flavor]}
          </span>
        </div>
        {product.stock < 10 && product.stock > 0 && (
          <div className="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded-full">
            Only {product.stock} left!
          </div>
        )}
        {product.stock === 0 && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <span className="text-white font-bold text-lg">Out of Stock</span>
          </div>
        )}
      </div>
      
      <div className="p-5">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-xl font-bold text-gray-800">{product.name}</h3>
          <span className="text-2xl font-bold text-purple-600">
            {formatPrice(product.price)}
          </span>
        </div>
        
        <p className="text-gray-600 text-sm mb-4">{product.description}</p>
        
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1">
            <span className="text-yellow-400">★</span>
            <span className="text-yellow-400">★</span>
            <span className="text-yellow-400">★</span>
            <span className="text-yellow-400">★</span>
            <span className="text-gray-300">★</span>
            <span className="text-gray-500 text-sm ml-1">(24)</span>
          </div>
          
          <button
            onClick={() => onAddToCart(product)}
            disabled={product.stock === 0}
            className={`px-5 py-2 rounded-full font-semibold transition-all duration-300
              ${product.stock > 0
                ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white hover:shadow-lg hover:scale-105'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
              }`}
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
};