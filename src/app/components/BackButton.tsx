// src/components/BackButton.tsx
"use client";

import React from 'react';
import { useRouter } from 'next/navigation';

export default function BackButton() {
  const router = useRouter();

  const handleBack = () => {
    // If opened in a new tab/window, close it. Otherwise, route back to dashboard.
    if (typeof window !== 'undefined' && window.opener) {
      window.close();
    } else {
      router.push('/'); // Change '/' to your actual dashboard route if different
    }
  };

  return (
    <button 
      onClick={handleBack} 
      className="btn btn-secondary"
      title="Go Back to Main Dashboard"
      style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
    >
      <i className="fa-solid fa-arrow-left"></i> Back to Main Dashboard
    </button>
  );
}