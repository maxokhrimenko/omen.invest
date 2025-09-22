import React from 'react';

const Logo: React.FC = () => {
  return (
    <img 
      src="/logo.png" 
      alt="Portfolio Analyzer Logo" 
      width="48" 
      height="48"
      style={{ 
        borderRadius: '50%',
        objectFit: 'cover'
      }}
    />
  );
};

export default Logo;
